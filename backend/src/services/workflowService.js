import * as eventModel from '../models/eventModel.js';
import * as resourceModel from '../models/resourceModel.js';
import * as planModel from '../models/planModel.js';
import * as aiEngine from './aiEngine.js';

export const executeWorkflow = async (eventData, eventId) => {
  const logs = [];

  try {
    // Step 1: Parse Workflow Input
    console.log('Step 1: Parsing workflow input...');
    await planModel.addExecutionLog(eventId, 'Parsing input', 'running', 'Parsing workflow payload');
    
    const parsed = await aiEngine.parseEventWithAI(eventData);
    logs.push({
      step: 'Parsing input',
      status: 'completed',
      data: parsed,
    });
    await planModel.addExecutionLog(eventId, 'Parsing input', 'completed', 'Workflow payload parsed successfully', parsed);

    // Step 2: Build Task Graph
    console.log('Step 2: Building task graph...');
    await planModel.addExecutionLog(eventId, 'Building task graph', 'running', 'Computing autonomous task graph');
    
    const taskGraph = await aiEngine.calculateIngredientsWithAI(parsed);
    logs.push({
      step: 'Building task graph',
      status: 'completed',
      data: taskGraph,
    });
    await planModel.addExecutionLog(eventId, 'Building task graph', 'completed', 'Task graph generated', taskGraph);

    // Step 3: Determine Agent Requirements
    console.log('Step 3: Determining agent requirements...');
    await planModel.addExecutionLog(eventId, 'Determining agents', 'running', 'Computing agent allocation');
    
    const agentRequirements = await aiEngine.determineStaffRequirementsWithAI(parsed);
    logs.push({
      step: 'Determining agent requirements',
      status: 'completed',
      data: agentRequirements,
    });
    await planModel.addExecutionLog(eventId, 'Determining agents', 'completed', 'Agent requirements determined', agentRequirements);

    // Step 4: Check Tool Capacity
    console.log('Step 4: Checking tool capacity...');
    await planModel.addExecutionLog(eventId, 'Checking tools', 'running', 'Verifying tool registry capacity');
    
    const inventory = await resourceModel.getInventoryStatus();
    const toolCheck = {
      available_tools: inventory.length,
      summary: inventory.length > 0 ? 'Tool capacity available' : 'No tool capacity',
      tools: inventory.slice(0, 5),
    };
    logs.push({
      step: 'Checking tools',
      status: 'completed',
      data: toolCheck,
    });
    await planModel.addExecutionLog(eventId, 'Checking tools', 'completed', 'Tool capacity check completed', toolCheck);

    // Step 5: Allocate Agents
    console.log('Step 5: Allocating agents...');
    await planModel.addExecutionLog(eventId, 'Allocating agents', 'running', 'Assigning available agents to workflow');
    
    const availableStaff = await resourceModel.getStaffByDate(parsed.event_date);
    const agentAllocation = {
      requested: agentRequirements.agents_required,
      available_agent_count: availableStaff.length,
      allocated: availableStaff.slice(0, 5),
    };
    logs.push({
      step: 'Allocating agents',
      status: 'completed',
      data: agentAllocation,
    });
    await planModel.addExecutionLog(eventId, 'Allocating agents', 'completed', 'Agents allocated', agentAllocation);

    // Step 6: Optimize Execution Plan
    console.log('Step 6: Optimizing execution plan...');
    await planModel.addExecutionLog(eventId, 'Optimizing plan', 'running', 'Applying optimizations');
    
    const optimization = await aiEngine.optimizePlanWithAI(taskGraph, agentRequirements, inventory);
    logs.push({
      step: 'Optimizing plan',
      status: 'completed',
      data: optimization,
    });
    await planModel.addExecutionLog(eventId, 'Optimizing plan', 'completed', 'Plan optimized', optimization);

    // Step 7: Finalize Autonomous Plan
    console.log('Step 7: Finalizing autonomous plan...');
    const executionPlan = await aiEngine.generateExecutionPlan(parsed, taskGraph, agentRequirements);
    executionPlan.optimization = optimization;
    executionPlan.agent_allocation = agentAllocation;
    executionPlan.tool_check = toolCheck;

    // Save the plan
    const plan = await planModel.createPlan(eventId, executionPlan);
    await eventModel.updateEventStatus(eventId, 'planning');

    logs.push({
      step: 'Finalizing plan',
      status: 'completed',
      data: { plan_id: plan.id },
    });

    return {
      success: true,
      event_id: eventId,
      plan_id: plan.id,
      logs,
      final_plan: executionPlan,
    };
  } catch (error) {
    console.error('Workflow execution error:', error);
    await planModel.addExecutionLog(eventId, 'Workflow', 'failed', error.message);
    throw error;
  }
};

export const getWorkflowStatus = async (eventId) => {
  const logs = await planModel.getExecutionLogs(eventId);
  const plan = await planModel.getPlanByEventId(eventId);
  const event = await eventModel.getEventById(eventId);

  return {
    event_id: eventId,
    event_status: event?.status,
    plan_status: plan?.status,
    execution_logs: logs,
    plan_data: plan?.plan_data,
  };
};
