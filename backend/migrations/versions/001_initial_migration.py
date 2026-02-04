"""Initial migration - create all tables

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('username', sa.String(length=32), nullable=True),
        sa.Column('first_name', sa.String(length=64), nullable=False),
        sa.Column('last_name', sa.String(length=64), nullable=True),
        sa.Column('language_code', sa.String(length=10), nullable=True),
        sa.Column('avatar_url', sa.String(length=512), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('coins', sa.Integer(), nullable=False, server_default='100'),
        sa.Column('crystals', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('arena_tokens', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_premium', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('premium_expires_at', sa.DateTime(), nullable=True),
        sa.Column('total_playtime_minutes', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('battles_won', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('battles_lost', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('quests_completed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('pets_created', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('language', sa.Enum('RUSSIAN', 'ENGLISH', 'SPANISH', 'GERMAN', 'FRENCH', name='language'), nullable=False, server_default='RUSSIAN'),
        sa.Column('notifications', sa.Enum('ALL', 'IMPORTANT', 'NONE', name='notificationlevel'), nullable=False, server_default='ALL'),
        sa.Column('privacy', sa.Enum('PUBLIC', 'FRIENDS_ONLY', 'PRIVATE', name='privacylevel'), nullable=False, server_default='FRIENDS_ONLY'),
        sa.Column('quiet_hours_start', sa.Integer(), nullable=True),
        sa.Column('quiet_hours_end', sa.Integer(), nullable=True),
        sa.Column('can_receive_gifts', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('can_be_invited', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('show_online_status', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_activity_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_daily_claim', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_id', 'users', ['id'])
    op.create_index('ix_users_username', 'users', ['username'])
    
    # Create pets table
    op.create_table(
        'pets',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('owner_id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(length=32), nullable=False),
        sa.Column('pet_type', sa.Enum('CAT', 'DOG', 'RABBIT', 'FOX', 'DRAGON', 'UNICORN', 'PHOENIX', 'ROBOT', 'SLIME', 'CUSTOM', name='pettype'), nullable=False),
        sa.Column('rarity', sa.Enum('COMMON', 'UNCOMMON', 'RARE', 'EPIC', 'LEGENDARY', 'MYTHIC', name='rarity'), nullable=False, server_default='COMMON'),
        sa.Column('personality', sa.Enum('PLAYFUL', 'LAZY', 'AGGRESSIVE', 'AFFECTIONATE', 'MYSTERIOUS', 'BRAVE', 'CLEVER', 'GREEDY', name='personality'), nullable=False, server_default='PLAYFUL'),
        sa.Column('level', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('experience', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('evolution_stage', sa.Enum('BABY', 'CHILD', 'TEEN', 'ADULT', 'ELITE', 'MASTER', name='evolutionstage'), nullable=False, server_default='BABY'),
        sa.Column('evolution_branch', sa.String(length=32), nullable=True),
        sa.Column('hunger', sa.Integer(), nullable=False, server_default='80'),
        sa.Column('happiness', sa.Integer(), nullable=False, server_default='50'),
        sa.Column('health', sa.Integer(), nullable=False, server_default='100'),
        sa.Column('energy', sa.Integer(), nullable=False, server_default='100'),
        sa.Column('hygiene', sa.Integer(), nullable=False, server_default='100'),
        sa.Column('attack', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('defense', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('speed', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('max_hp', sa.Integer(), nullable=False, server_default='100'),
        sa.Column('status', sa.Enum('ACTIVE', 'SLEEPING', 'SICK', 'DEPRESSED', 'RUNAWAY', 'DECEASED', 'IN_STORAGE', name='petstatus'), nullable=False, server_default='ACTIVE'),
        sa.Column('is_favorite', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('primary_color', sa.String(length=7), nullable=False, server_default='#FF6B6B'),
        sa.Column('secondary_color', sa.String(length=7), nullable=False, server_default='#4ECDC4'),
        sa.Column('eye_color', sa.String(length=7), nullable=False, server_default='#000000'),
        sa.Column('pattern', sa.String(length=32), nullable=False, server_default='solid'),
        sa.Column('accessories', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('image_url', sa.String(length=512), nullable=True),
        sa.Column('thumbnail_url', sa.String(length=512), nullable=True),
        sa.Column('animation_data', sa.JSON(), nullable=True),
        sa.Column('custom_description', sa.Text(), nullable=True),
        sa.Column('sleep_until', sa.DateTime(), nullable=True),
        sa.Column('last_fed_at', sa.DateTime(), nullable=True),
        sa.Column('last_played_at', sa.DateTime(), nullable=True),
        sa.Column('last_petted_at', sa.DateTime(), nullable=True),
        sa.Column('breeding_cooldown_until', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('born_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_pets_id', 'pets', ['id'])
    op.create_index('ix_pets_owner_id', 'pets', ['owner_id'])
    op.create_index('ix_pets_pet_type', 'pets', ['pet_type'])
    op.create_index('ix_pets_status', 'pets', ['status'])
    op.create_index('idx_pets_owner_status', 'pets', ['owner_id', 'status'])
    op.create_index('idx_pets_level', 'pets', ['level'])
    op.create_index('idx_pets_rarity', 'pets', ['rarity'])
    
    # Create items table
    op.create_table(
        'items',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(length=64), nullable=False, unique=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('item_type', sa.Enum('FOOD', 'TOY', 'MEDICINE', 'CONTAINER', 'CLOTHING', 'DECOR', 'EVOLUTION', 'SPECIAL', name='itemtype'), nullable=False),
        sa.Column('rarity', sa.Enum('COMMON', 'UNCOMMON', 'RARE', 'EPIC', 'LEGENDARY', 'MYTHIC', name='itemrarity'), nullable=False, server_default='COMMON'),
        sa.Column('buy_price_coins', sa.Integer(), nullable=True),
        sa.Column('buy_price_crystals', sa.Integer(), nullable=True),
        sa.Column('sell_price_coins', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_purchasable', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_sellable', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_tradable', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_consumable', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('min_level_required', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('max_stack_size', sa.Integer(), nullable=False, server_default='99'),
        sa.Column('effects', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('icon_url', sa.String(length=512), nullable=True),
        sa.Column('animation_url', sa.String(length=512), nullable=True),
        sa.Column('is_premium_only', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_event_item', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('event_id', sa.String(length=32), nullable=True),
        sa.Column('available_from', sa.String(length=64), nullable=True),
        sa.Column('available_until', sa.String(length=64), nullable=True),
        sa.Column('is_daily_deal', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('daily_deal_discount', sa.Integer(), nullable=False, server_default='0'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_items_item_type', 'items', ['item_type'])
    
    # Create inventory table
    op.create_table(
        'inventory',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('owner_id', sa.BigInteger(), nullable=False),
        sa.Column('item_id', sa.BigInteger(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('is_equipped', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('equipped_on_pet_id', sa.BigInteger(), nullable=True),
        sa.Column('durability', sa.Integer(), nullable=True),
        sa.Column('max_durability', sa.Integer(), nullable=True),
        sa.Column('obtained_from', sa.String(length=32), nullable=False, server_default='unknown'),
        sa.Column('obtained_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('custom_data', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['item_id'], ['items.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['equipped_on_pet_id'], ['pets.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('owner_id', 'item_id', name='uix_inventory_user_item')
    )
    op.create_index('ix_inventory_owner_id', 'inventory', ['owner_id'])
    
    # Create friends table
    op.create_table(
        'friends',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('friend_id', sa.BigInteger(), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'ACCEPTED', 'BLOCKED', 'DECLINED', name='friendstatus'), nullable=False, server_default='PENDING'),
        sa.Column('last_interaction_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('gifts_sent', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('gifts_received', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('battles_together', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('initiated_by', sa.BigInteger(), nullable=False),
        sa.Column('message', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['friend_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'friend_id', name='uix_friendship')
    )
    op.create_index('ix_friends_user_id', 'friends', ['user_id'])
    op.create_index('ix_friends_friend_id', 'friends', ['friend_id'])
    
    # Create battles table
    op.create_table(
        'battles',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('battle_type', sa.Enum('FRIENDLY', 'RANKED', 'BETTING', 'TOURNAMENT', 'GUILD', name='battletype'), nullable=False, server_default='FRIENDLY'),
        sa.Column('player1_id', sa.BigInteger(), nullable=False),
        sa.Column('pet1_id', sa.BigInteger(), nullable=False),
        sa.Column('player2_id', sa.BigInteger(), nullable=False),
        sa.Column('pet2_id', sa.BigInteger(), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'ACTIVE', 'FINISHED', 'CANCELLED', 'EXPIRED', name='battlestatus'), nullable=False, server_default='PENDING'),
        sa.Column('current_turn', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('turn_number', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('time_limit_seconds', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('turn_deadline', sa.DateTime(), nullable=True),
        sa.Column('pet1_current_hp', sa.Integer(), nullable=True),
        sa.Column('pet2_current_hp', sa.Integer(), nullable=True),
        sa.Column('pet1_buffs', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('pet2_buffs', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('battle_log', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('winner_id', sa.BigInteger(), nullable=True),
        sa.Column('winner_pet_id', sa.BigInteger(), nullable=True),
        sa.Column('bet_amount', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('exp_reward', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('coin_reward', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('arena_token_reward', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('player1_rating_change', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('player2_rating_change', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('finished_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['player1_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['player2_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['pet1_id'], ['pets.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['pet2_id'], ['pets.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['winner_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['winner_pet_id'], ['pets.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create battle_moves table
    op.create_table(
        'battle_moves',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('battle_id', sa.BigInteger(), nullable=False),
        sa.Column('turn_number', sa.Integer(), nullable=False),
        sa.Column('player_number', sa.Integer(), nullable=False),
        sa.Column('move_type', sa.Enum('ATTACK', 'DEFEND', 'HEAL', 'BUFF_ATTACK', 'BUFF_DEFENSE', 'BUFF_SPEED', 'SPECIAL', 'SKIP', name='battlemovetype'), nullable=False),
        sa.Column('damage_dealt', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('healing_done', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_critical', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_miss', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('pet1_hp_after', sa.Integer(), nullable=False),
        sa.Column('pet2_hp_after', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['battle_id'], ['battles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_battle_moves_battle_id', 'battle_moves', ['battle_id'])
    
    # Create quests table
    op.create_table(
        'quests',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('title', sa.String(length=128), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('quest_type', sa.Enum('FEED_PET', 'PLAY_GAME', 'PET_PET', 'WIN_BATTLE', 'LEVEL_UP_PET', 'BREED_PET', 'BUY_ITEM', 'USE_ITEM', 'VISIT_FRIEND', 'SEND_GIFT', 'COMPLETE_DAILY', 'PLAY_MINI_GAME', name='questtype'), nullable=False),
        sa.Column('frequency', sa.Enum('DAILY', 'WEEKLY', 'EVENT', 'ONE_TIME', name='questfrequency'), nullable=False, server_default='DAILY'),
        sa.Column('target_count', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('target_item_id', sa.BigInteger(), nullable=True),
        sa.Column('min_level_required', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('reward_coins', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('reward_crystals', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('reward_exp', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('reward_item_id', sa.BigInteger(), nullable=True),
        sa.Column('reward_item_quantity', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('icon_url', sa.String(length=512), nullable=True),
        sa.Column('event_id', sa.String(length=32), nullable=True),
        sa.Column('starts_at', sa.DateTime(), nullable=True),
        sa.Column('ends_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['target_item_id'], ['items.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['reward_item_id'], ['items.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_quests_quest_type', 'quests', ['quest_type'])
    
    # Create user_quests table
    op.create_table(
        'user_quests',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('quest_id', sa.BigInteger(), nullable=False),
        sa.Column('current_progress', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_completed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_claimed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('claimed_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['quest_id'], ['quests.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_user_quests_user_id', 'user_quests', ['user_id'])
    
    # Create achievements table
    op.create_table(
        'achievements',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(length=64), nullable=False, unique=True),
        sa.Column('title', sa.String(length=128), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('category', sa.Enum('GENERAL', 'COLLECTION', 'BATTLE', 'SOCIAL', 'CARE', 'SPECIAL', 'EVENT', name='achievementcategory'), nullable=False, server_default='GENERAL'),
        sa.Column('rarity', sa.Enum('BRONZE', 'SILVER', 'GOLD', 'PLATINUM', 'DIAMOND', name='achievementrarity'), nullable=False, server_default='BRONZE'),
        sa.Column('requirement_type', sa.String(length=32), nullable=False),
        sa.Column('requirement_value', sa.Integer(), nullable=False),
        sa.Column('requirement_data', sa.JSON(), nullable=True),
        sa.Column('reward_coins', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('reward_crystals', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('reward_title', sa.String(length=64), nullable=True),
        sa.Column('icon_url', sa.String(length=512), nullable=True),
        sa.Column('badge_color', sa.String(length=7), nullable=False, server_default='#CD7F32'),
        sa.Column('is_hidden', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('hidden_hint', sa.Text(), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create user_achievements table
    op.create_table(
        'user_achievements',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('achievement_id', sa.BigInteger(), nullable=False),
        sa.Column('progress', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('earned_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_reward_claimed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('claimed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['achievement_id'], ['achievements.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_user_achievements_user_id', 'user_achievements', ['user_id'])
    
    # Create breeding_requests table
    op.create_table(
        'breeding_requests',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('requester_id', sa.BigInteger(), nullable=False),
        sa.Column('pet1_id', sa.BigInteger(), nullable=False),
        sa.Column('recipient_id', sa.BigInteger(), nullable=False),
        sa.Column('pet2_id', sa.BigInteger(), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'ACCEPTED', 'IN_PROGRESS', 'COMPLETED', 'DECLINED', 'CANCELLED', 'EXPIRED', name='breedingstatus'), nullable=False, server_default='PENDING'),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('breeding_duration_hours', sa.Integer(), nullable=False, server_default='24'),
        sa.Column('breeding_started_at', sa.DateTime(), nullable=True),
        sa.Column('breeding_completed_at', sa.DateTime(), nullable=True),
        sa.Column('result_pet_id', sa.BigInteger(), nullable=True),
        sa.Column('inherited_traits', sa.JSON(), nullable=True),
        sa.Column('coins_cost', sa.Integer(), nullable=False, server_default='500'),
        sa.Column('crystals_cost', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('paid_by', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('responded_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['pet1_id'], ['pets.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['pet2_id'], ['pets.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['result_pet_id'], ['pets.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_breeding_requests_requester_id', 'breeding_requests', ['requester_id'])
    op.create_index('ix_breeding_requests_recipient_id', 'breeding_requests', ['recipient_id'])
    
    # Create market_listings table
    op.create_table(
        'market_listings',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('seller_id', sa.BigInteger(), nullable=False),
        sa.Column('item_id', sa.BigInteger(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('price_coins', sa.Integer(), nullable=False),
        sa.Column('price_crystals', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('status', sa.Enum('ACTIVE', 'SOLD', 'CANCELLED', 'EXPIRED', name='marketstatus'), nullable=False, server_default='ACTIVE'),
        sa.Column('notes', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('sold_at', sa.DateTime(), nullable=True),
        sa.Column('buyer_id', sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(['seller_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['buyer_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['item_id'], ['items.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_market_listings_seller_id', 'market_listings', ['seller_id'])
    
    # Create market_transactions table
    op.create_table(
        'market_transactions',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('listing_id', sa.BigInteger(), nullable=True),
        sa.Column('seller_id', sa.BigInteger(), nullable=False),
        sa.Column('buyer_id', sa.BigInteger(), nullable=False),
        sa.Column('item_id', sa.BigInteger(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('price_coins', sa.Integer(), nullable=False),
        sa.Column('price_crystals', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('market_fee_percent', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('market_fee_amount', sa.Integer(), nullable=False),
        sa.Column('seller_received', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_market_transactions_seller_id', 'market_transactions', ['seller_id'])
    op.create_index('ix_market_transactions_buyer_id', 'market_transactions', ['buyer_id'])
    
    # Create guilds table
    op.create_table(
        'guilds',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(length=32), nullable=False, unique=True),
        sa.Column('tag', sa.String(length=4), nullable=False, unique=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('leader_id', sa.BigInteger(), nullable=False),
        sa.Column('level', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('experience', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('max_members', sa.Integer(), nullable=False, server_default='20'),
        sa.Column('treasury_coins', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('emblem_url', sa.String(length=512), nullable=True),
        sa.Column('emblem_color', sa.String(length=7), nullable=False, server_default='#FFD700'),
        sa.Column('is_recruiting', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('min_level_required', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('is_public', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create guild_members table
    op.create_table(
        'guild_members',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('guild_id', sa.BigInteger(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('role', sa.Enum('LEADER', 'OFFICER', 'MEMBER', 'RECRUIT', name='guildrole'), nullable=False, server_default='RECRUIT'),
        sa.Column('total_contributed_coins', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('battles_won', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('quests_completed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_active_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['guild_id'], ['guilds.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_guild_members_guild_id', 'guild_members', ['guild_id'])
    op.create_index('ix_guild_members_user_id', 'guild_members', ['user_id'])


def downgrade() -> None:
    # Drop all tables in reverse order
    op.drop_table('guild_members')
    op.drop_table('guilds')
    op.drop_table('market_transactions')
    op.drop_table('market_listings')
    op.drop_table('breeding_requests')
    op.drop_table('user_achievements')
    op.drop_table('achievements')
    op.drop_table('user_quests')
    op.drop_table('quests')
    op.drop_table('battle_moves')
    op.drop_table('battles')
    op.drop_table('friends')
    op.drop_table('inventory')
    op.drop_table('items')
    op.drop_table('pets')
    op.drop_table('users')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS guildrole')
    op.execute('DROP TYPE IF EXISTS marketstatus')
    op.execute('DROP TYPE IF EXISTS breedingstatus')
    op.execute('DROP TYPE IF EXISTS achievementrarity')
    op.execute('DROP TYPE IF EXISTS achievementcategory')
    op.execute('DROP TYPE IF EXISTS questfrequency')
    op.execute('DROP TYPE IF EXISTS questtype')
    op.execute('DROP TYPE IF EXISTS battlemovetype')
    op.execute('DROP TYPE IF EXISTS battlestatus')
    op.execute('DROP TYPE IF EXISTS battletype')
    op.execute('DROP TYPE IF EXISTS friendstatus')
    op.execute('DROP TYPE IF EXISTS itemrarity')
    op.execute('DROP TYPE IF EXISTS itemtype')
    op.execute('DROP TYPE IF EXISTS petstatus')
    op.execute('DROP TYPE IF EXISTS evolutionstage')
    op.execute('DROP TYPE IF EXISTS personality')
    op.execute('DROP TYPE IF EXISTS rarity')
    op.execute('DROP TYPE IF EXISTS pettype')
    op.execute('DROP TYPE IF EXISTS privacylevel')
    op.execute('DROP TYPE IF EXISTS notificationlevel')
    op.execute('DROP TYPE IF EXISTS language')
