import { OpenAI } from 'openai';

// OpenAI client is optional in MVP mode.
const openai = process.env.OPENAI_API_KEY
  ? new OpenAI({ apiKey: process.env.OPENAI_API_KEY })
  : null;

export const calculateIngredientsWithAI = async (eventData) => {
  const { guest_count, menu_type, location, workflow_blueprint = [] } = eventData;

  const workloadUnits = Number(guest_count);
  const executionMode = menu_type === 'non-veg' ? 'parallel' : 'sequential';
  const normalizedBlueprint = Array.isArray(workflow_blueprint) ? workflow_blueprint : [];

  const baseTasks = normalizedBlueprint.length
    ? normalizedBlueprint.map((node) => ({
        name: node?.name || `${node?.type || 'node'} task`,
        owner: node?.owner || 'coordinator',
        complexity: node?.type === 'model' ? 3 : node?.type === 'tool' ? 2 : 1,
      }))
    : [
        { name: 'Intake & Context Parse', owner: 'coordinator', complexity: 1 },
        { name: 'Plan Task Graph', owner: 'planner', complexity: 2 },
        { name: 'Route To Specialist Agents', owner: 'router', complexity: 2 },
        { name: 'Execute Tool Actions', owner: 'executor', complexity: 3 },
        { name: 'Validate Outputs', owner: 'validator', complexity: 2 },
        { name: 'Generate Final Report', owner: 'reporter', complexity: 1 },
      ];

  const scaledTasks = baseTasks.map((task, index) => ({
    id: `task_${index + 1}`,
    name: task.name,
    owner: task.owner,
    status: 'planned',
    workload: Math.max(1, Math.ceil((workloadUnits * task.complexity) / 100)),
    depends_on: index === 0 ? [] : [`task_${index}`],
  }));

  return {
    tasks: scaledTasks,
    execution_mode: executionMode,
    target_system: location,
    estimated_run_cost: Number((workloadUnits * (executionMode === 'parallel' ? 1.35 : 1.1)).toFixed(2)),
  };
};

export const determineStaffRequirementsWithAI = async (eventData) => {
  const { guest_count, menu_type } = eventData;
  const workloadUnits = Number(guest_count);
  const isParallel = menu_type === 'non-veg';

  const coordinator = 1;
  const planners = Math.max(1, Math.ceil(workloadUnits / 120));
  const executors = Math.max(1, Math.ceil(workloadUnits / (isParallel ? 60 : 90)));
  const validators = Math.max(1, Math.ceil(workloadUnits / 150));

  return {
    agents_required: [
      { role: 'coordinator', count: coordinator, capability: 'workflow-control' },
      { role: 'planner', count: planners, capability: 'task-planning' },
      { role: 'executor', count: executors, capability: 'tool-execution' },
      { role: 'validator', count: validators, capability: 'quality-guardrails' },
    ],
    estimated_duration_hours: Math.max(1, Math.ceil(workloadUnits / (isParallel ? 55 : 35))),
  };
};

export const optimizePlanWithAI = async (ingredients, staffRequirements, inventory) => {
  const availableTools = inventory.length;
  const requiredAgents = staffRequirements.agents_required.reduce((acc, item) => acc + item.count, 0);
  const taskCount = ingredients.tasks.length;
  const efficiencyBase = 100 - Math.max(0, requiredAgents - availableTools) * 3;

  return {
    efficiency_score: Math.max(65, efficiencyBase),
    queue_strategy: ingredients.execution_mode === 'parallel' ? 'fan-out/fan-in' : 'serial-with-checkpoints',
    expected_bottleneck: availableTools < 4 ? 'tool-capacity' : 'agent-validation',
    recommendations: [
      'Batch independent tasks into one execution wave.',
      'Reserve one validator agent for final consistency checks.',
      taskCount > 5 ? 'Split reporting from execution for lower latency.' : 'Keep reporting inline for simplicity.',
    ],
  };
};

export const parseEventWithAI = async (eventData) => {
  // Keep underlying field names for DB compatibility, map semantics to workflow domain.
  const executionMode = eventData.menu_type === 'non-veg' ? 'parallel' : 'sequential';
  const safeBlueprint = Array.isArray(eventData.workflow_blueprint)
    ? eventData.workflow_blueprint.map((node, index) => ({
        id: node?.id || `node_${index + 1}`,
        type: node?.type || 'task',
        name: node?.name || `Node ${index + 1}`,
        owner: node?.owner || 'coordinator',
        config: node?.config || {},
      }))
    : [];

  const parsed = {
    name: eventData.name || 'Unnamed Workflow',
    guest_count: parseInt(eventData.guest_count) || 0,
    menu_type: (eventData.menu_type || 'veg').toLowerCase(),
    execution_mode: executionMode,
    event_date: new Date(eventData.event_date),
    location: eventData.location || 'Unspecified target system',
    workflow_blueprint: safeBlueprint,
    parsed_at: new Date(),
  };

  if (parsed.guest_count <= 0) {
    throw new Error('Workload units must be greater than 0');
  }

  if (!['veg', 'non-veg'].includes(parsed.menu_type)) {
    throw new Error('Execution mode is invalid');
  }

  return parsed;
};

export const generateExecutionPlan = async (eventData, ingredients, staffRequirements) => {
  const modelStack = (eventData.workflow_blueprint || [])
    .filter((node) => node.type === 'model')
    .map((node) => ({
      node_name: node.name,
      provider: node.config?.provider || 'OpenAI',
      model: node.config?.model || 'gpt-4o-mini',
    }));

  const workflow = {
    workflow_name: eventData.name,
    workload_units: eventData.guest_count,
    execution_mode: eventData.execution_mode,
    deadline: eventData.event_date,
    target_system: eventData.location,
  };

  const plan = {
    workflow,
    task_graph: ingredients,
    model_stack: modelStack,
    agent_requirements: staffRequirements,
    timeline: {
      intake: 'T+0m',
      planning: 'T+2m',
      assignment: 'T+4m',
      execution: 'T+6m',
      validation: 'T+10m',
      finalization: 'T+12m',
    },
    alerts: [],
    actions: [],
  };

  if (eventData.guest_count > 350) {
    plan.alerts.push('High workload detected; auto-scaling executor agents.');
    plan.actions.push('Spawn backup executor pool and increase validation sampling.');
  }

  if (staffRequirements.estimated_duration_hours > 8) {
    plan.alerts.push('Execution window exceeds standard SLA.');
    plan.actions.push('Switch to parallel task queue for throughput optimization.');
  }

  return plan;
};
