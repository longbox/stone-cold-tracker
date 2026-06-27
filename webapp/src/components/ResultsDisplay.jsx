export default function ResultsDisplay({ result }) {
  return (
    <div className="glass-panel animate-fade-in" style={{ padding: '2rem', marginTop: '1rem' }}>
      <h2 style={{ fontSize: '1.8rem', marginBottom: '1.5rem', color: '#10b981' }}>Analysis Results</h2>
      
      <div style={{ 
        lineHeight: '1.7', 
        fontSize: '1.1rem',
        whiteSpace: 'pre-wrap'
      }}>
        {result}
      </div>
    </div>
  );
}
