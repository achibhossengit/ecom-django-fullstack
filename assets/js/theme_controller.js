const setTheme = (mode) => {
  if (mode !== "light" && mode !== "dark") {
    console.error(`Got invalid theme mode: ${mode}. Resetting to light.`);
    mode = "light";
  }

  document.documentElement.dataset.theme = mode;
  localStorage.setItem("theme", mode);
};

const alter_theme = () => {
  const currentTheme = localStorage.getItem("theme", "light");

  if (currentTheme === "light") {
    setTheme("dark");
  } else {
    setTheme("light");
  }
};

const initTheme = () => {
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  const currentTheme = localStorage.getItem("theme");
  if (currentTheme) {
    setTheme(currentTheme);
  } else {
    if (prefersDark) {
      setTheme("dark");
    } else {
      setTheme("light");
    }
  }
};

window.addEventListener("load", () => {
  const buttons = document.getElementsByClassName("theme-toggle");
  Array.from(buttons).forEach((btn) => {
    btn.addEventListener("click", alter_theme);
  });
});

initTheme();
