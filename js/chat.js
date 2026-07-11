document.addEventListener("DOMContentLoaded", () => {
  const chatContainer = document.querySelector('[data-purpose="chat-messages-container"]')
  if (!chatContainer || !window.Y_CHAT) {
    return
  }

  const loadMessages = async () => {
    const response = await fetch(`/messages/${window.Y_CHAT.conversationId}`)
    if (!response.ok) {
      return
    }

    const data = await response.json()
    const messages = Array.isArray(data.messages) ? data.messages : []
    chatContainer.innerHTML = messages
      .map((message) => {
        const isMine = message.sender_id === window.Y_CHAT.currentUserId
        return `
          <div class="flex ${isMine ? "justify-end" : "justify-start"}">
            <div class="max-w-[80%] rounded-2xl px-4 py-3 ${isMine ? "bg-[#3183ff] text-white" : "bg-[#f0f1f2] text-black"}">
              <div class="text-sm">Clip: ${message.clip_id}</div>
            </div>
          </div>
        `
      })
      .join("")
  }

  loadMessages()
})
