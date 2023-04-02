from django.contrib import messages
from django.contrib.auth import login, authenticate, REDIRECT_FIELD_NAME
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LogoutView as BaseLogoutView, PasswordChangeView as BasePasswordChangeView,
    PasswordResetDoneView as BasePasswordResetDoneView, PasswordResetConfirmView as BasePasswordResetConfirmView,
)
from django.shortcuts import get_object_or_404, redirect
from django.utils.crypto import get_random_string
from django.utils.decorators import method_decorator
from django.utils.http import url_has_allowed_host_and_scheme as is_safe_url
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import View, FormView
from django.conf import settings
from .utils import (
    send_activation_email, send_reset_password_email, send_forgotten_username_email, send_activation_change_email,
)
from .forms import (
    SignInViaUsernameForm, SignInViaEmailForm, SignInViaEmailOrUsernameForm, SignUpForm,
    RestorePasswordForm, RestorePasswordViaEmailOrUsernameForm, RemindUsernameForm,
    ResendActivationCodeForm, ResendActivationCodeViaEmailForm, ChangeProfileForm, ChangeEmailForm,
)
from django.contrib.auth import get_user_model
from .models import User as MyUser
from django.views.generic import TemplateView
from django.forms import ValidationError
import json

User = get_user_model()

class IndexPageView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context =  super(IndexPageView, self).get_context_data(**kwargs)
        context['title'] = "Home"
        return context

class GuestOnlyView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)
        return super().dispatch(request, *args, **kwargs)
    
class LogInView(GuestOnlyView, FormView):
    template_name = 'accounts/log_in.html'

    @staticmethod
    def get_form_class(**kwargs):
        if settings.DISABLE_USERNAME or settings.LOGIN_VIA_EMAIL:
            return SignInViaEmailForm
        if settings.LOGIN_VIA_EMAIL_OR_USERNAME:
            return SignInViaEmailOrUsernameForm
        return SignInViaUsernameForm

    @method_decorator(sensitive_post_parameters('password'))
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        request.session.set_test_cookie()
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        request = self.request
        if request.session.test_cookie_worked():
            request.session.delete_test_cookie()
        if settings.USE_REMEMBER_ME:
            if not form.cleaned_data['remember_me']:
                request.session.set_expiry(0)
        login(request, form.user_cache)
        redirect_to = request.POST.get(REDIRECT_FIELD_NAME, request.GET.get(REDIRECT_FIELD_NAME))
        url_is_safe = is_safe_url(redirect_to, allowed_hosts=request.get_host(), require_https=request.is_secure())
        if url_is_safe:
            return redirect(redirect_to)
        return redirect(settings.LOGIN_REDIRECT_URL)
    
    def get_context_data(self, **kwargs):
        context = super(LogInView, self).get_context_data(**kwargs)
        context['title'] = 'Login'
        return context

class SignUpView(GuestOnlyView, FormView):
    template_name = 'accounts/sign_up.html'
    form_class = SignUpForm

    def form_valid(self, form):
        request = self.request
        user = form.save(commit=False)
        if settings.DISABLE_USERNAME:
            user.username = get_random_string()
        else:
            user.username = form.cleaned_data['username']
        if settings.ENABLE_USER_ACTIVATION:
            user.is_active = False
            user.save()
        if settings.DISABLE_USERNAME:
            user.username = f'user_{user.id}'
            user.save()
        if settings.ENABLE_USER_ACTIVATION:
            code = get_random_string(20)
            user.code = code
            user.save()
            send_activation_email(request, user.email, code)
            messages.success(
                request, _('You are signed up. To activate the account, follow the link sent to the mail.'))
        else:
            raw_password = form.cleaned_data['password1']
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            messages.success(request, _('You are successfully signed up!'))
        return redirect('accounts:log_in')
    
    def get_context_data(self, **kwargs):
        context = super(SignUpView, self).get_context_data(**kwargs)
        context['title'] = 'Register'
        return context

class ActivateView(View):
    @staticmethod
    def get(request, code):
        act = get_object_or_404(MyUser, code=code)
        act.is_active = True
        act.save()
        messages.success(request, _('You have successfully activated your account!'))
        return redirect('accounts:log_in')

class ResendActivationCodeView(GuestOnlyView, FormView):
    template_name = 'accounts/resend_activation_code.html'

    @staticmethod
    def get_form_class(**kwargs):
        if settings.DISABLE_USERNAME:
            return ResendActivationCodeViaEmailForm
        return ResendActivationCodeForm

    def form_valid(self, form):
        user = form.user_cache
        code = get_random_string(20)
        act = MyUser()
        act = user
        act.code = code
        act.save()
        send_activation_email(self.request, user.email, code)
        messages.success(self.request, _('A new activation code has been sent to your email address.'))
        return redirect('accounts:resend_activation_code')
    
    def get_context_data(self, **kwargs):
        context = super(ResendActivationCodeView, self).get_context_data(**kwargs)
        context['title'] = 'Resend Authentication Code'
        return context

