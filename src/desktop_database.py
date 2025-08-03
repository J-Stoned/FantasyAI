"""
Desktop Database Connection Module
Handles connection to the fantasy_ai_local database on desktop
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, date
import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, Session
import pandas as pd
from config.settings import settings

logger = logging.getLogger(__name__)


class DesktopDatabaseConnection:
    """Manages connection to desktop PostgreSQL database"""
    
    def __init__(self):
        self.desktop_url = settings.desktop_database_url
        self.sync_engine = None
        self.async_engine = None
        self.sync_session = None
        self.async_session = None
        
        if self.desktop_url:
            # Convert to async URL if needed
            if self.desktop_url.startswith("postgresql://"):
                self.async_url = self.desktop_url.replace("postgresql://", "postgresql+asyncpg://")
            else:
                self.async_url = self.desktop_url
                
    def init_sync_connection(self):
        """Initialize synchronous database connection"""
        if not self.desktop_url:
            raise ValueError("Desktop database URL not configured")
            
        try:
            self.sync_engine = create_engine(self.desktop_url)
            self.sync_session = sessionmaker(bind=self.sync_engine, class_=Session)
            logger.info("Desktop database sync connection established")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to desktop database: {e}")
            return False
            
    async def init_async_connection(self):
        """Initialize asynchronous database connection"""
        if not self.async_url:
            raise ValueError("Desktop database URL not configured")
            
        try:
            self.async_engine = create_async_engine(self.async_url)
            self.async_session = sessionmaker(
                bind=self.async_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            logger.info("Desktop database async connection established")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to desktop database: {e}")
            return False
    
    def get_sync_session(self) -> Session:
        """Get synchronous database session"""
        if not self.sync_session:
            self.init_sync_connection()
        return self.sync_session()
    
    async def get_async_session(self) -> AsyncSession:
        """Get asynchronous database session"""
        if not self.async_session:
            await self.init_async_connection()
        return self.async_session()
    
    async def test_connection(self) -> bool:
        """Test database connection"""
        try:
            async with await self.get_async_session() as session:
                result = await session.execute(text("SELECT 1"))
                return result.scalar() == 1
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    async def get_player_stats(
        self, 
        sport: str = None, 
        player_name: str = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get player statistics from desktop database"""
        try:
            async with await self.get_async_session() as session:
                query = "SELECT * FROM player_game_logs WHERE 1=1"
                params = {}
                
                if sport:
                    query += " AND sport = :sport"
                    params["sport"] = sport
                    
                if player_name:
                    query += " AND player_name ILIKE :player_name"
                    params["player_name"] = f"%{player_name}%"
                
                query += " ORDER BY game_date DESC LIMIT :limit"
                params["limit"] = limit
                
                result = await session.execute(text(query), params)
                columns = result.keys()
                
                return [dict(zip(columns, row)) for row in result.fetchall()]
                
        except Exception as e:
            logger.error(f"Error fetching player stats: {e}")
            return []
    
    async def get_dfs_salaries(
        self,
        game_date: date = None,
        platform: str = None
    ) -> List[Dict[str, Any]]:
        """Get DFS salary data"""
        try:
            async with await self.get_async_session() as session:
                query = """
                    SELECT 
                        player_id,
                        player_name,
                        position,
                        team,
                        platform,
                        salary,
                        projected_points,
                        projected_ownership,
                        game_date
                    FROM dfs_salaries
                    WHERE 1=1
                """
                params = {}
                
                if game_date:
                    query += " AND game_date = :game_date"
                    params["game_date"] = game_date
                    
                if platform:
                    query += " AND platform = :platform"
                    params["platform"] = platform
                    
                query += " ORDER BY salary DESC"
                
                result = await session.execute(text(query), params)
                columns = result.keys()
                
                return [dict(zip(columns, row)) for row in result.fetchall()]
                
        except Exception as e:
            logger.error(f"Error fetching DFS salaries: {e}")
            return []
    
    async def get_ml_predictions(
        self,
        sport: str,
        game_date: date = None
    ) -> pd.DataFrame:
        """Get ML predictions from enhanced tables"""
        try:
            table_map = {
                "NFL": "nfl_ml_enhanced",
                "NBA": "nba_ml_enhanced",
                "MLB": "mlb_ml_enhanced",
                "NHL": "nhl_ml_enhanced"
            }
            
            table_name = table_map.get(sport.upper())
            if not table_name:
                logger.error(f"Unknown sport: {sport}")
                return pd.DataFrame()
            
            async with await self.get_async_session() as session:
                query = f"SELECT * FROM {table_name}"
                params = {}
                
                if game_date:
                    query += " WHERE game_date = :game_date"
                    params["game_date"] = game_date
                else:
                    query += " ORDER BY game_date DESC LIMIT 1000"
                
                result = await session.execute(text(query), params)
                
                # Convert to DataFrame
                df = pd.DataFrame(result.fetchall(), columns=result.keys())
                return df
                
        except Exception as e:
            logger.error(f"Error fetching ML predictions: {e}")
            return pd.DataFrame()
    
    async def get_injury_reports(self) -> List[Dict[str, Any]]:
        """Get current injury reports"""
        try:
            async with await self.get_async_session() as session:
                query = """
                    SELECT 
                        player_id,
                        player_name,
                        team,
                        sport,
                        position,
                        injury_type,
                        body_part,
                        status,
                        severity,
                        fantasy_impact,
                        report_date,
                        notes
                    FROM injury_reports
                    WHERE report_date >= CURRENT_DATE - INTERVAL '7 days'
                    ORDER BY report_date DESC, severity DESC
                """
                
                result = await session.execute(text(query))
                columns = result.keys()
                
                return [dict(zip(columns, row)) for row in result.fetchall()]
                
        except Exception as e:
            logger.error(f"Error fetching injury reports: {e}")
            return []
    
    async def get_database_stats(self) -> Dict[str, Any]:
        """Get statistics about the desktop database"""
        try:
            async with await self.get_async_session() as session:
                stats = {}
                
                # Get table row counts
                tables = [
                    "players_master",
                    "player_game_logs", 
                    "games_master",
                    "dfs_salaries",
                    "injury_reports",
                    "ml_models"
                ]
                
                for table in tables:
                    result = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    stats[f"{table}_count"] = result.scalar()
                
                # Get date ranges
                result = await session.execute(text("""
                    SELECT 
                        MIN(game_date) as earliest_game,
                        MAX(game_date) as latest_game
                    FROM player_game_logs
                """))
                
                row = result.fetchone()
                if row:
                    stats["earliest_game_date"] = row[0]
                    stats["latest_game_date"] = row[1]
                
                return stats
                
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}


# Global instance
desktop_db = DesktopDatabaseConnection()


async def sync_yahoo_to_desktop(yahoo_data: Dict[str, Any], data_type: str):
    """Sync Yahoo API data to desktop database"""
    if not settings.enable_desktop_sync:
        return
        
    try:
        # This would be implemented to sync Yahoo API data
        # to the desktop database tables
        logger.info(f"Syncing {data_type} data to desktop database")
        # Implementation would go here
        
    except Exception as e:
        logger.error(f"Error syncing to desktop: {e}")