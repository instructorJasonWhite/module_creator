declare module 'notistack' {
  import { SnackbarKey } from 'notistack';

  export interface OptionsObject {
    variant?: 'success' | 'error' | 'warning' | 'info';
    action?: (key: SnackbarKey) => React.ReactNode;
    onClose?: (key: SnackbarKey) => void;
    onClick?: (key: SnackbarKey) => void;
    onExited?: (key: SnackbarKey) => void;
    className?: string;
    style?: React.CSSProperties;
    anchorOrigin?: {
      vertical: 'top' | 'bottom';
      horizontal: 'left' | 'center' | 'right';
    };
    autoHideDuration?: number;
    disableWindowBlurListener?: boolean;
    dense?: boolean;
    hideIconVariant?: boolean;
    maxSnack?: number;
    preventDuplicate?: boolean;
    resumeHideDuration?: number;
  }

  export interface EnqueueSnackbar {
    (message: string | React.ReactNode, options?: OptionsObject): SnackbarKey;
  }

  export interface CloseSnackbar {
    (key?: SnackbarKey): void;
  }

  export interface UseSnackbar {
    enqueueSnackbar: EnqueueSnackbar;
    closeSnackbar: CloseSnackbar;
  }

  export function useSnackbar(): UseSnackbar;

  export interface SnackbarProviderProps {
    children: React.ReactNode;
    maxSnack?: number;
    dense?: boolean;
    preventDuplicate?: boolean;
    anchorOrigin?: {
      vertical: 'top' | 'bottom';
      horizontal: 'left' | 'center' | 'right';
    };
    classes?: {
      containerRoot?: string;
      containerAnchorTopLeft?: string;
      containerAnchorTopCenter?: string;
      containerAnchorTopRight?: string;
      containerAnchorBottomLeft?: string;
      containerAnchorBottomCenter?: string;
      containerAnchorBottomRight?: string;
    };
  }

  export const SnackbarProvider: React.FC<SnackbarProviderProps>;
}
