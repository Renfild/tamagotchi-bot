import React from 'react';
import { motion } from 'framer-motion';
import { useTelegram } from '../hooks/useTelegram';
import './Games.css';

const GAMES = [
  { id: 'food_run', name: 'Бег за едой', emoji: '🏃', description: 'Собирайте монетки' },
  { id: 'puzzle', name: 'Пазл', emoji: '🧩', description: 'Соберите картинку' },
  { id: 'rhythm', name: 'Ритм-игра', emoji: '🎵', description: 'Нажимайте в такт' },
  { id: 'fishing', name: 'Рыбалка', emoji: '🎣', description: 'Ловите рыбу' },
  { id: 'maze', name: 'Лабиринт', emoji: '🎯', description: 'Найдите выход' },
  { id: 'duel', name: 'PvP Дуэль', emoji: '⚔️', description: 'Сразитесь с другом' },
];

const Games: React.FC = () => {
  const { hapticImpact } = useTelegram();

  const handleGameClick = (gameId: string) => {
    hapticImpact('medium');
    // TODO: Open game
  };

  return (
    <div className="games">
      <h1>🎮 Мини-игры</h1>
      
      <div className="games-grid">
        {GAMES.map((game, index) => (
          <motion.button
            key={game.id}
            className="game-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            onClick={() => handleGameClick(game.id)}
            whileTap={{ scale: 0.95 }}
          >
            <span className="game-emoji">{game.emoji}</span>
            <h3>{game.name}</h3>
            <p>{game.description}</p>
          </motion.button>
        ))}
      </div>
    </div>
  );
};

export default Games;
