import { logger, LogCategory } from '../utils/logger';
import { api } from './api';

export interface SystemStats {
  cpu_usage: number;
  memory_usage: {
    total: number;
    used: number;
    free: number;
    percent: number;
  };
  disk_usage: {
    total: number;
    used: number;
    free: number;
    percent: number;
  };
  network_stats: {
    bytes_sent: number;
    bytes_recv: number;
    packets_sent: number;
    packets_recv: number;
  };
  process_count: number;
  token_usage: number;
  estimated_cost: number;
}

export interface ModelSettings {
  model_name: string;
  api_key?: string;
  max_tokens: number;
  temperature: number;
  is_active: boolean;
  cost_per_token: number;
  provider: string;
  base_url?: string;
}

export interface TokenUsage {
  total_tokens: number;
  prompt_tokens: number;
  completion_tokens: number;
  estimated_cost: number;
  last_reset: string;
}

export interface AgentStatus {
  status: string;
  last_active: string;
}

export interface AgentStatuses {
  [key: string]: {
    status: string;
    last_active: string;
  };
}

export interface AgentContext {
  context_id: string;
  context: string;
  priority: number;
  is_active: boolean;
}

export interface Agent {
  name: string;
  description: string;
  role: string;
  contexts: AgentContext[];
  is_active: boolean;
  last_active: string;
  status: string;
}

const MAX_RETRIES = 3;
const RETRY_DELAY = 1000; // 1 second

const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export const fetchWithRetry = async (url: string, options: RequestInit = {}, retries = MAX_RETRIES): Promise<Response> => {
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${localStorage.getItem('adminToken')}`,
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response;
  } catch (error) {
    if (retries > 0) {
      logger.warn(LogCategory.API, `Retrying request to ${url}, ${retries} attempts remaining`, error, 'SystemService');
      await delay(RETRY_DELAY);
      return fetchWithRetry(url, options, retries - 1);
    }
    throw error;
  }
};

export const fetchSystemStats = async (): Promise<SystemStats> => {
  const response = await api.get('/api/v1/system/stats');
  return response.data;
};

export const fetchAgentStatus = async (): Promise<AgentStatuses> => {
  try {
    const response = await fetchWithRetry('http://localhost:8000/api/v1/system/agents/status');
    const data = await response.json();
    logger.debug(LogCategory.API, 'Agent status fetched successfully', data, 'SystemService');
    return data;
  } catch (error) {
    logger.error(LogCategory.ERROR, 'Failed to fetch agent status', error, 'SystemService');
    throw error;
  }
};

export const fetchModelSettings = async (): Promise<Record<string, ModelSettings>> => {
  const response = await api.get('/api/v1/system/models');
  return response.data;
};

export const updateModelSettings = async (modelName: string, settings: ModelSettings): Promise<ModelSettings> => {
  const response = await api.put(`/api/v1/system/models/${modelName}`, settings);
  return response.data;
};

export const fetchTokenUsage = async (): Promise<TokenUsage> => {
  try {
    const response = await fetchWithRetry('http://localhost:8000/api/v1/system/token-usage');
    const data = await response.json();
    logger.debug(LogCategory.API, 'Token usage fetched successfully', data, 'SystemService');
    return data;
  } catch (error) {
    logger.error(LogCategory.ERROR, 'Failed to fetch token usage', error, 'SystemService');
    throw error;
  }
};

export const resetTokenUsage = async (): Promise<void> => {
  try {
    await fetchWithRetry('http://localhost:8000/api/v1/system/token-usage/reset', {
      method: 'POST',
    });
    logger.debug(LogCategory.API, 'Token usage reset successfully', null, 'SystemService');
  } catch (error) {
    logger.error(LogCategory.ERROR, 'Failed to reset token usage', error, 'SystemService');
    throw error;
  }
};

export const deleteModelSettings = async (modelName: string): Promise<void> => {
  await api.delete(`/api/v1/system/models/${modelName}`);
};

export const createModelSettings = async (settings: ModelSettings): Promise<ModelSettings> => {
  const response = await api.post('/api/v1/system/models', settings);
  return response.data;
};

export const fetchAgents = async (): Promise<Agent[]> => {
  try {
    const response = await fetchWithRetry('http://localhost:8000/api/v1/system/agents');
    const data = await response.json();
    logger.debug(LogCategory.API, 'Agents fetched successfully', data, 'SystemService');
    return data;
  } catch (error) {
    logger.error(LogCategory.ERROR, 'Failed to fetch agents', error, 'SystemService');
    return [];
  }
};

export const fetchAgentContexts = async (): Promise<AgentContext[]> => {
  const response = await api.get('/api/v1/system/agents/contexts');
  return response.data;
};

export const createAgentContext = async (context: AgentContext): Promise<AgentContext> => {
  const response = await api.post('/api/v1/system/agents/contexts', context);
  return response.data;
};

export const updateAgentContext = async (contextId: string, context: AgentContext): Promise<AgentContext> => {
  const response = await api.put(`/api/v1/system/agents/contexts/${contextId}`, context);
  return response.data;
};

export const deleteAgentContext = async (contextId: string): Promise<void> => {
  await api.delete(`/api/v1/system/agents/contexts/${contextId}`);
};
