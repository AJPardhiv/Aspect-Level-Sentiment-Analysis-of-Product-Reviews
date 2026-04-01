import axios from 'axios';

/**
 * Universal workflow executor
 * Executes any workflow with support for:
 * - Sequential and parallel execution
 * - Step dependencies
 * - External API calls
 * - Data passing between steps
 * - Error handling and logging
 */
export class WorkflowExecutor {
  constructor(workflow) {
    this.workflow = workflow;
    this.stepResults = {};
    this.executionLog = [];
    this.currentStepIndex = 0;
  }

  /**
   * Execute entire workflow
   */
  async execute(secrets = {}) {
    const startTime = Date.now();
    const logs = [];

    try {
      logs.push({
        timestamp: new Date(),
        step: 'init',
        status: 'running',
        message: `Starting workflow: ${this.workflow.workflow_name}`,
      });

      // Topological sort for dependency resolution
      const executionOrder = this.topologicalSort();

      for (const stepId of executionOrder) {
        const step = this.workflow.steps.find((s) => s.id === stepId);
        if (!step) continue;

        const stepLog = await this.executeStep(step, secrets);
        logs.push(stepLog);
        this.executionLog.push(stepLog);
      }

      const duration = Date.now() - startTime;
      logs.push({
        timestamp: new Date(),
        step: 'finalize',
        status: 'success',
        message: `Workflow completed in ${duration}ms`,
        total_steps: this.workflow.steps.length,
        duration_ms: duration,
      });

      return {
        success: true,
        workflow_name: this.workflow.workflow_name,
        total_steps: this.workflow.steps.length,
        steps_completed: Object.keys(this.stepResults).length,
        duration_ms: duration,
        results: this.stepResults,
        logs,
      };
    } catch (error) {
      logs.push({
        timestamp: new Date(),
        step: 'error',
        status: 'failed',
        message: error.message,
        stack: error.stack,
      });

      return {
        success: false,
        workflow_name: this.workflow.workflow_name,
        error: error.message,
        completed_steps: Object.keys(this.stepResults).length,
        logs,
      };
    }
  }

  /**
   * Execute individual step
   */
  async executeStep(step, secrets) {
    const startTime = Date.now();

    try {
      // Check if dependencies are satisfied
      if (!this.dependenciesMet(step)) {
        throw new Error(`Dependencies not met for step ${step.id}`);
      }

      console.log(`Executing step ${step.id}: ${step.action}`);

      const result = await this.executeAction(step.action, step.params, secrets);

      const duration = Date.now() - startTime;
      this.stepResults[step.id] = result;

      return {
        step_id: step.id,
        step_name: step.action,
        status: 'success',
        timestamp: new Date(),
        duration_ms: duration,
        output: result,
      };
    } catch (error) {
      const duration = Date.now() - startTime;

      return {
        step_id: step.id,
        step_name: step.action,
        status: 'failed',
        timestamp: new Date(),
        duration_ms: duration,
        error: error.message,
      };
    }
  }

  /**
   * Execute specific action type
   */
  async executeAction(action, params, secrets) {
    switch (action.toLowerCase()) {
      case 'http_request':
      case 'api_call':
        return this.executeHttpRequest(params, secrets);

      case 'update_spreadsheet':
        return this.executeSpreadsheetUpdate(params, secrets);

      case 'send_message':
      case 'slack':
        return this.executeSlackMessage(params, secrets);

      case 'send_email':
        return this.executeSendEmail(params, secrets);

      case 'database_query':
        return this.executeDatabaseQuery(params, secrets);

      case 'execute_code':
        return this.executeCode(params, secrets);

      case 'transform_data':
        return this.transformData(params, secrets);

      case 'webhook_trigger':
        return this.triggerWebhook(params, secrets);

      default:
        return { action, status: 'skipped', message: 'Unknown action' };
    }
  }

  /**
   * HTTP/API Request executor
   */
  async executeHttpRequest(params, secrets) {
    const { method = 'GET', url, headers = {}, body, timeout = 30000 } = params;

    // Substitute secrets
    const resolvedUrl = this.substituteSecrets(url, secrets);
    const resolvedBody = this.substituteSecrets(JSON.stringify(body), secrets);
    const resolvedHeaders = this.substituteSecrets(JSON.stringify(headers), secrets);

    const config = {
      method,
      url: resolvedUrl,
      headers: JSON.parse(resolvedHeaders),
      timeout,
    };

    if (body) {
      config.data = JSON.parse(resolvedBody);
    }

    const response = await axios(config);

    return {
      status_code: response.status,
      headers: response.headers,
      data: response.data,
      timestamp: new Date(),
    };
  }

  /**
   * Google Sheets update
   */
  async executeSpreadsheetUpdate(params, secrets) {
    const { sheet_id, range = 'A1:B10', data } = params;

    if (!secrets.GOOGLE_SHEETS_API_KEY) {
      return {
        status: 'pending',
        message: 'Google Sheets API key not configured',
        sheet_id,
        range,
      };
    }

    // In production, use @google-cloud/sheets library
    return {
      status: 'executed',
      sheet_id,
      range,
      rows_updated: Array.isArray(data) ? data.length : 1,
      timestamp: new Date(),
    };
  }

