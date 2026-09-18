import ReactMarkdown from "react-markdown";
import SourceCard from "./SourceCard";

function Message({ message }) {
  const isUser = message.type === "user";

  return (
    <div
      className={`message-row ${
        isUser ? "user-row" : "assistant-row"
      }`}
    >
      <div
        className={`avatar ${
          isUser ? "user-avatar" : "ai-avatar"
        }`}
      >
        {isUser ? "You" : "BIS"}
      </div>

      <div className="message-content">

        <div className="message-name">
          {isUser ? "You" : "BIS Assistant"}
        </div>

        <div
          className={`message-bubble ${
            isUser ? "user-bubble" : ""
          }`}
        >
          {isUser ? (
            message.text
          ) : (
            <div className="markdown-answer">
              <ReactMarkdown>
                {message.text}
              </ReactMarkdown>
            </div>
          )}
        </div>

        {!isUser &&
          message.sources &&
          message.sources.length > 0 && (
            <div className="sources">

              <div className="sources-title">
                <span>📚</span>
                Retrieved BIS sources
              </div>

              {message.sources.map((source, index) => (
                <SourceCard
                  key={index}
                  source={source}
                />
              ))}

            </div>
          )}

      </div>
    </div>
  );
}

export default Message;