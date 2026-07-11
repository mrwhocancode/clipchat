/**
 * WebSocket client for realtime clip delivery.
 */
window.YWebSocket = (function () {
  let socket = null;
  let handlers = [];

  function connect() {
    if (socket && socket.readyState <= WebSocket.OPEN) return socket;

    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    socket = new WebSocket(`${protocol}://${window.location.host}/ws`);

    socket.addEventListener("message", (event) => {
      try {
        const payload = JSON.parse(event.data);
        handlers.forEach((handler) => handler(payload));
      } catch (error) {
        console.error("Invalid websocket payload", error);
      }
    });

    socket.addEventListener("close", () => {
      setTimeout(connect, 1500);
    });

    return socket;
  }

  function onMessage(handler) {
    handlers.push(handler);
    connect();
  }

  return { connect, onMessage };
})();
