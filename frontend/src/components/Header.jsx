function Header() {
  return (
    <header className="header">
      <div className="logo-section">
        <div className="logo-mark">B</div>

        <div>
          <div className="logo-title">BIS Smart Assistant</div>
          <div className="logo-subtitle">
            Indian Standards & Certification
          </div>
        </div>
      </div>

      <div className="header-right">
        <div className="status">
          <span className="status-dot"></span>
          Prototype Online
        </div>

        <button className="language-btn">
          EN <span>⌄</span>
        </button>
      </div>
    </header>
  );
}

export default Header;