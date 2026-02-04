import React from 'react';
import { motion } from 'framer-motion';
import './Arena.css';

const Arena: React.FC = () => {
  return (
    <div className="arena">
      <h1>⚔️ Арена</h1>
      
      <div className="arena-stats">
        <div className="stat-card">
          <span className="label">Рейтинг</span>
          <span className="value">Бронза III</span>
        </div>
        <div className="stat-card">
          <span className="label">Побед</span>
          <span className="value">0</span>
        </div>
        <div className="stat-card">
          <span className="label">Поражений</span>
          <span className="value">0</span>
        </div>
      </div>

      <div className="arena-modes">
        <motion.button 
          className="mode-card"
          whileTap={{ scale: 0.95 }}
        >
          <span className="emoji">🥊</span>
          <h3>Дружеский спарринг</h3>
          <p>Без потерь и ставок</p>
        </motion.button>
        
        <motion.button 
          className="mode-card"
          whileTap={{ scale: 0.95 }}
        >
          <span className="emoji">🏆</span>
          <h3>Рейтинговый бой</h3>
          <p>Поднимайтесь в лигах</p>
        </motion.button>
        
        <motion.button 
          className="mode-card"
          whileTap={{ scale: 0.95 }}
        >
          <span className="emoji">🎲</span>
          <h3>Ставочный бой</h3>
          <p>Ставьте на победу</p>
        </motion.button>
      </div>
    </div>
  );
};

export default Arena;
