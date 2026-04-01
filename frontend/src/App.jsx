import React, { useState } from 'react';
import EventForm from './components/EventForm';
import ExecutionLog from './components/ExecutionLog';
import FinalOutput from './components/FinalOutput';
import WorkflowBoard from './components/WorkflowBoard';
import WorkflowDesigner from './components/WorkflowDesigner';
import ChatWorkflow from './components/ChatWorkflow';
import * as apiService from './services/api';
import './App.css';

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [executionLogs, setExecutionLogs] = useState([]);
  const [finalPlan, setFinalPlan] = useState(null);
  const [currentEventId, setCurrentEventId] = useState(null);
  const [error, setError] = useState(null);
  const [workflowBlueprint, setWorkflowBlueprint] = useState([]);
  const [activeTab, setActiveTab] = useState('designer'); // 'designer' or 'chat'

  const handleEventSubmit = async (eventData) => {
    setIsLoading(true);
    setError(null);
    setExecutionLogs([]);
    setFinalPlan(null);

    try {
      // Add initial log
      setExecutionLogs([{ step: 'Initializing...', status: 'running', data: null }]);

      // Submit event and run workflow
      const result = await apiService.submitEventAndRun({
        ...eventData,
        workflow_blueprint: workflowBlueprint,
      });
      setCurrentEventId(result.event_id);

      // Update execution logs
      setExecutionLogs(result.logs || []);

      // Display final plan
      if (result.final_plan) {
        setFinalPlan(result.final_plan);
      }

      console.log('Workflow completed:', result);
    } catch (err) {
      setError(err.response?.data?.message || err.message || 'Workflow failed');
      setExecutionLogs(prev => [
        ...prev,
        { step: 'Error', status: 'failed', data: err.message }
      ]);
      console.error('Workflow error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleChatWorkflowExecuted = (result) => {
    if (result) {
      setFinalPlan(result);
      setExecutionLogs(result.logs || []);
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>🤖 AgentFlow AI</h1>
        <p>Natural Language & Node-Based Workflow Automation</p>
      </header>

      <main className="app-main">
        {/* Tab Navigation */}
        <div className="tab-navigation">
          <button
            className={`tab-button ${activeTab === 'designer' ? 'active' : ''}`}
            onClick={() => setActiveTab('designer')}
          >
            🎨 Workflow Designer
          </button>
          <button
            className={`tab-button ${activeTab === 'chat' ? 'active' : ''}`}
            onClick={() => setActiveTab('chat')}
          >
            ✨ Natural Language
          </button>
        </div>

        {activeTab === 'designer' && (
          <div className="layout-2col">
            {/* Left Column: Form */}
            <div className="column-left">
              <EventForm onSubmit={handleEventSubmit} isLoading={isLoading} />
              <WorkflowDesigner value={workflowBlueprint} onChange={setWorkflowBlueprint} />
            </div>

            {/* Right Column: Logs & Output */}
            <div className="column-right">
              <ExecutionLog logs={executionLogs} isRunning={isLoading} />
              <FinalOutput plan={finalPlan} loading={isLoading} />
            </div>
          </div>
        )}

        {activeTab === 'chat' && (
          <div className="chat-tab-content">
            <ChatWorkflow onWorkflowExecuted={handleChatWorkflowExecuted} />
          </div>
        )}

        {error && (
          <div className="error-banner">
            <span style={{ fontSize: '16px' }}>❌ {error}</span>
            <button onClick={() => setError(null)} style={{ marginLeft: '10px', cursor: 'pointer' }}>
              Dismiss
            </button>
          </div>
        )}

        {(activeTab === 'designer' || (activeTab === 'chat' && finalPlan)) && (
          <WorkflowBoard plan={finalPlan} logs={executionLogs} isRunning={isLoading} />
        )}
      </main>

      <footer className="app-footer">
        <p>© 2026 AgentFlow AI | Smart Workflow Automation</p>
      </footer>
    </div>
  );
}

export default App;
