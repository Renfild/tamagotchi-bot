import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { shopApi } from '../api/client';
import { useAuthStore } from '../store/authStore';
import { useTelegram } from '../hooks/useTelegram';
import './Shop.css';

interface ShopItem {
  id: number;
  name: string;
  description: string;
  type: string;
  price: {
    coins?: number;
    crystals?: number;
  };
  icon_url?: string;
}

const Shop: React.FC = () => {
  const [items, setItems] = useState<ShopItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const { user, updateUser } = useAuthStore();
  const { hapticNotification } = useTelegram();

  useEffect(() => {
    loadItems();
  }, []);

  const loadItems = async () => {
    try {
      const response = await shopApi.getItems();
      setItems(response.data);
    } catch (error) {
      console.error('Failed to load shop items:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleBuy = async (item: ShopItem) => {
    try {
      const response = await shopApi.buyItem(item.id);
      const { spent_coins, spent_crystals } = response.data;
      
      updateUser({
        coins: (user?.coins || 0) - spent_coins,
        crystals: (user?.crystals || 0) - spent_crystals,
      });
      
      hapticNotification('success');
    } catch (error) {
      hapticNotification('error');
    }
  };

  const categories = [
    { id: 'all', name: 'Все', emoji: '📦' },
    { id: 'food', name: 'Еда', emoji: '🍎' },
    { id: 'toy', name: 'Игрушки', emoji: '🎾' },
    { id: 'medicine', name: 'Лекарства', emoji: '💊' },
    { id: 'clothing', name: 'Одежда', emoji: '🧥' },
  ];

  const filteredItems = selectedCategory === 'all' 
    ? items 
    : items.filter(item => item.type === selectedCategory);

  if (loading) {
    return <div className="shop loading">Загрузка...</div>;
  }

  return (
    <div className="shop">
      <h1>🛒 Магазин</h1>
      
      {/* Currency */}
      <div className="shop-currency">
        <span>🪙 {user?.coins || 0}</span>
        <span>💎 {user?.crystals || 0}</span>
      </div>
      
      {/* Category Filter */}
      <div className="category-filter">
        {categories.map(cat => (
          <button
            key={cat.id}
            className={selectedCategory === cat.id ? 'active' : ''}
            onClick={() => setSelectedCategory(cat.id)}
          >
            {cat.emoji} {cat.name}
          </button>
        ))}
      </div>

      {/* Items */}
      <div className="shop-items">
        {filteredItems.map((item, index) => (
          <motion.div
            key={item.id}
            className="shop-item"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
          >
            <div className="item-icon">📦</div>
            <h3>{item.name}</h3>
            <p>{item.description}</p>
            <div className="item-price">
              {item.price.coins && <span>🪙 {item.price.coins}</span>}
              {item.price.crystals && <span>💎 {item.price.crystals}</span>}
            </div>
            <button 
              className="buy-btn"
              onClick={() => handleBuy(item)}
            >
              Купить
            </button>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default Shop;
