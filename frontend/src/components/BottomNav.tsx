import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useTelegram } from '../hooks/useTelegram';
import './BottomNav.css';

interface NavItem {
  path: string;
  icon: string;
  label: string;
}

const navItems: NavItem[] = [
  { path: '/pet', icon: '🐾', label: 'Питомец' },
  { path: '/inventory', icon: '🎒', label: 'Инвентарь' },
  { path: '/shop', icon: '🛒', label: 'Магазин' },
  { path: '/games', icon: '🎮', label: 'Игры' },
  { path: '/friends', icon: '👥', label: 'Друзья' },
];

const BottomNav: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { hapticImpact } = useTelegram();

  const handleClick = (path: string) => {
    hapticImpact('light');
    navigate(path);
  };

  return (
    <nav className="bottom-nav">
      {navItems.map((item) => (
        <button
          key={item.path}
          className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}
          onClick={() => handleClick(item.path)}
        >
          <span className="nav-icon">{item.icon}</span>
          <span className="nav-label">{item.label}</span>
        </button>
      ))}
    </nav>
  );
};

export default BottomNav;
