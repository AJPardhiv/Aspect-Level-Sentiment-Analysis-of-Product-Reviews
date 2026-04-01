import express from 'express';
import * as chatController from '../controllers/chatController.js';

const router = express.Router();

/**
 * Natural language to workflow conversion and execution
 * POST /api/chat/workflow
 * { user_request: "Update Google Sheet, send Slack message" }
 */
router.post('/workflow', chatController.chatToWorkflow);

/**
 * Execute pre-defined workflow JSON
 * POST /api/chat/execute
 * { workflow: {...}, secrets: {...} }
 */
router.post('/execute', chatController.executeWorkflow);

/**
 * Get workflow execution status and logs
 * GET /api/chat/status/:event_id
 */
router.get('/status/:event_id', chatController.getWorkflowStatus);

/**
 * List all chat-based workflows
 * GET /api/chat/workflows
 */
router.get('/workflows', chatController.listWorkflows);

/**
 * Validate workflow request without execution
 * POST /api/chat/validate
 * { user_request: "..." }
 */
router.post('/validate', chatController.validateWorkflowRequest);

export default router;
