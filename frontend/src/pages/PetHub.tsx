import React, { useEffect } from 'react';
import { motion } from 'framer-motion';
import { usePetStore } from '../store/petStore';
import { useAuthStore } from '../store/authStore';
import { useTelegram } from '../hooks/useTelegram';
import './PetHub.css';

const PetHub: React.FC = () => {
  const { activePet, fetchActivePet, feedPet, petPet, playWithPet } = usePetStore();
  const { user } = useAuthStore();
  const { hapticImpact, hapticNotification } = useTelegram();

  useEffect(() => {
    if (!activePet) {
      fetchActivePet();
    }
  }, [activePet, fetchActivePet]);

  const handleFeed = async () => {
    if (activePet) {
      hapticImpact('medium');
      await feedPet(activePet.id);
      hapticNotification('success');
    }
  };

  const handlePet = async () => {
    if (activePet) {
      hapticImpact('light');
      await petPet(activePet.id);
    }
  };

  const handlePlay = async () => {
    if (activePet) {
      hapticImpact('medium');
      await playWithPet(activePet.id);
      hapticNotification('success');
    }
  };

  if (!activePet) {
    return (
      <div className="pet-hub empty">
        <div className="empty-state">
          <span className="empty-icon">🐾</span>
          <h2>У вас нет питомца</h2>
          <p>Создайте своего первого питомца!</p>
        </div>
      </div>
    );
  }

  const getStatusEmoji = () => {
    switch (activePet.status) {
      case 'sleeping': return '😴';
      case 'sick': return '🤒';
      case 'depressed': return '😢';
      default: return '😊';
    }
  };

  const getRarityEmoji = () => {
    switch (activePet.rarity) {
      case 'legendary': return '🟡';
      case 'epic': return '🟣';
      case 'rare': return '🔵';
      case 'uncommon': return '🟢';
      default: return '⚪';
    }
  };

  return (
    <div className="pet-hub">
      {/* Currency Bar */}
      <div className="currency-bar">
        <div className="currency-item coins">
          <span>🪙</span>
          <span>{user?.coins || 0}</span>
        </div>
        <div className="currency-item crystals">
          <span>💎</span>
          <span>{user?.crystals || 0}</span>
        </div>
      </div>

      {/* Pet Display */}
      <motion.div 
        className="pet-display"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <motion.div 
          className="pet-avatar"
          animate={{ 
            scale: [1, 1.02, 1],
          }}
          transition={{ 
            duration: 3,
            repeat: Infinity,
            ease: "easeInOut"
          }}
          onClick={handlePet}
        >
          {getStatusEmoji()}
        </motion.div>
        
        <h2 className="pet-name">
          {activePet.name} {getRarityEmoji()}
        </h2>
        <p className="pet-info">
          Уровень {activePet.level} • {activePet.evolution_stage}
        </p>
        
        {/* Experience Bar */}
        <div className="exp-bar">
          <div 
            className="exp-fill"
            style={{ width: `${activePet.exp_progress_percent}%` }}
          />
          <span className="exp-text">
            {activePet.experience} / {activePet.exp_to_next_level} XP
          </span>
        </div>
      </motion.div>

      {/* Status Bars */}
      <div className="status-bars">
        <StatusBar 
          icon="🍖" 
          label="Сытость" 
          value={activePet.stats.hunger} 
          color="hunger"
        />
        <StatusBar 
          icon="😊" 
          label="Настроение" 
          value={activePet.stats.happiness} 
          color="happiness"
        />
        <StatusBar 
          icon="❤️" 
          label="Здоровье" 
          value={activePet.stats.health} 
          color="health"
        />
        <StatusBar 
          icon="⚡" 
          label="Энергия" 
          value={activePet.stats.energy} 
          color="energy"
        />
      </div>

      {/* Action Buttons */}
      <div className="action-buttons">
        <motion.button 
          className="action-btn feed"
          onClick={handleFeed}
          whileTap={{ scale: 0.95 }}
        >
          <span className="icon">🍎</span>
          <span>Покормить</span>
        </motion.button>
        
        <motion.button 
          className="action-btn play"
          onClick={handlePlay}
          whileTap={{ scale: 0.95 }}
        >
          <span className="icon">🎮</span>
          <span>Играть</span>
        </motion.button>
        
        <motion.button 
          className="action-btn sleep"
          whileTap={{ scale: 0.95 }}
        >
          <span className="icon">😴</span>
          <span>Спать</span>
        </motion.button>
        
        <motion.button 
          className="action-btn walk"
          whileTap={{ scale: 0.95 }}
        >
          <span className="icon">🚶</span>
          <span>Гулять</span>
        </motion.button>
      </div>
    </div>
  );
};

interface StatusBarProps {
  icon: string;
  label: string;
  value: number;
  color: string;
}

const StatusBar: React.FC<StatusBarProps> = ({ icon, label, value, color }) => {
  return (
    <div className={`status-item ${color}`}>
      <span className="icon">{icon}</span>
      <div className="bar">
        <motion.div 
          className="fill"
          initial={{ width: 0 }}
          animate={{ width: `${value}%` }}
          transition={{ duration: 0.5, ease: "easeOut" }}
        />
      </div>
      <span className="value">{value}%</span>
    </div>
  );
};

export default PetHub;
