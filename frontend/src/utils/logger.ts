// Log levels
export enum LogLevel {
  DEBUG = 'DEBUG',
  INFO = 'INFO',
  WARN = 'WARN',
  ERROR = 'ERROR'
}

// Log categories
export enum LogCategory {
  AUTH = 'AUTH',
  ERROR = 'ERROR',
  API = 'API',
  UI = 'UI',
  SYSTEM = 'SYSTEM',
  PERFORMANCE = 'PERFORMANCE',
  UPLOAD = 'UPLOAD'
}

// Format date without date-fns
const formatDate = (date: Date): string => {
  return date.toISOString().split('T')[0] + ' ' + date.toTimeString().split(' ')[0];
};

// Log message interface
interface LogEntry {
  timestamp: string;
  category: LogCategory;
  level: LogLevel;
  message: string;
  data?: any;
  source?: string;
}

// Logger class
export class Logger {
  private static instance: Logger;
  private logs: LogEntry[] = [];
  private isDevelopment: boolean;

  private constructor() {
    this.isDevelopment = process.env.NODE_ENV === 'development' || process.env.REACT_APP_DEBUG === 'true';
  }

  static getInstance(): Logger {
    if (!Logger.instance) {
      Logger.instance = new Logger();
    }
    return Logger.instance;
  }

  private log(level: LogLevel, category: LogCategory, message: string, data?: any, source?: string) {
    const entry: LogEntry = {
      timestamp: new Date().toISOString(),
      category,
      level,
      message,
      data,
      source
    };

    this.logs.push(entry);

    if (this.isDevelopment) {
      const consoleMessage = `[${entry.timestamp}] ${entry.level} [${entry.category}] ${entry.source ? `[${entry.source}] ` : ''}${message}`;

      switch (level) {
        case LogLevel.DEBUG:
          console.debug(consoleMessage, data || '');
          break;
        case LogLevel.INFO:
          console.info(consoleMessage, data || '');
          break;
        case LogLevel.WARN:
          console.warn(consoleMessage, data || '');
          break;
        case LogLevel.ERROR:
          console.error(consoleMessage, data || '');
          break;
      }
    }
  }

  debug(category: LogCategory, message: string, data?: any, source?: string) {
    this.log(LogLevel.DEBUG, category, message, data, source);
  }

  info(category: LogCategory, message: string, data?: any, source?: string) {
    this.log(LogLevel.INFO, category, message, data, source);
  }

  warn(category: LogCategory, message: string, data?: any, source?: string) {
    this.log(LogLevel.WARN, category, message, data, source);
  }

  error(category: LogCategory, message: string, data?: any, source?: string) {
    this.log(LogLevel.ERROR, category, message, data, source);
  }

  getLogs(): LogEntry[] {
    return [...this.logs];
  }

  clearLogs() {
    this.logs = [];
  }
}

export const logger = Logger.getInstance();
