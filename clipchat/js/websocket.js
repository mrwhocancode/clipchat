document.addEventListener("DOMContentLoaded", () => {
  if (!window.Y_USER) {
    return
  }

  const wsProtocol = window.location.protocol === "https:" ? "wss" : "ws"
  const socket = new WebSocket(`${wsProtocol}://${window.location.host}/ws`)

  socket.addEventListener("message", (event) => {
    try {
      const payload = JSON.parse(event.data)
      if (payload.type === "new_message" && payload.message) {
        const chatContainer = document.querySelector('[data-purpose="chat-messages-container"]')
        if (chatContainer) {
          const message = payload.message
          const isMine = message.sender_id === window.Y_USER.id
          chatContainer.insertAdjacentHTML(
            "beforeend",
            `
              <div class="flex ${isMine ? "justify-end" : "justify-start"}">
                <div class="max-w-[80%] rounded-2xl px-4 py-3 ${isMine ? "bg-[#3183ff] text-white" : "bg-[#f0f1f2] text-black"}">
                  <div class="text-sm">Clip: ${message.clip_id}</div>
                </div>
              </div>
            `
          )
        }
      }
    } catch (error) {
      console.error("Failed to parse websocket payload", error)
    }
  })
})
