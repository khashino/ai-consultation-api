(function () {
  const API_BASE =
    window.AI_CHATBOT_API_BASE || "http://127.0.0.1:8000";

  const BOT_TITLE =
    window.AI_CHATBOT_TITLE || "AI Assistant";

  const DEFAULT_TOPIC =
    window.AI_CHATBOT_TOPIC || "general";

  const USER_COUNTRY =
    window.AI_CHATBOT_USER_COUNTRY || null;

  const TARGET_COUNTRY =
    window.AI_CHATBOT_TARGET_COUNTRY || null;

  const STORAGE_KEY = "ai_chatbot_session_id";

  let SESSION_ID = localStorage.getItem(STORAGE_KEY);

  if (!SESSION_ID) {
    SESSION_ID = createSessionId();
    localStorage.setItem(STORAGE_KEY, SESSION_ID);
  }

  const styles = `
    #ai-chatbot-button {
      position: fixed;
      right: 24px;
      bottom: 24px;
      width: 60px;
      height: 60px;
      border-radius: 50%;
      background: #2563eb;
      color: white;
      border: none;
      cursor: pointer;
      box-shadow: 0 10px 30px rgba(37, 99, 235, 0.35);
      font-size: 26px;
      z-index: 999999;
    }

    #ai-chatbot-window {
      position: fixed;
      right: 24px;
      bottom: 96px;
      width: 360px;
      height: 520px;
      background: #ffffff;
      border-radius: 18px;
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.22);
      overflow: hidden;
      display: none;
      flex-direction: column;
      font-family: Arial, sans-serif;
      z-index: 999999;
      border: 1px solid #e5e7eb;
    }

    #ai-chatbot-header {
      background: #111827;
      color: white;
      padding: 16px;
      font-weight: bold;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    #ai-chatbot-header-actions {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    #ai-chatbot-reset,
    #ai-chatbot-close {
      background: transparent;
      border: none;
      color: white;
      cursor: pointer;
    }

    #ai-chatbot-reset {
      font-size: 12px;
      opacity: 0.85;
    }

    #ai-chatbot-close {
      font-size: 20px;
    }

    #ai-chatbot-messages {
      flex: 1;
      padding: 14px;
      overflow-y: auto;
      background: #f9fafb;
    }

    .ai-message-row {
      margin-bottom: 12px;
      display: flex;
    }

    .ai-message-row.user {
      justify-content: flex-end;
    }

    .ai-message-row.bot {
      justify-content: flex-start;
    }

    .ai-message {
      max-width: 82%;
      padding: 10px 12px;
      border-radius: 14px;
      font-size: 14px;
      line-height: 1.45;
      white-space: pre-wrap;
    }

    .ai-message.user {
      background: #2563eb;
      color: white;
      border-bottom-right-radius: 4px;
    }

    .ai-message.bot {
      background: white;
      color: #1f2937;
      border: 1px solid #e5e7eb;
      border-bottom-left-radius: 4px;
    }

    #ai-chatbot-input-area {
      display: flex;
      gap: 8px;
      padding: 12px;
      border-top: 1px solid #e5e7eb;
      background: white;
    }

    #ai-chatbot-input {
      flex: 1;
      border: 1px solid #d1d5db;
      border-radius: 12px;
      padding: 10px;
      font-size: 14px;
      outline: none;
    }

    #ai-chatbot-send {
      background: #2563eb;
      color: white;
      border: none;
      border-radius: 12px;
      padding: 0 14px;
      cursor: pointer;
      font-weight: bold;
    }

    #ai-chatbot-send:disabled {
      background: #9ca3af;
      cursor: not-allowed;
    }

    @media (max-width: 480px) {
      #ai-chatbot-window {
        right: 12px;
        left: 12px;
        bottom: 86px;
        width: auto;
        height: 70vh;
      }

      #ai-chatbot-button {
        right: 18px;
        bottom: 18px;
      }
    }
  `;

  function injectStyles() {
    const styleTag = document.createElement("style");
    styleTag.innerHTML = styles;
    document.head.appendChild(styleTag);
  }

  function createWidget() {
    const button = document.createElement("button");
    button.id = "ai-chatbot-button";
    button.innerHTML = "💬";

    const windowBox = document.createElement("div");
    windowBox.id = "ai-chatbot-window";

    windowBox.innerHTML = `
      <div id="ai-chatbot-header">
        <span>${escapeHtml(BOT_TITLE)}</span>
        <div id="ai-chatbot-header-actions">
          <button id="ai-chatbot-reset" title="Start new chat">New</button>
          <button id="ai-chatbot-close">×</button>
        </div>
      </div>

      <div id="ai-chatbot-messages"></div>

      <div id="ai-chatbot-input-area">
        <input
          id="ai-chatbot-input"
          type="text"
          placeholder="Ask something..."
        />
        <button id="ai-chatbot-send">Send</button>
      </div>
    `;

    document.body.appendChild(button);
    document.body.appendChild(windowBox);

    const messages = document.getElementById("ai-chatbot-messages");
    const input = document.getElementById("ai-chatbot-input");
    const sendButton = document.getElementById("ai-chatbot-send");
    const closeButton = document.getElementById("ai-chatbot-close");
    const resetButton = document.getElementById("ai-chatbot-reset");

    button.addEventListener("click", function () {
      windowBox.style.display =
        windowBox.style.display === "flex" ? "none" : "flex";

      if (windowBox.style.display === "flex") {
        input.focus();
      }
    });

    closeButton.addEventListener("click", function () {
      windowBox.style.display = "none";
    });

    resetButton.addEventListener("click", async function () {
      const oldSessionId = SESSION_ID;

      SESSION_ID = createSessionId();
      localStorage.setItem(STORAGE_KEY, SESSION_ID);

      messages.innerHTML = "";
      addBotMessage("New chat started. Ask me a question from the knowledge base.");

      try {
        await fetch(`${API_BASE}/chat/sessions/${encodeURIComponent(oldSessionId)}`, {
          method: "DELETE"
        });
      } catch (error) {
        // Ignore cleanup errors in widget.
      }
    });

    sendButton.addEventListener("click", sendMessage);

    input.addEventListener("keydown", function (event) {
      if (event.key === "Enter") {
        sendMessage();
      }
    });

    addBotMessage(
      "Hi! Ask me a question and I’ll answer using the local knowledge base."
    );

    async function sendMessage() {
      const question = input.value.trim();

      if (!question) return;

      addUserMessage(question);
      input.value = "";
      sendButton.disabled = true;

      const loadingId = addBotMessage("Thinking...");

      try {
        const response = await fetch(`${API_BASE}/chat`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            session_id: SESSION_ID,
            message: question,
            topic: DEFAULT_TOPIC,
            user_country: USER_COUNTRY,
            target_country: TARGET_COUNTRY
          })
        });

        const data = await response.json();

        removeMessage(loadingId);

        if (!response.ok) {
          addBotMessage("Sorry, something went wrong.");
          return;
        }

        addBotResponse(data);
      } catch (error) {
        removeMessage(loadingId);
        addBotMessage("Could not connect to the AI API.");
      } finally {
        sendButton.disabled = false;
        input.focus();
      }
    }

    function addUserMessage(text) {
      addMessage("user", escapeHtml(text));
    }

    function addBotMessage(text) {
      return addMessage("bot", escapeHtml(text));
    }

    function addBotResponse(data) {
      addMessage("bot", escapeHtml(data.answer || "No answer returned."));
    }

    function addMessage(type, html) {
      const id = "msg-" + Date.now() + "-" + Math.random().toString(16).slice(2);

      const row = document.createElement("div");
      row.className = `ai-message-row ${type}`;
      row.id = id;

      const bubble = document.createElement("div");
      bubble.className = `ai-message ${type}`;
      bubble.innerHTML = html;

      row.appendChild(bubble);
      messages.appendChild(row);
      messages.scrollTop = messages.scrollHeight;

      return id;
    }

    function removeMessage(id) {
      const element = document.getElementById(id);
      if (element) {
        element.remove();
      }
    }
  }

  function createSessionId() {
    if (window.crypto && crypto.randomUUID) {
      return crypto.randomUUID();
    }

    return "session-" + Date.now() + "-" + Math.random().toString(16).slice(2);
  }

  function escapeHtml(text) {
    if (text === null || text === undefined) return "";

    return String(text)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  injectStyles();
  createWidget();
})();