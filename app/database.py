import asyncpg
import asyncio
import random
import string
from typing import Optional, List, Dict, Any
from app.config import settings


class Database:
    def __init__(self):
        self.pool = None
    
    async def connect(self):
        """Create connection pool to the database"""
        self.pool = await asyncpg.create_pool(settings.DATABASE_URL)
    
    async def disconnect(self):
        """Close the connection pool"""
        if self.pool:
            await self.pool.close()
    
    async def init_db(self):
        """Initialize database and create tables"""
        await self.connect()
        await self.create_tables()
    
    async def create_tables(self):
        """Create database tables"""
        async with self.pool.acquire() as conn:
            # Users table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    telegram_id BIGINT UNIQUE NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    username VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Couples table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS couples (
                    id SERIAL PRIMARY KEY,
                    user1_id INTEGER REFERENCES users(id),
                    user2_id INTEGER REFERENCES users(id),
                    invite_code VARCHAR(6) UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Ideas table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS ideas (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    category VARCHAR(100) NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Date events table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS date_events (
                    id SERIAL PRIMARY KEY,
                    couple_id INTEGER REFERENCES couples(id),
                    idea_id INTEGER REFERENCES ideas(id),
                    proposer_id INTEGER REFERENCES users(id),
                    date_status VARCHAR(20) DEFAULT 'pending',
                    scheduled_date TIMESTAMP,
                    completed_date TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Populate initial ideas if table is empty
            count = await conn.fetchval('SELECT COUNT(*) FROM ideas')
            if count == 0:
                await self.populate_initial_ideas(conn)
    
    async def populate_initial_ideas(self, conn):
        """Populate initial date ideas"""
        initial_ideas = [
            ("Романтический ужин при свечах", "Приготовьте ужин дома при свечах с любимой музыкой", "романтика"),
            ("Прогулка в парке", "Неспешная прогулка по красивому парку или скверу", "активность"),
            ("Домашний кинотеатр", "Посмотрите фильм дома с попкорном и уютной атмосферой", "дом"),
            ("Посещение музея", "Сходите в местный музей или галерею", "культура"),
            ("Пикник на природе", "Организуйте пикник в живописном месте", "активность"),
            ("Кулинарный мастер-класс дома", "Готовьте новое блюдо вместе", "дом"),
            ("Концерт или театр", "Сходите на живое выступление", "культура"),
            ("Спа-день дома", "Устройте релаксирующий день дома с масками и массажем", "релакс"),
            ("Фотосессия", "Сделайте красивые фотографии друг друга", "творчество"),
            ("Ужин в ресторане", "Попробуйте новую кухню в хорошем ресторане", "ресторан"),
            ("Настольные игры", "Проведите вечер за любимыми настольными играми", "дом"),
            ("Велопрогулка", "Покатайтесь на велосипедах по городу или парку", "активность"),
            ("Кулинарные эксперименты", "Попробуйте приготовить блюдо новой кухни", "дом"),
            ("Танцевальный вечер", "Устройте танцы дома под любимую музыку", "романтика"),
            ("Книжный клуб на двоих", "Читайте одну книгу и обсуждайте", "культура"),
            ("Йога вместе", "Занимайтесь йогой или медитацией", "релакс")
        ]
        
        for title, description, category in initial_ideas:
            await conn.execute(
                "INSERT INTO ideas (title, description, category) VALUES ($1, $2, $3)",
                title, description, category
            )
    
    # Users methods
    async def create_user(self, telegram_id: int, name: str, username: str = None) -> Optional[Dict[str, Any]]:
        """Create a new user"""
        async with self.pool.acquire() as conn:
            try:
                user_id = await conn.fetchval(
                    "INSERT INTO users (telegram_id, name, username) VALUES ($1, $2, $3) RETURNING id",
                    telegram_id, name, username
                )
                return await self.get_user_by_id(user_id)
            except asyncpg.UniqueViolationError:
                return None
    
    async def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM users WHERE id = $1",
                user_id
            )
            return dict(row) if row else None
    
    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """Get user by Telegram ID"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM users WHERE telegram_id = $1",
                telegram_id
            )
            return dict(row) if row else None
    
    async def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM users ORDER BY created_at DESC")
            return [dict(row) for row in rows]
    
    # Couples methods
    def generate_invite_code(self) -> str:
        """Generate a unique invite code"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    async def create_couple(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Create a new couple and return the invite code"""
        async with self.pool.acquire() as conn:
            # Check if user is already in a couple
            existing_couple = await conn.fetchrow(
                "SELECT * FROM couples WHERE user1_id = $1 OR user2_id = $1",
                user_id
            )
            if existing_couple:
                return None
            
            invite_code = self.generate_invite_code()
            # Ensure unique invite code
            while await conn.fetchval("SELECT id FROM couples WHERE invite_code = $1", invite_code):
                invite_code = self.generate_invite_code()
            
            couple_id = await conn.fetchval(
                "INSERT INTO couples (user1_id, invite_code) VALUES ($1, $2) RETURNING id",
                user_id, invite_code
            )
            return await self.get_couple_by_id(couple_id)
    
    async def join_couple(self, user_id: int, invite_code: str) -> Optional[Dict[str, Any]]:
        """Join an existing couple using invite code"""
        async with self.pool.acquire() as conn:
            # Check if user is already in a couple
            existing_couple = await conn.fetchrow(
                "SELECT * FROM couples WHERE user1_id = $1 OR user2_id = $1",
                user_id
            )
            if existing_couple:
                return None
            
            # Check if invite code exists and couple is not full
            couple = await conn.fetchrow(
                "SELECT * FROM couples WHERE invite_code = $1 AND user2_id IS NULL",
                invite_code
            )
            if not couple or couple['user1_id'] == user_id:
                return None
            
            await conn.execute(
                "UPDATE couples SET user2_id = $1 WHERE invite_code = $2",
                user_id, invite_code
            )
            return await self.get_couple_by_id(couple['id'])
    
    async def get_couple_by_id(self, couple_id: int) -> Optional[Dict[str, Any]]:
        """Get couple by ID"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM couples WHERE id = $1",
                couple_id
            )
            return dict(row) if row else None
    
    async def get_couple_by_user_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get couple by user ID"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM couples WHERE user1_id = $1 OR user2_id = $1",
                user_id
            )
            return dict(row) if row else None
    
    # Ideas methods
    async def create_idea(self, title: str, description: str, category: str) -> Optional[Dict[str, Any]]:
        """Create a new idea"""
        async with self.pool.acquire() as conn:
            idea_id = await conn.fetchval(
                "INSERT INTO ideas (title, description, category) VALUES ($1, $2, $3) RETURNING id",
                title, description, category
            )
            return await self.get_idea_by_id(idea_id)
    
    async def get_idea_by_id(self, idea_id: int) -> Optional[Dict[str, Any]]:
        """Get idea by ID"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM ideas WHERE id = $1",
                idea_id
            )
            return dict(row) if row else None
    
    async def get_all_ideas(self) -> List[Dict[str, Any]]:
        """Get all active ideas"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM ideas WHERE is_active = TRUE ORDER BY created_at DESC"
            )
            return [dict(row) for row in rows]
    
    async def update_idea(self, idea_id: int, title: str = None, description: str = None, 
                         category: str = None, is_active: bool = None) -> Optional[Dict[str, Any]]:
        """Update an idea"""
        async with self.pool.acquire() as conn:
            updates = []
            values = []
            param_count = 1
            
            if title is not None:
                updates.append(f"title = ${param_count}")
                values.append(title)
                param_count += 1
            
            if description is not None:
                updates.append(f"description = ${param_count}")
                values.append(description)
                param_count += 1
            
            if category is not None:
                updates.append(f"category = ${param_count}")
                values.append(category)
                param_count += 1
            
            if is_active is not None:
                updates.append(f"is_active = ${param_count}")
                values.append(is_active)
                param_count += 1
            
            if not updates:
                return await self.get_idea_by_id(idea_id)
            
            values.append(idea_id)
            query = f"UPDATE ideas SET {', '.join(updates)} WHERE id = ${param_count} RETURNING id"
            
            updated_id = await conn.fetchval(query, *values)
            return await self.get_idea_by_id(updated_id) if updated_id else None
    
    async def delete_idea(self, idea_id: int) -> bool:
        """Delete an idea"""
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM ideas WHERE id = $1",
                idea_id
            )
            return result != "DELETE 0"
    
    # Date events methods
    async def create_date_proposal(self, couple_id: int, idea_id: int, proposer_id: int) -> Optional[Dict[str, Any]]:
        """Create a date proposal"""
        async with self.pool.acquire() as conn:
            event_id = await conn.fetchval(
                "INSERT INTO date_events (couple_id, idea_id, proposer_id) VALUES ($1, $2, $3) RETURNING id",
                couple_id, idea_id, proposer_id
            )
            return await self.get_date_event_by_id(event_id)
    
    async def respond_to_date_proposal(self, event_id: int, response: str) -> Optional[Dict[str, Any]]:
        """Respond to a date proposal"""
        async with self.pool.acquire() as conn:
            updated_id = await conn.fetchval(
                "UPDATE date_events SET date_status = $1 WHERE id = $2 AND date_status = 'pending' RETURNING id",
                response, event_id
            )
            return await self.get_date_event_by_id(updated_id) if updated_id else None
    
    async def get_date_event_by_id(self, event_id: int) -> Optional[Dict[str, Any]]:
        """Get date event by ID"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT de.*, i.title as idea_title, i.description as idea_description,
                       u.name as proposer_name
                FROM date_events de
                JOIN ideas i ON de.idea_id = i.id
                JOIN users u ON de.proposer_id = u.id
                WHERE de.id = $1
                """,
                event_id
            )
            return dict(row) if row else None
    
    async def get_date_history(self, couple_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get date history for a couple"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT de.*, i.title as idea_title, i.description as idea_description,
                       u.name as proposer_name
                FROM date_events de
                JOIN ideas i ON de.idea_id = i.id
                JOIN users u ON de.proposer_id = u.id
                WHERE de.couple_id = $1
                ORDER BY de.created_at DESC
                LIMIT $2
                """,
                couple_id, limit
            )
            return [dict(row) for row in rows]


# Global database instance
db = Database()