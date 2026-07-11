/**
 * Home page: load conversations and wire search/navigation.
 */
(function () {
  const chatList = document.querySelector('[data-purpose="chat-list"]');
  const searchButton = document.querySelector('[aria-label="Search"]');
  const profileAvatar = document.querySelector('[data-purpose="profile-avatar"]');
  const newChatButton = document.querySelector('[aria-label="New Chat"]');

  if (profileAvatar) {
    profileAvatar.style.cursor = "pointer";
    profileAvatar.addEventListener("click", () => {
      window.location.href = "/profile";
    });
  }

  if (searchButton && window.YSearch) {
    window.YSearch.bind(searchButton);
  }

  if (newChatButton && window.YSearch) {
    newChatButton.addEventListener("click", () => {
      window.YSearch.bind(searchButton);
      searchButton.click();
    });
  }

  function formatRelativeTime(isoDate) {
    const date = new Date(isoDate);
    const diffMs = Date.now() - date.getTime();
    const minutes = Math.floor(diffMs / 60000);
    if (minutes < 1) return "now";
    if (minutes < 60) return `${minutes}m`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h`;
    return `${Math.floor(hours / 24)}d`;
  }

  function renderConversation(conversation) {
    const otherUser = conversation.other_user;
    const lastMessage = conversation.last_message;
    const preview = lastMessage ? `Clip: ${lastMessage.clip_id}` : "New Chat";
    const time = lastMessage ? formatRelativeTime(lastMessage.created_at) : "";

    const item = document.createElement("div");
    item.className =
      "flex items-center px-4 py-3 hover:bg-gray-50 active:bg-gray-100 transition-colors cursor-pointer";
    item.setAttribute("data-purpose", "chat-item");
    item.innerHTML = `
      <div class="relative">
        <div class="w-14 h-14 rounded-full bg-ghost-surface border border-gray-100 flex items-center justify-center text-2xl overflow-hidden">
          ${
            otherUser.avatar
              ? `<img src="${otherUser.avatar}" alt="" class="w-full h-full object-cover" />`
              : `<span>${otherUser.display_name.charAt(0)}</span>`
          }
        </div>
      </div>
      <div class="ml-4 flex-1 border-b border-gray-50 pb-3 mt-3">
        <div class="flex justify-between items-baseline">
          <h2 class="text-base font-bold text-black">${otherUser.display_name}</h2>
          <span class="text-xs font-medium text-gray-400">${time}</span>
        </div>
        <div class="flex items-center gap-1.5 mt-0.5">
          <div class="w-3 h-3 bg-blue-500 rounded-sm"></div>
          <p class="text-sm font-semibold text-blue-500">${preview}</p>
        </div>
      </div>
    `;

    item.addEventListener("click", () => {
      window.location.href = `/chat/${conversation.id}`;
    });

    return item;
  }

  async function loadConversations() {
    if (!chatList) return;

    const response = await fetch("/conversations");
    if (!response.ok) return;

    const data = await response.json();
    chatList.innerHTML = "";

    if (!data.conversations.length) {
      chatList.innerHTML =
        '<p class="px-4 py-8 text-center text-sm text-gray-500">Search for users to start a clip chat.</p>';
      return;
    }

    data.conversations.forEach((conversation) => {
      chatList.appendChild(renderConversation(conversation));
    });
  }

  loadConversations();

  if (window.YWebSocket) {
    window.YWebSocket.onMessage((payload) => {
      if (payload.type === "new_message") {
        loadConversations();
      }
    });
  }
})();
