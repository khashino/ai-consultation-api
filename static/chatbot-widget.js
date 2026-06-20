(function () {
  const API_BASE =
    window.AI_CHATBOT_API_BASE || "http://127.0.0.1:8000";

  const BOT_TITLE =
    window.AI_CHATBOT_TITLE || "AI Assistant";

  const BOT_SUBTITLE =
    window.AI_CHATBOT_SUBTITLE || "Answers from your knowledge base";

  const DEFAULT_TOPIC =
    window.AI_CHATBOT_TOPIC || "general";

  const USER_COUNTRY =
    window.AI_CHATBOT_USER_COUNTRY || null;

  const TARGET_COUNTRY =
    window.AI_CHATBOT_TARGET_COUNTRY || null;

  const STORAGE_KEY = "ai_chatbot_session_id";

  let SESSION_ID = localStorage.getItem(STORAGE_KEY);
  let isOpen = false;
  let isSending = false;

  if (!SESSION_ID) {
    SESSION_ID = createSessionId();
    localStorage.setItem(STORAGE_KEY, SESSION_ID);
  }

  const styles = `
    #ai-chatbot-button,
    #ai-chatbot-window,
    #ai-chatbot-window * {
      box-sizing: border-box;
      font-family: Inter, Arial, sans-serif;
    }

    #ai-chatbot-button {
      position: fixed;
      right: 24px;
      bottom: 24px;
      width: 64px;
      height: 64px;
      border-radius: 24px;
      background: linear-gradient(135deg, #2563eb, #7c3aed);
      color: white;
      border: none;
      cursor: pointer;
      box-shadow: 0 18px 40px rgba(37, 99, 235, 0.35);
      font-size: 25px;
      z-index: 999999;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: transform 0.16s ease, box-shadow 0.16s ease;
    }

    #ai-chatbot-button:hover {
      transform: translateY(-2px) scale(1.03);
      box-shadow: 0 24px 50px rgba(37, 99, 235, 0.42);
    }

    #ai-chatbot-button.ai-open {
      border-radius: 22px;
    }

    #ai-chatbot-button-badge {
      position: absolute;
      top: -3px;
      right: -3px;
      width: 16px;
      height: 16px;
      border-radius: 999px;
      background: #22c55e;
      border: 3px solid white;
    }

    #ai-chatbot-window {
      position: fixed;
      right: 24px;
      bottom: 102px;
      width: 390px;
      height: 590px;
      max-height: calc(100vh - 126px);
      background: #ffffff;
      border-radius: 26px;
      box-shadow: 0 26px 80px rgba(15, 23, 42, 0.28);
      overflow: hidden;
      display: none;
      flex-direction: column;
      z-index: 999999;
      border: 1px solid #e2e8f0;
      transform-origin: bottom right;
    }

    #ai-chatbot-window.ai-visible {
      display: flex;
      animation: aiChatbotPop 0.18s ease-out;
    }

    @keyframes aiChatbotPop {
      from {
        opacity: 0;
        transform: translateY(10px) scale(0.97);
      }

      to {
        opacity: 1;
        transform: translateY(0) scale(1);
      }
    }

    #ai-chatbot-header {
      background:
        radial-gradient(circle at top left, rgba(255,255,255,0.22), transparent 28%),
        linear-gradient(135deg, #0f172a, #1e3a8a 54%, #6d28d9);
      color: white;
      padding: 18px;
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 12px;
    }

    #ai-chatbot-title-row {
      display: flex;
      gap: 11px;
      min-width: 0;
      align-items: center;
    }

    #ai-chatbot-avatar {
      width: 42px;
      height: 42px;
      border-radius: 16px;
      background: rgba(255,255,255,0.18);
      border: 1px solid rgba(255,255,255,0.22);
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 900;
      flex: 0 0 auto;
    }

    #ai-chatbot-title {
      font-weight: 900;
      font-size: 15px;
      line-height: 1.2;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    #ai-chatbot-subtitle {
      color: rgba(255,255,255,0.78);
      font-size: 12px;
      margin-top: 4px;
      line-height: 1.35;
    }

    #ai-chatbot-header-actions {
      display: flex;
      align-items: center;
      gap: 6px;
      flex: 0 0 auto;
    }

    #ai-chatbot-reset,
    #ai-chatbot-close {
      background: rgba(255,255,255,0.12);
      border: 1px solid rgba(255,255,255,0.14);
      color: white;
      cursor: pointer;
      border-radius: 11px;
      height: 32px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      transition: 0.14s ease;
    }

    #ai-chatbot-reset:hover,
    #ai-chatbot-close:hover {
      background: rgba(255,255,255,0.20);
    }

    #ai-chatbot-reset {
      padding: 0 10px;
      font-size: 12px;
      font-weight: 800;
    }

    #ai-chatbot-close {
      width: 32px;
      font-size: 20px;
      line-height: 1;
    }

    #ai-chatbot-messages {
      flex: 1;
      padding: 16px;
      overflow-y: auto;
      background:
        radial-gradient(circle at top right, rgba(37, 99, 235, 0.06), transparent 26%),
        #f8fafc;
    }

    #ai-chatbot-messages::-webkit-scrollbar {
      width: 8px;
    }

    #ai-chatbot-messages::-webkit-scrollbar-thumb {
      background: #cbd5e1;
      border-radius: 999px;
    }

    .ai-message-row {
      margin-bottom: 12px;
      display: flex;
      animation: aiMessageIn 0.14s ease-out;
    }

    @keyframes aiMessageIn {
      from {
        opacity: 0;
        transform: translateY(4px);
      }

      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    .ai-message-row.user {
      justify-content: flex-end;
    }

    .ai-message-row.bot {
      justify-content: flex-start;
    }

    .ai-message {
      max-width: 84%;
      padding: 11px 13px;
      border-radius: 16px;
      font-size: 14px;
      line-height: 1.48;
      white-space: pre-wrap;
      word-break: break-word;
      box-shadow: 0 2px 8px rgba(15,23,42,0.04);
    }

    .ai-message.user {
      background: #2563eb;
      color: white;
      border-bottom-right-radius: 5px;
    }

    .ai-message.bot {
      background: white;
      color: #0f172a;
      border: 1px solid #e2e8f0;
      border-bottom-left-radius: 5px;
    }

    .ai-message.ai-error {
      background: #fee2e2;
      color: #991b1b;
      border-color: #fecaca;
    }

    .ai-typing {
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }

    .ai-typing span {
      width: 6px;
      height: 6px;
      background: #94a3b8;
      border-radius: 999px;
      animation: aiTyping 1s infinite;
    }

    .ai-typing span:nth-child(2) {
      animation-delay: 0.15s;
    }

    .ai-typing span:nth-child(3) {
      animation-delay: 0.30s;
    }

    @keyframes aiTyping {
      0%, 80%, 100% {
        transform: translateY(0);
        opacity: 0.45;
      }

      40% {
        transform: translateY(-4px);
        opacity: 1;
      }
    }

    #ai-chatbot-suggestions {
      padding: 12px 14px 0;
      background: #f8fafc;
      display: flex;
      gap: 8px;
      overflow-x: auto;
      border-top: 1px solid #e2e8f0;
    }

    .ai-chatbot-suggestion {
      border: 1px solid #dbeafe;
      background: #eff6ff;
      color: #1d4ed8;
      border-radius: 999px;
      padding: 8px 10px;
      font-size: 12px;
      font-weight: 800;
      cursor: pointer;
      white-space: nowrap;
      transition: 0.14s ease;
    }

    .ai-chatbot-suggestion:hover {
      background: #dbeafe;
    }

    #ai-chatbot-input-area {
      display: flex;
      gap: 9px;
      padding: 12px 14px 14px;
      border-top: 1px solid #e2e8f0;
      background: white;
    }

    #ai-chatbot-input {
      flex: 1;
      border: 1px solid #cbd5e1;
      border-radius: 15px;
      padding: 12px 13px;
      font-size: 14px;
      outline: none;
      color: #0f172a;
      min-width: 0;
      transition: 0.14s ease;
    }

    #ai-chatbot-input:focus {
      border-color: #93c5fd;
      box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.10);
    }

    #ai-chatbot-send {
      background: #2563eb;
      color: white;
      border: none;
      border-radius: 15px;
      padding: 0 15px;
      cursor: pointer;
      font-weight: 900;
      min-width: 72px;
      transition: 0.14s ease;
    }

    #ai-chatbot-send:hover {
      background: #1d4ed8;
      transform: translateY(-1px);
    }

    #ai-chatbot-send:disabled {
      background: #94a3b8;
      cursor: not-allowed;
      transform: none;
    }

    #ai-chatbot-footer-note {
      padding: 0 14px 12px;
      background: white;
      color: #64748b;
      font-size: 11px;
      line-height: 1.35;
    }

    @media (max-width: 480px) {
      #ai-chatbot-window {
        right: 12px;
        left: 12px;
        bottom: 88px;
        width: auto;
        height: 72vh;
        max-height: 72vh;
        border-radius: 22px;
      }

      #ai-chatbot-button {
        right: 18px;
        bottom: 18px;
        width: 60px;
        height: 60px;
      }

      #ai-chatbot-header {
        padding: 15px;
      }

      .ai-message {
        max-width: 90%;
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
    button.setAttribute("aria-label", "Open AI chatbot");
    button.innerHTML = `
      <span id="ai-chatbot-button-icon">💬</span>
      <span id="ai-chatbot-button-badge"></span>
    `;

    const windowBox = document.createElement("div");
    windowBox.id = "ai-chatbot-window";
    windowBox.setAttribute("aria-label", "AI chatbot window");

    windowBox.innerHTML = `
      <div id="ai-chatbot-header">
        <div id="ai-chatbot-title-row">
          <div id="ai-chatbot-avatar">AI</div>
          <div>
            <div id="ai-chatbot-title">${escapeHtml(BOT_TITLE)}</div>
            <div id="ai-chatbot-subtitle">${escapeHtml(BOT_SUBTITLE)}</div>
          </div>
        </div>

        <div id="ai-chatbot-header-actions">
          <button id="ai-chatbot-reset" title="Start new chat">New</button>
          <button id="ai-chatbot-close" title="Close">×</button>
        </div>
      </div>

      <div id="ai-chatbot-messages"></div>

      <div id="ai-chatbot-suggestions">
        <button class="ai-chatbot-suggestion" data-question="Summarize the knowledge base.">Summarize</button>
        <button class="ai-chatbot-suggestion" data-question="What should I check first?">Checklist</button>
        <button class="ai-chatbot-suggestion" data-question="Explain this in simple words.">Simplify</button>
      </div>

      <div id="ai-chatbot-input-area">
        <input
          id="ai-chatbot-input"
          type="text"
          placeholder="Ask about the knowledge base..."
          autocomplete="off"
        />
        <button id="ai-chatbot-send">Send</button>
      </div>

      <div id="ai-chatbot-footer-note">
        Answers are generated from the local knowledge base. For important decisions, request human review.
      </div>
    `;

    document.body.appendChild(button);
    document.body.appendChild(windowBox);

    const messages = document.getElementById("ai-chatbot-messages");
    const input = document.getElementById("ai-chatbot-input");
    const sendButton = document.getElementById("ai-chatbot-send");
    const closeButton = document.getElementById("ai-chatbot-close");
    const resetButton = document.getElementById("ai-chatbot-reset");
    const buttonIcon = document.getElementById("ai-chatbot-button-icon");

    button.addEventListener("click", function () {
      toggleWindow();
    });

    closeButton.addEventListener("click", function () {
      closeWindow();
    });

    resetButton.addEventListener("click", function () {
      startNewChat(messages);
      input.focus();
    });

    sendButton.addEventListener("click", sendMessage);

    input.addEventListener("keydown", function (event) {
      if (event.key === "Enter") {
        sendMessage();
      }
    });

    document.querySelectorAll(".ai-chatbot-suggestion").forEach(function (item) {
      item.addEventListener("click", function () {
        input.value = item.getAttribute("data-question") || "";
        input.focus();
      });
    });

    addBotMessage(
      "Hi! I’m your RAG assistant. Ask me a question and I’ll answer using the local knowledge base."
    );

    function toggleWindow() {
      isOpen = !isOpen;

      if (isOpen) {
        windowBox.classList.add("ai-visible");
        button.classList.add("ai-open");
        buttonIcon.textContent = "×";
        input.focus();
      } else {
        closeWindow();
      }
    }

    function closeWindow() {
      isOpen = false;
      windowBox.classList.remove("ai-visible");
      button.classList.remove("ai-open");
      buttonIcon.textContent = "💬";
    }

    async function sendMessage() {
      if (isSending) return;

      const question = input.value.trim();

      if (!question) return;

      isSending = true;

      addUserMessage(question);
      input.value = "";
      sendButton.disabled = true;

      const loadingId = addTypingMessage();

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
          addBotMessage("Sorry, something went wrong while generating the answer.", true);
          return;
        }

        addBotResponse(data);
      } catch (error) {
        removeMessage(loadingId);
        addBotMessage("Could not connect to the AI API. Please check that FastAPI is running.", true);
      } finally {
        isSending = false;
        sendButton.disabled = false;
        input.focus();
      }
    }

    function startNewChat(messagesContainer) {
      SESSION_ID = createSessionId();
      localStorage.setItem(STORAGE_KEY, SESSION_ID);

      messagesContainer.innerHTML = "";
      addBotMessage("New chat started. Ask me a question from the local knowledge base.");
    }

    function addUserMessage(text) {
      addMessage("user", escapeHtml(text));
    }

    function addBotMessage(text, isError) {
      return addMessage("bot", escapeHtml(text), isError);
    }

    function addTypingMessage() {
      return addMessage(
        "bot",
        `<span class="ai-typing"><span></span><span></span><span></span></span>`
      );
    }

    function addBotResponse(data) {
      addMessage("bot", escapeHtml(data.answer || "No answer returned."));
    }

    function addMessage(type, html, isError) {
      const id = "msg-" + Date.now() + "-" + Math.random().toString(16).slice(2);

      const row = document.createElement("div");
      row.className = `ai-message-row ${type}`;
      row.id = id;

      const bubble = document.createElement("div");
      bubble.className = `ai-message ${type}${isError ? " ai-error" : ""}`;
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