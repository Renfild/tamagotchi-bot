import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { marketApi } from '../api/client';
import './Market.css';

interface Listing {
  id: number;
  item: {
    name: string;
    description: string;
  };
  quantity: number;
  price: {
    coins: number;
    crystals: number;
  };
  seller: {
    name: string;
  };
}

const Market: React.FC = () => {
  const [listings, setListings] = useState<Listing[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadListings();
  }, []);

  const loadListings = async () => {
    try {
      const response = await marketApi.getListings();
      setListings(response.data);
    } catch (error) {
      console.error('Failed to load listings:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="market loading">Загрузка...</div>;
  }

  return (
    <div className="market">
      <h1>🏪 Рынок</h1>
      
      <div className="market-actions">
        <button className="sell-btn">➕ Продать предмет</button>
      </div>

      <div className="listings">
        {listings.length === 0 ? (
          <div className="empty">Нет активных листингов</div>
        ) : (
          listings.map((listing, index) => (
            <motion.div
              key={listing.id}
              className="listing-card"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <div className="listing-icon">📦</div>
              <div className="listing-info">
                <h3>{listing.item.name}</h3>
                <p>{listing.item.description}</p>
                <span className="seller">Продавец: {listing.seller.name}</span>
              </div>
              <div className="listing-price">
                <span className="quantity">x{listing.quantity}</span>
                {listing.price.coins > 0 && (
                  <span className="price coins">🪙 {listing.price.coins}</span>
                )}
                {listing.price.crystals > 0 && (
                  <span className="price crystals">💎 {listing.price.crystals}</span>
                )}
              </div>
              <button className="buy-btn">Купить</button>
            </motion.div>
          ))
        )}
      </div>
    </div>
  );
};

export default Market;
