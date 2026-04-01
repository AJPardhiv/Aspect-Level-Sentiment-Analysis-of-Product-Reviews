import express from 'express';
import * as workflowController from '../controllers/workflowController.js';

const router = express.Router();

router.post('/run/:eventId', workflowController.runWorkflow);
router.get('/status/:eventId', workflowController.getWorkflowStatus);

export default router;
