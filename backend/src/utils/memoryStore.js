import { v4 as uuidv4 } from 'uuid';

const nowIso = () => new Date().toISOString();

const store = {
  events: [],
  plans: [],
  logs: [],
  assignments: [],
  staff: [
    { id: uuidv4(), name: 'Agent Alpha', role: 'cook', availability_date: '2026-12-31', is_available: true, hourly_rate: 60 },
    { id: uuidv4(), name: 'Agent Beta', role: 'helper', availability_date: '2026-12-31', is_available: true, hourly_rate: 40 },
    { id: uuidv4(), name: 'Agent Gamma', role: 'server', availability_date: '2026-12-31', is_available: true, hourly_rate: 35 },
    { id: uuidv4(), name: 'Agent Delta', role: 'cook', availability_date: '2026-12-31', is_available: true, hourly_rate: 65 },
    { id: uuidv4(), name: 'Agent Epsilon', role: 'helper', availability_date: '2026-12-31', is_available: true, hourly_rate: 42 },
  ],
  inventory: [
    { id: uuidv4(), name: 'CRM Connector', category: 'tool', quantity_available: 5, unit: 'license', cost_per_unit: 10 },
    { id: uuidv4(), name: 'Email Sender', category: 'tool', quantity_available: 8, unit: 'license', cost_per_unit: 6 },
    { id: uuidv4(), name: 'Billing API', category: 'tool', quantity_available: 3, unit: 'license', cost_per_unit: 15 },
    { id: uuidv4(), name: 'Validation Engine', category: 'tool', quantity_available: 4, unit: 'license', cost_per_unit: 12 },
  ],
};

export const isDbUnavailable = (err) => {
  if (!err) return false;
  if (err.code === 'ECONNREFUSED') return true;
  if (Array.isArray(err.errors) && err.errors.some((e) => e?.code === 'ECONNREFUSED')) return true;
  return false;
};

export const memoryEventModel = {
  createEvent(eventData) {
    const event = {
      id: uuidv4(),
      name: eventData.name,
      guest_count: Number(eventData.guest_count),
      menu_type: eventData.menu_type,
      event_date: eventData.event_date,
      location: eventData.location,
      status: 'pending',
      created_at: nowIso(),
      updated_at: nowIso(),
    };
    store.events.unshift(event);
    return event;
  },
  getEventById(eventId) {
    return store.events.find((e) => e.id === eventId);
  },
  updateEventStatus(eventId, status) {
    const event = store.events.find((e) => e.id === eventId);
    if (!event) return null;
    event.status = status;
    event.updated_at = nowIso();
    return event;
  },
  getAllEvents() {
    return [...store.events];
  },
};

export const memoryPlanModel = {
  createPlan(eventId, planData) {
    const plan = {
      id: uuidv4(),
      event_id: eventId,
      plan_data: planData,
      status: 'draft',
      created_at: nowIso(),
      updated_at: nowIso(),
    };
    store.plans.unshift(plan);
    return plan;
  },
  getPlanByEventId(eventId) {
    return store.plans.find((p) => p.event_id === eventId) || null;
  },
  updatePlanStatus(planId, status) {
    const plan = store.plans.find((p) => p.id === planId);
    if (!plan) return null;
    plan.status = status;
    plan.updated_at = nowIso();
    return plan;
  },
  addExecutionLog(eventId, step, status, message, data = null) {
    const entry = {
      id: uuidv4(),
      event_id: eventId,
      step,
      status,
      message,
      data,
      created_at: nowIso(),
    };
    store.logs.push(entry);
    return entry;
  },
  getExecutionLogs(eventId) {
    return store.logs.filter((l) => l.event_id === eventId);
  },
};

export const memoryResourceModel = {
  getStaffByDate() {
    return store.staff.filter((s) => s.is_available);
  },
  getInventoryStatus() {
    return [...store.inventory];
  },
  reserveInventory(inventoryId, quantity) {
    const item = store.inventory.find((i) => i.id === inventoryId);
    if (!item) return null;
    item.quantity_available = Math.max(0, item.quantity_available - Number(quantity));
    return item;
  },
  createStaffAssignment(eventId, staffId, role, startTime, endTime, cost) {
    const assignment = {
      id: uuidv4(),
      event_id: eventId,
      staff_id: staffId,
      role,
      start_time: startTime,
      end_time: endTime,
      cost,
      created_at: nowIso(),
    };
    store.assignments.push(assignment);
    return assignment;
  },
  getAssignmentsByEventId(eventId) {
    return store.assignments.filter((a) => a.event_id === eventId);
  },
};
