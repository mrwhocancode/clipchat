document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("form[action='/login']")
  if (!form) {
    return
  }

  form.addEventListener("submit", (event) => {
    const username = form.querySelector('input[name="username"]')?.value?.trim() || ""
    const password = form.querySelector('input[name="password"]')?.value || ""

    if (!username || !password) {
      event.preventDefault()
      return
    }
  })
})
