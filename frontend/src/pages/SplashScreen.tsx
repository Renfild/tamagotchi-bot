import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuthStore } from '../store/authStore';
import { usePetStore } from '../store/petStore';
import './SplashScreen.css';

const SplashScreen: React.FC = () => {
  const navigate = useNavigate();
  const { isAuthenticated, isLoading } = useAuthStore();
  const { activePet, fetchActivePet } = usePetStore();

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      fetchActivePet().then(() => {
        // Redirect after a short delay to show splash
        setTimeout(() => {
          if (activePet) {
            navigate('/pet');
          } else {
            navigate('/create');
          }
        }, 2000);
      });
    }
  }, [isAuthenticated, isLoading, navigate, fetchActivePet, activePet]);

  return (
    <div className="splash-screen">
      <motion.div
        className="splash-content"
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
      >
        <motion.div
          className="logo"
          animate={{ 
            y: [0, -20, 0],
            rotate: [0, 5, -5, 0]
          }}
          transition={{ 
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        >
          🐾
        </motion.div>
        
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          Tamagotchi
        </motion.h1>
        
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          Ваш виртуальный питомец
        </motion.p>
        
        <motion.div
          className="loading-dots"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.7 }}
        >
          <span></span>
          <span></span>
          <span></span>
        </motion.div>
      </motion.div>
    </div>
  );
};

export default SplashScreen;