class RestorePasswordView(GuestOnlyView, FormView):
    template_name = 'accounts/restore_password.html'

    @staticmethod
    def get_form_class(**kwargs):
        if settings.RESTORE_PASSWORD_VIA_EMAIL_OR_USERNAME:
            return RestorePasswordViaEmailOrUsernameForm
        return RestorePasswordForm

    def form_valid(self, form):
        user = form.user_cache
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        if isinstance(uid, bytes):
            uid = uid.decode()
        send_reset_password_email(self.request, user.email, token, uid)
        return redirect('accounts:restore_password_done')
    
    def get_context_data(self, **kwargs):
        context = super(RestorePasswordView, self).get_context_data(**kwargs)
        context['title'] = 'Restore Password'
        return context

class ChangeProfileView(LoginRequiredMixin, FormView):
    template_name = 'accounts/profile/change_profile.html'
    form_class = ChangeProfileForm

    def get_initial(self):
        user = self.request.user
        initial = super().get_initial()
        initial['first_name'] = user.first_name
        initial['last_name'] = user.last_name
        return initial

    def form_valid(self, form):
        user = self.request.user
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        user.save()
        messages.success(self.request, _('Profile data has been successfully updated.'))
        return redirect('accounts:change_profile')
        
    def get_context_data(self, **kwargs):
        context = super(ChangeProfileView, self).get_context_data(**kwargs)
        context['title'] = 'Change Profile'
        return context


class ChangeEmailView(LoginRequiredMixin, FormView):
    template_name = 'accounts/profile/change_email.html'
    form_class = ChangeEmailForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        initial['email'] = self.request.user.email
        return initial

    def form_valid(self, form):
        user = self.request.user
        email = form.cleaned_data['email']
        if settings.ENABLE_ACTIVATION_AFTER_EMAIL_CHANGE:
            code = get_random_string(20)
            user.code = code
            user.email = email
            user.save()
            send_activation_change_email(self.request, email, code)
            messages.success(self.request, _('To complete the change of email address, click on the link sent to it.'))
        else:
            user.email = email
            user.save()
            messages.success(self.request, _('Email successfully changed.'))
        return redirect('accounts:change_email')
    
    def get_context_data(self, **kwargs):
        context = super(ChangeEmailView, self).get_context_data(**kwargs)
        context['title'] = 'Change Email'
        return context

class ChangeEmailActivateView(View):
    @staticmethod
    def get(request, code):
        act = get_object_or_404(MyUser, code=code)
        user = act
        user.email = act.email
        user.save()
        messages.success(request, _('You have successfully changed your email!'))
        return redirect('accounts:change_email')

class RemindUsernameView(GuestOnlyView, FormView):
    template_name = 'accounts/remind_username.html'
    form_class = RemindUsernameForm

    def form_valid(self, form):
        user = form.user_cache
        send_forgotten_username_email(user.email, user.username)
        messages.success(self.request, _('Your username has been successfully sent to your email.'))
        return redirect('accounts:remind_username')
    
    def get_context_data(self, **kwargs):
        context = super(RemindUsernameView, self).get_context_data(**kwargs)
        context['title'] = 'Remind Username'
        return context

class ChangePasswordView(BasePasswordChangeView):
    template_name = 'accounts/profile/change_password.html'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, _('Your password was changed.'))
        return redirect('accounts:change_password')
    
    def get_context_data(self, **kwargs):
        context = super(ChangePasswordView, self).get_context_data(**kwargs)
        context['title'] = 'Restore Password'
        return context

class RestorePasswordConfirmView(BasePasswordResetConfirmView):
    template_name = 'accounts/restore_password_confirm.html'

    def form_valid(self, form):
        form.save()
        messages.success(self.request, _('Your password has been set. You may go ahead and log in now.'))
        return redirect('accounts:log_in')
    
    def get_context_data(self, **kwargs):
        context = super(RestorePasswordConfirmView, self).get_context_data(**kwargs)
        context['title'] = 'Restore Password'
        return context

class RestorePasswordDoneView(BasePasswordResetDoneView):
    template_name = 'accounts/restore_password_done.html'

    def get_context_data(self, **kwargs):
        context = super(RestorePasswordDoneView, self).get_context_data(**kwargs)
        context['title'] = 'Restore Password'
        return context

class LogOutView(LoginRequiredMixin, BaseLogoutView):
    template_name = 'accounts/log_out.html'

    def get_context_data(self, **kwargs):
        context = super(LogOutView, self).get_context_data(**kwargs)
        context['title'] = 'LogOut'
        return context