"""
Unit tests for Yahoo Fantasy database sync functionality
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import pytest_asyncio

from src.yahoo_wrapper.models import Base, YahooGame, YahooLeague, YahooTeam, YahooPlayer
from src.yahoo_wrapper.db_sync import YahooDataSync


class TestYahooDataSync:
    """Test Yahoo data synchronization to database"""
    
    @pytest_asyncio.fixture
    async def db_engine(self):
        """Create test database engine"""
        # Use in-memory SQLite for tests
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        
        # Create tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        yield engine
        
        # Cleanup
        await engine.dispose()
    
    @pytest_asyncio.fixture
    async def db_session(self, db_engine):
        """Create database session"""
        async_session = sessionmaker(
            db_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        async with async_session() as session:
            yield session
    
    @pytest_asyncio.fixture
    async def sync(self, db_session):
        """Create data sync instance"""
        return YahooDataSync(db_session)
    
    @pytest.mark.asyncio
    async def test_sync_game(self, sync, db_session):
        """Test syncing game data"""
        game_data = {
            "game_key": "nfl",
            "game_id": "399",
            "name": "Football",
            "code": "nfl",
            "type": "full",
            "url": "https://football.fantasysports.yahoo.com",
            "season": "2024",
            "is_live_draft_lobby_active": False,
            "is_game_over": False,
            "is_offseason": False
        }
        
        # Sync game
        game = await sync.sync_game(game_data)
        
        assert game is not None
        assert game.game_key == "nfl"
        assert game.name == "Football"
        assert game.season == 2024
        
        # Verify in database
        result = await db_session.get(YahooGame, "nfl")
        assert result is not None
        assert result.game_id == "399"
    
    @pytest.mark.asyncio
    async def test_sync_league(self, sync, db_session):
        """Test syncing league data"""
        # First sync the game
        game_data = {
            "game_key": "nfl",
            "game_id": "399",
            "name": "Football",
            "code": "nfl",
            "season": "2024"
        }
        await sync.sync_game(game_data)
        
        # Then sync league
        league_data = {
            "league_key": "nfl.l.12345",
            "league_id": "12345",
            "name": "Test League",
            "url": "https://football.fantasysports.yahoo.com/f1/12345",
            "draft_status": "postdraft",
            "num_teams": 10,
            "scoring_type": "head",
            "current_week": 10,
            "is_finished": False,
            "settings": {
                "draft_type": "live",
                "trade_deadline": "2024-11-15"
            }
        }
        
        league = await sync.sync_league(league_data)
        
        assert league is not None
        assert league.league_key == "nfl.l.12345"
        assert league.name == "Test League"
        assert league.num_teams == 10
        assert league.settings["draft_type"] == "live"
    
    @pytest.mark.asyncio
    async def test_sync_team(self, sync, db_session):
        """Test syncing team data"""
        # Setup game and league
        await sync.sync_game({
            "game_key": "nfl",
            "game_id": "399",
            "name": "Football",
            "code": "nfl",
            "season": "2024"
        })
        
        await sync.sync_league({
            "league_key": "nfl.l.12345",
            "league_id": "12345",
            "name": "Test League"
        })
        
        # Sync team
        team_data = {
            "team_key": "nfl.l.12345.t.1",
            "team_id": "1",
            "name": "Test Team",
            "url": "https://football.fantasysports.yahoo.com/f1/12345/1",
            "team_logos": [
                {"size": "large", "url": "https://example.com/logo.png"}
            ],
            "waiver_priority": 5,
            "faab_balance": 75,
            "number_of_moves": 10,
            "managers": [
                {
                    "manager_id": "1",
                    "nickname": "Test Manager",
                    "guid": "ABC123",
                    "is_commissioner": True
                }
            ]
        }
        
        team = await sync.sync_team(team_data)
        
        assert team is not None
        assert team.team_key == "nfl.l.12345.t.1"
        assert team.name == "Test Team"
        assert team.waiver_priority == 5
        assert team.faab_balance == 75
        
        # Check managers
        assert len(team.managers) == 1
        assert team.managers[0].nickname == "Test Manager"
        assert team.managers[0].is_commissioner is True
    
    @pytest.mark.asyncio
    async def test_sync_player(self, sync, db_session):
        """Test syncing player data"""
        player_data = {
            "player_key": "nfl.p.12345",
            "player_id": "12345",
            "name": {
                "full": "Patrick Mahomes",
                "first": "Patrick",
                "last": "Mahomes"
            },
            "status": "ACTIVE",
            "editorial_team_abbr": "KC",
            "display_position": "QB",
            "eligible_positions": ["QB"],
            "is_undroppable": True
        }
        
        player = await sync.sync_player(player_data)
        
        assert player is not None
        assert player.player_key == "nfl.p.12345"
        assert player.name_full == "Patrick Mahomes"
        assert player.display_position == "QB"
        assert player.is_undroppable is True
    
    @pytest.mark.asyncio
    async def test_sync_roster(self, sync, db_session):
        """Test syncing team roster"""
        # Setup required data
        await sync.sync_game({
            "game_key": "nfl",
            "game_id": "399",
            "name": "Football",
            "code": "nfl",
            "season": "2024"
        })
        
        await sync.sync_league({
            "league_key": "nfl.l.12345",
            "league_id": "12345",
            "name": "Test League"
        })
        
        await sync.sync_team({
            "team_key": "nfl.l.12345.t.1",
            "team_id": "1",
            "name": "Test Team"
        })
        
        # Sync roster
        players = [
            {
                "player_key": "nfl.p.12345",
                "player_id": "12345",
                "name": {"full": "Patrick Mahomes"},
                "selected_position": {
                    "position": "QB",
                    "is_flex": False
                }
            },
            {
                "player_key": "nfl.p.67890",
                "player_id": "67890",
                "name": {"full": "Christian McCaffrey"},
                "selected_position": {
                    "position": "RB",
                    "is_flex": False
                }
            }
        ]
        
        await sync.sync_roster(
            "nfl.l.12345.t.1",
            players,
            "week",
            "10"
        )
        
        # Verify roster entries
        from sqlalchemy import select
        from src.yahoo_wrapper.models import YahooRosterEntry
        
        result = await db_session.execute(
            select(YahooRosterEntry).where(
                YahooRosterEntry.team_key == "nfl.l.12345.t.1"
            )
        )
        roster_entries = result.scalars().all()
        
        assert len(roster_entries) == 2
        positions = [entry.selected_position for entry in roster_entries]
        assert "QB" in positions
        assert "RB" in positions
    
    @pytest.mark.asyncio
    async def test_sync_transaction(self, sync, db_session):
        """Test syncing transaction data"""
        # Setup league
        await sync.sync_game({
            "game_key": "nfl",
            "game_id": "399",
            "name": "Football",
            "code": "nfl",
            "season": "2024"
        })
        
        await sync.sync_league({
            "league_key": "nfl.l.12345",
            "league_id": "12345",
            "name": "Test League"
        })
        
        # Sync transaction
        transaction_data = {
            "transaction_key": "nfl.l.12345.tr.1",
            "transaction_id": "1",
            "type": "add/drop",
            "status": "successful",
            "timestamp": str(int(datetime.now().timestamp())),
            "players": [
                {
                    "player_key": "nfl.p.11111",
                    "transaction_data": {
                        "type": "add",
                        "destination_team_key": "nfl.l.12345.t.1"
                    }
                },
                {
                    "player_key": "nfl.p.22222",
                    "transaction_data": {
                        "type": "drop",
                        "source_team_key": "nfl.l.12345.t.1"
                    }
                }
            ]
        }
        
        transaction = await sync.sync_transaction(transaction_data)
        
        assert transaction is not None
        assert transaction.transaction_key == "nfl.l.12345.tr.1"
        assert transaction.type == "add/drop"
        assert transaction.status == "successful"
        assert len(transaction.players) == 2
    
    @pytest.mark.asyncio
    async def test_sync_player_stats(self, sync, db_session):
        """Test syncing player statistics"""
        # First sync player
        await sync.sync_player({
            "player_key": "nfl.p.12345",
            "player_id": "12345",
            "name": {"full": "Patrick Mahomes"}
        })
        
        # Sync stats
        stats_data = {
            "passing_yards": 4500,
            "passing_tds": 35,
            "interceptions": 8,
            "rushing_yards": 250,
            "rushing_tds": 2
        }
        
        await sync.sync_player_stats(
            "nfl.p.12345",
            stats_data,
            "season",
            "2024",
            points=350.5
        )
        
        # Verify stats
        from sqlalchemy import select
        from src.yahoo_wrapper.models import YahooPlayerStats
        
        result = await db_session.execute(
            select(YahooPlayerStats).where(
                (YahooPlayerStats.player_key == "nfl.p.12345") &
                (YahooPlayerStats.coverage_type == "season") &
                (YahooPlayerStats.coverage_value == "2024")
            )
        )
        stats = result.scalar_one()
        
        assert stats is not None
        assert stats.stats["passing_yards"] == 4500
        assert stats.points == 350.5
    
    @pytest.mark.asyncio
    async def test_sync_user_token(self, sync, db_session):
        """Test syncing user OAuth token"""
        user_info = {
            "guid": "USER123ABC",
            "email": "test@example.com",
            "nickname": "TestUser"
        }
        
        token = await sync.sync_user_token(
            user_info["guid"],
            "access_token_123",
            "refresh_token_456",
            datetime.now() + timedelta(hours=1),
            user_info
        )
        
        assert token is not None
        assert token.user_guid == "USER123ABC"
        assert token.access_token == "access_token_123"
        assert token.user_email == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_upsert_behavior(self, sync, db_session):
        """Test upsert behavior for existing records"""
        # Initial sync
        game_data = {
            "game_key": "nfl",
            "game_id": "399",
            "name": "Football",
            "code": "nfl",
            "season": "2024",
            "is_offseason": False
        }
        
        game1 = await sync.sync_game(game_data)
        created_at = game1.created_at
        
        # Update and sync again
        game_data["is_offseason"] = True
        await asyncio.sleep(0.1)  # Ensure time difference
        
        game2 = await sync.sync_game(game_data)
        
        # Verify update
        assert game2.game_key == game1.game_key
        assert game2.is_offseason is True
        assert game2.created_at == created_at  # Created time unchanged
        assert game2.updated_at > created_at  # Updated time changed


if __name__ == "__main__":
    pytest.main([__file__, "-v"])