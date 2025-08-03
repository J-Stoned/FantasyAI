# Yahoo Fantasy Sports API Wrapper

A comprehensive Python wrapper for the Yahoo Fantasy Sports API with OAuth2 authentication, caching, error handling, and database synchronization.

## Features

- **Complete API Coverage**: Supports all Yahoo Fantasy Sports resources (Games, Leagues, Teams, Players, Transactions, etc.)
- **OAuth2 Authentication**: Full OAuth2 flow with automatic token refresh
- **Response Caching**: Multiple cache backends (Memory, File, Redis) to reduce API calls
- **Error Handling**: Comprehensive error handling with retryable errors
- **Database Sync**: Automatic synchronization of Yahoo data to local database
- **Type Safety**: Full type hints for better IDE support
- **Async Support**: Built with async/await for high performance

## Installation

```bash
pip install aiohttp aiofiles redis sqlalchemy
```

## Quick Start

### Basic Usage

```python
from src.yahoo_wrapper import YahooFantasyAPI

# Initialize the API wrapper
yahoo_api = YahooFantasyAPI(cache_type="memory")

# Get authorization URL for user
auth_url = yahoo_api.get_authorization_url()
print(f"Please authorize at: {auth_url}")

# After user authorizes, exchange code for token
success = await yahoo_api.exchange_code_for_token(auth_code, state)

# Get user's leagues
leagues = await yahoo_api.get_user_leagues()
for league in leagues:
    print(f"League: {league['name']} ({league['league_id']})")

# Get league players
players = await yahoo_api.get_league_players(league_id)
for player in players:
    print(f"Player: {player['name']} - {player['position']}")
```

### Advanced Features

#### Player Search
```python
# Search for available players
available_players = await yahoo_api.search_players(
    league_key="nfl.l.12345",
    search="mahomes",
    position="QB",
    status="A",  # Available
    sort="AR",   # By rank
    count=10
)
```

#### Roster Management
```python
# Update lineup
roster_changes = [
    {"player_key": "nfl.p.12345", "position": "QB"},
    {"player_key": "nfl.p.67890", "position": "BN"}  # Bench
]

success = await yahoo_api.update_roster(
    team_key="nfl.l.12345.t.1",
    roster_changes=roster_changes,
    coverage_type="week",
    coverage_value=10
)
```

#### Transactions
```python
# Add a player
transaction = await yahoo_api.add_player(
    league_key="nfl.l.12345",
    team_key="nfl.l.12345.t.1",
    player_key="nfl.p.99999"
)

# Add/drop in one transaction
transaction = await yahoo_api.add_drop_players(
    league_key="nfl.l.12345",
    team_key="nfl.l.12345.t.1",
    add_player_key="nfl.p.99999",
    drop_player_key="nfl.p.88888",
    faab_bid=25  # For FAAB leagues
)
```

## Configuration

### Environment Variables

Create a `.env` file with your Yahoo App credentials:

```env
YAHOO_CLIENT_ID=your_client_id_here
YAHOO_CLIENT_SECRET=your_client_secret_here
YAHOO_REDIRECT_URI=http://localhost:8000/auth/callback
```

### Cache Configuration

```python
# Memory cache (default)
yahoo_api = YahooFantasyAPI(cache_type="memory")

# File cache
yahoo_api = YahooFantasyAPI(
    cache_type="file",
    cache_config={"cache_dir": "./cache"}
)

# Redis cache
yahoo_api = YahooFantasyAPI(
    cache_type="redis",
    cache_config={"redis_url": "redis://localhost:6379"}
)
```

## API Resources

### Games
- `get_game(game_key)` - Get game information
- `get_games(filters)` - Get multiple games

### Leagues
- `get_league_info(league_id)` - Get league information
- `get_league_settings(league_id)` - Get league settings
- `get_league_standings(league_id)` - Get league standings
- `get_league_transactions(league_id)` - Get league transactions
- `get_scoreboard(league_key, week)` - Get weekly scoreboard

