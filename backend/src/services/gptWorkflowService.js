import { OpenAI } from 'openai';

const openai = process.env.OPENAI_API_KEY
  ? new OpenAI({ apiKey: process.env.OPENAI_API_KEY })
  : null;

/**
 * Convert natural language request to structured workflow JSON
 * Example: "Update Google Sheet, send Slack message, post to API"
 * Output: { workflow_name, steps: [{ id, action, params, depends_on }] }
 */
export const convertChatToWorkflow = async (userRequest) => {
  if (!openai) {
    // Fallback: basic parsing for demo
    return generateFallbackWorkflow(userRequest);
  }

  try {
    const systemPrompt = `You are a workflow automation expert. Convert user requests into structured JSON workflows.

RULES:
1. Each step must have: id (number), action (string), params (object), depends_on (array of step ids)
2. Support common actions: http_request, update_spreadsheet, send_message, execute_code, api_call, database_query, conditional, loop
3. Extract parameters from the request (API endpoints, URLs, credentials references, etc.)
4. Create logical step dependencies
5. Always return valid JSON

Example workflow structure:
{
  "workflow_name": "Human readable name",
  "steps": [
    {
      "id": 1,
      "action": "http_request",
      "params": {
        "method": "GET",
        "url": "https://api.example.com/data",
        "headers": { "Authorization": "Bearer token" }
      },
      "depends_on": []
    },
    {
      "id": 2,
      "action": "update_spreadsheet",
      "params": {
        "sheet_id": "google_sheet_id",
        "range": "A1:B10",
        "data": "{{ step_1_response }}"
      },
      "depends_on": [1]
    }
  ]
}

CRITICAL: Return ONLY valid JSON, no explanations.`;

    const response = await openai.chat.completions.create({
      model: 'gpt-4-turbo-preview',
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userRequest },
      ],
      temperature: 0.7,
      max_tokens: 2000,
    });

    const content = response.choices[0]?.message?.content || '{}';
    const workflow = JSON.parse(content);

    return {
      success: true,
      workflow,
      raw_request: userRequest,
      model: 'gpt-4-turbo-preview',
    };
  } catch (error) {
    console.error('GPT error:', error.message);
    // Fallback to heuristic parsing
    return generateFallbackWorkflow(userRequest);
  }
};

/**
 * Fallback workflow generator for demo/testing
 */
export const generateFallbackWorkflow = (userRequest) => {
  const actions = parseActionsFromText(userRequest);
  
  const steps = actions.map((action, index) => ({
    id: index + 1,
    action: action.type,
    params: action.params,
    depends_on: index === 0 ? [] : [index],
  }));

  return {
    success: true,
    workflow: {
      workflow_name: userRequest.split('.')[0].substring(0, 50) || 'Auto Workflow',
      steps,
    },
    raw_request: userRequest,
    model: 'fallback',
  };
};

/**
 * Parse common action patterns from text
 */
const parseActionsFromText = (text) => {
  const actions = [];
  const lowerText = text.toLowerCase();

  // Extract common actions
  const patterns = [
    { regex: /google\s*sheet|update\s*spreadsheet|excel/i, type: 'update_spreadsheet', name: 'Google Sheets' },
    { regex: /slack|send\s*message|notify/i, type: 'send_message', name: 'Slack Message' },
    { regex: /api|http|post|get|fetch|request/i, type: 'http_request', name: 'API Call' },
    { regex: /database|query|sql|store/i, type: 'database_query', name: 'Database Query' },
    { regex: /email|send|mail/i, type: 'send_email', name: 'Email' },
    { regex: /webhook|trigger/i, type: 'webhook_trigger', name: 'Webhook' },
    { regex: /transform|process|convert|parse/i, type: 'execute_code', name: 'Data Transform' },
    { regex: /filter|map|loop/i, type: 'loop', name: 'Loop Action' },
  ];

  patterns.forEach((pattern) => {
    if (pattern.regex.test(lowerText)) {
      actions.push({
        type: pattern.type,
        params: inferParams(text, pattern.type),
      });
    }
  });

  // If no actions found, default to HTTP
  if (actions.length === 0) {
    actions.push({
      type: 'http_request',
      params: {
        method: 'POST',
        url: 'https://api.example.com/execute',
        body: { request: text },
      },
    });
  }

  return actions;
};

/**
 * Infer parameters from request text
 */
const inferParams = (text, actionType) => {
  const baseParams = {
    description: text,
    retry_on_failure: true,
    timeout_seconds: 30,
  };

  switch (actionType) {
    case 'update_spreadsheet':
      return {
        ...baseParams,
        sheet_id: 'YOUR_GOOGLE_SHEET_ID',
        sheet_name: 'Sheet1',
        range: 'A1',
      };
    case 'send_message':
      return {
        ...baseParams,
        channel: '#automation',
        text: text,
      };
    case 'http_request':
      return {
        ...baseParams,
        method: 'POST',
        url: 'https://api.example.com/action',
        headers: { 'Content-Type': 'application/json' },
      };
    case 'database_query':
      return {
        ...baseParams,
        query: 'SELECT * FROM table WHERE condition',
        database: 'default',
      };
    case 'send_email':
      return {
        ...baseParams,
        to: 'recipient@example.com',
        subject: 'Workflow Notification',
      };
    case 'execute_code':
      return {
        ...baseParams,
        language: 'javascript',
        code: `// Implement your logic here\nconsole.log('${text}');`,
      };
    default:
      return baseParams;
  }
};

/**
 * Validate workflow structure
 */
export const validateWorkflow = (workflow) => {
  const errors = [];

  if (!workflow.workflow_name || typeof workflow.workflow_name !== 'string') {
    errors.push('Missing or invalid workflow_name');
  }

  if (!Array.isArray(workflow.steps) || workflow.steps.length === 0) {
    errors.push('Steps must be a non-empty array');
  }

  workflow.steps?.forEach((step, index) => {
    if (!step.id) errors.push(`Step ${index}: missing id`);
    if (!step.action) errors.push(`Step ${index}: missing action`);
    if (typeof step.params !== 'object') errors.push(`Step ${index}: params must be an object`);
    if (!Array.isArray(step.depends_on)) errors.push(`Step ${index}: depends_on must be an array`);

    // Check dependencies reference valid steps
    const validIds = workflow.steps.map((s) => s.id);
    step.depends_on?.forEach((dep) => {
      if (!validIds.includes(dep)) {
        errors.push(`Step ${step.id}: depends_on references invalid step ${dep}`);
      }
    });
  });

  return {
    valid: errors.length === 0,
    errors,
  };
};
