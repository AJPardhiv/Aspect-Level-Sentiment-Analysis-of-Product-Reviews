import { query } from '../db.js';
import { v4 as uuidv4 } from 'uuid';
import { isDbUnavailable, memoryPlanModel } from '../utils/memoryStore.js';

export const createPlan = async (eventId, planData) => {
  const id = uuidv4();
  try {
    const result = await query(
      `INSERT INTO plans (id, event_id, plan_data, status)
       VALUES ($1, $2, $3, $4)
       RETURNING *`,
      [id, eventId, JSON.stringify(planData), 'draft']
    );
    return result.rows[0];
  } catch (err) {
    if (isDbUnavailable(err)) {
      return memoryPlanModel.createPlan(eventId, planData);
    }
    throw err;
  }
};

export const getPlanByEventId = async (eventId) => {
  try {
    const result = await query(
      'SELECT * FROM plans WHERE event_id = $1 ORDER BY created_at DESC LIMIT 1',
      [eventId]
    );
    return result.rows[0];
  } catch (err) {
    if (isDbUnavailable(err)) {
      return memoryPlanModel.getPlanByEventId(eventId);
    }
    throw err;
  }
};

export const updatePlanStatus = async (planId, status) => {
  try {
    const result = await query(
      'UPDATE plans SET status = $1, updated_at = CURRENT_TIMESTAMP WHERE id = $2 RETURNING *',
      [status, planId]
    );
    return result.rows[0];
  } catch (err) {
    if (isDbUnavailable(err)) {
      return memoryPlanModel.updatePlanStatus(planId, status);
    }
    throw err;
  }
};

export const addExecutionLog = async (eventId, step, status, message, data = null) => {
  const id = uuidv4();
  try {
    const result = await query(
      `INSERT INTO execution_logs (id, event_id, step, status, message, data)
       VALUES ($1, $2, $3, $4, $5, $6)
       RETURNING *`,
      [id, eventId, step, status, message, data ? JSON.stringify(data) : null]
    );
    return result.rows[0];
  } catch (err) {
    if (isDbUnavailable(err)) {
      return memoryPlanModel.addExecutionLog(eventId, step, status, message, data);
    }
    throw err;
  }
};

export const getExecutionLogs = async (eventId) => {
  try {
    const result = await query(
      'SELECT * FROM execution_logs WHERE event_id = $1 ORDER BY created_at ASC',
      [eventId]
    );
    return result.rows;
  } catch (err) {
    if (isDbUnavailable(err)) {
      return memoryPlanModel.getExecutionLogs(eventId);
    }
    throw err;
  }
};
