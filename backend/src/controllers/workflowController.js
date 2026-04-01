import * as workflowService from '../services/workflowService.js';
import * as eventModel from '../models/eventModel.js';

export const runWorkflow = async (req, res) => {
  try {
    const { eventId } = req.params;
    const requestData = req.body || {};

    // Check if event exists
    const event = await eventModel.getEventById(eventId);
    if (!event) {
      return res.status(404).json({ error: 'Event not found' });
    }

    // Execute the workflow
    const result = await workflowService.executeWorkflow(
      {
        name: event.name,
        guest_count: event.guest_count,
        menu_type: event.menu_type,
        event_date: event.event_date,
        location: event.location,
        workflow_blueprint: Array.isArray(requestData.workflow_blueprint) ? requestData.workflow_blueprint : [],
      },
      eventId
    );

    res.status(200).json(result);
  } catch (error) {
    console.error('Workflow error:', error);
    res.status(500).json({
      error: 'Workflow execution failed',
      message: error?.message || 'Unknown workflow error',
    });
  }
};

export const getWorkflowStatus = async (req, res) => {
  try {
    const { eventId } = req.params;
    const status = await workflowService.getWorkflowStatus(eventId);
    res.status(200).json(status);
  } catch (error) {
    console.error('getWorkflowStatus error:', error);
    res.status(500).json({ error: error?.message || 'Failed to fetch workflow status' });
  }
};
