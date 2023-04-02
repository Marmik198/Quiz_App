# Quiz_App

This is a quiz application developed with Django and Vanilla JS

## Steps to run the project

1. Clone this repository
2. Make sure you have python downloaded on your system
3. On the terminal run:
``` 
pip install -r requirements.txt
```

4. Now in the Quiz_App directory create a file named .env and enter following code in it:
```
SECRET_KEY=somesecretkey
DEBUG=True
EMAIL=test@gmail.com
PASSWORD=testtesttesttest
```
Notes : <br>
i. You have to create a django secret key and paste it corresponding to the SECRET_KEY variable in .env file <br>
ii. You have to add your gmail id and paste it corresponding to the EMAIL variable in .env file <br>
iii. You have to generate an app password for your gmail account from gmail settings (first enable 2-factor authentication) <br>
iv. You have to add your gmail's app password and paste it corresponding to the PASSWORD variable in .env file <br><br>

5. Again on terminal run,
```
python manage.py makemigrations
```

6. Now on terminal run,
```
python manage.py migrate
```

7. Create a superuser by running this command
```
python manage.py createsuperuser
```

8. Atlast your application is ready to run, run
```
python manage.py runserver
```
