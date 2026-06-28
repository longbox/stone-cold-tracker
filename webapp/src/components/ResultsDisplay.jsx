export default function ResultsDisplay({ result }) {
  // Check if result is the new object format or fallback to string
  const isObject = typeof result === 'object' && result !== null;
  const analysisText = isObject ? result.analysis_text : result;
  const score = isObject && typeof result.oxalate_score === 'number' ? result.oxalate_score : null;

  // Determine color based on score (0 = green/cold, 100 = red/hot)
  const getScoreColor = (value) => {
    if (value === null) return '#10b981';
    // HSL: 120 is green, 0 is red.
    const hue = ((100 - value) * 1.2).toString(10); 
    return `hsl(${hue}, 80%, 50%)`;
  };

  const meterColor = getScoreColor(score);

  return (
    <div className="glass-panel animate-fade-in" style={{ padding: '2rem', marginTop: '1rem' }}>
      <h2 style={{ fontSize: '1.8rem', marginBottom: '1.5rem', color: '#10b981' }}>Analysis Results</h2>
      
      {score !== null && (
        <div style={{ marginBottom: '2rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
            <span style={{ fontWeight: 600 }}>Oxalate Level</span>
            <span style={{ fontWeight: 600, color: meterColor }}>{score} / 100</span>
          </div>
          <div style={{ 
            width: '100%', 
            height: '24px', 
            background: 'rgba(255, 255, 255, 0.1)', 
            borderRadius: '12px',
            overflow: 'hidden'
          }}>
            <div style={{
              width: `${score}%`,
              height: '100%',
              background: `linear-gradient(90deg, #10b981 0%, ${meterColor} 100%)`,
              transition: 'width 1s ease-out'
            }}></div>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: 'rgba(255,255,255,0.5)', marginTop: '0.25rem' }}>
            <span>Low (Cold)</span>
            <span>High (Hot)</span>
          </div>
        </div>
      )}

      <div style={{ 
        lineHeight: '1.7', 
        fontSize: '1.1rem',
        whiteSpace: 'pre-wrap'
      }}>
        {analysisText}
      </div>
    </div>
  );
}

