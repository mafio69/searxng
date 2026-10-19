import React from 'react';
import Icon from './Icon.jsx';
import { isDevMode } from './api.js';

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error) {
    return { error };
  }

  render() {
    if (!this.state.error) return this.props.children;
    const showDetail = isDevMode(this.props.appEnv) && this.state.error?.message;
    return (
      <div className="app-shell">
        <div className="workspace">
          <main id="main" className="main-content">
            <section className="search-feedback" aria-live="polite" aria-atomic="true">
              <div className="message-card error-message" role="alert">
                <Icon name="globe" size={30} />
                <h2>Błąd. Przepraszamy</h2>
                <p>Wystąpił problem techniczny. Spróbuj ponownie za moment.</p>
                {showDetail && <p>{this.state.error.message}</p>}
                <button className="secondary-button" onClick={() => this.setState({ error: null })}>
                  Spróbuj ponownie <Icon name="arrow" size={16} />
                </button>
              </div>
            </section>
          </main>
        </div>
      </div>
    );
  }
}
