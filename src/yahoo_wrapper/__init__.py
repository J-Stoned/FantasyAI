"""
Yahoo Fantasy API Wrapper for Fantasy AI Ultimate merged project
Enhanced with comprehensive error handling, caching, and all resource types
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
import os
from datetime import datetime, timedelta
import requests
from oauthlib.oauth2 import WebApplicationClient
import json
import base64
import secrets
from dotenv import load_dotenv

# Load environment variables - but don't override existing ones in production
# This prevents local .env from overriding Render's environment variables
load_dotenv(override=False)

from src.shared.models import PlayerStats, LeagueInfo, TeamInfo, SportType, Position
from .api_client import YahooFantasyClient
from .response_parser import YahooResponseParser
from .cache import create_cache, YahooAPICache
from .exceptions import (
    YahooFantasyError,
    YahooAuthenticationError,
    YahooTokenExpiredError,
    YahooErrorHandler
)

logger = logging.getLogger(__name__)

class YahooFantasyAPI:
    """Enhanced Yahoo Fantasy Sports API wrapper with caching and error handling"""
    
    def __init__(self, cache_type: str = "memory", cache_config: Dict[str, Any] = None):
        # Yahoo OAuth2 configuration - load from environment
        self.client_id = os.getenv("YAHOO_CLIENT_ID", "")
        self.client_secret = os.getenv("YAHOO_CLIENT_SECRET", "")
        self.redirect_uri = os.getenv("YAHOO_REDIRECT_URI", "http://localhost:8000/auth/callback")
        
        # Log the loaded configuration
        logger.info(f"Yahoo OAuth2 configuration loaded:")
        logger.info(f"  Client ID: {self.client_id[:10]}..." if self.client_id else "  Client ID: NOT SET")
        logger.info(f"  Redirect URI: {self.redirect_uri}")
        logger.info(f"  Environment: {os.getenv('ENVIRONMENT', 'not set')}")
        
        # Validate credentials
        if not self.client_id or not self.client_secret:
            logger.warning("Yahoo API credentials not found in environment variables!")
            logger.warning("Please set YAHOO_CLIENT_ID and YAHOO_CLIENT_SECRET in your .env file")
        
        # OAuth2 state management
        self.oauth_client = WebApplicationClient(self.client_id)
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
        
        # API endpoints
        self.auth_url = "https://api.login.yahoo.com/oauth2/request_auth"
        self.token_url = "https://api.login.yahoo.com/oauth2/get_token"
        self.base_url = "https://fantasysports.yahooapis.com/fantasy/v2"
        
        # Initialize enhanced components
        self.api_client = None
        self.cache = create_cache(cache_type, **(cache_config or {}))
        self.parser = YahooResponseParser()
        
        logger.info(f"Yahoo OAuth2 API wrapper initialized with {cache_type} cache")
    
    def get_authorization_url(self) -> str:
        """Generate Yahoo OAuth2 authorization URL"""
        try:
            # Generate state parameter for security
            state = secrets.token_urlsafe(32)
            
            # Store state for verification (in production, use Redis/database)
            # For now, we'll store it in memory
            self._pending_state = state
            
            # Build the real Yahoo OAuth2 authorization URL with all required parameters
            auth_params = {
                'client_id': self.client_id,
                'redirect_uri': self.redirect_uri,
                'response_type': 'code',
                'state': state,
                'scope': 'fspt-r',  # Fantasy Sports read access - REQUIRED
                'language': 'en-us',
                'nonce': secrets.token_urlsafe(16)  # Additional security
            }
            
            # Log parameters for debugging
            logger.debug("OAuth2 parameters:")
            for key, value in auth_params.items():
                if key == 'client_id':
                    logger.debug(f"  {key}: {value[:20]}...")
                else:
                    logger.debug(f"  {key}: {value}")
            
            # Properly encode URL parameters
            from urllib.parse import urlencode
            encoded_params = urlencode(auth_params)
            auth_url = f"{self.auth_url}?{encoded_params}"
            
            logger.info("Generated real Yahoo OAuth2 authorization URL")
            logger.info(f"Auth URL: {auth_url[:100]}...")
            logger.debug(f"Full Auth URL: {auth_url}")
            
            return auth_url
            
        except Exception as e:
            logger.error(f"Error generating authorization URL: {e}")
            raise
    
    def test_oauth2_configuration(self) -> Dict[str, Any]:
        """Test OAuth2 configuration and return diagnostic information"""
        try:
            # Test basic configuration
            config_info = {
                "client_id": self.client_id[:20] + "..." if len(self.client_id) > 20 else self.client_id,
                "client_secret": "***" + self.client_secret[-4:] if self.client_secret else "None",
                "redirect_uri": self.redirect_uri,
                "auth_url": self.auth_url,
                "token_url": self.token_url,
                "base_url": self.base_url
            }
            
            # Test URL generation
            try:
                auth_url = self.get_authorization_url()
                config_info["auth_url_generated"] = True
                config_info["auth_url_length"] = len(auth_url)
                config_info["auth_url_sample"] = auth_url[:100] + "..." if len(auth_url) > 100 else auth_url
            except Exception as e:
                config_info["auth_url_generated"] = False
                config_info["auth_url_error"] = str(e)
            
            # Test client ID format
            config_info["client_id_length"] = len(self.client_id) if self.client_id else 0
            config_info["client_id_contains_special_chars"] = any(c in self.client_id for c in ['+', '/', '=']) if self.client_id else False
            
            logger.info(f"OAuth2 configuration test results: {config_info}")
            return config_info
            
        except Exception as e:
            logger.error(f"Error testing OAuth2 configuration: {e}")
            return {"error": str(e)}
    
    async def exchange_code_for_token(self, authorization_code: str, state: str) -> bool:
        """Exchange authorization code for access token"""
        try:
            # Verify state parameter
            if not hasattr(self, '_pending_state') or state != self._pending_state:
                logger.error("Invalid state parameter")
                return False
            
            # Prepare token request for real Yahoo API
            token_data = {
                'grant_type': 'authorization_code',
                'code': authorization_code,
                'redirect_uri': self.redirect_uri,
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            logger.info("Exchanging authorization code for access token...")
            
            # Make token request
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.post(self.token_url, headers=headers, data=token_data) as response:
                    response_text = await response.text()
                    logger.debug(f"Token response status: {response.status}")
                    logger.debug(f"Token response: {response_text[:200]}...")
                    
                    if response.status == 200:
                        token_response = await response.json()
                        
                        # Store tokens
                        self.access_token = token_response.get('access_token')
                        self.refresh_token = token_response.get('refresh_token')
                        
                        # Calculate expiration
                        expires_in = token_response.get('expires_in', 3600)
                        self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
                        
                        logger.info("Successfully obtained access token from Yahoo")
                        logger.info(f"Token expires at: {self.token_expires_at}")
                        
                        # Clear pending state
                        delattr(self, '_pending_state')
                        
                        return True
                    else:
                        logger.error(f"Token exchange failed: {response.status}")
                        logger.error(f"Error response: {response_text}")
                        
                        # Parse error response if possible
                        try:
                            error_data = json.loads(response_text)
                            error_desc = error_data.get('error_description', 'Unknown error')
                            logger.error(f"OAuth error: {error_desc}")
                        except:
                            pass
                        
                        return False
                        
        except Exception as e:
            logger.error(f"Error exchanging code for token: {e}")
            return False
    
    async def refresh_access_token(self) -> bool:
        """Refresh the access token using refresh token"""
        try:
            if not self.refresh_token:
                logger.error("No refresh token available")
                return False
            
            # Prepare refresh request
            refresh_data = {
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token
            }
            
            # Encode credentials
            credentials = f"{self.client_id}:{self.client_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                'Authorization': f'Basic {encoded_credentials}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            logger.info("Refreshing access token...")
            
            # Make refresh request
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.post(self.token_url, headers=headers, data=refresh_data) as response:
                    if response.status == 200:
                        token_response = await response.json()
                        
                        # Update tokens
                        self.access_token = token_response.get('access_token')
                        if 'refresh_token' in token_response:
                            self.refresh_token = token_response.get('refresh_token')
                        
                        # Update expiration
                        expires_in = token_response.get('expires_in', 3600)
                        self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
                        
                        logger.info("Successfully refreshed access token")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Token refresh failed: {response.status} - {error_text}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error refreshing access token: {e}")
            return False
    
    async def ensure_valid_token(self) -> bool:
        """Ensure we have a valid access token"""
        try:
            # Check if token exists and is not expired
            if self.access_token and self.token_expires_at:
                # Add 5 minute buffer before expiration
                if datetime.now() < (self.token_expires_at - timedelta(minutes=5)):
                    logger.info("Access token is still valid")
                    return True
                else:
                    logger.info("Access token expired, refreshing...")
                    return await self.refresh_access_token()
            else:
                logger.warning("No access token available")
                return False
                
        except Exception as e:
            logger.error(f"Error ensuring valid token: {e}")
            return False
    
    async def _get_api_client(self) -> YahooFantasyClient:
        """Get or create API client instance"""
        if not self.api_client and self.access_token:
            self.api_client = YahooFantasyClient(self.access_token, self.refresh_token)
        elif self.api_client and self.access_token:
            # Update token if changed
            self.api_client.access_token = self.access_token
            self.api_client.refresh_token = self.refresh_token
        return self.api_client
    
    async def authenticate(self):
        """Authenticate with Yahoo Fantasy API"""
        try:
            logger.info("Starting Yahoo OAuth2 authentication...")
            
            # Check if we already have a valid token
            if await self.ensure_valid_token():
                logger.info("Already have valid access token")
                return True
            
            # If no valid token, user needs to go through OAuth flow
            logger.warning("No valid access token. User needs to authorize the application.")
            logger.info("Use get_authorization_url() to start OAuth flow")
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to authenticate with Yahoo API: {e}")
            raise
    
    async def get_user_leagues(self) -> List[Dict[str, Any]]:
        """Get user's Yahoo Fantasy leagues with caching"""
        try:
            logger.info("Starting get_user_leagues request")
            
            # Check cache first
            cache_key = "user_leagues"
            cached_data = await self.cache.get("leagues", cache_key, {"game_keys": "nfl,nba,mlb,nhl"})
            if cached_data:
                logger.info("Returning cached user leagues data")
                return cached_data
            
            # Ensure we have a valid token
            if not await self.ensure_valid_token():
                logger.error("No valid access token for API request")
                return []
            
            # Get API client
            client = await self._get_api_client()
            if not client:
                logger.error("Failed to get API client")
                return []
            
            try:
                logger.info("Making Yahoo API call for user leagues...")
                async with client:
                    response = await client.get_user_leagues()
                    
                    # Parse response
                    leagues = self.parser.extract_collection(response, 'leagues')
                    
                    if leagues:
                        logger.info(f"Successfully retrieved {len(leagues)} leagues")
                        # Cache the result
                        await self.cache.set("leagues", cache_key, leagues, {"game_keys": "nfl,nba,mlb,nhl"})
                        return leagues
                    else:
                        logger.warning("No leagues found in response")
                        return []
                        
            except YahooFantasyError as e:
                logger.error(f"Yahoo API error: {e}")
                if YahooErrorHandler.is_retryable(e):
                    logger.info("Error is retryable")
                raise
            except Exception as e:
                logger.error(f"Unexpected error getting leagues: {e}")
                raise
            
        except Exception as e:
            logger.error(f"Error getting user leagues: {e}")
            # Return empty list instead of raising for backwards compatibility
            return []
    
    async def get_league_info(self, league_id: str) -> Dict[str, Any]:
        """Get specific league information"""
        try:
            # Ensure we have a valid token
            if not await self.ensure_valid_token():
                logger.error("No valid access token for API request")
                return {}
            
            # Get real data from Yahoo
            logger.info(f"Getting league info for ID: {league_id}")
            response = await self._make_api_request(f"league/{league_id}")
            
            if response and 'fantasy_content' in response:
                league_info = self._parse_yahoo_league_response(response)
                if league_info:
                    logger.info(f"Successfully loaded league data for {league_id}")
                    return league_info
                else:
                    logger.error(f"Failed to parse league data for {league_id}")
                    return {}
            else:
                logger.error(f"Invalid response format for league {league_id}")
                return {}
            
        except Exception as e:
            logger.error(f"Error getting league info: {e}")
            raise
    
    async def get_league_players(self, league_id: str) -> List[Dict[str, Any]]:
        """Get all players in a league"""
        try:
            # Check if we're using mock OAuth2 flow
            if self.access_token and self.access_token.startswith("mock_"):
                logger.info(f"Using mock OAuth2 flow - returning mock players data for league {league_id}")
                return self._get_mock_players(league_id)
            
            # Ensure we have a valid token
            if not await self.ensure_valid_token():
                logger.error("No valid access token for API request")
                return self._get_mock_players(league_id)
            
            # Try to get real data first
            try:
                logger.info(f"Attempting to get real players for league ID: {league_id}")
                response = await self._make_api_request(f"league/{league_id}/players")
                
                if response and 'fantasy_content' in response:
                    players = self._parse_yahoo_players_response(response)
                    if players:
                        logger.info(f"Successfully loaded {len(players)} real players")
                        return players
            except Exception as e:
                logger.warning(f"Failed to get real Yahoo players data: {e}")
            
            # Fallback to mock data
            logger.info(f"Using mock data for league {league_id} players")
            return self._get_mock_players(league_id)
            
        except Exception as e:
            logger.error(f"Error getting league players: {e}")
            raise
    
    async def _make_api_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make API request to Yahoo Fantasy Sports"""
        try:
            # Normal OAuth2 Bearer token flow
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Accept": "application/json"
            }
            
            url = f"{self.base_url}/{endpoint}"
            
            # Add format parameter for JSON response
            if params is None:
                params = {}
            params['format'] = 'json'
            
            logger.debug(f"Making API request to: {url}")
            logger.debug(f"With params: {params}")
            
            # Use aiohttp for async HTTP requests
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    response_text = await response.text()
                    logger.debug(f"Response status: {response.status}")
                    
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Yahoo API request failed: {response.status}")
                        logger.error(f"Error response: {response_text[:500]}...")
                        
                        # Handle specific error codes
                        if response.status == 401:
                            raise Exception("Unauthorized - Access token may be invalid or expired")
                        elif response.status == 404:
                            raise Exception(f"Resource not found: {endpoint}")
                        else:
                            raise Exception(f"API request failed: {response.status} - {response_text[:200]}")
                
        except Exception as e:
            logger.error(f"API request error: {e}")
            raise
    
    def _parse_yahoo_leagues_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse Yahoo Fantasy API leagues response"""
        leagues = []
        
        try:
            fantasy_content = response.get('fantasy_content', {})
            users = fantasy_content.get('users', {})
            
            # Navigate through Yahoo's nested structure
            for user_key, user_data in users.items():
                if isinstance(user_data, dict) and 'games' in user_data:
                    games = user_data['games']
                    
                    for game_key, game_data in games.items():
                        if isinstance(game_data, dict) and 'leagues' in game_data:
                            leagues_data = game_data['leagues']
                            
                            for league_key, league_data in leagues_data.items():
                                if isinstance(league_data, dict) and 'league' in league_data:
                                    league = league_data['league']
                                    
                                    # Extract league information
                                    league_info = {
                                        "league_id": league.get('league_id', ''),
                                        "name": league.get('name', ''),
                                        "sport": league.get('game_code', '').lower(),
                                        "season": league.get('season', ''),
                                        "num_teams": len(league.get('teams', {})),
                                        "scoring_type": league.get('scoring_type', 'standard'),
                                        "draft_type": league.get('draft_type', 'snake')
                                    }
                                    
                                    leagues.append(league_info)
            
            return leagues
            
        except Exception as e:
            logger.error(f"Error parsing Yahoo leagues response: {e}")
            return []
    
    def _parse_yahoo_league_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Yahoo Fantasy API single league response"""
        try:
            fantasy_content = response.get('fantasy_content', {})
            league_data = fantasy_content.get('league', {})
            
            if league_data:
                league_info = {
                    "league_id": league_data.get('league_id', ''),
                    "name": league_data.get('name', ''),
                    "sport": league_data.get('game_code', '').lower(),
                    "season": league_data.get('season', ''),
                    "num_teams": len(league_data.get('teams', {})),
                    "scoring_type": league_data.get('scoring_type', 'standard'),
                    "draft_type": league_data.get('draft_type', 'snake'),
                    "settings": {
                        "roster_positions": league_data.get('roster_positions', ["QB", "RB", "RB", "WR", "WR", "TE", "FLEX", "K", "DEF"]),
                        "bench_slots": league_data.get('bench_slots', 6),
                        "ir_slots": league_data.get('ir_slots', 1)
                    }
                }
                
                return league_info
            
            return None
            
        except Exception as e:
            logger.error(f"Error parsing Yahoo league response: {e}")
            return None
    
    def _parse_yahoo_players_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse Yahoo Fantasy API players response"""
        players = []
        
        try:
            fantasy_content = response.get('fantasy_content', {})
            league_data = fantasy_content.get('league', {})
            
            if league_data and 'players' in league_data:
                players_data = league_data['players']
                
                for player_key, player_data in players_data.items():
                    if isinstance(player_data, dict) and 'player' in player_data:
                        player = player_data['player']
                        
                        # Extract player information
                        player_info = {
                            "player_id": player.get('player_id', ''),
                            "name": player.get('name', {}).get('full', ''),
                            "position": player.get('display_position', ''),
                            "team": player.get('editorial_team_abbr', ''),
                            "league_id": league_data.get('league_id', ''),
                            "points": float(player.get('player_points', {}).get('total', 0)),
                            "games_played": int(player.get('player_stats', {}).get('games_played', 0)),
                            "avg_points": float(player.get('player_points', {}).get('total', 0)) / max(int(player.get('player_stats', {}).get('games_played', 1)), 1),
                            "stats": player.get('player_stats', {})
                        }
                        
                        players.append(player_info)
            
            return players
            
        except Exception as e:
            logger.error(f"Error parsing Yahoo players response: {e}")
            return []
    
    # Mock data methods for fallback
    def _get_mock_leagues(self) -> List[Dict[str, Any]]:
        """Get mock league data"""
        return [
            {
                "league_id": "123456",
                "name": "Fantasy Football League 2024",
                "sport": "nfl",
                "season": 2024,
                "num_teams": 12,
                "scoring_type": "standard",
                "draft_type": "snake"
            },
            {
                "league_id": "789012",
                "name": "Basketball Dynasty League",
                "sport": "nba",
                "season": 2024,
                "num_teams": 10,
                "scoring_type": "points",
                "draft_type": "auction"
            }
        ]
    
    def _get_mock_league_info(self, league_id: str) -> Dict[str, Any]:
        """Get mock league info"""
        return {
            "league_id": league_id,
            "name": f"League {league_id}",
            "sport": "nfl",
            "season": 2024,
            "num_teams": 12,
            "scoring_type": "standard",
            "draft_type": "snake",
            "settings": {
                "roster_positions": ["QB", "RB", "RB", "WR", "WR", "TE", "FLEX", "K", "DEF"],
                "bench_slots": 6,
                "ir_slots": 1
            }
        }
    
    def _get_mock_players(self, league_id: str) -> List[Dict[str, Any]]:
        """Get mock player data"""
        return [
            {
                "player_id": "12345",
                "name": "Patrick Mahomes",
                "position": "QB",
                "team": "KC",
                "league_id": league_id,
                "points": 285.5,
                "games_played": 8,
                "avg_points": 35.7,
                "stats": {
                    "passing_yards": 2456,
                    "passing_tds": 18,
                    "interceptions": 3,
                    "rushing_yards": 156,
                    "rushing_tds": 2
                }
            },
            {
                "player_id": "67890",
                "name": "Christian McCaffrey",
                "position": "RB",
                "team": "SF",
                "league_id": league_id,
                "points": 245.8,
                "games_played": 8,
                "avg_points": 30.7,
                "stats": {
                    "rushing_yards": 825,
                    "rushing_tds": 8,
                    "receiving_yards": 456,
                    "receiving_tds": 3,
                    "receptions": 38
                }
            }
        ]
    
    # Keep existing methods for compatibility
    async def get_player_stats(self, player_id: str, league_id: str) -> Dict[str, Any]:
        """Get detailed stats for a specific player"""
        try:
            # Check if we're using mock OAuth2 flow
            if self.access_token and self.access_token.startswith("mock_"):
                logger.info(f"Using mock OAuth2 flow - returning mock player stats for {player_id}")
                return self._get_mock_player_stats(player_id, league_id)
            
            if not await self.ensure_valid_token():
                return self._get_mock_player_stats(player_id, league_id)
            
            # Try real API call
            try:
                response = await self._make_api_request(f"player/{player_id}/stats")
                if response and 'fantasy_content' in response:
                    return self._parse_yahoo_player_stats_response(response)
            except Exception as e:
                logger.warning(f"Failed to get real player stats: {e}")
            
            return self._get_mock_player_stats(player_id, league_id)
            
        except Exception as e:
            logger.error(f"Error getting player stats: {e}")
            raise
    
    def _get_mock_player_stats(self, player_id: str, league_id: str) -> Dict[str, Any]:
        """Get mock player stats"""
        return {
            "player_id": player_id,
            "name": "Player Name",
            "position": "QB",
            "team": "TEAM",
            "league_id": league_id,
            "points": 200.0,
            "games_played": 8,
            "avg_points": 25.0,
            "stats": {
                "passing_yards": 2000,
                "passing_tds": 15,
                "interceptions": 5,
                "rushing_yards": 100,
                "rushing_tds": 1
            },
            "recent_games": [
                {"week": 8, "points": 28.5, "opponent": "BUF"},
                {"week": 7, "points": 22.1, "opponent": "NE"},
                {"week": 6, "points": 31.2, "opponent": "NYJ"}
            ]
        }
    
    def _parse_yahoo_player_stats_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Yahoo player stats response"""
        try:
            fantasy_content = response.get('fantasy_content', {})
            player_data = fantasy_content.get('player', {})
            
            if player_data:
                return {
                    "player_id": player_data.get('player_id', ''),
                    "name": player_data.get('name', {}).get('full', ''),
                    "position": player_data.get('display_position', ''),
                    "team": player_data.get('editorial_team_abbr', ''),
                    "points": float(player_data.get('player_points', {}).get('total', 0)),
                    "games_played": int(player_data.get('player_stats', {}).get('games_played', 0)),
                    "avg_points": float(player_data.get('player_points', {}).get('total', 0)) / max(int(player_data.get('player_stats', {}).get('games_played', 1)), 1),
                    "stats": player_data.get('player_stats', {})
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error parsing Yahoo player stats response: {e}")
            return None
    
    async def get_player_history(self, player_id: str, league_id: str) -> List[Dict[str, Any]]:
        """Get historical performance data for a player"""
        try:
            # Check if we're using mock OAuth2 flow
            if self.access_token and self.access_token.startswith("mock_"):
                logger.info(f"Using mock OAuth2 flow - returning mock player history for {player_id}")
                return self._get_mock_player_history(player_id, league_id)
            
            if not await self.ensure_valid_token():
                return self._get_mock_player_history(player_id, league_id)
            
            # Try real API call
            try:
                response = await self._make_api_request(f"player/{player_id}/stats;type=week")
                if response and 'fantasy_content' in response:
                    return self._parse_yahoo_player_history_response(response)
            except Exception as e:
                logger.warning(f"Failed to get real player history: {e}")
            
            return self._get_mock_player_history(player_id, league_id)
            
        except Exception as e:
            logger.error(f"Error getting player history: {e}")
            raise
    
    def _get_mock_player_history(self, player_id: str, league_id: str) -> List[Dict[str, Any]]:
        """Get mock player history"""
        return [
            {"week": 1, "points": 25.5, "opponent": "DAL"},
            {"week": 2, "points": 18.2, "opponent": "PHI"},
            {"week": 3, "points": 32.1, "opponent": "WAS"},
            {"week": 4, "points": 22.8, "opponent": "NYG"},
            {"week": 5, "points": 28.9, "opponent": "DAL"},
            {"week": 6, "points": 19.4, "opponent": "PHI"},
            {"week": 7, "points": 31.2, "opponent": "WAS"},
            {"week": 8, "points": 26.7, "opponent": "NYG"}
        ]
    
    def _parse_yahoo_player_history_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse Yahoo player history response"""
        history = []
        
        try:
            fantasy_content = response.get('fantasy_content', {})
            player_data = fantasy_content.get('player', {})
            
            if player_data and 'player_stats' in player_data:
                stats = player_data['player_stats']
                
                # Parse weekly stats
                for week_key, week_data in stats.items():
                    if isinstance(week_data, dict) and 'stats' in week_data:
                        week_stats = week_data['stats']
                        
                        # Extract points and opponent
                        points = float(week_stats.get('points', 0))
                        opponent = week_stats.get('opponent', '')
                        
                        history.append({
                            "week": int(week_key),
                            "points": points,
                            "opponent": opponent
                        })
            
            return history
            
        except Exception as e:
            logger.error(f"Error parsing Yahoo player history response: {e}")
            return []
    
    async def get_team_info(self, team_id: str, league_id: str) -> Dict[str, Any]:
        """Get team information and roster"""
        try:
            # Check if we're using mock OAuth2 flow
            if self.access_token and self.access_token.startswith("mock_"):
                logger.info(f"Using mock OAuth2 flow - returning mock team info for {team_id}")
                return self._get_mock_team_info(team_id, league_id)
            
            if not await self.ensure_valid_token():
                return self._get_mock_team_info(team_id, league_id)
            
            # Try real API call
            try:
                response = await self._make_api_request(f"team/{team_id}")
                if response and 'fantasy_content' in response:
                    return self._parse_yahoo_team_response(response)
            except Exception as e:
                logger.warning(f"Failed to get real team info: {e}")
            
            return self._get_mock_team_info(team_id, league_id)
            
        except Exception as e:
            logger.error(f"Error getting team info: {e}")
            raise
    
    def _get_mock_team_info(self, team_id: str, league_id: str) -> Dict[str, Any]:
        """Get mock team info"""
        return {
            "team_id": team_id,
            "name": f"Team {team_id}",
            "owner": "Team Owner",
            "league_id": league_id,
            "wins": 6,
            "losses": 2,
            "ties": 0,
            "points_for": 1250.5,
            "points_against": 1180.2,
            "players": [
                {
                    "player_id": "12345",
                    "name": "Patrick Mahomes",
                    "position": "QB",
                    "team": "KC",
                    "points": 285.5,
                    "avg_points": 35.7
                },
                {
                    "player_id": "67890",
                    "name": "Christian McCaffrey",
                    "position": "RB",
                    "team": "SF",
                    "points": 245.8,
                    "avg_points": 30.7
                }
            ]
        }
    
    def _parse_yahoo_team_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Yahoo team response"""
        try:
            fantasy_content = response.get('fantasy_content', {})
            team_data = fantasy_content.get('team', {})
            
            if team_data:
                return {
                    "team_id": team_data.get('team_id', ''),
                    "name": team_data.get('name', ''),
                    "owner": team_data.get('managers', {}).get('manager', {}).get('nickname', ''),
                    "league_id": team_data.get('league_id', ''),
                    "wins": int(team_data.get('team_standings', {}).get('outcome_totals', {}).get('wins', 0)),
                    "losses": int(team_data.get('team_standings', {}).get('outcome_totals', {}).get('losses', 0)),
                    "ties": int(team_data.get('team_standings', {}).get('outcome_totals', {}).get('ties', 0)),
                    "points_for": float(team_data.get('team_standings', {}).get('points_for', 0)),
                    "points_against": float(team_data.get('team_standings', {}).get('points_against', 0)),
                    "players": self._parse_team_players(team_data.get('roster', {}))
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error parsing Yahoo team response: {e}")
            return None
    
    def _parse_team_players(self, roster_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse team roster players"""
        players = []
        
        try:
            if roster_data and '0' in roster_data:
                players_data = roster_data['0']['players']
                
                for player_key, player_data in players_data.items():
                    if isinstance(player_data, dict) and 'player' in player_data:
                        player = player_data['player']
                        
                        players.append({
                            "player_id": player.get('player_id', ''),
                            "name": player.get('name', {}).get('full', ''),
                            "position": player.get('display_position', ''),
                            "team": player.get('editorial_team_abbr', ''),
                            "points": float(player.get('player_points', {}).get('total', 0)),
                            "avg_points": float(player.get('player_points', {}).get('total', 0)) / max(int(player.get('player_stats', {}).get('games_played', 1)), 1)
                        })
            
            return players
            
        except Exception as e:
            logger.error(f"Error parsing team players: {e}")
            return []
    
    async def get_league_stats(self, league_id: str) -> Dict[str, Any]:
        """Get comprehensive league statistics"""
        try:
            # Check if we're using mock OAuth2 flow
            if self.access_token and self.access_token.startswith("mock_"):
                logger.info(f"Using mock OAuth2 flow - returning mock league stats for {league_id}")
                return self._get_mock_league_stats(league_id)
            
            if not await self.ensure_valid_token():
                return self._get_mock_league_stats(league_id)
            
            # Try real API call
            try:
                response = await self._make_api_request(f"league/{league_id}/standings")
                if response and 'fantasy_content' in response:
                    return self._parse_yahoo_league_stats_response(response)
            except Exception as e:
                logger.warning(f"Failed to get real league stats: {e}")
            
            return self._get_mock_league_stats(league_id)
            
        except Exception as e:
            logger.error(f"Error getting league stats: {e}")
            raise
    
    # New enhanced methods using the API client
    async def get_league_transactions(
        self, 
        league_id: str,
        transaction_types: List[str] = None,
        team_key: str = None,
        count: int = 25
    ) -> List[Dict[str, Any]]:
        """Get league transactions with filtering"""
        try:
            if not await self.ensure_valid_token():
                return []
                
            client = await self._get_api_client()
            if not client:
                return []
                
            async with client:
                response = await client.get_league_transactions(
                    league_id,
                    transaction_types=transaction_types,
                    team_key=team_key,
                    count=count
                )
                
                transactions = self.parser.extract_collection(response, 'transactions')
                return transactions
                
        except Exception as e:
            logger.error(f"Error getting league transactions: {e}")
            return []
    
    async def update_roster(
        self,
        team_key: str,
        roster_changes: List[Dict[str, str]],
        coverage_type: str = "week",
        coverage_value: Union[int, str] = None
    ) -> bool:
        """Update team roster (set lineups)"""
        try:
            if not await self.ensure_valid_token():
                raise YahooAuthenticationError("No valid access token")
                
            client = await self._get_api_client()
            if not client:
                raise YahooFantasyError("Failed to get API client")
                
            # Use current week/date if not specified
            if not coverage_value:
                if coverage_type == "week":
                    # Get current week from league info
                    league_key = team_key.rsplit('.t.', 1)[0]
                    league_info = await self.get_league_info(league_key)
                    coverage_value = league_info.get('current_week', 1)
                else:
                    coverage_value = datetime.now().strftime("%Y-%m-%d")
                    
            async with client:
                response = await client.update_roster(
                    team_key,
                    coverage_type,
                    coverage_value,
                    roster_changes
                )
                
                return response is not None
                
        except Exception as e:
            logger.error(f"Error updating roster: {e}")
            raise
    
    async def add_player(self, league_key: str, team_key: str, player_key: str) -> Dict[str, Any]:
        """Add a player to team"""
        try:
            if not await self.ensure_valid_token():
                raise YahooAuthenticationError("No valid access token")
                
            client = await self._get_api_client()
            if not client:
                raise YahooFantasyError("Failed to get API client")
                
            async with client:
                response = await client.add_player(league_key, team_key, player_key)
                return self.parser.parse_transaction(response)
                
        except Exception as e:
            logger.error(f"Error adding player: {e}")
            raise
    
    async def drop_player(self, league_key: str, team_key: str, player_key: str) -> Dict[str, Any]:
        """Drop a player from team"""
        try:
            if not await self.ensure_valid_token():
                raise YahooAuthenticationError("No valid access token")
                
            client = await self._get_api_client()
            if not client:
                raise YahooFantasyError("Failed to get API client")
                
            async with client:
                response = await client.drop_player(league_key, team_key, player_key)
                return self.parser.parse_transaction(response)
                
        except Exception as e:
            logger.error(f"Error dropping player: {e}")
            raise
    
    async def search_players(
        self,
        league_key: str,
        search: str = None,
        position: str = None,
        status: str = "A",  # Available players
        sort: str = "AR",   # By rank
        start: int = 0,
        count: int = 25
    ) -> List[Dict[str, Any]]:
        """Search for players in league context"""
        try:
            # Check cache
            cache_params = {
                "search": search,
                "position": position,
                "status": status,
                "sort": sort,
                "start": start,
                "count": count
            }
            
            cached_data = await self.cache.get("player_search", league_key, cache_params)
            if cached_data:
                return cached_data
                
            if not await self.ensure_valid_token():
                return []
                
            client = await self._get_api_client()
            if not client:
                return []
                
            async with client:
                response = await client.search_players(
                    league_key,
                    search=search,
                    position=position,
                    status=status,
                    sort=sort,
                    start=start,
                    count=count
                )
                
                players = self.parser.extract_collection(response, 'players')
                
                # Cache results
                await self.cache.set("player_search", league_key, players, cache_params, ttl=300)
                
                return players
                
        except Exception as e:
            logger.error(f"Error searching players: {e}")
            return []
    
    async def get_scoreboard(self, league_key: str, week: int = None) -> Dict[str, Any]:
        """Get league scoreboard for a specific week"""
        try:
            if not await self.ensure_valid_token():
                return {}
                
            client = await self._get_api_client()
            if not client:
                return {}
                
            async with client:
                response = await client.get_league_scoreboard(league_key, week)
                
                # Parse matchups
                content = self.parser.extract_content(response)
                if 'league' in content and 'scoreboard' in content['league']:
                    return content['league']['scoreboard']
                    
                return {}
                
        except Exception as e:
            logger.error(f"Error getting scoreboard: {e}")
            return {}
    
    async def close(self):
        """Close API connections and cache"""
        try:
            if self.api_client:
                await self.api_client.__aexit__(None, None, None)
            await self.cache.close()
        except Exception as e:
            logger.error(f"Error closing API connections: {e}")
    
    def _get_mock_league_stats(self, league_id: str) -> Dict[str, Any]:
        """Get mock league stats"""
        return {
            "league_id": league_id,
            "teams": [
                {
                    "team_id": "team1",
                    "name": "Team Alpha",
                    "wins": 7,
                    "losses": 1,
                    "points_for": 1350.5,
                    "points_against": 1200.2
                },
                {
                    "team_id": "team2",
                    "name": "Team Beta",
                    "wins": 6,
                    "losses": 2,
                    "points_for": 1280.3,
                    "points_against": 1180.5
                }
            ],
            "players": [
                {
                    "player_id": "12345",
                    "name": "Patrick Mahomes",
                    "position": "QB",
                    "points": 285.5,
                    "avg_points": 35.7
                },
                {
                    "player_id": "67890",
                    "name": "Christian McCaffrey",
                    "position": "RB",
                    "points": 245.8,
                    "avg_points": 30.7
                }
            ],
            "top_scorers": [
                {"player_id": "12345", "name": "Patrick Mahomes", "points": 285.5},
                {"player_id": "67890", "name": "Christian McCaffrey", "points": 245.8}
            ]
        }
    
    def _parse_yahoo_league_stats_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Yahoo league stats response"""
        try:
            fantasy_content = response.get('fantasy_content', {})
            league_data = fantasy_content.get('league', {})
            
            if league_data:
                teams = []
                players = []
                
                # Parse teams
                if 'standings' in league_data:
                    standings = league_data['standings']
                    for team_key, team_data in standings.items():
                        if isinstance(team_data, dict) and 'team' in team_data:
                            team = team_data['team']
                            teams.append({
                                "team_id": team.get('team_id', ''),
                                "name": team.get('name', ''),
                                "wins": int(team.get('team_standings', {}).get('outcome_totals', {}).get('wins', 0)),
                                "losses": int(team.get('team_standings', {}).get('outcome_totals', {}).get('losses', 0)),
                                "points_for": float(team.get('team_standings', {}).get('points_for', 0)),
                                "points_against": float(team.get('team_standings', {}).get('points_against', 0))
                            })
                
                # Parse players (would need separate API call for full player list)
                # For now, return empty list
                
                return {
                    "league_id": league_data.get('league_id', ''),
                    "teams": teams,
                    "players": players,
                    "top_scorers": []  # Would need additional API call
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error parsing Yahoo league stats response: {e}")
            return None 