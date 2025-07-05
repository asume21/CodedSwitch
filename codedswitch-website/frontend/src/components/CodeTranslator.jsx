import React, { useState, useEffect } from 'react';
import './CodeTranslator.css';

const CodeTranslator = ({ userSubscription }) => {
  const [sourceCode, setSourceCode] = useState('');
  const [translatedCode, setTranslatedCode] = useState('');
  const [sourceLanguage, setSourceLanguage] = useState('python');
  const [targetLanguage, setTargetLanguage] = useState('javascript');
  const [isTranslating, setIsTranslating] = useState(false);
  const [translationHistory, setTranslationHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);

  const supportedLanguages = [
    { id: 'python', name: 'Python', icon: '🐍' },
    { id: 'javascript', name: 'JavaScript', icon: '⚡' },
    { id: 'java', name: 'Java', icon: '☕' },
    { id: 'cpp', name: 'C++', icon: '⚙️' },
    { id: 'php', name: 'PHP', icon: '🐘' },
    { id: 'csharp', name: 'C#', icon: '🎯' },
    { id: 'ruby', name: 'Ruby', icon: '💎' },
    { id: 'go', name: 'Go', icon: '🚀' },
    { id: 'rust', name: 'Rust', icon: '🦀' },
    { id: 'swift', name: 'Swift', icon: '🍎' }
  ];

  const codeExamples = {
    python: `def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Calculate first 10 Fibonacci numbers
for i in range(10):
    print(fibonacci(i))`,
    
    javascript: `function fibonacci(n) {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

// Calculate first 10 Fibonacci numbers
for (let i = 0; i < 10; i++) {
    console.log(fibonacci(i));
}`,
    
    java: `public class Fibonacci {
    public static int fibonacci(int n) {
        if (n <= 1) return n;
        return fibonacci(n - 1) + fibonacci(n - 2);
    }
    
    public static void main(String[] args) {
        // Calculate first 10 Fibonacci numbers
        for (int i = 0; i < 10; i++) {
            System.out.println(fibonacci(i));
        }
    }
}`
  };

  useEffect(() => {
    // Load example code when language changes
    if (codeExamples[sourceLanguage]) {
      setSourceCode(codeExamples[sourceLanguage]);
    }
  }, [sourceLanguage]);

  const translateCode = async () => {
    if (!sourceCode.trim()) {
      alert('Please enter some code to translate!');
      return;
    }

    setIsTranslating(true);
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/translate-code`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          sourceCode,
          sourceLanguage,
          targetLanguage,
          userId: 'anonymous'
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setTranslatedCode(data.translatedCode);
        
        // Add to history
        const newEntry = {
          id: Date.now(),
          sourceLanguage,
          targetLanguage,
          sourceCode,
          translatedCode: data.translatedCode,
          timestamp: new Date().toISOString()
        };
        setTranslationHistory(prev => [newEntry, ...prev.slice(0, 9)]); // Keep last 10
      } else {
        throw new Error('Translation failed');
      }
    } catch (error) {
      console.error('Error translating code:', error);
      // Fallback to demo translation
      setTranslatedCode(generateDemoTranslation());
    } finally {
      setIsTranslating(false);
    }
  };

  const generateDemoTranslation = () => {
    const translations = {
      'python-javascript': `function fibonacci(n) {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

// Calculate first 10 Fibonacci numbers
for (let i = 0; i < 10; i++) {
    console.log(fibonacci(i));
}`,
      'javascript-python': `def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Calculate first 10 Fibonacci numbers
for i in range(10):
    print(fibonacci(i))`,
      'python-java': `public class Fibonacci {
    public static int fibonacci(int n) {
        if (n <= 1) return n;
        return fibonacci(n - 1) + fibonacci(n - 2);
    }
    
    public static void main(String[] args) {
        // Calculate first 10 Fibonacci numbers
        for (int i = 0; i < 10; i++) {
            System.out.println(fibonacci(i));
        }
    }
}`
    };
    
    const key = `${sourceLanguage}-${targetLanguage}`;
    return translations[key] || `// Translation from ${sourceLanguage} to ${targetLanguage}\n// Demo translation - connect to AI service for real translation\n\n${sourceCode}`;
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    alert('Code copied to clipboard!');
  };

  const downloadCode = (code, filename) => {
    const blob = new Blob([code], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  const swapLanguages = () => {
    setSourceLanguage(targetLanguage);
    setTargetLanguage(sourceLanguage);
    setSourceCode(translatedCode);
    setTranslatedCode('');
  };

  return (
    <div className="code-translator">
      <div className="translator-header">
        <h2>💻 AI Code Translator</h2>
        <p>Translate code between 10+ programming languages with AI intelligence</p>
      </div>

      <div className="language-selector">
        <div className="language-group">
          <label>From:</label>
          <select 
            value={sourceLanguage} 
            onChange={(e) => setSourceLanguage(e.target.value)}
          >
            {supportedLanguages.map(lang => (
              <option key={lang.id} value={lang.id}>
                {lang.icon} {lang.name}
              </option>
            ))}
          </select>
        </div>

        <button className="swap-btn" onClick={swapLanguages}>
          🔄
        </button>

        <div className="language-group">
          <label>To:</label>
          <select 
            value={targetLanguage} 
            onChange={(e) => setTargetLanguage(e.target.value)}
          >
            {supportedLanguages.map(lang => (
              <option key={lang.id} value={lang.id}>
                {lang.icon} {lang.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="code-editor-container">
        <div className="code-editor">
          <div className="editor-header">
            <span>{supportedLanguages.find(l => l.id === sourceLanguage)?.icon} {supportedLanguages.find(l => l.id === sourceLanguage)?.name}</span>
            <div className="editor-actions">
              <button onClick={() => copyToClipboard(sourceCode)} className="action-btn">
                📋 Copy
              </button>
              <button onClick={() => downloadCode(sourceCode, `source.${sourceLanguage}`)} className="action-btn">
                💾 Download
              </button>
            </div>
          </div>
          <textarea
            value={sourceCode}
            onChange={(e) => setSourceCode(e.target.value)}
            placeholder={`Enter your ${supportedLanguages.find(l => l.id === sourceLanguage)?.name} code here...`}
            className="code-textarea"
          />
        </div>

        <div className="translate-button-container">
          <button 
            className="translate-btn"
            onClick={translateCode}
            disabled={isTranslating || !sourceCode.trim()}
          >
            {isTranslating ? '🔄 Translating...' : '🚀 Translate'}
          </button>
        </div>

        <div className="code-editor">
          <div className="editor-header">
            <span>{supportedLanguages.find(l => l.id === targetLanguage)?.icon} {supportedLanguages.find(l => l.id === targetLanguage)?.name}</span>
            <div className="editor-actions">
              <button onClick={() => copyToClipboard(translatedCode)} className="action-btn">
                📋 Copy
              </button>
              <button onClick={() => downloadCode(translatedCode, `translated.${targetLanguage}`)} className="action-btn">
                💾 Download
              </button>
            </div>
          </div>
          <textarea
            value={translatedCode}
            readOnly
            placeholder="Translated code will appear here..."
            className="code-textarea"
          />
        </div>
      </div>

      <div className="translator-footer">
        <button 
          className="history-btn"
          onClick={() => setShowHistory(!showHistory)}
        >
          📚 Translation History
        </button>
        
        {userSubscription?.plan === 'free' && (
          <div className="upgrade-notice">
            <p>💡 Upgrade to Pro for unlimited translations and advanced features!</p>
            <button 
              className="upgrade-btn"
              onClick={() => window.location.href = '/pricing'}
            >
              Upgrade Now
            </button>
          </div>
        )}
      </div>

      {showHistory && translationHistory.length > 0 && (
        <div className="translation-history">
          <h3>Recent Translations</h3>
          <div className="history-list">
            {translationHistory.map(entry => (
              <div key={entry.id} className="history-item">
                <div className="history-header">
                  <span>{supportedLanguages.find(l => l.id === entry.sourceLanguage)?.icon} → {supportedLanguages.find(l => l.id === entry.targetLanguage)?.icon}</span>
                  <span className="history-time">
                    {new Date(entry.timestamp).toLocaleString()}
                  </span>
                </div>
                <div className="history-preview">
                  <pre>{entry.sourceCode.substring(0, 100)}...</pre>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default CodeTranslator; 