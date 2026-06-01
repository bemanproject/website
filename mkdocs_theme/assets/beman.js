const toggle = document.querySelector(".nav-toggle");
const menu = document.querySelector("#nav-menu");
const themeToggles = document.querySelectorAll(".theme-toggle");

function currentTheme() {
  return document.documentElement.getAttribute("data-theme") === "dark"
    ? "dark"
    : "light";
}

function setTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  themeToggles.forEach((themeToggle) => {
    const label = `Switch between dark and light mode (currently ${theme} mode)`;
    themeToggle.setAttribute("aria-label", label);
    themeToggle.setAttribute("title", label);
    themeToggle.setAttribute("aria-pressed", String(theme === "dark"));
  });
  try {
    window.localStorage.setItem("theme", theme);
  } catch (err) {
    // Ignore storage failures in private browsing contexts.
  }
}

if (toggle && menu) {
  toggle.addEventListener("click", () => {
    const expanded = toggle.getAttribute("aria-expanded") === "true";
    toggle.setAttribute("aria-expanded", String(!expanded));
    menu.classList.toggle("open", !expanded);
  });
}

setTheme(currentTheme());

themeToggles.forEach((themeToggle) => {
  themeToggle.addEventListener("click", () => {
    setTheme(currentTheme() === "dark" ? "light" : "dark");
  });
});