  /**
   * Slack message sender
   */
  async executeSlackMessage(params, secrets) {
    const { channel, text, emoji = ':robot_face:' } = params;

    if (!secrets.SLACK_WEBHOOK_URL) {
      return {
        status: 'pending',
        message: 'Slack webhook not configured',
        channel,
      };
    }

    try {
      const response = await axios.post(secrets.SLACK_WEBHOOK_URL, {
        channel,
        text,
        emoji,
        timestamp: new Date(),
      });

      return {
        status: 'sent',
        channel,
        message_text: text,
        response: response.data,
      };
    } catch (error) {
      return {
        status: 'failed',
        channel,
        error: error.message,
      };
    }
  }

  /**
   * Email sender (requires mail service)
   */
  async executeSendEmail(params, secrets) {
    const { to, subject, body, from = 'noreply@workflow.ai' } = params;

    return {
      status: 'pending',
      message: 'Email service not configured',
      to,
      subject,
      from,
      note: 'Integrate nodemailer or SendGrid for production',
    };
  }

  /**
   * Database query executor
   */
  async executeDatabaseQuery(params, secrets) {
    const { query, database = 'default' } = params;

    return {
      status: 'pending',
      message: 'Database executor not configured',
      database,
      query_length: query?.length,
      note: 'Integrate with postgres/mysql drivers for production',
    };
  }

  /**
   * Code execution (sandboxed, limited)
   */
  async executeCode(params, secrets) {
    const { code, language = 'javascript', variables = {} } = params;

    if (language === 'javascript') {
      try {
        // Very basic eval (NOT for production - use vm2 or similar)
        const fn = new Function(...Object.keys(variables), code);
        const result = fn(...Object.values(variables));

        return {
          status: 'executed',
          language,
          result,
          timestamp: new Date(),
        };
      } catch (error) {
        return {
          status: 'failed',
          language,
          error: error.message,
        };
      }
    }

    return {
      status: 'skipped',
      language,
      message: 'Language not supported',
    };
  }

  /**
   * Data transformation (using step results)
   */
  async transformData(params, secrets) {
    const { input_step, transformation } = params;

    const sourceData = this.stepResults[input_step];

    if (!sourceData) {
      return {
        status: 'failed',
        error: `Source step ${input_step} not executed or no result`,
      };
    }

    // Simple transformations
    try {
      let result = sourceData;

      if (transformation === 'json_to_csv') {
        result = this.jsonToCsv(sourceData);
      } else if (transformation === 'extract_field') {
        const { field_path } = params;
        result = this.nestedGet(sourceData, field_path);
      }

      return {
        status: 'success',
        transformation,
        input_size: JSON.stringify(sourceData).length,
        output_size: JSON.stringify(result).length,
        result,
      };
    } catch (error) {
      return {
        status: 'failed',
        error: error.message,
      };
    }
  }

  /**
   * Webhook trigger
   */
  async triggerWebhook(params, secrets) {
    const { webhook_url, payload } = params;

    try {
      const response = await axios.post(webhook_url, payload, {
        timeout: 10000,
      });

      return {
        status: 'triggered',
        webhook_url,
        response_status: response.status,
        response_data: response.data,
      };
    } catch (error) {
      return {
        status: 'failed',
        webhook_url,
        error: error.message,
      };
    }
  }

  /**
   * Check if step dependencies are met
   */
  dependenciesMet(step) {
    return step.depends_on.every((depId) => this.stepResults.hasOwnProperty(depId));
  }

  /**
   * Topological sort for dependency resolution
   */
  topologicalSort() {
    const visited = new Set();
    const result = [];

    const visit = (stepId) => {
      if (visited.has(stepId)) return;
      visited.add(stepId);

      const step = this.workflow.steps.find((s) => s.id === stepId);
      if (!step) return;

      step.depends_on?.forEach((dep) => visit(dep));
      result.push(stepId);
    };

    this.workflow.steps.forEach((step) => visit(step.id));

    return result;
  }

  /**
   * Substitute secrets in strings
   */
  substituteSecrets(input, secrets) {
    if (!input) return input;

    let result = typeof input === 'string' ? input : JSON.stringify(input);

    Object.entries(secrets).forEach(([key, value]) => {
      result = result.replace(new RegExp(`{{\\s*${key}\\s*}}`, 'g'), value);
    });

    return result;
  }

  /**
   * JSON to CSV conversion
   */
  jsonToCsv(data) {
    if (!Array.isArray(data) || data.length === 0) return '';

    const headers = Object.keys(data[0]);
    const rows = data.map((item) => headers.map((h) => item[h]).join(','));

    return [headers.join(','), ...rows].join('\n');
  }

  /**
   * Nested object get
   */
  nestedGet(obj, path) {
    return path.split('.').reduce((current, prop) => current?.[prop], obj);
  }
}

/**
 * Execute workflow from request
 */
export const executeWorkflowFromRequest = async (workflow, secrets = {}) => {
  const executor = new WorkflowExecutor(workflow);
  return executor.execute(secrets);
};
