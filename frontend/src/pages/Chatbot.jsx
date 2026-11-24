import { useEffect, useRef, useState } from "react";
import { useOutletContext } from "react-router-dom";
import api from "../api";
import "./Chatbot.css";

const SUGGESTIONS = [
  "Analyse my portfolio performance",
  "What is my portfolio's biggest risk?",
  "Explain my portfolio's Sharpe ratio",
  "What happens if I add more shares?",
];

function getConfig() {
  const token = localStorage.getItem("token");

  return {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  };
}

function Chatbot() {
  const { selectedPortfolioId } = useOutletContext();

  const [messages, setMessages] = useState([]);
  const [history, setHistory] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [error, setError] = useState("");

  const bottomRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    loadHistory();
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function loadHistory() {
    try {
      setHistoryLoading(true);

      const response = await api.get(
        "/chat/history?limit=50&offset=0",
        getConfig()
      );

      setHistory(response.data || []);
    } catch (err) {
      console.error("Chat history error:", err);
    } finally {
      setHistoryLoading(false);
    }
  }

  async function sendMessage(message = input) {
    const question = message.trim();

    if (question.length < 2 || loading) return;

    if (question.length > 2000) {
      setError("Message cannot exceed 2,000 characters.");
      return;
    }

    setError("");
    setInput("");

    setMessages((prev) => [
      ...prev,
      {
        id: Date.now(),
        role: "user",
        content: question,
      },
    ]);

    setLoading(true);

    try {
      const response = await api.post(
        "/chat/",
        {
          message: question,
          portfolio_id: selectedPortfolioId
            ? Number(selectedPortfolioId)
            : null,
        },
        getConfig()
      );

      const data = response.data;

      setMessages((prev) => [
        ...prev,
        {
          id: data.chat_id || Date.now() + 1,
          role: "assistant",
          content: data.response,
          validationStatus: data.validation_status,
          responseMethod: data.response_method,
        },
      ]);

      await loadHistory();
    } catch (err) {
      console.error("Chat request error:", err);

      setError(
        err.response?.data?.detail ||
          "Unable to get a response. Please try again."
      );
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  }

  function openHistory(item) {
    setMessages([
      {
        id: `${item.chat_id}-user`,
        role: "user",
        content: item.query,
      },
      {
        id: `${item.chat_id}-assistant`,
        role: "assistant",
        content: item.response,
      },
    ]);

    setError("");
  }

  function newChat() {
    setMessages([]);
    setInput("");
    setError("");
  }

  function handleKeyDown(event) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  }

  return (
    <div className="chatbot-page">
      <aside className="chatbot-history">
        <div className="chatbot-history-header">
          <div>
            <h2>Conversations</h2>
            <p>Previous analyses</p>
          </div>

          <button onClick={newChat}>+ New chat</button>
        </div>

        <div className="chatbot-history-list">
          {historyLoading ? (
            <p className="chatbot-muted">Loading history...</p>
          ) : history.length === 0 ? (
            <p className="chatbot-muted">No conversations yet.</p>
          ) : (
            history.map((item) => (
              <button
                key={item.chat_id}
                className="chatbot-history-item"
                onClick={() => openHistory(item)}
              >
                <span>{item.query}</span>
                <small>
                  {new Date(item.created_at).toLocaleDateString()}
                </small>
              </button>
            ))
          )}
        </div>
      </aside>

      <main className="chatbot-main">
        <header className="chatbot-header">
          <div>
            <h1>StockSense AI</h1>
            <p>Your personal portfolio analysis assistant</p>
          </div>

          <span className="chatbot-status">
            <span />
            AI Assistant
          </span>
        </header>

        <section className="chatbot-messages">
          {messages.length === 0 ? (
            <div className="chatbot-welcome">
              <div className="chatbot-welcome-icon">✦</div>
              <h2>How can I help you today?</h2>
              <p>
                Ask questions about your portfolio, performance,
                risk metrics, or investment scenarios.
              </p>

              <div className="chatbot-suggestions">
                {SUGGESTIONS.map((prompt) => (
                  <button
                    key={prompt}
                    onClick={() => sendMessage(prompt)}
                    disabled={loading}
                  >
                    {prompt}
                    <span>→</span>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="chatbot-message-list">
              {messages.map((message) => (
                <article
                  key={message.id}
                  className={`chatbot-message chatbot-${message.role}`}
                >
                  <div className="chatbot-avatar">
                    {message.role === "assistant" ? "✦" : "You"}
                  </div>

                  <div className="chatbot-message-body">
                    <strong>
                      {message.role === "assistant"
                        ? "StockSense AI"
                        : "You"}
                    </strong>

                    <div className="chatbot-message-content">
                      {message.content}
                    </div>

                    {message.role === "assistant" &&
                      message.validationStatus && (
                        <small className="chatbot-verification">
                          {message.validationStatus === "passed"
                            ? "✓ Response verified"
                            : message.validationStatus === "failed"
                            ? "⚠ Verification unsuccessful"
                            : "Verification not applicable"}
                        </small>
                      )}
                  </div>
                </article>
              ))}

              {loading && (
                <article className="chatbot-message chatbot-assistant">
                  <div className="chatbot-avatar">✦</div>
                  <div className="chatbot-message-body">
                    <strong>StockSense AI</strong>
                    <div className="chatbot-typing">
                      <span />
                      <span />
                      <span />
                    </div>
                  </div>
                </article>
              )}

              <div ref={bottomRef} />
            </div>
          )}
        </section>

        <footer className="chatbot-composer-area">
          {error && (
            <div className="chatbot-error">
              {error}
              <button onClick={() => setError("")}>×</button>
            </div>
          )}

          <div className="chatbot-composer">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(event) => setInput(event.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask StockSense anything..."
              rows={1}
              maxLength={2000}
              disabled={loading}
            />

            <button
              className="chatbot-send"
              onClick={() => sendMessage()}
              disabled={loading || input.trim().length < 2}
            >
              ↑
            </button>
          </div>

          <div className="chatbot-composer-footer">
            <span>Enter to send · Shift + Enter for a new line</span>
            <span>{input.length}/2000</span>
          </div>

          <p className="chatbot-disclaimer">
            AI-generated responses may contain errors. Verify important
            investment decisions independently.
          </p>
        </footer>
      </main>
    </div>
  );
}

export default Chatbot;