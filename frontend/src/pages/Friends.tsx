import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { friendsApi } from '../api/client';
import './Friends.css';

interface Friend {
  id: number;
  username?: string;
  first_name: string;
  avatar?: string;
}

const Friends: React.FC = () => {
  const [friends, setFriends] = useState<Friend[]>([]);
  const [requests, setRequests] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'friends' | 'requests'>('friends');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [friendsRes, requestsRes] = await Promise.all([
        friendsApi.getFriends(),
        friendsApi.getRequests(),
      ]);
      setFriends(friendsRes.data);
      setRequests(requestsRes.data);
    } catch (error) {
      console.error('Failed to load friends:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAccept = async (requestId: number) => {
    try {
      await friendsApi.acceptRequest(requestId);
      loadData();
    } catch (error) {
      console.error('Failed to accept request:', error);
    }
  };

  if (loading) {
    return <div className="friends loading">Загрузка...</div>;
  }

  return (
    <div className="friends">
      <h1>👥 Друзья</h1>
      
      {/* Tabs */}
      <div className="tabs">
        <button 
          className={activeTab === 'friends' ? 'active' : ''}
          onClick={() => setActiveTab('friends')}
        >
          Друзья ({friends.length})
        </button>
        <button 
          className={activeTab === 'requests' ? 'active' : ''}
          onClick={() => setActiveTab('requests')}
        >
          Заявки ({requests.length})
        </button>
      </div>

      {/* Content */}
      {activeTab === 'friends' ? (
        <div className="friends-list">
          {friends.length === 0 ? (
            <div className="empty">У вас пока нет друзей</div>
          ) : (
            friends.map((friend, index) => (
              <motion.div
                key={friend.id}
                className="friend-card"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
              >
                <div className="friend-avatar">👤</div>
                <div className="friend-info">
                  <h3>{friend.first_name}</h3>
                  {friend.username && <p>@{friend.username}</p>}
                </div>
              </motion.div>
            ))
          )}
        </div>
      ) : (
        <div className="requests-list">
          {requests.length === 0 ? (
            <div className="empty">Нет новых заявок</div>
          ) : (
            requests.map((request, index) => (
              <motion.div
                key={request.id}
                className="request-card"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
              >
                <div className="request-info">
                  <h3>{request.first_name}</h3>
                  {request.message && <p>{request.message}</p>}
                </div>
                <div className="request-actions">
                  <button 
                    className="accept-btn"
                    onClick={() => handleAccept(request.id)}
                  >
                    ✓
                  </button>
                  <button className="decline-btn">✕</button>
                </div>
              </motion.div>
            ))
          )}
        </div>
      )}
    </div>
  );
};

export default Friends;
