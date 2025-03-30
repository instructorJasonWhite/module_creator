import { AgentConfig } from './types';
import { OpenAIAgent } from './OpenAIAgent';
import { OllamaAgent } from './OllamaAgent';

export enum AgentType {
  OPENAI = 'openai',
  OLLAMA = 'ollama'
}

export class AgentFactory {
  static createAgent(type: AgentType, config: AgentConfig) {
    switch (type) {
      case AgentType.OPENAI:
        return new OpenAIAgent(config);
      case AgentType.OLLAMA:
        return new OllamaAgent(config);
      default:
        throw new Error(`Unsupported agent type: ${type}`);
    }
  }
}
