import * as gptWorkflowService from '../services/gptWorkflowService.js';
import * as workflowExecutor from '../services/workflowExecutor.js';
import * as eventModel from '../models/eventModel.js';
import * as planModel from '../models/planModel.js';
import { v4 as uuidv4 } from 'uuid';

/**
 * Convert natural language request to workflow and execute
 * POST /api/chat/workflow
 * Body: { user_request: "Update Google Sheet, send Slack message, post to API" }
 */
export const chatToWorkflow = async (req, res) => {
  try {
    const { user_request, auto_execute = true, secrets = {} } = req.body;

    if (!user_request || typeof user_request !== 'string') {
      return res.status(400).json({
        success: false,
        error: 'user_request is required and must be a string',
      });
    }

    console.log('Chat request:', user_request);

    // Step 1: Convert chat to workflow JSON
    const conversionResult = await gptWorkflowService.convertChatToWorkflow(user_request);

    if (!conversionResult.success) {
      return res.status(500).json({
        success: false,
        error: 'Failed to convert request to workflow',
        details: conversionResult,
      });
    }

    const workflow = conversionResult.workflow;

    // Step 2: Validate workflow structure
    const validation = gptWorkflowService.validateWorkflow(workflow);

    if (!validation.valid) {
      return res.status(400).json({
        success: false,
        error: 'Generated workflow validation failed',
        validation_errors: validation.errors,
        workflow,
      });
    }

    // Step 3: Store workflow in database
    const eventId = uuidv4();
    const event = await eventModel.createEvent({
      name: workflow.workflow_name,
      guest_count: workflow.steps.length,
      menu_type: 'gpt-workflow',
      event_date: new Date(),
      location: 'chat-interface',
      workflow_blueprint: workflow.steps.map((step) => ({
        id: `step_${step.id}`,
        type: step.action,
        name: `${step.action} #${step.id}`,
        owner: 'ai-agent',
        config: step.params,
      })),
    });

    // Step 4: Execute workflow if auto_execute is true
    let executionResult = null;
    if (auto_execute) {
      const executor = new workflowExecutor.WorkflowExecutor(workflow);
      executionResult = await executor.execute(secrets);

      // Store execution status
      await eventModel.updateEventStatus(event.id, 'completed');
      await planModel.createPlan(event.id, {
        workflow_name: workflow.workflow_name,
        status: executionResult.success ? 'completed' : 'failed',
        steps_completed: executionResult.steps_completed,
        total_steps: executionResult.total_steps,
        results: executionResult.results,
        duration_ms: executionResult.duration_ms,
      });

      // Log each step
      executionResult.logs?.forEach(async (log) => {
        await planModel.addExecutionLog(event.id, log.step, log.status, log.message, log);
      });
    }

    res.status(200).json({
      success: true,
      event_id: event.id,
      workflow_name: workflow.workflow_name,
      workflow,
      execution: executionResult,
      conversion_model: conversionResult.model,
    });
  } catch (error) {
    console.error('chatToWorkflow error:', error);
    res.status(500).json({
      success: false,
      error: error.message,
      stack: process.env.NODE_ENV === 'development' ? error.stack : undefined,
    });
  }
};

/**
 * Execute pre-defined workflow
 * POST /api/chat/execute
 * Body: { workflow: {...}, secrets: {...} }
 */
export const executeWorkflow = async (req, res) => {
  try {
    const { workflow, secrets = {} } = req.body;

    if (!workflow) {
      return res.status(400).json({
        success: false,
        error: 'workflow is required',
      });
    }

    // Validate workflow
    const validation = gptWorkflowService.validateWorkflow(workflow);
    if (!validation.valid) {
      return res.status(400).json({
        success: false,
        error: 'Workflow validation failed',
        errors: validation.errors,
      });
    }

    // Execute
    const executor = new workflowExecutor.WorkflowExecutor(workflow);
    const result = await executor.execute(secrets);

    res.status(200).json({
      success: true,
      execution: result,
    });
  } catch (error) {
    console.error('executeWorkflow error:', error);
    res.status(500).json({
      success: false,
      error: error.message,
    });
  }
};

/**
 * Get workflow execution status
 * GET /api/chat/status/:event_id
 */
export const getWorkflowStatus = async (req, res) => {
  try {
    const { event_id } = req.params;

    const event = await eventModel.getEventById(event_id);
    if (!event) {
      return res.status(404).json({
        success: false,
        error: 'Workflow not found',
      });
    }

    const plan = await planModel.getPlanByEventId(event_id);
    const logs = await planModel.getExecutionLogs(event_id);

    res.status(200).json({
      success: true,
      event,
      plan,
      logs,
    });
  } catch (error) {
    console.error('getWorkflowStatus error:', error);
    res.status(500).json({
      success: false,
      error: error.message,
    });
  }
};

/**
 * List all chat-based workflows
 * GET /api/chat/workflows
 */
export const listWorkflows = async (req, res) => {
  try {
    const events = await eventModel.getAllEvents();
    const chatWorkflows = events.filter((e) => e.menu_type === 'gpt-workflow');

    res.status(200).json({
      success: true,
      count: chatWorkflows.length,
      workflows: chatWorkflows,
    });
  } catch (error) {
    console.error('listWorkflows error:', error);
    res.status(500).json({
      success: false,
      error: error.message,
    });
  }
};

/**
 * Test workflow without execution
 * POST /api/chat/validate
 * Body: { user_request: "..." }
 */
export const validateWorkflowRequest = async (req, res) => {
  try {
    const { user_request } = req.body;

    if (!user_request) {
      return res.status(400).json({
        success: false,
        error: 'user_request is required',
      });
    }

    const conversionResult = await gptWorkflowService.convertChatToWorkflow(user_request);
    const validation = gptWorkflowService.validateWorkflow(conversionResult.workflow);

    res.status(200).json({
      success: validation.valid,
      workflow: conversionResult.workflow,
      validation,
      model: conversionResult.model,
    });
  } catch (error) {
    console.error('validateWorkflowRequest error:', error);
    res.status(500).json({
      success: false,
      error: error.message,
    });
  }
};
