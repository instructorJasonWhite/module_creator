declare module 'react-hot-toast' {
  export interface ToastOptions {
    duration?: number;
    position?: 'top-left' | 'top-center' | 'top-right' | 'bottom-left' | 'bottom-center' | 'bottom-right';
    style?: React.CSSProperties;
    className?: string;
    icon?: string | React.ReactNode;
    ariaProps?: {
      role: string;
      'aria-live': string;
    };
  }

  export interface Toast {
    id: string;
    type: 'success' | 'error' | 'loading' | 'blank' | 'custom';
    message: string;
    options?: ToastOptions;
  }

  interface ToastFunction {
    (message: string, options?: ToastOptions): string;
    success(message: string, options?: ToastOptions): string;
    error(message: string, options?: ToastOptions): string;
    loading(message: string, options?: ToastOptions): string;
    custom(message: string, options?: ToastOptions): string;
    dismiss(toastId?: string): void;
    promise<T>(
      promise: Promise<T>,
      messages: {
        loading: string;
        success: string;
        error: string;
      },
      options?: ToastOptions
    ): Promise<T>;
  }

  const toast: ToastFunction;
  export default toast;
}
