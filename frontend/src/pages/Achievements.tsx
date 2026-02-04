import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { achievementsApi } from '../api/client';
import './Achievements.css';

interface Achievement {
  id: number;
  achievement: {
    title: string;
    description: string;
    rarity: string;
    icon_url?: string;
    rewards: {
      coins: number;
      crystals: number;
    };
  };
  earned_at: string;
  is_reward_claimed: boolean;
}

const Achievements: React.FC = () => {
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAchievements();
  }, []);

  const loadAchievements = async () => {
    try {
      const response = await achievementsApi.getAchievements();
      setAchievements(response.data);
    } catch (error) {
      console.error('Failed to load achievements:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRarityColor = (rarity: string) => {
    switch (rarity) {
      case 'diamond': return '#B9F2FF';
      case 'platinum': return '#E5E4E2';
      case 'gold': return '#FFD700';
      case 'silver': return '#C0C0C0';
      default: return '#CD7F32';
    }
  };

  if (loading) {
    return <div className="achievements loading">Загрузка...</div>;
  }

  return (
    <div className="achievements">
      <h1>🏆 Достижения</h1>
      
      <div className="achievements-stats">
        <span>Получено: {achievements.length}</span>
      </div>
      
      <div className="achievements-list">
        {achievements.map((ach, index) => (
          <motion.div
            key={ach.id}
            className="achievement-card"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.05 }}
            style={{ 
              borderColor: getRarityColor(ach.achievement.rarity) 
            }}
          >
            <div 
              className="achievement-icon"
              style={{ background: getRarityColor(ach.achievement.rarity) }}
            >
              🏅
            </div>
            <div className="achievement-info">
              <h3>{ach.achievement.title}</h3>
              <p>{ach.achievement.description}</p>
              <div className="achievement-rewards">
                {ach.achievement.rewards.coins > 0 && (
                  <span>🪙 {ach.achievement.rewards.coins}</span>
                )}
                {ach.achievement.rewards.crystals > 0 && (
                  <span>💎 {ach.achievement.rewards.crystals}</span>
                )}
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default Achievements;
