"""
Unified Data Service
Combines data from Yahoo Fantasy API and Desktop Database
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
import pandas as pd
from sqlalchemy import text

from src.yahoo_wrapper import YahooFantasyAPI
from src.desktop_database import desktop_db
from config.settings import settings

logger = logging.getLogger(__name__)


class UnifiedDataService:
    """Unified access to fantasy sports data from multiple sources"""
    
    def __init__(self):
        self.yahoo_api = YahooFantasyAPI(cache_type="memory")
        self.desktop_db = desktop_db
        self._desktop_available = False
        
    async def initialize(self):
        """Initialize data connections"""
        # Check desktop database availability
        if settings.desktop_database_url:
            self._desktop_available = await self.desktop_db.test_connection()
            if self._desktop_available:
                logger.info("Desktop database connected successfully")
            else:
                logger.warning("Desktop database not available")
                
    async def get_player_data(
        self,
        player_name: str = None,
        player_id: str = None,
        sport: str = None,
        include_stats: bool = True,
        include_projections: bool = True
    ) -> Dict[str, Any]:
        """Get comprehensive player data from all sources"""
        
        player_data = {
            "player_info": None,
            "recent_stats": [],
            "season_stats": None,
            "projections": None,
            "injury_status": None,
            "dfs_salaries": [],
            "ml_predictions": None
        }
        
        try:
            # Get data from desktop database if available
            if self._desktop_available:
                # Get player game logs
                if include_stats:
                    stats = await self.desktop_db.get_player_stats(
                        sport=sport,
                        player_name=player_name,
                        limit=20
                    )
                    player_data["recent_stats"] = stats
                    
                    # Calculate season averages
                    if stats:
                        df = pd.DataFrame(stats)
                        season_avg = {
                            "games_played": len(df),
                            "avg_fantasy_points": df["fantasy_points"].mean(),
                            "avg_dk_points": df["dk_points"].mean() if "dk_points" in df else None,
                            "avg_fd_points": df["fd_points"].mean() if "fd_points" in df else None,
                        }
                        player_data["season_stats"] = season_avg
                
                # Get injury status
                injuries = await self._get_player_injury_status(player_name)
                if injuries:
                    player_data["injury_status"] = injuries[0]
                
                # Get DFS salaries
                salaries = await self._get_player_dfs_salaries(player_name)
                player_data["dfs_salaries"] = salaries
                
                # Get ML predictions if available
                if include_projections and sport:
                    predictions = await self._get_ml_predictions_for_player(
                        player_name, sport
                    )
                    player_data["ml_predictions"] = predictions
            
            # Get Yahoo Fantasy data if available
            if self.yahoo_api.access_token:
                # This would fetch from Yahoo API
                pass
                
        except Exception as e:
            logger.error(f"Error getting player data: {e}")
            
        return player_data
    
    async def get_dfs_slate(
        self,
        sport: str,
        slate_date: date = None,
        platform: str = "draftkings"
    ) -> Dict[str, Any]:
        """Get DFS slate information"""
        
        if not slate_date:
            slate_date = datetime.now().date()
            
        slate_data = {
            "date": slate_date,
            "sport": sport,
            "platform": platform,
            "players": [],
            "games": [],
            "injuries": [],
            "weather": []
        }
        
        try:
            if self._desktop_available:
                # Get DFS salaries
                salaries = await self.desktop_db.get_dfs_salaries(
                    game_date=slate_date,
                    platform=platform
                )
                
                # Enhance with additional data
                for salary in salaries:
                    # Get recent stats
                    stats = await self.desktop_db.get_player_stats(
                        sport=sport,
                        player_name=salary["player_name"],
                        limit=5
                    )
                    
                    if stats:
                        recent_avg = sum(s["fantasy_points"] for s in stats) / len(stats)
                        salary["recent_avg"] = recent_avg
                        salary["value"] = recent_avg / (salary["salary"] / 1000) if salary["salary"] > 0 else 0
                    
                    slate_data["players"].append(salary)
                
                # Get injuries
                injuries = await self.desktop_db.get_injury_reports()
                slate_data["injuries"] = [
                    inj for inj in injuries 
                    if inj["sport"] == sport
                ]
                
        except Exception as e:
            logger.error(f"Error getting DFS slate: {e}")
            
        return slate_data
    
    async def get_ml_predictions(
        self,
        sport: str,
        game_date: date = None,
        min_confidence: float = 0.7
    ) -> pd.DataFrame:
        """Get ML predictions with confidence filtering"""
        
        if not self._desktop_available:
            return pd.DataFrame()
            
        try:
            df = await self.desktop_db.get_ml_predictions(sport, game_date)
            
            if not df.empty and "confidence_score" in df.columns:
                # Filter by confidence
                df = df[df["confidence_score"] >= min_confidence]
                
                # Add value calculations
                if "fantasy_points" in df.columns:
                    df["fp_vs_avg"] = df["fantasy_points"] - df.get("fp_avg_season", 0)
                    
            return df
            
        except Exception as e:
            logger.error(f"Error getting ML predictions: {e}")
            return pd.DataFrame()
    
    async def get_optimization_data(
        self,
        sport: str,
        contest_type: str = "main",
        slate_date: date = None
    ) -> Dict[str, Any]:
        """Get data optimized for lineup building"""
        
        if not slate_date:
            slate_date = datetime.now().date()
            
        optimization_data = {
            "players": [],
            "correlations": {},
            "stacks": [],
            "leverage_plays": []
        }
        
        try:
            # Get base slate data
            slate = await self.get_dfs_slate(sport, slate_date)
            
            # Analyze for optimization
            if slate["players"]:
                df = pd.DataFrame(slate["players"])
                
                # Find value plays
                if "value" in df.columns:
                    value_plays = df.nlargest(10, "value")
                    optimization_data["players"] = value_plays.to_dict("records")
                
                # Find leverage plays (low ownership, high upside)
                if "projected_ownership" in df.columns:
                    leverage = df[
                        (df["projected_ownership"] < 10) & 
                        (df.get("recent_avg", 0) > df["projected_points"])
                    ]
                    optimization_data["leverage_plays"] = leverage.to_dict("records")
                    
        except Exception as e:
            logger.error(f"Error getting optimization data: {e}")
            
        return optimization_data
    
    async def _get_player_injury_status(self, player_name: str) -> List[Dict[str, Any]]:
        """Get injury status for a player"""
        try:
            async with await self.desktop_db.get_async_session() as session:
                query = """
                    SELECT * FROM injury_reports
                    WHERE player_name ILIKE :player_name
                    ORDER BY report_date DESC
                    LIMIT 1
                """
                result = await session.execute(
                    text(query),
                    {"player_name": f"%{player_name}%"}
                )
                
                columns = result.keys()
                rows = result.fetchall()
                
                return [dict(zip(columns, row)) for row in rows]
                
        except Exception as e:
            logger.error(f"Error getting injury status: {e}")
            return []
    
    async def _get_player_dfs_salaries(self, player_name: str) -> List[Dict[str, Any]]:
        """Get current DFS salaries for a player"""
        try:
            async with await self.desktop_db.get_async_session() as session:
                query = """
                    SELECT * FROM dfs_salaries
                    WHERE player_name ILIKE :player_name
                    ORDER BY game_date DESC
                    LIMIT 5
                """
                result = await session.execute(
                    text(query),
                    {"player_name": f"%{player_name}%"}
                )
                
                columns = result.keys()
                rows = result.fetchall()
                
                return [dict(zip(columns, row)) for row in rows]
                
        except Exception as e:
            logger.error(f"Error getting DFS salaries: {e}")
            return []
    
    async def _get_ml_predictions_for_player(
        self, 
        player_name: str,
        sport: str
    ) -> Optional[Dict[str, Any]]:
        """Get ML predictions for a specific player"""
        try:
            df = await self.desktop_db.get_ml_predictions(sport)
            
            if not df.empty:
                player_df = df[df["player_name"].str.contains(player_name, case=False, na=False)]
                
                if not player_df.empty:
                    latest = player_df.iloc[0]
                    return {
                        "predicted_points": latest.get("fantasy_points"),
                        "confidence": latest.get("confidence_score"),
                        "recent_form": latest.get("fp_avg_last_5"),
                        "season_avg": latest.get("fp_avg_season"),
                        "matchup_rating": latest.get("matchup_rating"),
                    }
                    
        except Exception as e:
            logger.error(f"Error getting ML predictions: {e}")
            
        return None


# Global instance
unified_data = UnifiedDataService()