/**
 * User search for home.html.
 */
window.YSearch = (function () {
  let panel = null;
  let input = null;
  let results = null;
  let debounceTimer = null;
  let isBound = false;

  function ensurePanel() {
    if (panel) return panel;

    panel = document.createElement("div");
    panel.className =
      "fixed inset-x-0 top-16 z-[60] mx-auto max-w-md bg-white border-b border-gray-100 shadow-sm px-4 py-3 hidden";
    panel.innerHTML = `
      <input
        type="search"
        placeholder="Search users..."
        class="w-full h-11 px-4 bg-ghost-surface rounded-full border border-gray-100 focus:outline-none"
      />
      <div class="mt-3 max-h-64 overflow-y-auto space-y-2" data-purpose="search-results"></div>
    `;
    document.body.appendChild(panel);
    input = panel.querySelector("input");
    results = panel.querySelector('[data-purpose="search-results"]');

    input.addEventListener("input", () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => searchUsers(input.value), 250);
    });

    return panel;
  }

  async function searchUsers(query) {
    if (!results) return;
    if (!query.trim()) {
      results.innerHTML = "";
      return;
    }

    const response = await fetch(`/users/search?q=${encodeURIComponent(query)}`);
    if (!response.ok) {
      results.innerHTML = `<p class="text-sm text-gray-500 px-2">Search unavailable</p>`;
      return;
    }

    const data = await response.json();
    if (!data.users.length) {
      results.innerHTML = `<p class="text-sm text-gray-500 px-2">No users found</p>`;
      return;
    }

    results.innerHTML = data.users
      .map(
        (user) => `
          <button
            type="button"
            class="w-full flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50 text-left"
            data-user-id="${user.id}"
          >
            <div class="w-10 h-10 rounded-full bg-ghost-surface flex items-center justify-center overflow-hidden">
              ${
                user.avatar
                  ? `<img src="${user.avatar}" alt="" class="w-full h-full object-cover" />`
                  : `<span class="text-sm font-bold">${user.display_name.charAt(0)}</span>`
              }
            </div>
            <div>
              <p class="font-bold text-sm">${user.display_name}</p>
              <p class="text-xs text-gray-500">@${user.username}</p>
            </div>
          </button>
        `
      )
      .join("");

    results.querySelectorAll("[data-user-id]").forEach((button) => {
      button.addEventListener("click", () => {
        const userId = button.getAttribute("data-user-id");
        window.location.href = `/conversations/open/${userId}`;
      });
    });
  }

  function bind(searchButton) {
    if (isBound) return;
    isBound = true;
    const panelEl = ensurePanel();
    searchButton.addEventListener("click", () => {
      panelEl.classList.toggle("hidden");
      if (!panelEl.classList.contains("hidden") && input) {
        input.focus();
      }
    });
  }

  return { bind };
})();
