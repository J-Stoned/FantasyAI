"""
Yahoo Fantasy Data Database Synchronization
Handles syncing Yahoo API data to local database
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.sql import insert

from .models import (
    YahooGame, YahooLeague, YahooTeam, YahooPlayer,
    YahooRosterEntry, YahooTeamManager, YahooTransaction,
    YahooPlayerStats, YahooUserToken
)

logger = logging.getLogger(__name__)


class YahooDataSync:
    """Sync Yahoo Fantasy data to database"""
    
    def __init__(self, db_session: AsyncSession):
        self.session = db_session
        
    async def sync_game(self, game_data: Dict[str, Any]) -> YahooGame:
        """Sync game data to database"""
        try:
            # Check if game exists
            result = await self.session.execute(
                select(YahooGame).where(YahooGame.game_key == game_data['game_key'])
            )
            game = result.scalar_one_or_none()
            
            if game:
                # Update existing
                game.name = game_data['name']
                game.code = game_data['code']
                game.type = game_data.get('type', 'full')
                game.url = game_data.get('url')
                game.season = int(game_data['season'])
                game.is_live_draft_lobby_active = game_data.get('is_live_draft_lobby_active', False)
                game.is_game_over = game_data.get('is_game_over', False)
                game.is_offseason = game_data.get('is_offseason', False)
                game.updated_at = datetime.now()
            else:
                # Create new
                game = YahooGame(
                    game_key=game_data['game_key'],
                    game_id=game_data['game_id'],
                    name=game_data['name'],
                    code=game_data['code'],
                    type=game_data.get('type', 'full'),
                    url=game_data.get('url'),
                    season=int(game_data['season']),
                    is_live_draft_lobby_active=game_data.get('is_live_draft_lobby_active', False),
                    is_game_over=game_data.get('is_game_over', False),
                    is_offseason=game_data.get('is_offseason', False)
                )
                self.session.add(game)
            
            await self.session.commit()
            return game
            
        except Exception as e:
            logger.error(f"Error syncing game: {e}")
            await self.session.rollback()
            raise
            
    async def sync_league(self, league_data: Dict[str, Any]) -> YahooLeague:
        """Sync league data to database"""
        try:
            # Extract game_key from league_key
            league_key = league_data['league_key']
            game_key = league_key.split('.l.')[0]
            
            # Upsert league data
            stmt = insert(YahooLeague).values(
                league_key=league_key,
                league_id=league_data['league_id'],
                game_key=game_key,
                name=league_data['name'],
                url=league_data.get('url'),
                draft_status=league_data.get('draft_status'),
                num_teams=league_data.get('num_teams', 0),
                edit_key=league_data.get('edit_key'),
                weekly_deadline=league_data.get('weekly_deadline'),
                league_update_timestamp=league_data.get('league_update_timestamp'),
                scoring_type=league_data.get('scoring_type'),
                league_type=league_data.get('league_type', 'private'),
                renew=league_data.get('renew'),
                renewed=league_data.get('renewed'),
                short_invitation_url=league_data.get('short_invitation_url'),
                is_pro_league=league_data.get('is_pro_league', False),
                current_week=league_data.get('current_week'),
                start_week=league_data.get('start_week'),
                end_week=league_data.get('end_week'),
                is_finished=league_data.get('is_finished', False),
                settings=league_data.get('settings', {})
            )
            
            stmt = stmt.on_conflict_do_update(
                index_elements=['league_key'],
                set_=dict(
                    name=stmt.excluded.name,
                    url=stmt.excluded.url,
                    draft_status=stmt.excluded.draft_status,
                    num_teams=stmt.excluded.num_teams,
                    current_week=stmt.excluded.current_week,
                    is_finished=stmt.excluded.is_finished,
                    settings=stmt.excluded.settings,
                    updated_at=datetime.now()
                )
            )
            
            await self.session.execute(stmt)
            await self.session.commit()
            
            # Fetch and return the league
            result = await self.session.execute(
                select(YahooLeague).where(YahooLeague.league_key == league_key)
            )
            return result.scalar_one()
            
        except Exception as e:
            logger.error(f"Error syncing league: {e}")
            await self.session.rollback()
            raise
            
    async def sync_team(self, team_data: Dict[str, Any]) -> YahooTeam:
        """Sync team data to database"""
        try:
            # Extract league_key from team_key
            team_key = team_data['team_key']
            league_key = '.'.join(team_key.split('.')[:-2])
            
            # Upsert team data
            stmt = insert(YahooTeam).values(
                team_key=team_key,
                team_id=team_data['team_id'],
                league_key=league_key,
                name=team_data['name'],
                url=team_data.get('url'),
                team_logos=team_data.get('team_logos', []),
                waiver_priority=team_data.get('waiver_priority'),
                faab_balance=team_data.get('faab_balance'),
                number_of_moves=team_data.get('number_of_moves', 0),
                number_of_trades=team_data.get('number_of_trades', 0),
                roster_adds=team_data.get('roster_adds', {}),
                clinched_playoffs=team_data.get('clinched_playoffs', False),
                league_scoring_type=team_data.get('league_scoring_type'),
                has_draft_grade=team_data.get('has_draft_grade', False),
                draft_grade=team_data.get('draft_grade'),
                draft_recap_url=team_data.get('draft_recap_url')
            )
            
            stmt = stmt.on_conflict_do_update(
                index_elements=['team_key'],
                set_=dict(
                    name=stmt.excluded.name,
                    url=stmt.excluded.url,
                    team_logos=stmt.excluded.team_logos,
                    waiver_priority=stmt.excluded.waiver_priority,
                    faab_balance=stmt.excluded.faab_balance,
                    number_of_moves=stmt.excluded.number_of_moves,
                    number_of_trades=stmt.excluded.number_of_trades,
                    clinched_playoffs=stmt.excluded.clinched_playoffs,
                    updated_at=datetime.now()
                )
            )
            
            await self.session.execute(stmt)
            
            # Sync managers
            if 'managers' in team_data:
                await self._sync_team_managers(team_key, team_data['managers'])
                
            await self.session.commit()
            
            # Fetch and return the team
            result = await self.session.execute(
                select(YahooTeam).where(YahooTeam.team_key == team_key)
            )
            return result.scalar_one()
            
        except Exception as e:
            logger.error(f"Error syncing team: {e}")
            await self.session.rollback()
            raise
            
    async def _sync_team_managers(self, team_key: str, managers: List[Dict[str, Any]]):
        """Sync team managers"""
        try:
            # Delete existing managers
            await self.session.execute(
                YahooTeamManager.__table__.delete().where(
                    YahooTeamManager.team_key == team_key
                )
            )
            
            # Insert new managers
            for manager in managers:
                stmt = insert(YahooTeamManager).values(
                    team_key=team_key,
                    manager_id=manager['manager_id'],
                    nickname=manager.get('nickname'),
                    guid=manager.get('guid'),
                    is_commissioner=manager.get('is_commissioner', False),
                    is_current_login=manager.get('is_current_login', False),
                    email=manager.get('email'),
                    image_url=manager.get('image_url')
                )
                await self.session.execute(stmt)
                
        except Exception as e:
            logger.error(f"Error syncing team managers: {e}")
            raise
            
    async def sync_player(self, player_data: Dict[str, Any]) -> YahooPlayer:
        """Sync player data to database"""
        try:
            # Upsert player data
            stmt = insert(YahooPlayer).values(
                player_key=player_data['player_key'],
                player_id=player_data['player_id'],
                name_full=player_data['name']['full'],
                name_first=player_data['name'].get('first'),
                name_last=player_data['name'].get('last'),
                name_ascii_first=player_data['name'].get('ascii_first'),
                name_ascii_last=player_data['name'].get('ascii_last'),
                status=player_data.get('status'),
                status_full=player_data.get('status_full'),
                injury_note=player_data.get('injury_note'),
                editorial_player_key=player_data.get('editorial_player_key'),
                editorial_team_key=player_data.get('editorial_team_key'),
                editorial_team_full_name=player_data.get('editorial_team_full_name'),
                editorial_team_abbr=player_data.get('editorial_team_abbr'),
                bye_weeks=player_data.get('bye_weeks', []),
                uniform_number=player_data.get('uniform_number'),
                display_position=player_data.get('display_position'),
                headshot_url=player_data.get('headshot', {}).get('url'),
                image_url=player_data.get('image_url'),
                is_undroppable=player_data.get('is_undroppable', False),
                position_type=player_data.get('position_type'),
                eligible_positions=player_data.get('eligible_positions', []),
                has_player_notes=player_data.get('has_player_notes', False),
                has_recent_player_notes=player_data.get('has_recent_player_notes', False)
            )
            
            stmt = stmt.on_conflict_do_update(
                index_elements=['player_key'],
                set_=dict(
                    name_full=stmt.excluded.name_full,
                    status=stmt.excluded.status,
                    status_full=stmt.excluded.status_full,
                    injury_note=stmt.excluded.injury_note,
                    editorial_team_abbr=stmt.excluded.editorial_team_abbr,
                    display_position=stmt.excluded.display_position,
                    eligible_positions=stmt.excluded.eligible_positions,
                    has_player_notes=stmt.excluded.has_player_notes,
                    has_recent_player_notes=stmt.excluded.has_recent_player_notes,
                    updated_at=datetime.now()
                )
            )
            
            await self.session.execute(stmt)
            await self.session.commit()
            
            # Fetch and return the player
            result = await self.session.execute(
                select(YahooPlayer).where(YahooPlayer.player_key == player_data['player_key'])
            )
            return result.scalar_one()
            
        except Exception as e:
            logger.error(f"Error syncing player: {e}")
            await self.session.rollback()
            raise
            
    async def sync_roster(
        self, 
        team_key: str, 
        players: List[Dict[str, Any]], 
        coverage_type: str,
        coverage_value: str
    ):
        """Sync team roster"""
        try:
            # Delete existing roster entries for this coverage
            await self.session.execute(
                YahooRosterEntry.__table__.delete().where(
                    (YahooRosterEntry.team_key == team_key) &
                    (YahooRosterEntry.coverage_type == coverage_type) &
                    (YahooRosterEntry.coverage_value == coverage_value)
                )
            )
            
            # Insert new roster entries
            for player_data in players:
                # First sync the player
                await self.sync_player(player_data)
                
                # Then create roster entry
                selected_pos = player_data.get('selected_position', {})
                stmt = insert(YahooRosterEntry).values(
                    team_key=team_key,
                    player_key=player_data['player_key'],
                    selected_position=selected_pos.get('position'),
                    is_flex=selected_pos.get('is_flex', False),
                    coverage_type=coverage_type,
                    coverage_value=coverage_value
                )
                await self.session.execute(stmt)
                
            await self.session.commit()
            
        except Exception as e:
            logger.error(f"Error syncing roster: {e}")
            await self.session.rollback()
            raise
            
    async def sync_transaction(self, transaction_data: Dict[str, Any]) -> YahooTransaction:
        """Sync transaction data to database"""
        try:
            # Extract league_key from transaction_key
            transaction_key = transaction_data['transaction_key']
            parts = transaction_key.split('.')
            league_key = f"{parts[0]}.l.{parts[2]}"
            
            # Convert timestamp
            timestamp = None
            if 'timestamp' in transaction_data:
                timestamp = datetime.fromtimestamp(int(transaction_data['timestamp']))
                
            # Upsert transaction
            stmt = insert(YahooTransaction).values(
                transaction_key=transaction_key,
                transaction_id=transaction_data.get('transaction_id'),
                league_key=league_key,
                type=transaction_data['type'],
                status=transaction_data.get('status'),
                timestamp=timestamp,
                trader_team_key=transaction_data.get('trader_team_key'),
                tradee_team_key=transaction_data.get('tradee_team_key'),
                trade_note=transaction_data.get('trade_note'),
                waiver_priority=transaction_data.get('waiver_priority'),
                faab_bid=transaction_data.get('faab_bid'),
                players=transaction_data.get('players', [])
            )
            
            stmt = stmt.on_conflict_do_update(
                index_elements=['transaction_key'],
                set_=dict(
                    status=stmt.excluded.status,
                    updated_at=datetime.now()
                )
            )
            
            await self.session.execute(stmt)
            await self.session.commit()
            
            # Fetch and return the transaction
            result = await self.session.execute(
                select(YahooTransaction).where(
                    YahooTransaction.transaction_key == transaction_key
                )
            )
            return result.scalar_one()
            
        except Exception as e:
            logger.error(f"Error syncing transaction: {e}")
            await self.session.rollback()
            raise
            
    async def sync_player_stats(
        self,
        player_key: str,
        stats_data: Dict[str, Any],
        coverage_type: str,
        coverage_value: str,
        points: float = None
    ):
        """Sync player statistics"""
        try:
            # Upsert player stats
            stmt = insert(YahooPlayerStats).values(
                player_key=player_key,
                coverage_type=coverage_type,
                coverage_value=coverage_value,
                stats=stats_data,
                points=points
            )
            
            stmt = stmt.on_conflict_do_update(
                constraint='uq_player_stats_coverage',
                set_=dict(
                    stats=stmt.excluded.stats,
                    points=stmt.excluded.points,
                    updated_at=datetime.now()
                )
            )
            
            await self.session.execute(stmt)
            await self.session.commit()
            
        except Exception as e:
            logger.error(f"Error syncing player stats: {e}")
            await self.session.rollback()
            raise
            
    async def sync_user_token(
        self,
        user_guid: str,
        access_token: str,
        refresh_token: str,
        expires_at: datetime,
        user_info: Dict[str, Any] = None
    ) -> YahooUserToken:
        """Sync user OAuth token"""
        try:
            # Upsert user token
            stmt = insert(YahooUserToken).values(
                user_guid=user_guid,
                access_token=access_token,
                refresh_token=refresh_token,
                token_expires_at=expires_at,
                user_email=user_info.get('email') if user_info else None,
                user_nickname=user_info.get('nickname') if user_info else None
            )
            
            stmt = stmt.on_conflict_do_update(
                index_elements=['user_guid'],
                set_=dict(
                    access_token=stmt.excluded.access_token,
                    refresh_token=stmt.excluded.refresh_token,
                    token_expires_at=stmt.excluded.token_expires_at,
                    updated_at=datetime.now()
                )
            )
            
            await self.session.execute(stmt)
            await self.session.commit()
            
            # Fetch and return the token
            result = await self.session.execute(
                select(YahooUserToken).where(YahooUserToken.user_guid == user_guid)
            )
            return result.scalar_one()
            
        except Exception as e:
            logger.error(f"Error syncing user token: {e}")
            await self.session.rollback()
            raise
            
    async def get_user_token(self, user_guid: str) -> Optional[YahooUserToken]:
        """Get user token from database"""
        try:
            result = await self.session.execute(
                select(YahooUserToken).where(YahooUserToken.user_guid == user_guid)
            )
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(f"Error getting user token: {e}")
            return None