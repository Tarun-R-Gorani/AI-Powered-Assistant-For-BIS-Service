import Message from "./Message";

function ChatWindow({ messages }) {
  return (
    <section className="chat-window">
      {messages.map((message) => (
        <Message key={message.id} message={message} />
      ))}
    </section>
  );
}

export default ChatWindow;