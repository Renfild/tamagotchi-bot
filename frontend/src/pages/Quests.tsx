import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { questsApi } from '../api/client';
import { useTelegram } from '../hooks/useTelegram';
import './Quests.css';

interface Quest {
  id: number;
  quest: {
    title: string;
    description: string;
    reward_coins: number;
    reward_crystals: number;
  };
  progress: {
    current: number;
    target: number;
    percent: number;
  };
  is_completed: boolean;
  is_claimed: boolean;
}

const Quests: React.FC = () => {
  const [quests, setQuests] = useState<Quest[]>([]);
  const [loading, setLoading] = useState(true);
  const { hapticNotification } = useTelegram();

  useEffect(() => {
    loadQuests();
  }, []);

  const loadQuests = async () => {
    try {
      const response = await questsApi.getQuests();
      setQuests(response.data);
    } catch (error) {
      console.error('Failed to load quests:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleClaim = async (questId: number) => {
    try {
      await questsApi.claimReward(questId);
      hapticNotification('success');
      loadQuests();
    } catch (error) {
      hapticNotification('error');
    }
  };

  if (loading) {
    return <div className="quests loading">Загрузка...</div>;
  }

  return (
    <div className="quests">
      <h1>📜 Квесты</h1>
      
      <div className="quests-list">
        {quests.map((quest, index) => (
          <motion.div
            key={quest.id}
            className={`quest-card ${quest.is_completed ? 'completed' : ''}`}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
          >
            <div className="quest-info">
              <h3>{quest.quest.title}</h3>
              <p>{quest.quest.description}</p>
              
              {/* Progress Bar */}
              <div className="quest-progress">
                <div 
                  className="progress-fill"
                  style={{ width: `${quest.progress.percent}%` }}
                />
                <span>{quest.progress.current} / {quest.progress.target}</span>
              </div>
              
              {/* Rewards */}
              <div className="quest-rewards">
                {quest.quest.reward_coins > 0 && (
                  <span>🪙 {quest.quest.reward_coins}</span>
                )}
                {quest.quest.reward_crystals > 0 && (
                  <span>💎 {quest.quest.reward_crystals}</span>
                )}
              </div>
            </div>
            
            {/* Action */}
            {quest.is_completed && !quest.is_claimed && (
              <button 
                className="claim-btn"
                onClick={() => handleClaim(quest.id)}
              >
                Забрать
              </button>
            )}
            {quest.is_claimed && (
              <span className="claimed-badge">✓</span>
            )}
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default Quests;
