import { create } from 'zustand';
import { petApi } from '../api/client';

interface PetStats {
  hunger: number;
  happiness: number;
  health: number;
  energy: number;
  hygiene: number;
}

interface BattleStats {
  attack: number;
  defense: number;
  speed: number;
  max_hp: number;
}

interface Pet {
  id: number;
  name: string;
  pet_type: string;
  rarity: string;
  personality: string;
  level: number;
  experience: number;
  exp_to_next_level: number;
  exp_progress_percent: number;
  evolution_stage: string;
  stats: PetStats;
  battle_stats: BattleStats;
  status: string;
  is_favorite: boolean;
  appearance: {
    primary_color: string;
    secondary_color: string;
    eye_color: string;
    pattern: string;
  };
  images: {
    full?: string;
    thumbnail?: string;
  };
  age_days: number;
  can_battle: boolean;
  can_breed: boolean;
  is_alive: boolean;
}

interface PetState {
  pets: Pet[];
  activePet: Pet | null;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  fetchPets: () => Promise<void>;
  fetchActivePet: () => Promise<void>;
  createPet: (data: any) => Promise<void>;
  feedPet: (petId: number) => Promise<void>;
  petPet: (petId: number) => Promise<void>;
  playWithPet: (petId: number) => Promise<void>;
  sleepPet: (petId: number) => Promise<void>;
  wakePet: (petId: number) => Promise<void>;
  updatePet: (petId: number, data: Partial<Pet>) => void;
}

export const usePetStore = create<PetState>((set, get) => ({
  pets: [],
  activePet: null,
  isLoading: false,
  error: null,

  fetchPets: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await petApi.getPets();
      set({ pets: response.data, isLoading: false });
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
    }
  },

  fetchActivePet: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await petApi.getActivePet();
      set({ activePet: response.data, isLoading: false });
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
    }
  },

  createPet: async (data) => {
    set({ isLoading: true, error: null });
    try {
      const response = await petApi.createPet(data);
      const newPet = response.data;
      set(state => ({
        pets: [...state.pets, newPet],
        activePet: state.activePet || newPet,
        isLoading: false,
      }));
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
    }
  },

  feedPet: async (petId) => {
    try {
      const response = await petApi.feedPet(petId);
      const { hunger_after, leveled_up, new_level } = response.data;
      
      set(state => {
        const updatePet = (pet: Pet) => {
          if (pet.id !== petId) return pet;
          return {
            ...pet,
            stats: { ...pet.stats, hunger: hunger_after },
            level: leveled_up ? new_level : pet.level,
          };
        };
        
        return {
          pets: state.pets.map(updatePet),
          activePet: state.activePet ? updatePet(state.activePet) : null,
        };
      });
    } catch (error: any) {
      set({ error: error.message });
    }
  },

  petPet: async (petId) => {
    try {
      const response = await petApi.petPet(petId);
      const { happiness_after } = response.data;
      
      set(state => {
        const updatePet = (pet: Pet) => {
          if (pet.id !== petId) return pet;
          return {
            ...pet,
            stats: { ...pet.stats, happiness: happiness_after },
          };
        };
        
        return {
          pets: state.pets.map(updatePet),
          activePet: state.activePet ? updatePet(state.activePet) : null,
        };
      });
    } catch (error: any) {
      set({ error: error.message });
    }
  },

  playWithPet: async (petId) => {
    try {
      const response = await petApi.playWithPet(petId);
      const { happiness_after, energy_after, leveled_up, new_level } = response.data;
      
      set(state => {
        const updatePet = (pet: Pet) => {
          if (pet.id !== petId) return pet;
          return {
            ...pet,
            stats: {
              ...pet.stats,
              happiness: happiness_after,
              energy: energy_after,
            },
            level: leveled_up ? new_level : pet.level,
          };
        };
        
        return {
          pets: state.pets.map(updatePet),
          activePet: state.activePet ? updatePet(state.activePet) : null,
        };
      });
    } catch (error: any) {
      set({ error: error.message });
    }
  },

  sleepPet: async (petId) => {
    try {
      const response = await petApi.sleepPet(petId);
      const { sleep_until } = response.data;
      
      set(state => {
        const updatePet = (pet: Pet) => {
          if (pet.id !== petId) return pet;
          return {
            ...pet,
            status: 'sleeping',
          };
        };
        
        return {
          pets: state.pets.map(updatePet),
          activePet: state.activePet ? updatePet(state.activePet) : null,
        };
      });
    } catch (error: any) {
      set({ error: error.message });
    }
  },

  wakePet: async (petId) => {
    try {
      const response = await petApi.wakePet(petId);
      const { energy } = response.data;
      
      set(state => {
        const updatePet = (pet: Pet) => {
          if (pet.id !== petId) return pet;
          return {
            ...pet,
            status: 'active',
            stats: { ...pet.stats, energy },
          };
        };
        
        return {
          pets: state.pets.map(updatePet),
          activePet: state.activePet ? updatePet(state.activePet) : null,
        };
      });
    } catch (error: any) {
      set({ error: error.message });
    }
  },

  updatePet: (petId, data) => {
    set(state => {
      const updatePet = (pet: Pet) => {
        if (pet.id !== petId) return pet;
        return { ...pet, ...data };
      };
      
      return {
        pets: state.pets.map(updatePet),
        activePet: state.activePet ? updatePet(state.activePet) : null,
      };
    });
  },
}));
