# MLB League Import Test Guide

## Prerequisites

1. **Start the server**:
   ```bash
   python scripts/start.py
   ```

2. **Complete OAuth Authentication**:
   - Visit: http://localhost:8000
   - Click "Login with Yahoo"
   - Authorize the app
   - You should be redirected back with success

## Run the MLB Import Test

### Option 1: Automated Test (Recommended)
```bash
# Run the comprehensive test
python test_mlb_league_import.py
```

This will test:
- ✓ OAuth authentication status
- ✓ Fetching your leagues
- ✓ Finding MLB leagues
- ✓ Importing league data
- ✓ Importing player rosters
- ✓ Importing statistics

### Option 2: Manual Testing via API

1. **Check Auth Status**:
   ```bash
   curl http://localhost:8000/auth/status
   ```

2. **Get Your Leagues**:
   ```bash
   curl http://localhost:8000/yahoo/leagues
   ```
   
   Look for MLB leagues in the response:
   ```json
   {
     "leagues": [
       {
         "league_id": "mlb.l.12345",
         "name": "Your MLB League Name",
         "game_name": "Baseball",
         "season": "2025"
       }
     ]
   }
   ```

3. **Import Specific MLB League**:
   ```bash
   # Replace with your actual MLB league ID
   curl http://localhost:8000/yahoo/league/mlb.l.12345
   ```

4. **Get MLB Players**:
   ```bash
   curl http://localhost:8000/yahoo/players/mlb.l.12345
   ```

5. **Get League Stats**:
   ```bash
   curl http://localhost:8000/yahoo/league/mlb.l.12345/stats
   ```

## Expected Results

### Successful Import Should Show:
- League name and settings
- Number of teams (usually 8-12)
- Scoring type (Head-to-Head, Rotisserie, Points)
- Player roster with MLB players
- Current season stats

### Common Issues:

1. **No MLB Leagues Found**:
   - Make sure you're in an active MLB fantasy league
   - The league must be for the current season (2025)

2. **Authentication Failed**:
   - Re-do the OAuth flow
   - Check your Yahoo app credentials

3. **Empty Player Lists**:
   - MLB season might not have started
   - League might be in draft mode

## Quick Troubleshooting

```bash
# Check server logs
# Look for errors in the terminal where you started the server

# Check OAuth config
curl http://localhost:8000/auth/test-config

# Re-authenticate if needed
curl http://localhost:8000/auth/login
```

## Success Criteria

Before deployment, ensure:
- [x] Can authenticate with Yahoo
- [x] Can see your MLB leagues
- [x] Can import league details
- [x] Can fetch player rosters
- [x] Can retrieve stats

Once all tests pass, you're ready to deploy!