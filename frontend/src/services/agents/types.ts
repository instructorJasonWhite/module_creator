export interface ModelConfig {
  name: string;
  provider: string;
  model: string;
  max_tokens: number;
  temperature: number;
  api_key?: string;
  base_url?: string;
}

export interface AgentContext {
  context_id: string;
  context: string;
  priority: number;
  is_active: boolean;
}

export interface AgentConfig {
  name: string;
  description: string;
  model: ModelConfig;
  contexts: AgentContext[];
  maxRetries: number;
  timeout: number;
}

export interface AgentResponse {
  success: boolean;
  response: string;
  processingTime: number;
  error: string | null;
}

export interface AgentRequest {
  prompt: string;
  context?: string;
  options?: {
    temperature?: number;
    max_tokens?: number;
    stop?: string[];
  };
}

export enum AgentStatus {
  IDLE = 'idle',
  RUNNING = 'running',
  ERROR = 'error',
  COMPLETED = 'completed'
}

export interface AgentState {
  status: AgentStatus;
  lastError?: string;
  lastResponse?: AgentResponse;
  isActive: boolean;
}
