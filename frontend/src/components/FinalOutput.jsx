import React from 'react';

const FinalOutput = ({ plan, loading }) => {
  if (loading) {
    return (
      <div style={styles.outputContainer}>
        <h2 style={styles.heading}>Workflow Plan</h2>
        <p style={styles.loadingText}>⏳ Executing autonomous workflow...</p>
      </div>
    );
  }

  if (!plan) {
    return (
      <div style={styles.outputContainer}>
        <h2 style={styles.heading}>Workflow Plan</h2>
        <p style={styles.emptyText}>Execution result will appear here after Run AI</p>
      </div>
    );
  }

  return (
    <div style={styles.outputContainer}>
      <h2 style={styles.heading}>✅ Workflow Plan Generated</h2>

      <div style={styles.section}>
        <h3 style={styles.sectionTitle}>Workflow Summary</h3>
        <div style={styles.infoGrid}>
          <div style={styles.infoItem}>
            <span style={styles.label}>Workload:</span>
            <span style={styles.value}>{plan.workflow?.workload_units}</span>
          </div>
          <div style={styles.infoItem}>
            <span style={styles.label}>Mode:</span>
            <span style={styles.value}>{plan.workflow?.execution_mode}</span>
          </div>
          <div style={styles.infoItem}>
            <span style={styles.label}>Target:</span>
            <span style={styles.value}>{plan.workflow?.target_system}</span>
          </div>
        </div>
      </div>

      <div style={styles.section}>
        <h3 style={styles.sectionTitle}>Execution Metrics</h3>
        <div style={styles.costBreakdown}>
          <div style={styles.costItem}>
            <span>Estimated Run Cost:</span>
            <span style={styles.costValue}>${plan.task_graph?.estimated_run_cost?.toFixed(2)}</span>
          </div>
          <div style={styles.costItem}>
            <span>Expected Duration:</span>
            <span style={styles.costValue}>{plan.agent_requirements?.estimated_duration_hours}h</span>
          </div>
          <div style={{ ...styles.costItem, borderTop: '2px solid #ddd', paddingTop: '10px', marginTop: '10px', fontWeight: 'bold' }}>
            <span>Total Resource Score:</span>
            <span style={{ ...styles.costValue, fontSize: '16px', color: '#0066cc' }}>
              {plan.optimization?.efficiency_score || 'N/A'}
            </span>
          </div>
        </div>
      </div>

      <div style={styles.section}>
        <h3 style={styles.sectionTitle}>Agent Allocation</h3>
        <div style={styles.staffGrid}>
          {plan.agent_requirements?.agents_required?.map((agent, idx) => (
            <div key={idx} style={styles.staffCard}>
              <div style={styles.staffRole}>{agent.role}</div>
              <div style={styles.staffCount}>{agent.count} agents</div>
              <div style={styles.staffCost}>{agent.capability}</div>
            </div>
          ))}
        </div>
      </div>

      <div style={styles.section}>
        <h3 style={styles.sectionTitle}>Task Graph</h3>
        <div style={styles.ingredientList}>
          {plan.task_graph?.tasks?.slice(0, 8).map((task, idx) => (
            <div key={idx} style={styles.ingredientItem}>
              <span>{task.name}</span>
              <span style={styles.ingredientQty}>{task.owner} · {task.status}</span>
            </div>
          ))}
          {plan.task_graph?.tasks?.length > 8 && (
            <div style={styles.moreItems}>
              +{plan.task_graph?.tasks?.length - 8} more tasks
            </div>
          )}
        </div>
      </div>

      <div style={styles.section}>
        <h3 style={styles.sectionTitle}>Model Stack</h3>
        <div style={styles.ingredientList}>
          {(plan.model_stack || []).length > 0 ? (
            plan.model_stack.map((model, idx) => (
              <div key={idx} style={styles.ingredientItem}>
                <span>{model.node_name}</span>
                <span style={styles.ingredientQty}>{model.provider} · {model.model}</span>
              </div>
            ))
          ) : (
            <div style={styles.moreItems}>No model nodes configured</div>
          )}
        </div>
      </div>

      <div style={styles.section}>
        <h3 style={styles.sectionTitle}>⚠️ Alerts</h3>
        <div style={styles.riskList}>
          {plan.alerts?.length > 0 ? (
            plan.alerts.map((alert, idx) => (
              <div key={idx} style={styles.riskItem}>• {alert}</div>
            ))
          ) : (
            <p style={styles.noRisks}>No critical alerts</p>
          )}
        </div>
      </div>

      <div style={styles.section}>
        <h3 style={styles.sectionTitle}>🔧 Automated Actions</h3>
        <div style={styles.contingencyList}>
          {plan.actions?.length > 0 ? (
            plan.actions.map((action, idx) => (
              <div key={idx} style={styles.contingencyItem}>✓ {action}</div>
            ))
          ) : (
            <p style={styles.noContingency}>No fallback actions needed</p>
          )}
        </div>
      </div>
    </div>
  );
};

