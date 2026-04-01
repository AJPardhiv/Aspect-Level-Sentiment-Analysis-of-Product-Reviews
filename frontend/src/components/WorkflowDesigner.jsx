import React, { useMemo, useState } from 'react';

const NODE_TEMPLATES = [
  { type: 'trigger', label: 'Trigger', owner: 'coordinator' },
  { type: 'model', label: 'Model', owner: 'planner' },
  { type: 'tool', label: 'Tool', owner: 'executor' },
  { type: 'condition', label: 'Condition', owner: 'validator' },
  { type: 'output', label: 'Output', owner: 'reporter' },
];

const modelDefaults = {
  provider: 'OpenAI',
  model: 'gpt-4o-mini',
  prompt: 'Summarize and plan the next task with strict JSON output.',
};

const toolDefaults = {
  tool_name: 'CRM',
  action: 'create_or_update_record',
};

const WorkflowDesigner = ({ value = [], onChange }) => {
  const [selectedType, setSelectedType] = useState('model');

  const safeNodes = useMemo(() => (Array.isArray(value) ? value : []), [value]);

  const emit = (next) => {
    if (typeof onChange === 'function') onChange(next);
  };

  const addNode = () => {
    const template = NODE_TEMPLATES.find((t) => t.type === selectedType);
    const base = {
      id: `node_${Date.now()}_${Math.floor(Math.random() * 1000)}`,
      type: selectedType,
      name: template ? `${template.label} Node` : 'Node',
      owner: template?.owner || 'coordinator',
      config: {},
    };

    if (selectedType === 'model') base.config = { ...modelDefaults };
    if (selectedType === 'tool') base.config = { ...toolDefaults };

    emit([...safeNodes, base]);
  };

  const updateNode = (id, updater) => {
    const next = safeNodes.map((node) => (node.id === id ? updater(node) : node));
    emit(next);
  };

  const removeNode = (id) => {
    emit(safeNodes.filter((n) => n.id !== id));
  };

  return (
    <div className="designer-card">
      <div className="designer-top">
        <h3>Workflow Designer</h3>
        <span>{safeNodes.length} nodes</span>
      </div>

      <div className="designer-actions">
        <select value={selectedType} onChange={(e) => setSelectedType(e.target.value)} className="designer-select">
          {NODE_TEMPLATES.map((template) => (
            <option key={template.type} value={template.type}>{template.label}</option>
          ))}
        </select>
        <button type="button" onClick={addNode} className="designer-add-btn">Add Node</button>
      </div>

      {!safeNodes.length ? (
        <div className="designer-empty">Start by adding Trigger, Model, Tool and Output nodes.</div>
      ) : (
        <div className="designer-node-list">
          {safeNodes.map((node, index) => (
            <div className="designer-node" key={node.id}>
              <div className="designer-node-head">
                <strong>{index + 1}. {node.type.toUpperCase()}</strong>
                <button type="button" onClick={() => removeNode(node.id)} className="designer-remove-btn">Remove</button>
              </div>

              <input
                value={node.name}
                onChange={(e) => updateNode(node.id, (n) => ({ ...n, name: e.target.value }))}
                className="designer-input"
                placeholder="Node name"
              />

              {node.type === 'model' && (
                <div className="designer-grid-2">
                  <input
                    value={node.config?.provider || ''}
                    onChange={(e) => updateNode(node.id, (n) => ({ ...n, config: { ...n.config, provider: e.target.value } }))}
                    className="designer-input"
                    placeholder="Provider"
                  />
                  <input
                    value={node.config?.model || ''}
                    onChange={(e) => updateNode(node.id, (n) => ({ ...n, config: { ...n.config, model: e.target.value } }))}
                    className="designer-input"
                    placeholder="Model"
                  />
                  <textarea
                    value={node.config?.prompt || ''}
                    onChange={(e) => updateNode(node.id, (n) => ({ ...n, config: { ...n.config, prompt: e.target.value } }))}
                    className="designer-textarea"
                    placeholder="System prompt"
                  />
                </div>
              )}

              {node.type === 'tool' && (
                <div className="designer-grid-2">
                  <input
                    value={node.config?.tool_name || ''}
                    onChange={(e) => updateNode(node.id, (n) => ({ ...n, config: { ...n.config, tool_name: e.target.value } }))}
                    className="designer-input"
                    placeholder="Tool name"
                  />
                  <input
                    value={node.config?.action || ''}
                    onChange={(e) => updateNode(node.id, (n) => ({ ...n, config: { ...n.config, action: e.target.value } }))}
                    className="designer-input"
                    placeholder="Action"
                  />
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default WorkflowDesigner;
