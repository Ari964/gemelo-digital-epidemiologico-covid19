/**
 * Structured Logger for Digital Twin Epidemiological Engine
 */
export type LogLevel = 'info' | 'warn' | 'error' | 'debug';

class Logger {
  private formatMessage(level: LogLevel, message: string, context?: Record<string, any>): string {
    const timestamp = new Date().toISOString();
    const ctxStr = context ? ` | ${JSON.stringify(context)}` : '';
    return `[${timestamp}] [${level.toUpperCase()}] ${message}${ctxStr}`;
  }

  info(message: string, context?: Record<string, any>) {
    console.info(this.formatMessage('info', message, context));
  }

  warn(message: string, context?: Record<string, any>) {
    console.warn(this.formatMessage('warn', message, context));
  }

  error(message: string, context?: Record<string, any>, error?: Error) {
    console.error(this.formatMessage('error', message, context), error || '');
  }

  debug(message: string, context?: Record<string, any>) {
    if (process.env.NODE_ENV !== 'production') {
      console.debug(this.formatMessage('debug', message, context));
    }
  }
}

export const logger = new Logger();
