import { useState } from "react";
import SourceCard from "./SourceCard";

function formatInline(text) {
  const parts = text.split(/(\*\*.*?\*\*)/g);

  return parts.map((part, index) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return (
        <strong key={index}>
          {part.slice(2, -2)}
        </strong>
      );
    }

    const standardParts = part.split(
      /(IS\s?\d+(?::\d+)*(?:-\d+)?)/gi
    );

    return standardParts.map((item, i) => {
      if (/^IS\s?\d+(?::\d+)*(?:-\d+)?$/i.test(item)) {
        return (
          <span key={`${index}-${i}`} className="standard-tag">
            {item}
          </span>
        );
      }

      return item;
    });
  });
}

function formatAnswer(text) {
  if (!text) return null;

  const lines = text
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);

  const output = [];

  lines.forEach((line, index) => {
    /* Markdown headings */
    if (line.startsWith("### ")) {
      output.push(
        <h4 key={`heading-small-${index}`} className="answer-heading-small">
          {formatInline(line.replace("### ", ""))}
        </h4>
      );
      return;
    }

    if (line.startsWith("## ")) {
      output.push(
        <h3 key={`heading-${index}`} className="answer-heading">
          {formatInline(line.replace("## ", ""))}
        </h3>
      );
      return;
    }

    /* Existing bullet */
    if (line.startsWith("- ") || line.startsWith("• ")) {
      output.push(
        <div key={`bullet-${index}`} className="answer-bullet">
          <span>•</span>
          <div>{formatInline(line.replace(/^[-•]\s*/, ""))}</div>
        </div>
      );
      return;
    }

    /* Existing numbered list */
    if (/^\d+\.\s/.test(line)) {
      const match = line.match(/^(\d+)\.\s(.*)/);

      output.push(
        <div key={`number-${index}`} className="answer-numbered">
          <span>{match[1]}</span>
          <div>{formatInline(match[2])}</div>
        </div>
      );
      return;
    }

    /*
      IMPORTANT:
      If backend returns a normal paragraph,
      automatically turn each sentence into a bullet.
    */

    const sentences = line.match(/[^.!?]+[.!?]+(?=\s|$)|[^.!?]+$/g);

    if (sentences && sentences.length > 1) {
      sentences.forEach((sentence, sentenceIndex) => {
        const cleanSentence = sentence.trim();

        if (!cleanSentence) return;

        output.push(
          <div
            key={`auto-bullet-${index}-${sentenceIndex}`}
            className="answer-bullet"
          >
            <span>•</span>
            <div>{formatInline(cleanSentence)}</div>
          </div>
        );
      });
    } else {
      output.push(
        <p key={`paragraph-${index}`} className="answer-paragraph">
          {formatInline(line)}
        </p>
      );
    }
  });

  return output;
}

function Message({ message }) {
  const isUser = message.type === "user";
  const [copied, setCopied] = useState(false);

  const copyAnswer = async () => {
    try {
      await navigator.clipboard.writeText(message.text);
      setCopied(true);

      setTimeout(() => {
        setCopied(false);
      }, 1800);
    } catch (error) {
      console.error("Copy failed:", error);
    }
  };

  return (
    <div className={`message-row ${isUser ? "user-row" : "assistant-row"}`}>
      <div className={`avatar ${isUser ? "user-avatar" : "ai-avatar"}`}>
        {isUser ? "You" : "B"}
      </div>

      <div className="message-content">

        <div className="message-name">
          {isUser ? "You" : "BIS Assistant"}
        </div>

        <div
          className={`message-bubble ${
            isUser ? "user-bubble" : "assistant-bubble"
          }`}
        >

          {isUser ? (
            <p className="user-text">{message.text}</p>
          ) : (
            <>
              {/* AI HEADER */}

              <div className="answer-header">

                <div className="answer-label">
                  <span className="answer-icon">✦</span>
                  BIS Knowledge Assistant
                </div>

                <button
                  className="copy-button"
                  onClick={copyAnswer}
                  title="Copy answer"
                >
                  {copied ? "✓ Copied" : "⧉ Copy"}
                </button>

              </div>

              {/* ANSWER */}

              <div className="answer-body">

                <div className="answer-section-title">
                  Answer
                </div>

                {formatAnswer(message.text)}

              </div>

              {/* GROUNDING */}

              <div className="grounding-note">
                <span>✓</span>
                Answer grounded in retrieved BIS sources
              </div>

            </>
          )}

        </div>

        {/* SOURCES */}

        {!isUser && message.sources?.length > 0 && (
          <div className="sources">

            <div className="sources-title">
              <span>📚</span>
              Retrieved BIS sources
            </div>

            <div className="sources-list">
              {message.sources.map((source, index) => (
                <SourceCard
                  key={index}
                  source={source}
                />
              ))}
            </div>

          </div>
        )}

      </div>
    </div>
  );
}

export default Message;