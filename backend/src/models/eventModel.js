import { query } from '../db.js';
import { v4 as uuidv4 } from 'uuid';
import { isDbUnavailable, memoryEventModel } from '../utils/memoryStore.js';

export const createEvent = async (eventData) => {
  const { name, guest_count, menu_type, event_date, location } = eventData;
  const id = uuidv4();
  try {
    const result = await query(
      `INSERT INTO events (id, name, guest_count, menu_type, event_date, location, status)
       VALUES ($1, $2, $3, $4, $5, $6, $7)
       RETURNING *`,
      [id, name, guest_count, menu_type, event_date, location, 'pending']
    );
    return result.rows[0];
  } catch (err) {
    if (isDbUnavailable(err)) {
      return memoryEventModel.createEvent(eventData);
    }
    throw err;
  }
};

export const getEventById = async (eventId) => {
  try {
    const result = await query(
      'SELECT * FROM events WHERE id = $1',
      [eventId]
    );
    return result.rows[0];
  } catch (err) {
    if (isDbUnavailable(err)) {
      return memoryEventModel.getEventById(eventId);
    }
    throw err;
  }
};

export const updateEventStatus = async (eventId, status) => {
  try {
    const result = await query(
      'UPDATE events SET status = $1, updated_at = CURRENT_TIMESTAMP WHERE id = $2 RETURNING *',
      [status, eventId]
    );
    return result.rows[0];
  } catch (err) {
    if (isDbUnavailable(err)) {
      return memoryEventModel.updateEventStatus(eventId, status);
    }
    throw err;
  }
};

export const getAllEvents = async () => {
  try {
    const result = await query('SELECT * FROM events ORDER BY created_at DESC');
    return result.rows;
  } catch (err) {
    if (isDbUnavailable(err)) {
      return memoryEventModel.getAllEvents();
    }
    throw err;
  }
};
