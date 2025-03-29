// Log levels
export enum LogLevel {
  DEBUG = 'DEBUG',
  INFO = 'INFO',
  WARN = 'WARN',
  ERROR = 'ERROR'
}

// Log categories
export enum LogCategory {
  AUTH = 'Authentication',
  API = 'API Calls',
  UI = 'User Interface',
  STATE = 'State Management',
  FILE = 'File Operations',
  AGENT = 'Agent Status',
  VALIDATION = 'Validation',
  PERFORMANCE = 'Performance',
  ERROR = 'Error Tracking'
}

// Format date without date-fns
const formatDate = (date: Date): string => {
  return date.toISOString().split('T')[0] + ' ' + date.toTimeString().split(' ')[0];
};

// Log message interface
interface LogMessage {
  timestamp: string;
  level: LogLevel;
  category: LogCategory;
  message: string;
  data?: any;
  component?: string;
}

// Logger class
export class Logger {
  private static instance: Logger;
  private logs: LogMessage[] = [];
  private maxLogs: number = 1000;

  private constructor() {}

  static getInstance(): Logger {
    if (!Logger.instance) {
      Logger.instance = new Logger();
    }
    return Logger.instance;
  }

  private addLog(level: LogLevel, category: LogCategory, message: string, data?: any, component?: string) {
    const log: LogMessage = {
      timestamp: formatDate(new Date()),
      level,
      category,
      message,
      data,
      component
    };

    this.logs.push(log);
    if (this.logs.length > this.maxLogs) {
      this.logs.shift();
    }
  }

  debug(category: LogCategory, message: string, data?: any, component?: string) {
    this.addLog(LogLevel.DEBUG, category, message, data, component);
    console.debug(`[${LogLevel.DEBUG}] [${category}] ${component ? `[${component}] ` : ''}${message}`, data || '');
  }

  info(category: LogCategory, message: string, data?: any, component?: string) {
    this.addLog(LogLevel.INFO, category, message, data, component);
    console.info(`[${LogLevel.INFO}] [${category}] ${component ? `[${component}] ` : ''}${message}`, data || '');
  }

  warn(category: LogCategory, message: string, data?: any, component?: string) {
    this.addLog(LogLevel.WARN, category, message, data, component);
    console.warn(`[${LogLevel.WARN}] [${category}] ${component ? `[${component}] ` : ''}${message}`, data || '');
  }

  error(category: LogCategory, message: string, data?: any, component?: string) {
    this.addLog(LogLevel.ERROR, category, message, data, component);
    console.error(`[${LogLevel.ERROR}] [${category}] ${component ? `[${component}] ` : ''}${message}`, data || '');
  }

  getLogs(): LogMessage[] {
    return [...this.logs];
  }

  clearLogs() {
    this.logs = [];
  }

  setMaxLogs(max: number) {
    this.maxLogs = max;
    while (this.logs.length > this.maxLogs) {
      this.logs.shift();
    }
  }
}

export const logger = Logger.getInstance();
