"""
Enhanced Yahoo Fantasy Sports API Client
Implements all resource types and collections from the Yahoo Fantasy Sports API
"""

import asyncio
import logging
import json
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from urllib.parse import urlencode, quote
import aiohttp
from enum import Enum

logger = logging.getLogger(__name__)


class YahooResourceType(Enum):
    """Yahoo Fantasy Sports resource types"""
    GAME = "game"
    LEAGUE = "league"
    TEAM = "team"
    PLAYER = "player"
    TRANSACTION = "transaction"
    USER = "user"
    ROSTER = "roster"


class YahooCollectionType(Enum):
    """Yahoo Fantasy Sports collection types"""
    GAMES = "games"
    LEAGUES = "leagues"
    TEAMS = "teams"
    PLAYERS = "players"
    TRANSACTIONS = "transactions"
    USERS = "users"


class YahooFantasyClient:
    """Enhanced Yahoo Fantasy Sports API Client"""
    
    def __init__(self, access_token: str, refresh_token: str = None):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.base_url = "https://fantasysports.yahooapis.com/fantasy/v2"
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    def _build_headers(self) -> Dict[str, str]:
        """Build request headers with OAuth2 token"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
    def _parse_resource_key(self, key: str) -> Dict[str, str]:
        """Parse Yahoo resource keys (e.g., '223.l.431.t.1')"""
        parts = key.split('.')
        result = {}
        
        if len(parts) >= 2:
            result['game_id'] = parts[0]
            
        if len(parts) >= 4 and parts[1] == 'l':
            result['league_id'] = parts[2]
            
        if len(parts) >= 6 and parts[3] == 't':
            result['team_id'] = parts[4]
            
        if len(parts) >= 3 and parts[1] == 'p':
            result['player_id'] = parts[2]
            
        return result
        
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Dict[str, Any] = None,
        data: Dict[str, Any] = None,
        xml_data: str = None
    ) -> Dict[str, Any]:
        """Make API request with error handling and retry logic"""
        if not self.session:
            self.session = aiohttp.ClientSession()
            
        url = f"{self.base_url}/{endpoint}"
        
        # Add format parameter for JSON response
        if params is None:
            params = {}
        params['format'] = 'json'
        
        headers = self._build_headers()
        
        # Handle XML data for PUT/POST requests
        if xml_data:
            headers['Content-Type'] = 'application/xml'
            
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                logger.debug(f"Making {method} request to: {url}")
                logger.debug(f"Params: {params}")
                
                async with self.session.request(
                    method,
                    url,
                    headers=headers,
                    params=params,
                    json=data if not xml_data else None,
                    data=xml_data.encode() if xml_data else None
                ) as response:
                    response_text = await response.text()
                    
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 401:
                        raise Exception("Unauthorized - Access token may be invalid or expired")
                    elif response.status == 429:
                        # Rate limited - wait and retry
                        retry_after = int(response.headers.get('Retry-After', retry_delay))
                        logger.warning(f"Rate limited. Waiting {retry_after} seconds...")
                        await asyncio.sleep(retry_after)
                        retry_delay *= 2
                        continue
                    else:
                        logger.error(f"API request failed: {response.status}")
                        logger.error(f"Response: {response_text[:500]}")
                        raise Exception(f"API request failed: {response.status}")
                        
            except aiohttp.ClientError as e:
                logger.error(f"Network error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    raise
                    
        raise Exception(f"Max retries ({max_retries}) exceeded")
        
    # Game Resource Methods
    async def get_game(self, game_key: str, sub_resources: List[str] = None) -> Dict[str, Any]:
        """Get game information"""
        endpoint = f"game/{game_key}"
        if sub_resources:
            endpoint += f";out={','.join(sub_resources)}"
        return await self._make_request("GET", endpoint)
        
    async def get_games(
        self, 
        game_keys: List[str] = None,
        is_available: bool = None,
        game_types: List[str] = None,
        game_codes: List[str] = None,
        seasons: List[int] = None
    ) -> Dict[str, Any]:
        """Get multiple games with filters"""
        endpoint = "games"
        params = {}
        
        if game_keys:
            endpoint += f";game_keys={','.join(game_keys)}"
        if is_available is not None:
            params['is_available'] = 1 if is_available else 0
        if game_types:
            params['game_types'] = ','.join(game_types)
        if game_codes:
            params['game_codes'] = ','.join(game_codes)
        if seasons:
            params['seasons'] = ','.join(map(str, seasons))
            
        return await self._make_request("GET", endpoint, params)
        
    # League Resource Methods
    async def get_league(
        self, 
        league_key: str, 
        sub_resources: List[str] = None
    ) -> Dict[str, Any]:
        """Get league information"""
        endpoint = f"league/{league_key}"
        if sub_resources:
            endpoint += f";out={','.join(sub_resources)}"
        return await self._make_request("GET", endpoint)
        
    async def get_league_settings(self, league_key: str) -> Dict[str, Any]:
        """Get league settings"""
        return await self._make_request("GET", f"league/{league_key}/settings")
        
    async def get_league_standings(self, league_key: str) -> Dict[str, Any]:
        """Get league standings"""
        return await self._make_request("GET", f"league/{league_key}/standings")
        
    async def get_league_scoreboard(self, league_key: str, week: int = None) -> Dict[str, Any]:
        """Get league scoreboard"""
        endpoint = f"league/{league_key}/scoreboard"
        params = {}
        if week:
            params['week'] = week
        return await self._make_request("GET", endpoint, params)
        
    async def get_league_transactions(
        self,
        league_key: str,
        transaction_types: List[str] = None,
        team_key: str = None,
        count: int = None
    ) -> Dict[str, Any]:
        """Get league transactions"""
        endpoint = f"league/{league_key}/transactions"
        params = {}
        
        if transaction_types:
            params['types'] = ','.join(transaction_types)
        if team_key:
            params['team_key'] = team_key
        if count:
            params['count'] = count
            
        return await self._make_request("GET", endpoint, params)
        
    # Team Resource Methods
    async def get_team(
        self, 
        team_key: str, 
        sub_resources: List[str] = None
    ) -> Dict[str, Any]:
        """Get team information"""
        endpoint = f"team/{team_key}"
        if sub_resources:
            endpoint += f";out={','.join(sub_resources)}"
        return await self._make_request("GET", endpoint)
        
    async def get_team_stats(
        self,
        team_key: str,
        type: str = "season",
        week: int = None,
        date: str = None
    ) -> Dict[str, Any]:
        """Get team statistics"""
        endpoint = f"team/{team_key}/stats"
        params = {"type": type}
        
        if week and type == "week":
            params['week'] = week
        if date and type == "date":
            params['date'] = date
            
        return await self._make_request("GET", endpoint, params)
        
    async def get_team_roster(
        self,
        team_key: str,
        week: int = None,
        date: str = None
    ) -> Dict[str, Any]:
        """Get team roster"""
        endpoint = f"team/{team_key}/roster"
        params = {}
        
        if week:
            params['week'] = week
        if date:
            params['date'] = date
            
        return await self._make_request("GET", endpoint, params)
        
    async def update_roster(
        self,
        team_key: str,
        coverage_type: str,
        coverage_value: Union[int, str],
        players: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Update team roster (set lineups)"""
        xml_data = f"""<?xml version="1.0"?>
<fantasy_content>
  <roster>
    <coverage_type>{coverage_type}</coverage_type>
    <{coverage_type}>{coverage_value}</{coverage_type}>
    <players>
"""
        for player in players:
            xml_data += f"""      <player>
        <player_key>{player['player_key']}</player_key>
        <position>{player['position']}</position>
      </player>
"""
        xml_data += """    </players>
  </roster>
</fantasy_content>"""
        
        return await self._make_request(
            "PUT",
            f"team/{team_key}/roster",
            xml_data=xml_data
        )
        
    async def get_team_matchups(
        self,
        team_key: str,
        weeks: List[int] = None
    ) -> Dict[str, Any]:
        """Get team matchups"""
        endpoint = f"team/{team_key}/matchups"
        if weeks:
            endpoint += f";weeks={','.join(map(str, weeks))}"
        return await self._make_request("GET", endpoint)
        
    # Player Resource Methods
    async def get_player(
        self,
        player_key: str,
        sub_resources: List[str] = None
    ) -> Dict[str, Any]:
        """Get player information"""
        endpoint = f"player/{player_key}"
        if sub_resources:
            endpoint += f";out={','.join(sub_resources)}"
        return await self._make_request("GET", endpoint)
        
    async def get_player_stats(
        self,
        player_key: str,
        type: str = "season",
        season: int = None,
        week: int = None,
        date: str = None
    ) -> Dict[str, Any]:
        """Get player statistics"""
        endpoint = f"player/{player_key}/stats"
        params = {"type": type}
        
        if season:
            params['season'] = season
        if week and type == "week":
            params['week'] = week
        if date and type == "date":
            params['date'] = date
            
        return await self._make_request("GET", endpoint, params)
        
    async def search_players(
        self,
        league_key: str,
        search: str = None,
        position: str = None,
        status: str = None,
        sort: str = None,
        sort_type: str = None,
        start: int = 0,
        count: int = 25
    ) -> Dict[str, Any]:
        """Search for players in a league context"""
        endpoint = f"league/{league_key}/players"
        params = {
            "start": start,
            "count": count
        }
        
        if search:
            params['search'] = search
        if position:
            params['position'] = position
        if status:
            params['status'] = status
        if sort:
            params['sort'] = sort
        if sort_type:
            params['sort_type'] = sort_type
            
        return await self._make_request("GET", endpoint, params)
        
    # Transaction Methods
    async def add_player(
        self,
        league_key: str,
        team_key: str,
        player_key: str
    ) -> Dict[str, Any]:
        """Add a player to team"""
        xml_data = f"""<fantasy_content>
  <transaction>
    <type>add</type>
    <player>
      <player_key>{player_key}</player_key>
      <transaction_data>
        <type>add</type>
        <destination_team_key>{team_key}</destination_team_key>
      </transaction_data>
    </player>
  </transaction>
</fantasy_content>"""
        
        return await self._make_request(
            "POST",
            f"league/{league_key}/transactions",
            xml_data=xml_data
        )
        
    async def drop_player(
        self,
        league_key: str,
        team_key: str,
        player_key: str
    ) -> Dict[str, Any]:
        """Drop a player from team"""
        xml_data = f"""<fantasy_content>
  <transaction>
    <type>drop</type>
    <player>
      <player_key>{player_key}</player_key>
      <transaction_data>
        <type>drop</type>
        <source_team_key>{team_key}</source_team_key>
      </transaction_data>
    </player>
  </transaction>
</fantasy_content>"""
        
        return await self._make_request(
            "POST",
            f"league/{league_key}/transactions",
            xml_data=xml_data
        )
        
    async def add_drop_players(
        self,
        league_key: str,
        team_key: str,
        add_player_key: str,
        drop_player_key: str,
        faab_bid: int = None
    ) -> Dict[str, Any]:
        """Add and drop players in single transaction"""
        faab_element = f"<faab_bid>{faab_bid}</faab_bid>" if faab_bid else ""
        
        xml_data = f"""<fantasy_content>
  <transaction>
    <type>add/drop</type>
    {faab_element}
    <players>
      <player>
        <player_key>{add_player_key}</player_key>
        <transaction_data>
          <type>add</type>
          <destination_team_key>{team_key}</destination_team_key>
        </transaction_data>
      </player>
      <player>
        <player_key>{drop_player_key}</player_key>
        <transaction_data>
          <type>drop</type>
          <source_team_key>{team_key}</source_team_key>
        </transaction_data>
      </player>
    </players>
  </transaction>
</fantasy_content>"""
        
        return await self._make_request(
            "POST",
            f"league/{league_key}/transactions",
            xml_data=xml_data
        )
        
    async def propose_trade(
        self,
        league_key: str,
        trader_team_key: str,
        tradee_team_key: str,
        trader_players: List[str],
        tradee_players: List[str],
        trade_note: str = ""
    ) -> Dict[str, Any]:
        """Propose a trade between teams"""
        players_xml = ""
        
        # Add trader's players
        for player_key in trader_players:
            players_xml += f"""      <player>
        <player_key>{player_key}</player_key>
        <transaction_data>
          <type>pending_trade</type>
          <source_team_key>{trader_team_key}</source_team_key>
          <destination_team_key>{tradee_team_key}</destination_team_key>
        </transaction_data>
      </player>
"""
        
        # Add tradee's players
        for player_key in tradee_players:
            players_xml += f"""      <player>
        <player_key>{player_key}</player_key>
        <transaction_data>
          <type>pending_trade</type>
          <source_team_key>{tradee_team_key}</source_team_key>
          <destination_team_key>{trader_team_key}</destination_team_key>
        </transaction_data>
      </player>
"""
        
        xml_data = f"""<?xml version='1.0'?>
<fantasy_content>
  <transaction>
    <type>pending_trade</type>
    <trader_team_key>{trader_team_key}</trader_team_key>
    <tradee_team_key>{tradee_team_key}</tradee_team_key>
    <trade_note>{trade_note}</trade_note>
    <players>
{players_xml}    </players>
  </transaction>
</fantasy_content>"""
        
        return await self._make_request(
            "POST",
            f"league/{league_key}/transactions",
            xml_data=xml_data
        )
        
    async def accept_trade(
        self,
        transaction_key: str,
        trade_note: str = ""
    ) -> Dict[str, Any]:
        """Accept a pending trade"""
        xml_data = f"""<?xml version='1.0'?>
<fantasy_content>
  <transaction>
    <transaction_key>{transaction_key}</transaction_key>
    <type>pending_trade</type>
    <action>accept</action>
    <trade_note>{trade_note}</trade_note>
  </transaction>
</fantasy_content>"""
        
        return await self._make_request(
            "PUT",
            f"transaction/{transaction_key}",
            xml_data=xml_data
        )
        
    async def reject_trade(
        self,
        transaction_key: str,
        trade_note: str = ""
    ) -> Dict[str, Any]:
        """Reject a pending trade"""
        xml_data = f"""<?xml version='1.0'?>
<fantasy_content>
  <transaction>
    <transaction_key>{transaction_key}</transaction_key>
    <type>pending_trade</type>
    <action>reject</action>
    <trade_note>{trade_note}</trade_note>
  </transaction>
</fantasy_content>"""
        
        return await self._make_request(
            "PUT",
            f"transaction/{transaction_key}",
            xml_data=xml_data
        )
        
    async def cancel_transaction(self, transaction_key: str) -> Dict[str, Any]:
        """Cancel a pending waiver claim or proposed trade"""
        return await self._make_request(
            "DELETE",
            f"transaction/{transaction_key}"
        )
        
    # User Methods
    async def get_user_games(self) -> Dict[str, Any]:
        """Get games for logged-in user"""
        return await self._make_request(
            "GET",
            "users;use_login=1/games"
        )
        
    async def get_user_leagues(
        self,
        game_keys: List[str] = None
    ) -> Dict[str, Any]:
        """Get leagues for logged-in user"""
        endpoint = "users;use_login=1/games"
        if game_keys:
            endpoint += f";game_keys={','.join(game_keys)}"
        endpoint += "/leagues"
        
        return await self._make_request("GET", endpoint)
        
    async def get_user_teams(self) -> Dict[str, Any]:
        """Get all teams for logged-in user"""
        return await self._make_request(
            "GET",
            "users;use_login=1/teams"
        )
        
    # Utility Methods
    def parse_response(self, response: Dict[str, Any]) -> Any:
        """Parse Yahoo API response to extract relevant data"""
        if 'fantasy_content' in response:
            return response['fantasy_content']
        return response
        
    def extract_collection(
        self,
        response: Dict[str, Any],
        collection_type: str
    ) -> List[Dict[str, Any]]:
        """Extract collection items from response"""
        content = self.parse_response(response)
        items = []
        
        if collection_type in content:
            collection = content[collection_type]
            # Yahoo API uses numeric keys for items
            for key, value in collection.items():
                if isinstance(value, dict) and key.isdigit():
                    items.append(value)
                    
        return items