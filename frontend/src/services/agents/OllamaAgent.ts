import { BaseAgent } from './BaseAgent';
import { AgentRequest, AgentResponse, AgentConfig } from './types';

export class OllamaAgent extends BaseAgent {
  private baseUrl: string;

  constructor(config: AgentConfig) {
    super(config);
    this.baseUrl = config.model.base_url || 'http://localhost:11434';
  }

  async process(request: AgentRequest): Promise<AgentResponse> {
    try {
      const startTime = Date.now();
      const prompt = this.buildPrompt(request);

      const response = await fetch(`${this.baseUrl}/api/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: this.config.model.model,
          prompt,
          options: {
            temperature: this.config.model.temperature,
            num_predict: this.config.model.max_tokens,
          },
        }),
      });

      if (!response.ok) {
        throw new Error(`Ollama API error: ${response.statusText}`);
      }

      const data = await response.json();
      const processingTime = Date.now() - startTime;

      return {
        success: true,
        response: data.response,
        processingTime,
        error: null
      };
    } catch (error) {
      return {
        success: false,
        response: '',
        processingTime: 0,
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      };
    }
  }

  private buildPrompt(request: AgentRequest): string {
    let prompt = '';

    // Sort contexts by priority
    const sortedContexts = [...this.config.contexts].sort((a, b) => a.priority - b.priority);

    // Add system contexts
    sortedContexts
      .filter(context => context.is_active)
      .forEach(context => {
        prompt += `${context.context}\n\n`;
      });

    // Add current request
    prompt += `User: ${request.prompt}\n\n`;

    return prompt;
  }

  protected async validateRequest(request: AgentRequest): Promise<boolean> {
    if (!request.prompt) {
      throw new Error('Prompt is required');
    }

    // Check if base URL is provided
    if (!this.config.model.base_url) {
      throw new Error('Ollama base URL is required');
    }

    return true;
  }
}
