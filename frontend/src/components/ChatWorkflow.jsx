import React, { useState } from 'react';
import './ChatWorkflow.css';

const ChatWorkflow = ({ onWorkflowExecuted }) => {
  const [userRequest, setUserRequest] = useState('');
  const [workflow, setWorkflow] = useState(null);
  const [executionResult, setExecutionResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [executionLogs, setExecutionLogs] = useState([]);
  const [step, setStep] = useState('input'); // input, review, executing, complete

  /**
   * Convert user request to workflow and optionally execute
   */
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!userRequest.trim()) return;

    setLoading(true);
    setError(null);
    setStep('review');

    try {
      // Call backend to convert chat to workflow
      const response = await fetch('http://localhost:5000/api/chat/workflow', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_request: userRequest,
          auto_execute: false,
        }),
      });

      const data = await response.json();

      if (!data.success) {
        setError(data.error || 'Failed to process request');
        setStep('input');
        return;
      }

      setWorkflow(data.workflow);
      setExecutionLogs([]);
      setExecutionResult(null);
    } catch (err) {
      setError(err.message);
      setStep('input');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Execute the generated workflow
   */
  const handleExecute = async () => {
    if (!workflow) return;

    setLoading(true);
    setError(null);
    setStep('executing');
    setExecutionLogs([]);

    try {
      const response = await fetch('http://localhost:5000/api/chat/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          workflow,
          secrets: {
            // Users can add secrets here
          },
        }),
      });

      const data = await response.json();

      if (!data.success) {
        setError(data.error || 'Execution failed');
        return;
      }

      setExecutionResult(data.execution);
      setExecutionLogs(data.execution.logs || []);
      setStep('complete');
      onWorkflowExecuted?.(data.execution);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Reset to input screen
   */
  const handleReset = () => {
    setUserRequest('');
    setWorkflow(null);
    setExecutionResult(null);
    setExecutionLogs([]);
    setError(null);
    setStep('input');
  };

  return (
    <div className="chat-workflow-container">
      <div className="chat-header">
        <h2>✨ Natural Language Workflow Builder</h2>
        <p>Describe what you want to automate in plain English</p>
      </div>

      {step === 'input' && (
        <div className="chat-input-section">
          <form onSubmit={handleSubmit}>
            <textarea
              placeholder="Example: Update Google Sheet with data, send Slack notification, then post to API..."
              value={userRequest}
              onChange={(e) => setUserRequest(e.target.value)}
              rows={4}
              className="chat-textarea"
              disabled={loading}
            />
            <button type="submit" className="btn-primary" disabled={loading || !userRequest.trim()}>
              {loading ? 'Processing...' : '🤖 Parse Workflow'}
            </button>
          </form>
          {error && <div className="error-message">{error}</div>}
        </div>
      )}

      {step === 'review' && workflow && (
        <div className="workflow-review-section">
          <div className="workflow-info">
            <h3>📋 Generated Workflow</h3>
            <div className="workflow-details">
              <p className="workflow-name">
                <strong>Name:</strong> {workflow.workflow_name}
              </p>
              <p className="workflow-steps">
                <strong>Steps:</strong> {workflow.steps.length}
              </p>
            </div>
          </div>

          <div className="steps-preview">
            <h4>Workflow Steps:</h4>
            <div className="steps-list">
              {workflow.steps.map((step, index) => (
                <div key={step.id} className="step-item">
                  <div className="step-header">
                    <span className="step-number">{step.id}</span>
                    <span className="step-action">{step.action}</span>
                    {step.depends_on.length > 0 && (
                      <span className="step-deps">depends on: {step.depends_on.join(', ')}</span>
                    )}
                  </div>
                  <div className="step-params">
                    <pre>{JSON.stringify(step.params, null, 2)}</pre>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="workflow-actions">
            <button className="btn-primary" onClick={handleExecute} disabled={loading}>
              {loading ? 'Executing...' : '▶️ Execute Workflow'}
            </button>
            <button className="btn-secondary" onClick={handleReset} disabled={loading}>
              ← Edit Request
            </button>
          </div>

          {error && <div className="error-message">{error}</div>}
        </div>
      )}

      {step === 'executing' && (
        <div className="execution-section">
          <h3>⚙️ Executing Workflow...</h3>
          <div className="execution-logs">
            {executionLogs.map((log, index) => (
              <div key={index} className={`log-entry log-${log.status}`}>
                <div className="log-time">{new Date(log.timestamp).toLocaleTimeString()}</div>
                <div className="log-step">{log.step_name || log.step}</div>
                <div className="log-status">
                  {log.status === 'success' && '✓'}
                  {log.status === 'failed' && '✗'}
                  {log.status === 'running' && '⏳'}
                  {log.status === 'pending' && '⊙'} {log.status}
                </div>
                {log.error && <div className="log-error">{log.error}</div>}
              </div>
            ))}
          </div>
        </div>
      )}

      {step === 'complete' && executionResult && (
        <div className="execution-complete-section">
          <div className="result-header">
            {executionResult.success ? (
              <>
                <h3>✅ Workflow Completed Successfully</h3>
              </>
            ) : (
              <>
                <h3>❌ Workflow Failed</h3>
              </>
            )}
          </div>

          <div className="result-summary">
            <div className="summary-stat">
              <label>Duration</label>
              <value>{executionResult.duration_ms}ms</value>
            </div>
            <div className="summary-stat">
              <label>Steps Completed</label>
              <value>
                {executionResult.steps_completed}/{executionResult.total_steps}
              </value>
            </div>
            {executionResult.error && (
              <div className="summary-stat error">
                <label>Error</label>
                <value>{executionResult.error}</value>
              </div>
            )}
          </div>

          <div className="results-section">
            <h4>📊 Step Results:</h4>
            <div className="results-list">
              {executionLogs.map((log, index) => (
                <div key={index} className={`result-item result-${log.status}`}>
                  <div className="result-header-mini">
                    <span className="result-status">
                      {log.status === 'success' && '✓'}
                      {log.status === 'failed' && '✗'}
                      {log.status === 'running' && '⏳'}
                    </span>
                    <strong>{log.step_name || log.step}</strong>
                    <span className="result-time">{log.duration_ms}ms</span>
                  </div>
                  {log.output && (
                    <details className="result-output">
                      <summary>Output</summary>
                      <pre>{JSON.stringify(log.output, null, 2)}</pre>
                    </details>
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="completion-actions">
            <button className="btn-primary" onClick={handleReset}>
              ← New Workflow
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatWorkflow;
