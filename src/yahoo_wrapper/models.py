"""
Database models for storing Yahoo Fantasy Sports data
Uses SQLAlchemy for ORM with async support
"""

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, 
    ForeignKey, Text, JSON, UniqueConstraint, Index
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class YahooGame(Base):
    """Yahoo Fantasy Game (sport)"""
    __tablename__ = 'yahoo_games'
    
    game_key = Column(String(50), primary_key=True)
    game_id = Column(String(10), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    code = Column(String(10), nullable=False)  # nfl, mlb, nba, nhl
    type = Column(String(20))  # full, pickem
    url = Column(String(255))
    season = Column(Integer, nullable=False)
    is_live_draft_lobby_active = Column(Boolean, default=False)
    is_game_over = Column(Boolean, default=False)
    is_offseason = Column(Boolean, default=False)
    
    # Relationships
    leagues = relationship("YahooLeague", back_populates="game", cascade="all, delete-orphan")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_game_code_season', 'code', 'season'),
    )


class YahooLeague(Base):
    """Yahoo Fantasy League"""
    __tablename__ = 'yahoo_leagues'
    
    league_key = Column(String(50), primary_key=True)
    league_id = Column(String(20), nullable=False)
    game_key = Column(String(50), ForeignKey('yahoo_games.game_key'), nullable=False)
    name = Column(String(255), nullable=False)
    url = Column(String(255))
    draft_status = Column(String(20))  # predraft, drafting, postdraft
    num_teams = Column(Integer, default=0)
    edit_key = Column(String(10))
    weekly_deadline = Column(String(50))
    league_update_timestamp = Column(String(20))
    scoring_type = Column(String(20))  # head, roto, points
    league_type = Column(String(20))  # private, public
    renew = Column(String(50))
    renewed = Column(String(50))
    short_invitation_url = Column(String(255))
    is_pro_league = Column(Boolean, default=False)
    current_week = Column(Integer)
    start_week = Column(Integer)
    end_week = Column(Integer)
    is_finished = Column(Boolean, default=False)
    
    # Settings (stored as JSON)
    settings = Column(JSON)
    
    # Relationships
    game = relationship("YahooGame", back_populates="leagues")
    teams = relationship("YahooTeam", back_populates="league", cascade="all, delete-orphan")
    transactions = relationship("YahooTransaction", back_populates="league", cascade="all, delete-orphan")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        UniqueConstraint('game_key', 'league_id', name='uq_game_league'),
        Index('idx_league_game', 'game_key'),
        Index('idx_league_status', 'draft_status', 'is_finished'),
    )


class YahooTeam(Base):
    """Yahoo Fantasy Team"""
    __tablename__ = 'yahoo_teams'
    
    team_key = Column(String(50), primary_key=True)
    team_id = Column(String(20), nullable=False)
    league_key = Column(String(50), ForeignKey('yahoo_leagues.league_key'), nullable=False)
    name = Column(String(255), nullable=False)
    url = Column(String(255))
    team_logos = Column(JSON)  # List of logo URLs
    waiver_priority = Column(Integer)
    faab_balance = Column(Integer)
    number_of_moves = Column(Integer, default=0)
    number_of_trades = Column(Integer, default=0)
    roster_adds = Column(JSON)
    clinched_playoffs = Column(Boolean, default=False)
    league_scoring_type = Column(String(20))
    has_draft_grade = Column(Boolean, default=False)
    draft_grade = Column(String(5))
    draft_recap_url = Column(String(255))
    
    # Team stats
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    ties = Column(Integer, default=0)
    points_for = Column(Float, default=0.0)
    points_against = Column(Float, default=0.0)
    standing = Column(Integer)
    
    # Relationships
    league = relationship("YahooLeague", back_populates="teams")
    managers = relationship("YahooTeamManager", back_populates="team", cascade="all, delete-orphan")
    roster_entries = relationship("YahooRosterEntry", back_populates="team", cascade="all, delete-orphan")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        UniqueConstraint('league_key', 'team_id', name='uq_league_team'),
        Index('idx_team_league', 'league_key'),
        Index('idx_team_standing', 'league_key', 'standing'),
    )


class YahooPlayer(Base):
    """Yahoo Fantasy Player"""
    __tablename__ = 'yahoo_players'
    
    player_key = Column(String(50), primary_key=True)
    player_id = Column(String(20), unique=True, nullable=False)
    name_full = Column(String(255), nullable=False)
    name_first = Column(String(100))
    name_last = Column(String(100))
    name_ascii_first = Column(String(100))
    name_ascii_last = Column(String(100))
    status = Column(String(20))  # NA, O, Q, D, etc.
    status_full = Column(String(50))
    injury_note = Column(Text)
    editorial_player_key = Column(String(50))
    editorial_team_key = Column(String(50))
    editorial_team_full_name = Column(String(255))
    editorial_team_abbr = Column(String(10))
    bye_weeks = Column(JSON)  # List of bye week numbers
    uniform_number = Column(String(10))
    display_position = Column(String(50))
    headshot_url = Column(String(255))
    image_url = Column(String(255))
    is_undroppable = Column(Boolean, default=False)
    position_type = Column(String(10))  # O, D, etc.
    eligible_positions = Column(JSON)  # List of positions
    has_player_notes = Column(Boolean, default=False)
    has_recent_player_notes = Column(Boolean, default=False)
    
    # Stats cache
    season_stats = Column(JSON)
    last_updated_stats = Column(DateTime)
    
    # Relationships
    roster_entries = relationship("YahooRosterEntry", back_populates="player")
    player_stats = relationship("YahooPlayerStats", back_populates="player", cascade="all, delete-orphan")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_player_position', 'display_position'),
        Index('idx_player_team', 'editorial_team_abbr'),
        Index('idx_player_name', 'name_last', 'name_first'),
    )


