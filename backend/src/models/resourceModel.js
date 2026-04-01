import { query } from '../db.js';
import { isDbUnavailable, memoryResourceModel } from '../utils/memoryStore.js';

export const getStaffByDate = async (eventDate) => {
  try {
    const result = await query(
      `SELECT * FROM staff 
       WHERE availability_date <= $1 AND is_available = TRUE
       ORDER BY role, hourly_rate`,
      [eventDate]
    );
    return result.rows;
  } catch (err) {
    if (isDbUnavailable(err)) {
      return memoryResourceModel.getStaffByDate(eventDate);
    }
    throw err;
  }
};

export const getInventoryStatus = async () => {
  try {
    const result = await query(
      'SELECT * FROM inventory ORDER BY category'
    );
    return result.rows;
  } catch (err) {
    if (isDbUnavailable(err)) {
      return memoryResourceModel.getInventoryStatus();
    }
    throw err;
  }
};

export const reserveInventory = async (inventoryId, quantity) => {
  try {
    const result = await query(
      'UPDATE inventory SET quantity_available = quantity_available - $1 WHERE id = $2 RETURNING *',
      [quantity, inventoryId]
    );
    return result.rows[0];
  } catch (err) {
    if (isDbUnavailable(err)) {
      return memoryResourceModel.reserveInventory(inventoryId, quantity);
    }
    throw err;
  }
};

export const createStaffAssignment = async (eventId, staffId, role, startTime, endTime, cost) => {
  try {
    const result = await query(
      `INSERT INTO event_staff_assignments (event_id, staff_id, role, start_time, end_time, cost)
       VALUES ($1, $2, $3, $4, $5, $6)
       RETURNING *`,
      [eventId, staffId, role, startTime, endTime, cost]
    );
    return result.rows[0];
  } catch (err) {
    if (isDbUnavailable(err)) {
      return memoryResourceModel.createStaffAssignment(eventId, staffId, role, startTime, endTime, cost);
    }
    throw err;
  }
};

export const getAssignmentsByEventId = async (eventId) => {
  try {
    const result = await query(
      `SELECT esa.*, s.name, s.role as staff_role 
       FROM event_staff_assignments esa
       JOIN staff s ON esa.staff_id = s.id
       WHERE esa.event_id = $1`,
      [eventId]
    );
    return result.rows;
  } catch (err) {
    if (isDbUnavailable(err)) {
      return memoryResourceModel.getAssignmentsByEventId(eventId);
    }
    throw err;
  }
};
