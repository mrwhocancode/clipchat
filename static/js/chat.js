/**
 * Chat page: load messages, send clips, receive realtime updates.
 */
(function () {
  const config = window.Y_CHAT || {};
  const conversationId = config.conversationId;
  const currentUserId = config.currentUserId;
  const receiverId = config.receiverId;

  const messagesContainer = document.querySelector('[data-purpose="chat-messages-container"] > div');
  const backButton = document.querySelector('[aria-label="Go back"]');
  const cameraButton = document.querySelector('[data-purpose="camera-action"]');
  const sendButton = document.querySelector('[data-purpose="voice-action"]');
  const textInput = document.querySelector('[data-purpose="chat-text-input"]');
  const headerName = document.querySelector('[data-purpose="chat-header"] .font-bold');

  if (headerName && config.receiverName) {
    headerName.textContent = config.receiverName;
  }

  if (backButton) {
    backButton.addEventListener("click", () => {
      window.location.href = "/home";
    });
  }

  function clipUrl(clipId) {
    return `/static/clips/${clipId}`;
  }

  function renderMessage(message) {
    const isMine = message.sender_id === currentUserId;
    const wrapper = document.createElement("div");
    wrapper.className = `flex ${isMine ? "justify-end" : "justify-start"}`;
    const bubble = document.createElement("div");
    bubble.className = "w-fit max-w-[280px] rounded-2xl overflow-hidden border border-gray-100 shadow-sm bg-ghost-lightGray";
    const video = document.createElement("video");
    video.src = clipUrl(message.clip_id);
    video.playsInline = true;
    video.className = "w-full max-h-52 bg-black object-contain cursor-pointer";
    video.setAttribute("aria-label", "Play or pause clip");
    video.addEventListener("click", () => {
      if (video.paused) video.play().catch(() => {});
      else video.pause();
    });
    bubble.appendChild(video);
    const time = document.createElement("p");
    time.className = "px-3 py-1 text-[11px] text-ghost-gray";
    time.textContent = new Date(message.created_at).toLocaleTimeString();
    bubble.appendChild(time);
    wrapper.appendChild(bubble);
    return wrapper;
  }

  function appendMessage(message) {
    if (!messagesContainer) return;
    const existing = messagesContainer.querySelector(`[data-message-id="${message.id}"]`);
    if (existing) return;

    const node = renderMessage(message);
    node.firstElementChild.setAttribute("data-message-id", message.id);
    messagesContainer.appendChild(node);
    messagesContainer.parentElement.scrollTop = messagesContainer.parentElement.scrollHeight;
  }

  async function loadMessages() {
    if (!conversationId || !messagesContainer) return;

    const response = await fetch(`/messages/${conversationId}`);
    if (!response.ok) return;

    const data = await response.json();
    messagesContainer.innerHTML = "";
    data.messages.forEach(appendMessage);
  }

  async function sendClip(clipId) {
    if (!receiverId || !clipId) return;

    const response = await fetch("/send", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ receiver_id: receiverId, clip_id: clipId }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      alert(error.detail || "Unable to send clip");
      return;
    }

    const data = await response.json();
    appendMessage(data.message);
    if (textInput) textInput.value = "";
  }

  let clipPicker;

  function getClipPicker() {
    if (clipPicker) return clipPicker;
    clipPicker = document.createElement("div");
    clipPicker.className = "fixed inset-x-3 bottom-20 z-50 max-w-md mx-auto max-h-64 overflow-y-auto rounded-2xl border border-gray-100 bg-white p-3 shadow-lg";
    document.body.appendChild(clipPicker);
    return clipPicker;
  }

  function showClipChoices(clips, emptyMessage) {
    const picker = getClipPicker();
    picker.replaceChildren();
    if (!clips.length) {
      const empty = document.createElement("p");
      empty.className = "px-2 py-3 text-sm text-ghost-gray";
      empty.textContent = emptyMessage;
      picker.appendChild(empty);
      return;
    }
    clips.forEach((clip) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "block w-full rounded-xl px-3 py-2 text-left hover:bg-[#f0f1f2]";
      const title = document.createElement("p");
      title.className = "font-semibold text-sm";
      title.textContent = clip.title || clip.clip_id;
      const transcript = document.createElement("p");
      transcript.className = "text-xs text-ghost-gray";
      transcript.textContent = clip.transcript || clip.clip_id;
      button.append(title, transcript);
      button.addEventListener("click", async () => {
        picker.remove();
        clipPicker = null;
        await sendClip(clip.clip_id);
      });
      picker.appendChild(button);
    });
  }

  async function searchClips(query) {
    const response = await fetch(`/clips/search?q=${encodeURIComponent(query)}`);
    if (!response.ok) return;
    const data = await response.json();
    showClipChoices(data.clips, "No matching clips yet. Add a tagged dialogue clip to static/clips/.");
  }

  async function openClipPicker() {
    const response = await fetch("/clips");
    if (!response.ok) return;

    const data = await response.json();
    if (!data.clips.length) {
      alert("No clips available in static/clips/");
      return;
    }

    showClipChoices(
      data.clips.map((clipId) => ({ clip_id: clipId, title: clipId, transcript: "" })),
      "No clips available in static/clips/"
    );
  }

  if (cameraButton) {
    cameraButton.addEventListener("click", openClipPicker);
  }

  if (sendButton && textInput) {
    sendButton.addEventListener("click", async () => {
      const query = textInput.value.trim();
      if (query) {
        await searchClips(query);
      } else {
        await openClipPicker();
      }
    });

    textInput.addEventListener("keydown", async (event) => {
      if (event.key === "Enter" && textInput.value.trim()) {
        event.preventDefault();
        await searchClips(textInput.value.trim());
      }
    });
  }

  if (window.YWebSocket) {
    window.YWebSocket.onMessage((payload) => {
      if (
        payload.type === "new_message" &&
        payload.message &&
        payload.message.conversation_id === conversationId
      ) {
        appendMessage(payload.message);
      }
    });
  }

  loadMessages();
})();
