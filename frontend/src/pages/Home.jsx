import { useState } from "react";
import Header from "../components/Header";
import ChatWindow from "../components/ChatWindow";
import ChatInput from "../components/ChatInput";
import ExampleQuestions from "../components/ExampleQuestions";

function Home() {
  const [messages, setMessages] = useState([]);

  const handleSend = async (text) => {
    if (!text.trim()) return;

    // 1. Add user message to UI
    const userMessage = {
      id: Date.now(),
      type: "user",
      text: text,
    };
    setMessages((prev) => [...prev, userMessage]);
    
    // Optional: Add a loading state if you have one configured
    // setIsLoading(true);

    try {
      // 2. Fetch from your running FastAPI backend
      const response = await fetch("http://localhost:8000/api/v1/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Accept": "application/json",
        },
        body: JSON.stringify({ query: text, language: "en" }),
      });

      if (!response.ok) throw new Error("Backend connection failed");
      
      const data = await response.json();

      // 3. Map backend citations to match Moksha's ChatWindow prop expectations
      const mappedSources = data.citations?.map((cite) => ({
        title: cite.standard_id || cite.scheme || cite.source_file,
        description: cite.title || cite.doc_type || "BIS Knowledge Base",
      })) || [];

      // 4. Add the real AI response to the UI
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          type: "assistant",
          text: data.answer,
          sources: mappedSources,
        },
      ]);
    } catch (error) {
      console.error("Error connecting to backend:", error);
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          type: "assistant",
          text: "I couldn't connect to the backend. Please ensure the FastAPI server is running on localhost:8000.",
          sources: [],
        },
      ]);
    }
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