import React from 'react';

const ExecutionLog = ({ logs, isRunning }) => {
  return (
    <div style={styles.logContainer}>
      <h2 style={styles.heading}>Execution Log</h2>
      <div style={styles.logContent}>
        {logs.length === 0 && !isRunning && (
          <p style={styles.emptyMessage}>Submit a workflow and click "Run AI" to see autonomous execution logs</p>
        )}
        
        {logs.map((log, index) => (
          <div key={index} style={{
            ...styles.logEntry,
            borderLeftColor: log.status === 'completed' ? '#28a745' : log.status === 'running' ? '#ffc107' : '#dc3545',
          }}>
            <div style={styles.stepHeader}>
              <span style={styles.stepName}>{log.step}</span>
              <span style={{
                ...styles.badge,
                backgroundColor: log.status === 'completed' ? '#28a745' : log.status === 'running' ? '#ffc107' : '#dc3545',
              }}>
                {log.status === 'completed' && '✓'}
                {log.status === 'running' && '⏳'}
                {log.status === 'failed' && '✗'}
              </span>
            </div>
            {log.data && (
              <pre style={styles.dataPreview}>{JSON.stringify(log.data, null, 2).substring(0, 200)}...</pre>
            )}
          </div>
        ))}

        {isRunning && (
          <div style={styles.loadingMessage}>
            <p>🔄 Processing workflow...</p>
          </div>
        )}
      </div>
    </div>
  );
};

const styles = {
  logContainer: {
    backgroundColor: '#f9f9f9',
    border: '1px solid #e0e0e0',
    borderRadius: '8px',
    padding: '20px',
    width: '100%',
    maxWidth: '700px',
    maxHeight: '500px',
    overflowY: 'auto',
  },
  heading: {
    fontSize: '16px',
    fontWeight: '600',
    marginBottom: '15px',
    color: '#1a1a1a',
  },
  logContent: {
    display: 'flex',
    flexDirection: 'column',
    gap: '10px',
  },
  emptyMessage: {
    color: '#666',
    fontSize: '13px',
    fontStyle: 'italic',
    padding: '20px',
    textAlign: 'center',
    backgroundColor: '#fff',
    borderRadius: '4px',
  },
  logEntry: {
    borderLeft: '4px solid #0066cc',
    backgroundColor: '#fff',
    padding: '12px',
    borderRadius: '4px',
    fontSize: '12px',
  },
  stepHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '8px',
  },
  stepName: {
    fontWeight: '600',
    color: '#1a1a1a',
  },
  badge: {
    color: '#fff',
    padding: '4px 8px',
    borderRadius: '3px',
    fontSize: '11px',
    fontWeight: '600',
  },
  dataPreview: {
    backgroundColor: '#f5f5f5',
    padding: '8px',
    borderRadius: '3px',
    fontSize: '11px',
    overflow: 'hidden',
    color: '#333',
    margin: '0',
  },
  loadingMessage: {
    padding: '15px',
    backgroundColor: '#e3f2fd',
    borderRadius: '4px',
    color: '#0066cc',
    textAlign: 'center',
    fontWeight: '500',
  },
};

export default ExecutionLog;
