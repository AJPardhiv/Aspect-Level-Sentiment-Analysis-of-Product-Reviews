import * as eventModel from '../models/eventModel.js';
import * as workflowService from '../services/workflowService.js';

export const submitEvent = async (req, res) => {
  try {
    const eventData = req.body;

    if (!eventData.name || !eventData.guest_count || !eventData.event_date || !eventData.location) {
      return res.status(400).json({
        error: 'Missing required fields',
        required: ['name', 'guest_count', 'event_date', 'location', 'menu_type'],
      });
    }

    const event = await eventModel.createEvent(eventData);
    res.status(201).json({
      success: true,
      event,
    });
  } catch (error) {
    console.error('submitEvent error:', error);
    res.status(500).json({ error: error?.message || 'Failed to create workflow request' });
  }
};

export const getEvent = async (req, res) => {
  try {
    const { eventId } = req.params;
    const event = await eventModel.getEventById(eventId);

    if (!event) {
      return res.status(404).json({ error: 'Event not found' });
    }

    res.status(200).json(event);
  } catch (error) {
    console.error('getEvent error:', error);
    res.status(500).json({ error: error?.message || 'Failed to fetch workflow request' });
  }
};

export const listEvents = async (req, res) => {
  try {
    const events = await eventModel.getAllEvents();
    res.status(200).json(events);
  } catch (error) {
    console.error('listEvents error:', error);
    res.status(500).json({ error: error?.message || 'Failed to list workflow requests' });
  }
};