class YahooRosterEntry(Base):
    """Player on a team roster"""
    __tablename__ = 'yahoo_roster_entries'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    team_key = Column(String(50), ForeignKey('yahoo_teams.team_key'), nullable=False)
    player_key = Column(String(50), ForeignKey('yahoo_players.player_key'), nullable=False)
    selected_position = Column(String(20))  # Current position
    is_flex = Column(Boolean, default=False)
    coverage_type = Column(String(10))  # week, date
    coverage_value = Column(String(20))  # week number or date
    acquisition_type = Column(String(20))  # draft, add, trade
    acquisition_date = Column(DateTime)
    
    # Relationships
    team = relationship("YahooTeam", back_populates="roster_entries")
    player = relationship("YahooPlayer", back_populates="roster_entries")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        UniqueConstraint('team_key', 'player_key', 'coverage_type', 'coverage_value', 
                        name='uq_team_player_coverage'),
        Index('idx_roster_team', 'team_key'),
        Index('idx_roster_player', 'player_key'),
        Index('idx_roster_coverage', 'coverage_type', 'coverage_value'),
    )


class YahooTeamManager(Base):
    """Team manager/owner"""
    __tablename__ = 'yahoo_team_managers'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    team_key = Column(String(50), ForeignKey('yahoo_teams.team_key'), nullable=False)
    manager_id = Column(String(20), nullable=False)
    nickname = Column(String(255))
    guid = Column(String(100))
    is_commissioner = Column(Boolean, default=False)
    is_current_login = Column(Boolean, default=False)
    email = Column(String(255))
    image_url = Column(String(255))
    
    # Relationships
    team = relationship("YahooTeam", back_populates="managers")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        UniqueConstraint('team_key', 'manager_id', name='uq_team_manager'),
        Index('idx_manager_guid', 'guid'),
    )


class YahooTransaction(Base):
    """League transaction (add/drop/trade)"""
    __tablename__ = 'yahoo_transactions'
    
    transaction_key = Column(String(100), primary_key=True)
    transaction_id = Column(String(20))
    league_key = Column(String(50), ForeignKey('yahoo_leagues.league_key'), nullable=False)
    type = Column(String(20), nullable=False)  # add, drop, add/drop, trade
    status = Column(String(20))  # successful, pending, rejected
    timestamp = Column(DateTime)
    
    # Trade specific
    trader_team_key = Column(String(50))
    tradee_team_key = Column(String(50))
    trade_note = Column(Text)
    
    # Waiver specific
    waiver_priority = Column(Integer)
    faab_bid = Column(Integer)
    
    # Transaction details (JSON)
    players = Column(JSON)  # List of players involved
    
    # Relationships
    league = relationship("YahooLeague", back_populates="transactions")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_transaction_league', 'league_key'),
        Index('idx_transaction_type', 'type', 'status'),
        Index('idx_transaction_timestamp', 'timestamp'),
    )


class YahooPlayerStats(Base):
    """Player statistics by period"""
    __tablename__ = 'yahoo_player_stats'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    player_key = Column(String(50), ForeignKey('yahoo_players.player_key'), nullable=False)
    coverage_type = Column(String(20), nullable=False)  # season, week, date
    coverage_value = Column(String(20), nullable=False)  # season year, week num, date
    stats = Column(JSON, nullable=False)  # Dictionary of stat_id: value
    points = Column(Float)  # Fantasy points (if calculated)
    
    # Relationships
    player = relationship("YahooPlayer", back_populates="player_stats")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        UniqueConstraint('player_key', 'coverage_type', 'coverage_value', 
                        name='uq_player_stats_coverage'),
        Index('idx_stats_player', 'player_key'),
        Index('idx_stats_coverage', 'coverage_type', 'coverage_value'),
    )


class YahooUserToken(Base):
    """Store Yahoo OAuth tokens for users"""
    __tablename__ = 'yahoo_user_tokens'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_guid = Column(String(100), unique=True, nullable=False)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=False)
    token_expires_at = Column(DateTime, nullable=False)
    
    # User info
    user_email = Column(String(255))
    user_nickname = Column(String(255))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_token_guid', 'user_guid'),
        Index('idx_token_expires', 'token_expires_at'),
    )