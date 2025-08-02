"""
Shared data models for Fantasy AI Ultimate merged project
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class SportType(str, Enum):
    """Supported sports types"""
    NFL = "nfl"
    NBA = "nba"
    MLB = "mlb"
    NHL = "nhl"

class Position(str, Enum):
    """Player positions"""
    QB = "QB"
    RB = "RB"
    WR = "WR"
    TE = "TE"
    K = "K"
    DEF = "DEF"
    # Basketball positions
    PG = "PG"
    SG = "SG"
    SF = "SF"
    PF = "PF"
    C = "C"

class PlayerStats(BaseModel):
    """Player statistics model"""
    player_id: str
    name: str
    position: Position
    team: str
    league_id: str
    
    # Performance stats
    points: Optional[float] = None
    games_played: Optional[int] = None
    avg_points: Optional[float] = None
    
    # Sport-specific stats
    stats: Dict[str, Any] = Field(default_factory=dict)
    
    # AI analysis
    ai_score: Optional[float] = None
    trend: Optional[str] = None
    risk_level: Optional[str] = None
    
    class Config:
        use_enum_values = True

class LeagueInfo(BaseModel):
    """League information model"""
    league_id: str
    name: str
    sport: SportType
    season: int
    num_teams: int
    scoring_type: str
    draft_type: str
    
    # League settings
    settings: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        use_enum_values = True

class TeamInfo(BaseModel):
    """Team information model"""
    team_id: str
    name: str
    owner: str
    league_id: str
    
    # Team stats
    wins: int = 0
    losses: int = 0
    ties: int = 0
    points_for: float = 0.0
    points_against: float = 0.0
    
    # Roster
    players: List[PlayerStats] = Field(default_factory=list)
    
    # AI optimization
    suggested_changes: List[Dict[str, Any]] = Field(default_factory=list)

class FantasyData(BaseModel):
    """Comprehensive fantasy data model"""
    league: LeagueInfo
    teams: List[TeamInfo] = Field(default_factory=list)
    players: List[PlayerStats] = Field(default_factory=list)
    
    # Metadata
    last_updated: datetime = Field(default_factory=datetime.now)
    data_source: str = "yahoo_fantasy"

class AIAnalysis(BaseModel):
    """AI analysis results model"""
    player_id: str
    analysis_type: str
    
    # Analysis results
    confidence_score: float
    prediction: Dict[str, Any] = Field(default_factory=dict)
    insights: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    
    # Metadata
    model_version: str
    analysis_date: datetime = Field(default_factory=datetime.now)

class PerformancePrediction(BaseModel):
    """Performance prediction model"""
    player_id: str
    next_game_prediction: float
    confidence_interval: tuple[float, float]
    factors: List[str] = Field(default_factory=list)
    risk_assessment: str
    
    # Historical context
    historical_avg: float
    recent_trend: str

class TeamOptimization(BaseModel):
    """Team optimization recommendations"""
    team_id: str
    current_score: float
    optimized_score: float
    
    # Recommendations
    add_players: List[Dict[str, Any]] = Field(default_factory=list)
    drop_players: List[Dict[str, Any]] = Field(default_factory=list)
    start_players: List[str] = Field(default_factory=list)
    bench_players: List[str] = Field(default_factory=list)
    
    # Reasoning
    reasoning: List[str] = Field(default_factory=list)

class APIResponse(BaseModel):
    """Standard API response model"""
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now) 