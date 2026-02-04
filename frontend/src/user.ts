export interface User {
  id: number;
  first_name?: string;
  last_name?: string;
  username?: string;
  language_code?: string;
  coins?: number;
  crystals?: number;
  is_premium?: boolean;
  stats?: {
    battles_won?: number;
    quests_completed?: number;
    pets_created?: number;
    wins?: number;
    quests?: number;
    level?: number;
    experience?: number;
  };
}