import React from 'react';
import { useAuthStore } from '../store/authStore';
import { useTelegram } from '../hooks/useTelegram';
import './Settings.css';

const Settings: React.FC = () => {
  const { user } = useAuthStore();
  const { closeApp } = useTelegram();

  return (
    <div className="settings">
      <h1>⚙️ Настройки</h1>
      
      {/* Profile */}
      <div className="profile-card">
        <div className="profile-avatar">👤</div>
        <div className="profile-info">
          <h2>{user?.first_name}</h2>
          <p>ID: {user?.id}</p>
        </div>
      </div>

      {/* Stats */}
      <div className="settings-section">
        <h3>Статистика</h3>
        <div className="stats-grid">
          <div className="stat-item">
            <span className="label">Побед</span>
            <span className="value">{user?.stats?.battles_won || 0}</span>
          </div>
          <div className="stat-item">
            <span className="label">Квестов</span>
            <span className="value">{user?.stats?.quests_completed || 0}</span>
          </div>
          <div className="stat-item">
            <span className="label">Питомцев</span>
            <span className="value">{user?.stats?.pets_created || 0}</span>
          </div>
        </div>
      </div>

      {/* Settings */}
      <div className="settings-section">
        <h3>Настройки</h3>
        <div className="settings-list">
          <button className="setting-item">
            <span>🌍 Язык</span>
            <span>Русский →</span>
          </button>
          <button className="setting-item">
            <span>🔔 Уведомления</span>
            <span>Включены →</span>
          </button>
          <button className="setting-item">
            <span>👁 Приватность</span>
            <span>Друзья →</span>
          </button>
        </div>
      </div>

      {/* Actions */}
      <div className="settings-actions">
        <button className="action-btn secondary" onClick={closeApp}>
          Закрыть приложение
        </button>
      </div>
    </div>
  );
};

export default Settings;
