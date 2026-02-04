import React, { useEffect } from 'react';
import { motion } from 'framer-motion';
import { inventoryApi } from '../api/client';
import './Inventory.css';

interface InventoryItem {
  id: number;
  item: {
    id: number;
    name: string;
    description: string;
    type: string;
    icon_url?: string;
  };
  quantity: number;
  is_equipped: boolean;
}

const Inventory: React.FC = () => {
  const [items, setItems] = React.useState<InventoryItem[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [selectedCategory, setSelectedCategory] = React.useState('all');

  useEffect(() => {
    loadInventory();
  }, []);

  const loadInventory = async () => {
    try {
      const response = await inventoryApi.getInventory();
      setItems(response.data);
    } catch (error) {
      console.error('Failed to load inventory:', error);
    } finally {
      setLoading(false);
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
    : items.filter(item => item.item?.type === selectedCategory);

  if (loading) {
    return <div className="inventory loading">Загрузка...</div>;
  }

  return (
    <div className="inventory">
      <h1>🎒 Инвентарь</h1>
      
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

      {/* Items Grid */}
      <div className="items-grid">
        {filteredItems.length === 0 ? (
          <div className="empty">Нет предметов</div>
        ) : (
          filteredItems.map((item, index) => (
            <motion.div
              key={item.id}
              className="item-card"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <div className="item-icon">📦</div>
              <div className="item-info">
                <h3>{item.item?.name}</h3>
                <p>{item.item?.description}</p>
              </div>
              <div className="item-quantity">x{item.quantity}</div>
              {item.is_equipped && <div className="equipped-badge">👕</div>}
            </motion.div>
          ))
        )}
      </div>
    </div>
  );
};

export default Inventory;
