import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { usePetStore } from '../store/petStore';
import { useTelegram } from '../hooks/useTelegram';
import './PetGenerator.css';

const PET_TYPES = [
  { id: 'cat', emoji: '🐱', name: 'Кошка' },
  { id: 'dog', emoji: '🐶', name: 'Собака' },
  { id: 'rabbit', emoji: '🐰', name: 'Кролик' },
  { id: 'fox', emoji: '🦊', name: 'Лиса' },
  { id: 'dragon', emoji: '🐲', name: 'Дракон' },
  { id: 'unicorn', emoji: '🦄', name: 'Единорог' },
];

const PERSONALITIES = [
  { id: 'playful', name: 'Игривый', emoji: '🎮' },
  { id: 'lazy', name: 'Ленивый', emoji: '😴' },
  { id: 'affectionate', name: 'Ласковый', emoji: '🥰' },
  { id: 'brave', name: 'Храбрый', emoji: '🦁' },
  { id: 'clever', name: 'Умный', emoji: '🧠' },
];

const PetGenerator: React.FC = () => {
  const navigate = useNavigate();
  const { createPet } = usePetStore();
  const { hapticImpact } = useTelegram();
  
  const [step, setStep] = useState(1);
  const [petData, setPetData] = useState({
    name: '',
    pet_type: '',
    personality: 'playful',
    primary_color: '#FF6B6B',
  });
  const [isGenerating, setIsGenerating] = useState(false);

  const handleTypeSelect = (type: string) => {
    hapticImpact('light');
    setPetData(prev => ({ ...prev, pet_type: type }));
    setStep(2);
  };

  const handlePersonalitySelect = (personality: string) => {
    hapticImpact('light');
    setPetData(prev => ({ ...prev, personality }));
    setStep(3);
  };

  const handleNameSubmit = async () => {
    if (!petData.name.trim()) return;
    
    hapticImpact('medium');
    setIsGenerating(true);
    
    // Simulate generation delay
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    await createPet({
      name: petData.name,
      pet_type: petData.pet_type,
      personality: petData.personality,
      primary_color: petData.primary_color,
    });
    
    setIsGenerating(false);
    navigate('/pet');
  };

  return (
    <div className="pet-generator">
      <AnimatePresence mode="wait">
        {step === 1 && (
          <motion.div
            key="step1"
            className="step"
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -50 }}
          >
            <h2>Выберите вид питомца</h2>
            <div className="type-grid">
              {PET_TYPES.map(type => (
                <motion.button
                  key={type.id}
                  className="type-card"
                  onClick={() => handleTypeSelect(type.id)}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <span className="emoji">{type.emoji}</span>
                  <span className="name">{type.name}</span>
                </motion.button>
              ))}
            </div>
          </motion.div>
        )}

        {step === 2 && (
          <motion.div
            key="step2"
            className="step"
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -50 }}
          >
            <button className="back-btn" onClick={() => setStep(1)}>←</button>
            <h2>Выберите характер</h2>
            <div className="personality-list">
              {PERSONALITIES.map(p => (
                <motion.button
                  key={p.id}
                  className="personality-card"
                  onClick={() => handlePersonalitySelect(p.id)}
                  whileTap={{ scale: 0.98 }}
                >
                  <span className="emoji">{p.emoji}</span>
                  <span className="name">{p.name}</span>
                </motion.button>
              ))}
            </div>
          </motion.div>
        )}

        {step === 3 && (
          <motion.div
            key="step3"
            className="step"
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -50 }}
          >
            <button className="back-btn" onClick={() => setStep(2)}>←</button>
            <h2>Дайте имя питомцу</h2>
            <div className="name-input-container">
              <input
                type="text"
                value={petData.name}
                onChange={(e) => setPetData(prev => ({ ...prev, name: e.target.value }))}
                placeholder="Введите имя..."
                maxLength={20}
                className="name-input"
              />
              <motion.button
                className="create-btn"
                onClick={handleNameSubmit}
                disabled={!petData.name.trim() || isGenerating}
                whileTap={{ scale: 0.95 }}
              >
                {isGenerating ? (
                  <span className="spinner"></span>
                ) : (
                  'Создать питомца'
                )}
              </motion.button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Progress indicator */}
      <div className="progress-dots">
        {[1, 2, 3].map(i => (
          <span key={i} className={step >= i ? 'active' : ''} />
        ))}
      </div>
    </div>
  );
};

export default PetGenerator;
