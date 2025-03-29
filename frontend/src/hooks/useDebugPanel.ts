import { useState, useEffect } from 'react';
import { logger, LogCategory } from '../utils/logger';

export const useDebugPanel = () => {
  const [isVisible, setIsVisible] = useState(false);

  // Toggle debug panel with keyboard shortcut (Ctrl/Cmd + Shift + D)
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'D') {
        e.preventDefault();
        setIsVisible(prev => !prev);
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, []);

  // Log debug panel state changes
  useEffect(() => {
    logger.info(
      LogCategory.UI,
      `Debug Panel ${isVisible ? 'opened' : 'closed'}`,
      { timestamp: new Date().toISOString() },
      'DebugPanel'
    );
  }, [isVisible]);

  return {
    isVisible,
    toggle: () => setIsVisible(prev => !prev),
    show: () => setIsVisible(true),
    hide: () => setIsVisible(false),
  };
};
