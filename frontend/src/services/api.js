import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const createEvent = async (eventData) => {
  const response = await api.post('/events', eventData);
  return response.data;
};

export const submitEventAndRun = async (eventData) => {
  // Create event
  const eventResponse = await api.post('/events', eventData);
  const eventId = eventResponse.data.event.id;

  // Wait a moment for event to be saved
  await new Promise(resolve => setTimeout(resolve, 500));

  // Run workflow
  const workflowResponse = await api.post(`/workflow/run/${eventId}`, eventData);
  return { eventId, ...workflowResponse.data };
};

export const getWorkflowStatus = async (eventId) => {
  const response = await api.get(`/workflow/status/${eventId}`);
  return response.data;
};

export const getEvent = async (eventId) => {
  const response = await api.get(`/events/${eventId}`);
  return response.data;
};

export default api;
