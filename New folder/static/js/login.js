/**
 * Login and registration wiring for index.html.
 * Adds a display_name field when signing up without changing the template layout.
 */
(function () {
  const form = document.querySelector("form");
  const signUpBtn = document.querySelector("footer button");
  const footerText = document.querySelector("footer p");
  if (!form || !signUpBtn) return;

  let isRegisterMode = false;
  let displayNameInput = null;

  function setMode(registerMode) {
    isRegisterMode = registerMode;
    form.action = registerMode ? "/register" : "/login";
    signUpBtn.textContent = registerMode ? "Log In" : "Sign Up";
    if (footerText) {
      footerText.textContent = registerMode
        ? "Already have an account?"
        : "Don't have an account?";
    }

    if (registerMode && !displayNameInput) {
      const passwordGroup = document.getElementById("password")?.closest(".input-group");
      if (!passwordGroup) return;

      displayNameInput = document.createElement("div");
      displayNameInput.className = "input-group relative";
      displayNameInput.innerHTML = `
        <input name="display_name" class="peer w-full h-14 bg-surface border-[1.5px] border-on-background rounded-lg px-4 font-body-md text-body-md focus:outline-none focus:ring-0 focus:border-on-background transition-all" id="display-name" placeholder=" " type="text" required />
        <label class="absolute left-4 top-4 font-label-bold text-on-surface-variant origin-top-left" for="display-name">
          Display Name
        </label>
      `;
      passwordGroup.parentNode.insertBefore(displayNameInput, passwordGroup);
    }

    if (displayNameInput) {
      displayNameInput.style.display = registerMode ? "block" : "none";
      const input = displayNameInput.querySelector("input");
      if (input) input.required = registerMode;
    }
  }

  signUpBtn.addEventListener("click", (event) => {
    event.preventDefault();
    setMode(!isRegisterMode);
  });

  setMode(false);
})();
