import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth-storage');
    if (token) {
      try {
        const parsed = JSON.parse(token);
        if (parsed.state?.token) {
          config.headers.Authorization = `Bearer ${parsed.state.token}`;
        }
      } catch (e) {
        // Ignore parse errors
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      localStorage.removeItem('auth-storage');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

// Pet API
export const petApi = {
  getPets: () => api.get('/pets'),
  getActivePet: () => api.get('/pets/active'),
  createPet: (data: any) => api.post('/pets', data),
  feedPet: (petId: number) => api.post(`/pets/${petId}/feed`),
  petPet: (petId: number) => api.post(`/pets/${petId}/pet`),
  playWithPet: (petId: number) => api.post(`/pets/${petId}/play`),
  sleepPet: (petId: number) => api.post(`/pets/${petId}/sleep`),
  wakePet: (petId: number) => api.post(`/pets/${petId}/wake`),
};

// Inventory API
export const inventoryApi = {
  getInventory: () => api.get('/inventory'),
  useItem: (data: any) => api.post('/inventory/use', data),
  equipItem: (itemId: number, petId?: number) => 
    api.post(`/inventory/equip/${itemId}`, { pet_id: petId }),
};

// Shop API
export const shopApi = {
  getItems: (category?: string) => api.get('/shop/items', { params: { item_type: category } }),
  buyItem: (itemId: number, quantity: number = 1) => 
    api.post('/shop/buy', { item_id: itemId, quantity }),
};

// Games API
export const gamesApi = {
  submitResult: (data: any) => api.post('/games/result', data),
  getLeaderboard: (gameType: string) => api.get(`/games/leaderboard/${gameType}`),
};

// Friends API
export const friendsApi = {
  getFriends: () => api.get('/friends'),
  getRequests: () => api.get('/friends/requests'),
  sendRequest: (friendId: number, message?: string) => 
    api.post('/friends/request', { friend_id: friendId, message }),
  acceptRequest: (requestId: number) => api.post(`/friends/accept/${requestId}`),
  declineRequest: (requestId: number) => api.post(`/friends/decline/${requestId}`),
};

// Battles API
export const battlesApi = {
  getBattles: (status?: string) => api.get('/battles', { params: { status } }),
  createBattle: (data: any) => api.post('/battles', data),
  getBattle: (battleId: number) => api.get(`/battles/${battleId}`),
  makeMove: (battleId: number, moveType: string) => 
    api.post(`/battles/${battleId}/move`, { move_type: moveType }),
};

// Quests API
export const questsApi = {
  getQuests: () => api.get('/quests'),
  getAvailable: () => api.get('/quests/available'),
  acceptQuest: (questId: number) => api.post(`/quests/${questId}/accept`),
  claimReward: (questId: number) => api.post(`/quests/${questId}/claim`),
};

// Achievements API
export const achievementsApi = {
  getAchievements: () => api.get('/achievements'),
  getAll: () => api.get('/achievements/all'),
  claimReward: (achievementId: number) => api.post(`/achievements/${achievementId}/claim`),
};

// Leaderboard API
export const leaderboardApi = {
  getBattleLeaderboard: (limit?: number) => api.get('/leaderboard/battles', { params: { limit } }),
  getQuestLeaderboard: (limit?: number) => api.get('/leaderboard/quests', { params: { limit } }),
  getRichest: (limit?: number) => api.get('/leaderboard/richest', { params: { limit } }),
};

// Breeding API
export const breedingApi = {
  getRequests: () => api.get('/breeding/requests'),
  createRequest: (data: any) => api.post('/breeding/request', data),
  acceptRequest: (requestId: number) => api.post(`/breeding/accept/${requestId}`),
  completeBreeding: (requestId: number) => api.post(`/breeding/complete/${requestId}`),
};

// Market API
export const marketApi = {
  getListings: (itemId?: number) => api.get('/market/listings', { params: { item_id: itemId } }),
  createListing: (data: any) => api.post('/market/listings', data),
  buyListing: (listingId: number) => api.post('/market/buy', { listing_id: listingId }),
  getMyListings: () => api.get('/market/my-listings'),
};