const styles = {
  outputContainer: {
    backgroundColor: '#f5f9fc',
    border: '1px solid #b3d9ff',
    borderRadius: '8px',
    padding: '25px',
    width: '100%',
    maxWidth: '700px',
  },
  heading: {
    fontSize: '18px',
    fontWeight: '700',
    color: '#0066cc',
    marginBottom: '20px',
  },
  loadingText: {
    color: '#666',
    fontSize: '14px',
    textAlign: 'center',
    padding: '40px 20px',
  },
  emptyText: {
    color: '#999',
    fontSize: '13px',
    textAlign: 'center',
    padding: '40px 20px',
    fontStyle: 'italic',
  },
  section: {
    marginBottom: '25px',
  },
  sectionTitle: {
    fontSize: '14px',
    fontWeight: '600',
    color: '#1a1a1a',
    borderBottom: '2px solid #e0e0e0',
    paddingBottom: '8px',
    marginBottom: '12px',
  },
  infoGrid: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr 1fr',
    gap: '10px',
  },
  infoItem: {
    display: 'flex',
    flexDirection: 'column',
    padding: '10px',
    backgroundColor: '#fff',
    borderRadius: '4px',
    border: '1px solid #e0e0e0',
  },
  label: {
    fontSize: '11px',
    fontWeight: '600',
    color: '#666',
    textTransform: 'uppercase',
  },
  value: {
    fontSize: '14px',
    fontWeight: '600',
    color: '#0066cc',
    marginTop: '4px',
  },
  costBreakdown: {
    backgroundColor: '#fff',
    padding: '15px',
    borderRadius: '4px',
    border: '1px solid #e0e0e0',
  },
  costItem: {
    display: 'flex',
    justifyContent: 'space-between',
    padding: '8px 0',
    fontSize: '13px',
  },
  costValue: {
    fontWeight: '600',
    color: '#28a745',
  },
  staffGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: '12px',
  },
  staffCard: {
    backgroundColor: '#fff',
    padding: '15px',
    borderRadius: '4px',
    border: '1px solid #e0e0e0',
    textAlign: 'center',
  },
  staffRole: {
    fontSize: '12px',
    fontWeight: '600',
    color: '#666',
    textTransform: 'uppercase',
  },
  staffCount: {
    fontSize: '20px',
    fontWeight: '700',
    color: '#0066cc',
    margin: '8px 0',
  },
  staffCost: {
    fontSize: '11px',
    color: '#666',
  },
  ingredientList: {
    backgroundColor: '#fff',
    padding: '12px',
    borderRadius: '4px',
    border: '1px solid #e0e0e0',
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '8px',
  },
  ingredientItem: {
    display: 'flex',
    justifyContent: 'space-between',
    fontSize: '12px',
    padding: '6px 0',
    borderBottom: '1px solid #f0f0f0',
  },
  ingredientQty: {
    color: '#666',
    fontWeight: '600',
  },
  moreItems: {
    fontSize: '11px',
    color: '#0066cc',
    fontWeight: '600',
    gridColumn: '1 / -1',
    padding: '8px',
    textAlign: 'center',
  },
  riskList: {
    backgroundColor: '#fff3cd',
    padding: '12px',
    borderRadius: '4px',
    border: '1px solid #ffeeba',
  },
  riskItem: {
    fontSize: '12px',
    color: '#856404',
    padding: '6px 0',
  },
  noRisks: {
    fontSize: '12px',
    color: '#28a745',
    fontWeight: '600',
  },
  contingencyList: {
    backgroundColor: '#d4edda',
    padding: '12px',
    borderRadius: '4px',
    border: '1px solid #c3e6cb',
  },
  contingencyItem: {
    fontSize: '12px',
    color: '#155724',
    padding: '6px 0',
  },
  noContingency: {
    fontSize: '12px',
    color: '#155724',
    fontWeight: '600',
  },
};

export default FinalOutput;
