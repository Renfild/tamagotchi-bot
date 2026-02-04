import { useEffect, useState, useCallback } from 'react';

declare global {
  interface Window {
    Telegram?: {
      WebApp: {
        initData: string;
        initDataUnsafe: {
          user?: {
            id: number;
            first_name: string;
            last_name?: string;
            username?: string;
            language_code?: string;
          };
          query_id?: string;
        };
        ready: () => void;
        expand: () => void;
        close: () => void;
        MainButton: {
          text: string;
          show: () => void;
          hide: () => void;
          onClick: (callback: () => void) => void;
          offClick: (callback: () => void) => void;
        };
        BackButton: {
          show: () => void;
          hide: () => void;
          onClick: (callback: () => void) => void;
        };
        HapticFeedback: {
          impactOccurred: (style: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft') => void;
          notificationOccurred: (type: 'error' | 'success' | 'warning') => void;
        };
        themeParams: {
          bg_color?: string;
          text_color?: string;
          hint_color?: string;
          link_color?: string;
          button_color?: string;
          button_text_color?: string;
        };
      };
    };
  }
}

export const useTelegram = () => {
  const [isReady, setIsReady] = useState(false);
  const [initData, setInitData] = useState<string>('');
// На это:
  const [user, setUser] = useState<{
  id?: number; 
  first_name?: string; 
  last_name?: string; 
  username?: string;
  stats?: { wins?: number; quests?: number };
} | null>(null);

  useEffect(() => {
    const tg = window.Telegram?.WebApp;
    
    if (tg) {
      tg.ready();
      tg.expand();
      
      setInitData(tg.initData);
      setUser(tg.initDataUnsafe.user || null);
      setIsReady(true);

      // Apply theme
      if (tg.themeParams.bg_color) {
        document.documentElement.style.setProperty('--tg-theme-bg-color', tg.themeParams.bg_color);
      }
      if (tg.themeParams.text_color) {
        document.documentElement.style.setProperty('--tg-theme-text-color', tg.themeParams.text_color);
      }
      if (tg.themeParams.button_color) {
        document.documentElement.style.setProperty('--tg-theme-button-color', tg.themeParams.button_color);
      }
    }
  }, []);

  const showMainButton = useCallback((text: string, onClick: () => void) => {
    const tg = window.Telegram?.WebApp;
    if (tg) {
      tg.MainButton.text = text;
      tg.MainButton.onClick(onClick);
      tg.MainButton.show();
    }
  }, []);

  const hideMainButton = useCallback(() => {
    const tg = window.Telegram?.WebApp;
    if (tg) {
      tg.MainButton.hide();
    }
  }, []);

  const showBackButton = useCallback((onClick: () => void) => {
    const tg = window.Telegram?.WebApp;
    if (tg) {
      tg.BackButton.onClick(onClick);
      tg.BackButton.show();
    }
  }, []);

  const hideBackButton = useCallback(() => {
    const tg = window.Telegram?.WebApp;
    if (tg) {
      tg.BackButton.hide();
    }
  }, []);

  const hapticImpact = useCallback((style: 'light' | 'medium' | 'heavy' = 'medium') => {
    const tg = window.Telegram?.WebApp;
    if (tg?.HapticFeedback) {
      tg.HapticFeedback.impactOccurred(style);
    }
  }, []);

  const hapticNotification = useCallback((type: 'error' | 'success' | 'warning' = 'success') => {
    const tg = window.Telegram?.WebApp;
    if (tg?.HapticFeedback) {
      tg.HapticFeedback.notificationOccurred(type);
    }
  }, []);

  const closeApp = useCallback(() => {
    const tg = window.Telegram?.WebApp;
    if (tg) {
      tg.close();
    }
  }, []);

  return {
    isReady,
    initData,
    user,
    showMainButton,
    hideMainButton,
    showBackButton,
    hideBackButton,
    hapticImpact,
    hapticNotification,
    closeApp,
  };
};
