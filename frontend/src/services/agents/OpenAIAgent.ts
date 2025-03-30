import { BaseAgent } from './BaseAgent';
import { AgentRequest, AgentResponse, AgentConfig } from './types';

interface ChatMessage {
  role: 'system' | 'user';
  content: string;
}

export class OpenAIAgent extends BaseAgent {
  private apiKey: string;
  private baseUrl = 'https://api.openai.com/v1/chat/completions';

  constructor(config: AgentConfig) {
    super(config);
    if (!config.model.api_key) {
      throw new Error('OpenAI API key is required');
    }
    this.apiKey = config.model.api_key;
  }

  async process(request: AgentRequest): Promise<AgentResponse> {
    try {
      // Validate request
      await this.validateRequest(request);

      // Start timing
      const startTime = Date.now();

      // Build messages
      const messages = this.buildMessages(request);

      // Make API call
      const response = await fetch(this.baseUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.apiKey}`
        },
        body: JSON.stringify({
          model: this.config.model.model,
          messages,
          temperature: this.config.model.temperature,
          max_tokens: this.config.model.max_tokens,
        })
      });

      if (!response.ok) {
        throw new Error(`OpenAI API error: ${response.statusText}`);
      }

      const completion = await response.json();
      const processingTime = Date.now() - startTime;
      const content = completion.choices[0]?.message?.content || '';

      return {
        success: true,
        response: content,
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

  private buildMessages(request: AgentRequest): ChatMessage[] {
    const messages: ChatMessage[] = [
      {
        role: 'system',
        content: this.config.contexts.map(c => c.context).join('\n')
      }
    ];

    if (request.context) {
      messages.push({
        role: 'system',
        content: request.context
      });
    }

    messages.push({
      role: 'user',
      content: request.prompt
    });

    return messages;
  }

  protected async validateRequest(request: AgentRequest): Promise<boolean> {
    if (!request.prompt) {
      throw new Error('Prompt is required');
    }

    if (!this.apiKey) {
      throw new Error('OpenAI API key is required');
    }

    return true;
  }
}
