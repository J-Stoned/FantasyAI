"""
Database Manager for Fantasy AI Ultimate merged project
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import os
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import redis.asyncio as redis

logger = logging.getLogger(__name__)

Base = declarative_base()

class PlayerData(Base):
    """Player data table"""
    __tablename__ = "players"
    
    player_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    position = Column(String, nullable=False)
    team = Column(String, nullable=False)
    league_id = Column(String, nullable=False)
    points = Column(Float, default=0.0)
    games_played = Column(Integer, default=0)
    avg_points = Column(Float, default=0.0)
    stats = Column(JSON, default={})
    ai_score = Column(Float, default=0.0)
    trend = Column(String, default="stable")
    risk_level = Column(String, default="low")
    last_updated = Column(DateTime, default=datetime.utcnow)

class LeagueData(Base):
    """League data table"""
    __tablename__ = "leagues"
    
    league_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    sport = Column(String, nullable=False)
    season = Column(Integer, nullable=False)
    num_teams = Column(Integer, default=0)
    scoring_type = Column(String, default="standard")
    draft_type = Column(String, default="snake")
    settings = Column(JSON, default={})
    last_updated = Column(DateTime, default=datetime.utcnow)

class TeamData(Base):
    """Team data table"""
    __tablename__ = "teams"
    
    team_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    owner = Column(String, nullable=False)
    league_id = Column(String, nullable=False)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    ties = Column(Integer, default=0)
    points_for = Column(Float, default=0.0)
    points_against = Column(Float, default=0.0)
    players = Column(JSON, default=[])
    last_updated = Column(DateTime, default=datetime.utcnow)

class AIAnalysisData(Base):
    """AI analysis results table"""
    __tablename__ = "ai_analyses"
    
    id = Column(String, primary_key=True)
    player_id = Column(String, nullable=False)
    analysis_type = Column(String, nullable=False)
    confidence_score = Column(Float, default=0.0)
    prediction = Column(JSON, default={})
    insights = Column(JSON, default=[])
    recommendations = Column(JSON, default=[])
    model_version = Column(String, default="1.0.0")
    analysis_date = Column(DateTime, default=datetime.utcnow)

class DatabaseManager:
    """Database manager for handling data persistence and caching"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self.redis_client = None
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize database connections"""
        # In production, check if DATABASE_URL is provided
        if os.getenv("ENVIRONMENT") == "production" and not os.getenv("DATABASE_URL"):
            logger.warning("Running in production without database - using in-memory mode")
            self.is_initialized = True
            return
            
        try:
            # Initialize PostgreSQL connection
            await self._initialize_postgresql()
            
            # Initialize Redis connection
            await self._initialize_redis()
            
            # Create tables
            await self._create_tables()
            
            self.is_initialized = True
            logger.info("Database Manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Database Manager: {e}")
            # In production, continue without database for OAuth testing
            if os.getenv("ENVIRONMENT") == "production":
                logger.warning("Continuing without database in production mode")
                self.is_initialized = True
            else:
                raise
    
    async def _initialize_postgresql(self):
        """Initialize PostgreSQL connection"""
        try:
            # Get database URL from environment or use default
            database_url = os.getenv(
                "DATABASE_URL",
                "postgresql+asyncpg://user:password@localhost/fantasy_ai_db"
            )
            
            # Create async engine
            self.engine = create_async_engine(
                database_url,
                echo=False,
                pool_pre_ping=True
            )
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                bind=self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            logger.info("PostgreSQL connection initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL: {e}")
            # Fallback to SQLite for development
            await self._initialize_sqlite()
    
    async def _initialize_sqlite(self):
        """Initialize SQLite connection as fallback"""
        try:
            database_url = "sqlite+aiosqlite:///./fantasy_ai.db"
            
            self.engine = create_async_engine(
                database_url,
                echo=False
            )
            
            self.SessionLocal = sessionmaker(
                bind=self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            logger.info("SQLite connection initialized (fallback)")
            
        except Exception as e:
            logger.error(f"Failed to initialize SQLite: {e}")
            raise
    
    async def _initialize_redis(self):
        """Initialize Redis connection for caching"""
        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            self.redis_client = redis.from_url(redis_url)
            
            # Test connection
            await self.redis_client.ping()
            logger.info("Redis connection initialized")
            
        except Exception as e:
            logger.warning(f"Failed to initialize Redis: {e}")
            self.redis_client = None
    
    async def _create_tables(self):
        """Create database tables"""
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created")
            
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise
    
    async def close(self):
        """Close database connections"""
        try:
            if self.engine:
                await self.engine.dispose()
            
            if self.redis_client:
                await self.redis_client.close()
                
            logger.info("Database connections closed")
            
        except Exception as e:
            logger.error(f"Error closing database connections: {e}")
    
    async def save_player_data(self, player_data: Dict[str, Any]):
        """Save player data to database"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            if not self.SessionLocal:
                logger.warning("Database not available - skipping save")
                return
            
            async with self.SessionLocal() as session:
                # Check if player exists
                existing_player = await session.get(PlayerData, player_data['player_id'])
                
                if existing_player:
                    # Update existing player
                    for key, value in player_data.items():
                        if hasattr(existing_player, key):
                            setattr(existing_player, key, value)
                    existing_player.last_updated = datetime.utcnow()
                else:
                    # Create new player
                    new_player = PlayerData(**player_data)
                    session.add(new_player)
                
                await session.commit()
                
                # Update cache
                await self._cache_player_data(player_data['player_id'], player_data)
                
        except Exception as e:
            logger.error(f"Error saving player data: {e}")
            raise
    
    async def get_player_data(self, player_id: str) -> Optional[Dict[str, Any]]:
        """Get player data from database or cache"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            # Try cache first
            cached_data = await self._get_cached_player_data(player_id)
            if cached_data:
                return cached_data
            
            if not self.SessionLocal:
                logger.warning("Database not available - returning None")
                return None
            
            # Get from database
            async with self.SessionLocal() as session:
                player = await session.get(PlayerData, player_id)
                
                if player:
                    player_dict = {
                        'player_id': player.player_id,
                        'name': player.name,
                        'position': player.position,
                        'team': player.team,
                        'league_id': player.league_id,
                        'points': player.points,
                        'games_played': player.games_played,
                        'avg_points': player.avg_points,
                        'stats': player.stats,
                        'ai_score': player.ai_score,
                        'trend': player.trend,
                        'risk_level': player.risk_level,
                        'last_updated': player.last_updated.isoformat()
                    }
                    
                    # Cache the data
                    await self._cache_player_data(player_id, player_dict)
                    
                    return player_dict
                
                return None
                
        except Exception as e:
            logger.error(f"Error getting player data: {e}")
            raise
    
    async def save_league_data(self, league_data: Dict[str, Any]):
        """Save league data to database"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            if not self.SessionLocal:
                logger.warning("Database not available - skipping save")
                return
            
            async with self.SessionLocal() as session:
                existing_league = await session.get(LeagueData, league_data['league_id'])
                
                if existing_league:
                    for key, value in league_data.items():
                        if hasattr(existing_league, key):
                            setattr(existing_league, key, value)
                    existing_league.last_updated = datetime.utcnow()
                else:
                    new_league = LeagueData(**league_data)
                    session.add(new_league)
                
                await session.commit()
                
        except Exception as e:
            logger.error(f"Error saving league data: {e}")
            raise
    
    async def save_team_data(self, team_data: Dict[str, Any]):
        """Save team data to database"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            if not self.SessionLocal:
                logger.warning("Database not available - skipping save")
                return
            
            async with self.SessionLocal() as session:
                existing_team = await session.get(TeamData, team_data['team_id'])
                
                if existing_team:
                    for key, value in team_data.items():
                        if hasattr(existing_team, key):
                            setattr(existing_team, key, value)
                    existing_team.last_updated = datetime.utcnow()
                else:
                    new_team = TeamData(**team_data)
                    session.add(new_team)
                
                await session.commit()
                
        except Exception as e:
            logger.error(f"Error saving team data: {e}")
            raise
    
    async def save_ai_analysis(self, analysis_data: Dict[str, Any]):
        """Save AI analysis results to database"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            if not self.SessionLocal:
                logger.warning("Database not available - skipping save")
                return
            
            async with self.SessionLocal() as session:
                new_analysis = AIAnalysisData(**analysis_data)
                session.add(new_analysis)
                await session.commit()
                
        except Exception as e:
            logger.error(f"Error saving AI analysis: {e}")
            raise
    
    async def _cache_player_data(self, player_id: str, data: Dict[str, Any]):
        """Cache player data in Redis"""
        try:
            if self.redis_client:
                cache_key = f"player:{player_id}"
                await self.redis_client.setex(
                    cache_key,
                    3600,  # 1 hour expiration
                    json.dumps(data)
                )
        except Exception as e:
            logger.warning(f"Failed to cache player data: {e}")
    
    async def _get_cached_player_data(self, player_id: str) -> Optional[Dict[str, Any]]:
        """Get cached player data from Redis"""
        try:
            if self.redis_client:
                cache_key = f"player:{player_id}"
                cached_data = await self.redis_client.get(cache_key)
                
                if cached_data:
                    return json.loads(cached_data)
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to get cached player data: {e}")
            return None
    
    async def get_players_by_league(self, league_id: str) -> List[Dict[str, Any]]:
        """Get all players in a league"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            if not self.SessionLocal:
                logger.warning("Database not available - returning empty list")
                return []
            
            async with self.SessionLocal() as session:
                players = await session.query(PlayerData).filter(
                    PlayerData.league_id == league_id
                ).all()
                
                return [
                    {
                        'player_id': p.player_id,
                        'name': p.name,
                        'position': p.position,
                        'team': p.team,
                        'points': p.points,
                        'avg_points': p.avg_points,
                        'ai_score': p.ai_score,
                        'trend': p.trend,
                        'risk_level': p.risk_level
                    }
                    for p in players
                ]
                
        except Exception as e:
            logger.error(f"Error getting players by league: {e}")
            raise
    
    async def get_teams_by_league(self, league_id: str) -> List[Dict[str, Any]]:
        """Get all teams in a league"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            if not self.SessionLocal:
                logger.warning("Database not available - returning empty list")
                return []
            
            async with self.SessionLocal() as session:
                teams = await session.query(TeamData).filter(
                    TeamData.league_id == league_id
                ).all()
                
                return [
                    {
                        'team_id': t.team_id,
                        'name': t.name,
                        'owner': t.owner,
                        'wins': t.wins,
                        'losses': t.losses,
                        'ties': t.ties,
                        'points_for': t.points_for,
                        'points_against': t.points_against
                    }
                    for t in teams
                ]
                
        except Exception as e:
            logger.error(f"Error getting teams by league: {e}")
            raise 