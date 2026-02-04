import React from 'react';
import { motion } from 'framer-motion';
import './Breeding.css';

const Breeding: React.FC = () => {
  return (
    <div className="breeding">
      <h1>🐾 Разведение</h1>
      
      <div className="breeding-info">
        <div className="info-card">
          <h3>Условия разведения</h3>
          <ul>
            <li>Оба питомца 10+ уровня</li>
            <li>Питомцы здоровы</li>
            <li>Кулдаун 7 дней</li>
          </ul>
        </div>
        
        <div className="cost-card">
          <span>Стоимость:</span>
          <span className="cost">🪙 500</span>
        </div>
      </div>

      <motion.button 
        className="find-partner-btn"
        whileTap={{ scale: 0.95 }}
      >
        🔍 Найти партнера
      </motion.button>
    </div>
  );
};

export default Breeding;
