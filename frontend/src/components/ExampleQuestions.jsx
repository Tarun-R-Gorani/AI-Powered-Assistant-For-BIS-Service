const questions = [
  {
    icon: "🔎",
    title: "Find a standard",
    text: "Which BIS standard applies to packaged drinking water?",
  },
  {
    icon: "📋",
    title: "Certification",
    text: "How can a manufacturer apply for BIS certification?",
  },
  {
    icon: "🛡️",
    title: "ISI Mark",
    text: "What are the requirements for using the ISI mark?",
  },
  {
    icon: "💡",
    title: "Compliance help",
    text: "What documents are required for product certification?",
  },
];

function ExampleQuestions({ onSelect }) {
  return (
    <section className="examples">
      <div className="examples-heading">
        <span>Try asking</span>
        <span className="sparkle">✦</span>
      </div>

      <div className="question-grid">
        {questions.map((question) => (
          <button
            className="question-card"
            key={question.title}
            onClick={() => onSelect(question.text)}
          >
            <div className="question-icon">{question.icon}</div>

            <div className="question-content">
              <strong>{question.title}</strong>
              <p>{question.text}</p>
            </div>

            <span className="arrow">→</span>
          </button>
        ))}
      </div>
    </section>
  );
}

export default ExampleQuestions;