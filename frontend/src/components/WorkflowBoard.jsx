import React from 'react';

const statusColor = {
  completed: '#2e7d32',
  running: '#f9a825',
  failed: '#c62828',
  planned: '#455a64',
};

const WorkflowBoard = ({ plan, logs, isRunning }) => {
  const tasks = plan?.task_graph?.tasks || [];

  const logMap = (logs || []).reduce((acc, log) => {
    if (log?.step) acc[log.step.toLowerCase()] = log.status;
    return acc;
  }, {});

  const inferStatus = (task) => {
    const name = task.name.toLowerCase();
    if (name.includes('parse')) return logMap['parsing input'] || task.status;
    if (name.includes('plan task graph')) return logMap['building task graph'] || task.status;
    if (name.includes('route')) return logMap['determining agent requirements'] || task.status;
    if (name.includes('execute')) return logMap['allocating agents'] || task.status;
    if (name.includes('validate')) return logMap['optimizing plan'] || task.status;
    if (name.includes('report')) return logMap['finalizing plan'] || task.status;
    return task.status;
  };

  return (
    <section className="workflow-board">
      <div className="workflow-board-header">
        <h2>Workflow Board</h2>
        <span className={`workflow-board-chip ${isRunning ? 'running' : 'idle'}`}>
          {isRunning ? 'Running' : 'Ready'}
        </span>
      </div>

      {!tasks.length ? (
        <div className="workflow-board-empty">
          Run AI to generate a visual workflow graph.
        </div>
      ) : (
        <div className="workflow-lane">
          {tasks.map((task, index) => {
            const runtimeStatus = inferStatus(task);
            const color = statusColor[runtimeStatus] || '#455a64';

            return (
              <React.Fragment key={task.id || index}>
                <div className="workflow-node" style={{ borderColor: color }}>
                  <div className="workflow-node-top">
                    <span className="workflow-node-owner">{task.owner}</span>
                    <span className="workflow-node-status" style={{ color }}>
                      {runtimeStatus}
                    </span>
                  </div>
                  <div className="workflow-node-title">{task.name}</div>
                  <div className="workflow-node-meta">Load: {task.workload}</div>
                </div>
                {index < tasks.length - 1 && <div className="workflow-edge">→</div>}
              </React.Fragment>
            );
          })}
        </div>
      )}
    </section>
  );
};

export default WorkflowBoard;
