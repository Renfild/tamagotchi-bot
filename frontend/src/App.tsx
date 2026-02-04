import React, { useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import { useTelegram } from './hooks/useTelegram';
import { useAuthStore } from './store/authStore';

// Pages
import SplashScreen from './pages/SplashScreen';
import PetGenerator from './pages/PetGenerator';
import PetHub from './pages/PetHub';
import Inventory from './pages/Inventory';
import Shop from './pages/Shop';
import Games from './pages/Games';
import Friends from './pages/Friends';
import Arena from './pages/Arena';
import Quests from './pages/Quests';
import Achievements from './pages/Achievements';
import Settings from './pages/Settings';
import Breeding from './pages/Breeding';
import Market from './pages/Market';

// Components
import BottomNav from './components/BottomNav';
import LoadingScreen from './components/LoadingScreen';

import './App.css';

function App() {
  const { initData, isReady } = useTelegram();
  const { isAuthenticated, isLoading, checkAuth } = useAuthStore();

  useEffect(() => {
    if (initData) {
      checkAuth(initData);
    }
  }, [initData, checkAuth]);

  if (!isReady || isLoading) {
    return <LoadingScreen />;
  }

  return (
    <div className="app">
      <main className="main-content">
        <Routes>
          <Route path="/" element={<SplashScreen />} />
          <Route path="/create" element={<PetGenerator />} />
          <Route path="/pet" element={<PetHub />} />
          <Route path="/inventory" element={<Inventory />} />
          <Route path="/shop" element={<Shop />} />
          <Route path="/games" element={<Games />} />
          <Route path="/friends" element={<Friends />} />
          <Route path="/arena" element={<Arena />} />
          <Route path="/quests" element={<Quests />} />
          <Route path="/achievements" element={<Achievements />} />
          <Route path="/breeding" element={<Breeding />} />
          <Route path="/market" element={<Market />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </main>
      {isAuthenticated && <BottomNav />}
    </div>
  );
}

export default App;
