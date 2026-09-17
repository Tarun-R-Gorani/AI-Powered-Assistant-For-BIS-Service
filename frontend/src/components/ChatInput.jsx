import { useState } from "react";

function ChatInput({ onSend }) {
  const [input, setInput] = useState("");

  const submitMessage = () => {
    if (!input.trim()) return;

    onSend(input);
    setInput("");
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      submitMessage();
    }
  };

  return (
    <div className="input-wrapper">
      <div className="input-box">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about BIS standards, certification, ISI, Hallmarking..."
          rows="1"
        />

        <div className="input-actions">
          <button className="voice-btn" title="Voice input">
            🎙
          </button>

          <button
            className="send-btn"
            onClick={submitMessage}
            disabled={!input.trim()}
          >
            ↑
          </button>
        </div>
      </div>
    </div>
  );
}

export default ChatInput;