### Teams
- `get_team_info(team_id, league_id)` - Get team information
- `get_team_roster(team_key)` - Get team roster
- `get_team_stats(team_key)` - Get team statistics
- `get_team_matchups(team_key)` - Get team matchups

### Players
- `get_player_stats(player_id, league_id)` - Get player statistics
- `get_player_history(player_id, league_id)` - Get player history
- `search_players(league_key, filters)` - Search for players

### Transactions
- `add_player()` - Add a player
- `drop_player()` - Drop a player
- `add_drop_players()` - Add and drop in one transaction
- `propose_trade()` - Propose a trade
- `accept_trade()` - Accept a trade
- `reject_trade()` - Reject a trade

## Database Models

The wrapper includes SQLAlchemy models for storing Yahoo data:

- **YahooGame**: Fantasy games (NFL, NBA, MLB, NHL)
- **YahooLeague**: User's fantasy leagues
- **YahooTeam**: Teams in leagues
- **YahooPlayer**: Player information
- **YahooRosterEntry**: Team rosters
- **YahooTransaction**: League transactions
- **YahooPlayerStats**: Player statistics
- **YahooUserToken**: OAuth tokens

### Database Sync

```python
from src.yahoo_wrapper.db_sync import YahooDataSync
from sqlalchemy.ext.asyncio import AsyncSession

# Create sync instance
sync = YahooDataSync(db_session)

# Sync league data
league_data = await yahoo_api.get_league_info("nfl.l.12345")
await sync.sync_league(league_data)

# Sync team roster
roster = await yahoo_api.get_team_roster("nfl.l.12345.t.1")
await sync.sync_roster(
    team_key="nfl.l.12345.t.1",
    players=roster['players'],
    coverage_type="week",
    coverage_value="10"
)
```

## Error Handling

The wrapper includes comprehensive error handling:

```python
from src.yahoo_wrapper.exceptions import (
    YahooAuthenticationError,
    YahooRateLimitError,
    YahooTransactionError
)

try:
    players = await yahoo_api.get_league_players(league_id)
except YahooAuthenticationError:
    # Token expired, refresh it
    await yahoo_api.refresh_access_token()
except YahooRateLimitError as e:
    # Wait and retry
    await asyncio.sleep(e.retry_after)
except YahooTransactionError as e:
    # Handle transaction errors
    print(f"Transaction failed: {e.reason}")
```

## Response Parsing

The wrapper includes a comprehensive response parser:

```python
from src.yahoo_wrapper.response_parser import YahooResponseParser

# Parse different response types
game = YahooResponseParser.parse_game(response)
league = YahooResponseParser.parse_league(response)
team = YahooResponseParser.parse_team(response)
player = YahooResponseParser.parse_player(response)
```

## Rate Limiting

The API client includes automatic rate limit handling:
- Respects Yahoo's rate limits
- Automatic retry with exponential backoff
- Returns cached data when rate limited

## Testing

```python
# Test OAuth2 configuration
config_test = yahoo_api.test_oauth2_configuration()
print(f"OAuth2 config test: {config_test}")

# Use mock data for development
yahoo_api.access_token = "mock_token"
leagues = await yahoo_api.get_user_leagues()  # Returns mock data
```

## Best Practices

1. **Use Caching**: Enable caching to reduce API calls
2. **Handle Errors**: Always wrap API calls in try/except blocks
3. **Batch Operations**: Use collection endpoints when possible
4. **Token Management**: Store refresh tokens securely
5. **Rate Limits**: Implement proper backoff strategies

## Troubleshooting

### Common Issues

1. **Invalid Client ID/Secret**
   - Verify credentials in `.env` file
   - Check Yahoo App settings

2. **Token Expired**
   - Use `refresh_access_token()` method
   - Implement automatic refresh logic

3. **Rate Limited**
   - Enable caching
   - Reduce request frequency
   - Use batch endpoints

4. **Invalid League/Team Keys**
   - Use correct key format: `{game_id}.l.{league_id}`
   - Verify user has access to resource

## License

This wrapper is part of the Fantasy AI Ultimate project.