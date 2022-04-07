const doc = document.firstElementChild;
const themeToggle = document.querySelector(".theme-toggle");
const themeToggleBtnLight = document.querySelector(".theme-toggle-light");
const themeToggleBtnDark = document.querySelector(".theme-toggle-dark");

// Get the users theme preference
// First checks for any preference set in local storage
// Then for dark mode preference at the OS level
const getThemePreference = () => {
  if (localStorage.getItem("pla-theme")) {
    return localStorage.getItem("pla-theme");
  } else {
    return window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light";
  }
};

const setThemePreference = () => {
  localStorage.setItem("pla-theme", theme);
  applyTheme();
};

const applyTheme = () => {
  doc.setAttribute("color-scheme", theme);
  themeToggle?.setAttribute("aria-live", theme);
  themeToggleBtnDark?.classList.toggle("hidden", theme === "dark");
  themeToggleBtnLight?.classList.toggle("hidden", theme === "light");
};

let theme = getThemePreference();

// set early so no page flashes
applyTheme();

window.onload = () => {
  // set on load so screen readers can see latest value on the button
  applyTheme();

  themeToggle.addEventListener("click", (e) => {
    theme = theme === "light" ? "dark" : "light";
    setThemePreference();
  });
};

window
  .matchMedia("(prefers-color-scheme: dark)")
  .addEventListener("change", ({ matches: isDark }) => {
    theme = isDark ? "dark" : "light";
    setThemePreference();
  });
