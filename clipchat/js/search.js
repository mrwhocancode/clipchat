document.addEventListener("DOMContentLoaded", () => {
  const searchButton = document.querySelector('button[aria-label="Search"]')
  const chatList = document.querySelector('[data-purpose="chat-list"]')
  const input = document.createElement("input")
  input.type = "text"
  input.placeholder = "Search users"
  input.className = "hidden"
  input.id = "user-search"

  if (searchButton && chatList) {
    searchButton.addEventListener("click", () => {
      input.classList.toggle("hidden")
      if (!input.classList.contains("hidden")) {
        input.focus()
      }
    })

    input.addEventListener("input", async () => {
      const query = input.value.trim()
      if (!query) {
        return
      }

      const response = await fetch(`/users/search?q=${encodeURIComponent(query)}`)
      if (!response.ok) {
        return
      }

      const data = await response.json()
      if (!Array.isArray(data.users)) {
        return
      }

      chatList.innerHTML = data.users
        .map((user) => `
          <div class="flex items-center px-4 py-3 hover:bg-gray-50 cursor-pointer" data-user-id="${user.id}">
            <div class="w-12 h-12 rounded-full bg-ghost-surface border border-gray-100 flex items-center justify-center">
              ${user.display_name?.[0] || "U"}
            </div>
            <div class="ml-4 flex-1 border-b border-gray-50 pb-3 mt-3">
              <div class="flex justify-between items-baseline">
                <h2 class="text-base font-bold text-black">${user.display_name}</h2>
              </div>
              <p class="text-sm text-gray-500">@${user.username}</p>
            </div>
          </div>
        `)
        .join("")

      chatList.querySelectorAll("[data-user-id]").forEach((item) => {
        item.addEventListener("click", () => {
          const userId = item.getAttribute("data-user-id")
          window.location.href = `/conversations/open/${userId}`
        })
      })
    })

    chatList.before(input)
  }
})
