import { AgentRequest, AgentResponse, AgentConfig } from './types';

export abstract class BaseAgent {
  protected config: AgentConfig;
  protected state: { status: string; lastError?: string; lastResponse?: AgentResponse };

  constructor(config: AgentConfig) {
    this.config = config;
    this.state = { status: 'idle' };
  }

  abstract process(request: AgentRequest): Promise<AgentResponse>;

  protected async validateRequest(request: AgentRequest): Promise<boolean> {
    if (!request.prompt) {
      throw new Error('Prompt is required');
    }
    return true;
  }

  protected handleError(error: any): AgentResponse {
    return {
      success: false,
      response: '',
      processingTime: 0,
      error: error instanceof Error ? error.message : 'Unknown error occurred'
    };
  }

  protected handleSuccess(response: string, processingTime: number): AgentResponse {
    return {
      success: true,
      response,
      processingTime,
      error: null
    };
  }

  public getState(): { status: string; lastError?: string; lastResponse?: AgentResponse } {
    return { ...this.state };
  }

  public getConfig(): AgentConfig {
    return { ...this.config };
  }

  public setActive(active: boolean): void {
    // Implementation of setActive method
  }

  protected async retry<T>(
    operation: () => Promise<T>,
    maxRetries: number = this.config.maxRetries
  ): Promise<T> {
    let lastError: Error | null = null;

    for (let i = 0; i < maxRetries; i++) {
      try {
        return await operation();
      } catch (error) {
        lastError = error as Error;
        if (i < maxRetries - 1) {
          await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
        }
      }
    }

    throw lastError;
  }
}
