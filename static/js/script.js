"use strict";

///////////////////////////////////////
//// VARIABLES
const navLogo = document.querySelector(".nav--logo");
const allNavBtns = document.querySelectorAll(".nav--scroll");

const nav = document.querySelector(".nav");
const header = document.querySelector(".header");

///////////////////////////////////////
//// NAV FADE ANIMATION (PASSING 'ARGUMENTS' TO EVENT HANDLERS)
const handleHover = function (e) {
  if (e.target.classList.contains("nav__link")) {
    const link = e.target;
    const siblings = link.closest(".nav").querySelectorAll(".nav__link");
    const logo = link.closest(".nav").querySelector("img");

    siblings.forEach((ele) => {
      if (ele != link) ele.style.opacity = this;
    });
    logo.style.opacity = this;
  }
};

nav.addEventListener("mouseover", handleHover.bind(0.5));
nav.addEventListener("mouseout", handleHover.bind(1));
