import React, { useState } from 'react';
import './App.css';

function App() {
  const [connection, setConnection] = useState({
    host: 'localhost',
    user: 'root',
    password: '',
    database: '',
    port: ''
  });
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleConnect = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:5000/api/connect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(connection)
      });
      
      const data = await response.json();
      if (!data.success) throw new Error(data.message);
      setError('');
    } catch (err) {
      setError(`Connection failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleQuery = async () => {

    if (!query.trim()) return;

    

    setLoading(true);

    try {

      const response = await fetch('http://localhost:5000/api/query', {

        method: 'POST',

        headers: { 'Content-Type': 'application/json' },

        body: JSON.stringify({ query })

      });

      

      const data = await response.json();

      if (data.status !== "success") throw new Error(data.message); // Access message, not error

      

      setResults(data.result);

      setHistory([{ query, sql: data.sql, result: data.result }, ...history]); // Ensure 'sql' is used here, not 'generated_sql'

      setError('');

    } catch (err) {
      setError(`Query failed : ${err.message}`);

    } finally {

      setLoading(false);

    }

};

  return (
    <div className="app-container">
      <h1>Natural Language SQL Assistant</h1>
      
      <div className="connection-panel">
        <h2>Database Connection</h2>
        <div className="input-group">
          {Object.entries(connection).map(([key, value]) => (
            <input
              key={key}
              type={key === 'password' ? 'password' : 'text'}
              placeholder={key.toUpperCase()}
              value={value}
              onChange={(e) => setConnection({ ...connection, [key]: e.target.value })}
            />
          ))}
        </div>
        <button onClick={handleConnect} disabled={loading}>
          {loading ? 'Connecting...' : 'Connect'}
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="query-section">
        <h2>Enter Your Request</h2>
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="e.g., Show all customers from California"
          disabled={loading}
        />
        <button onClick={handleQuery} disabled={loading}>
          {loading ? 'Processing...' : 'Execute'}
        </button>
      </div>

      <div className="results-section">
        <div className="results-panel">
          <h3>Results</h3>
          <ResultsDisplay data={results} />
        </div>
        
        <div className="history-panel">
          <h3>History</h3>
          {history.map((item, idx) => (
            <div key={idx} className="history-item">
              <p><strong>Query:</strong> {item.query}</p>
              <p><strong>SQL:</strong> <code>{item.sql}</code></p>
              <p><strong>Result:</strong> {typeof item.result === 'string' ? 
                item.result : `${item.result?.length} rows returned`}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

const ResultsDisplay = ({ data }) => {
  if (!data) return <div className="no-results">Submit a query to see results</div>;
  
  if (typeof data === 'string') return <div className="result-text">{data}</div>;
  
  if (Array.isArray(data) && data.length === 0) 
    return <div className="no-results">No results found</div>;

  return (
    <table className="result-table">
      <thead>
        <tr>
          {Object.keys(data[0]).map((key) => (
            <th key={key}>{key}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {data.map((row, idx) => (
          <tr key={idx}>
            {Object.values(row).map((value, i) => (
              <td key={i}>{String(value)}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default App;