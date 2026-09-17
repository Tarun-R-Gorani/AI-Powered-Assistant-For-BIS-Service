import { useState } from "react";
import Header from "../components/Header";
import ChatWindow from "../components/ChatWindow";
import ChatInput from "../components/ChatInput";
import ExampleQuestions from "../components/ExampleQuestions";

function Home() {
  const [messages, setMessages] = useState([]);

  const handleSend = (text) => {
    if (!text.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: "user",
      text: text,
    };

    setMessages((prev) => [...prev, userMessage]);

    // Temporary response.
    // Tomorrow this will call the FastAPI + RAG backend.
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          type: "assistant",
          text: "I’m currently using the prototype knowledge base. The RAG backend will retrieve the relevant BIS Standard and provide a grounded answer with its source.",
          sources: [
            {
              title: "BIS Standards Knowledge Base",
              description: "Source retrieved from the BIS standards dataset.",
            },
          ],
        },
      ]);
    }, 700);
  };

  const handleExampleClick = (question) => {
    handleSend(question);
  };

  return (
    <div className="app">
      <Header />

      <main className="main-container">
        <section className="hero">
          <div className="badge">
            <span className="badge-dot"></span>
            AI-Powered BIS Assistant
          </div>

          <h1>
            Understand Indian Standards.
            <span> Get certified with confidence.</span>
          </h1>

          <p className="hero-description">
            Ask questions about BIS standards, certification schemes,
            compliance requirements and product standards in simple language.
          </p>
        </section>

        {messages.length === 0 ? (
          <ExampleQuestions onSelect={handleExampleClick} />
        ) : (
          <ChatWindow messages={messages} />
        )}

        <div className="chat-area">
          <ChatInput onSend={handleSend} />
          <p className="disclaimer">
            AI-generated responses are grounded in retrieved BIS sources.
            Always verify regulatory requirements with official BIS information.
          </p>
        </div>
      </main>
    </div>
  );
}

export default Home;