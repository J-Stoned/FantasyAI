"""
Fantasy AI Ultimate - Merged Project
Main FastAPI application integrating Fantasy AI Ultimate and Yahoo Fantasy Wrapper
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta

from src.shared.database import DatabaseManager
from src.shared.ai_engine import AIAnalysisEngine
from src.yahoo_wrapper import YahooFantasyAPI
from src.monitoring import metrics_middleware, get_health_status, metrics
from src.unified_data_service import unified_data

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Fantasy AI Ultimate - Merged Project",
    description="AI-powered fantasy sports analysis platform",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add metrics middleware
app.middleware("http")(metrics_middleware)

# Initialize components
db_manager = DatabaseManager()
ai_engine = AIAnalysisEngine()
yahoo_api = YahooFantasyAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="src/static"), name="static")

@app.on_event("startup")
async def startup_event():
    """Initialize database and AI engine on startup"""
    await db_manager.initialize()
    await ai_engine.initialize()
    await unified_data.initialize()
    logger.info("All services initialized successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await db_manager.close()

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main web interface"""
    try:
        with open("src/static/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Fantasy AI Ultimate</h1><p>Static files not found</p>")

@app.get("/api")
async def api_root():
    """API root endpoint"""
    return {
        "message": "Fantasy AI Ultimate API",
        "version": "1.0.1",
        "endpoints": {
            "yahoo": "/yahoo/*",
            "ai": "/ai/*",
            "auth": "/auth/*"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "components": ["database", "ai_engine", "yahoo_api"]}

@app.get("/api/debug/oauth-config")
async def debug_oauth_config():
    """Debug endpoint to check OAuth configuration"""
    import os
    return {
        "redirect_uri": yahoo_api.redirect_uri,
        "client_id": yahoo_api.client_id[:10] + "..." if yahoo_api.client_id else "NOT SET",
        "env_redirect": os.getenv("YAHOO_REDIRECT_URI"),
        "env_exists": "YAHOO_REDIRECT_URI" in os.environ,
        "environment": os.getenv("ENVIRONMENT", "NOT SET"),
        "num_env_vars": len(os.environ),
        "has_yahoo_vars": any(k.startswith("YAHOO") for k in os.environ.keys())
    }

# OAuth2 Authorization Endpoints
@app.get("/auth/authorize")
async def authorize():
    """Generate Yahoo OAuth2 authorization URL"""
    try:
        auth_url = yahoo_api.get_authorization_url()
        
        # Parse URL for debugging
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(auth_url)
        params = parse_qs(parsed.query)
        
        logger.info("Generated OAuth URL parameters:")
        for key, values in params.items():
            if key == 'client_id':
                logger.info(f"  {key}: {values[0][:20]}...")
            else:
                logger.info(f"  {key}: {values[0] if values else 'None'}")
        
        return {
            "authorization_url": auth_url,
            "message": "Click the URL to authorize with Yahoo",
            "debug_info": {
                "has_scope": 'scope' in params,
                "scope_value": params.get('scope', ['None'])[0],
                "has_all_required": all(k in params for k in ['client_id', 'redirect_uri', 'response_type', 'scope']),
                "url_length": len(auth_url)
            }
        }
    except Exception as e:
        logger.error(f"Error generating authorization URL: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/auth/callback")
async def auth_callback(
    code: str = Query(None), 
    state: str = Query(None),
    error: str = Query(None),
    error_description: str = Query(None)
):
    """Handle OAuth2 callback from Yahoo"""
    try:
        # Check for OAuth errors first
        if error:
            logger.error(f"OAuth error: {error} - {error_description}")
            return RedirectResponse(
                url=f"/?auth=error&error={error}&desc={error_description or 'Unknown error'}",
                status_code=302
            )
        
        # Check if code is missing
        if not code:
            logger.error("OAuth callback received without authorization code")
            return RedirectResponse(
                url="/?auth=error&error=missing_code&desc=No authorization code received",
                status_code=302
            )
        
        logger.info(f"Received real OAuth callback with code: {code[:10]}... and state: {state[:10] if state else 'None'}...")
        
        # Exchange authorization code for access token
        success = await yahoo_api.exchange_code_for_token(code, state)
        
        if success:
            logger.info("Real OAuth2 authentication successful")
            # Redirect to success page
            return RedirectResponse(
                url="/?auth=success&real=true",
                status_code=302
            )
        else:
            logger.error("OAuth2 token exchange failed")
            # Redirect to error page
            return RedirectResponse(
                url="/?auth=error",
                status_code=302
            )
            
    except Exception as e:
        logger.error(f"Error in OAuth callback: {e}")
        return RedirectResponse(
            url="/?auth=error",
            status_code=302
        )

@app.get("/auth/mock-callback")
async def mock_auth_callback(code: str = Query(...), state: str = Query(...)):
    """Handle mock OAuth2 callback for testing"""
    try:
        logger.info(f"Received mock OAuth callback with code: {code} and state: {state}")
        
        # For mock flow, we'll simulate successful authentication
        # In a real implementation, this would exchange the code for a token
        yahoo_api.access_token = "mock_access_token_for_testing"
        yahoo_api.refresh_token = "mock_refresh_token_for_testing"
        yahoo_api.token_expires_at = datetime.now() + timedelta(hours=1)
        
        logger.info("Mock OAuth2 authentication successful")
        
        # Redirect to success page
        return RedirectResponse(
            url="/?auth=success&mock=true",
            status_code=302
        )
            
    except Exception as e:
        logger.error(f"Error in mock OAuth callback: {e}")
        return RedirectResponse(
            url="/?auth=error",
            status_code=302
        )

@app.get("/auth/status")
async def auth_status():
    """Check OAuth2 authentication status"""
    try:
        has_valid_token = await yahoo_api.ensure_valid_token()
        return {
            "authenticated": has_valid_token,
            "has_access_token": yahoo_api.access_token is not None,
            "has_refresh_token": yahoo_api.refresh_token is not None,
            "token_expires_at": yahoo_api.token_expires_at.isoformat() if yahoo_api.token_expires_at else None
        }
    except Exception as e:
        logger.error(f"Error checking auth status: {e}")
        return {
            "authenticated": False,
            "error": str(e)
        }

@app.get("/auth/test-config")
async def test_oauth2_config():
    """Test OAuth2 configuration and return diagnostic information"""
    try:
        config_info = yahoo_api.test_oauth2_configuration()
        return {
            "oauth2_config": config_info,
            "message": "OAuth2 configuration test completed"
        }
    except Exception as e:
        logger.error(f"Error testing OAuth2 config: {e}")
        return {
            "error": str(e),
            "message": "OAuth2 configuration test failed"
        }

# Yahoo Fantasy API Endpoints
@app.get("/yahoo/leagues")
async def get_user_leagues():
    """Get user's Yahoo Fantasy leagues"""
    try:
        leagues = await yahoo_api.get_user_leagues()
        return {"leagues": leagues}
    except Exception as e:
        logger.error(f"Error getting user leagues: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/yahoo/league/{league_id}")
async def get_league_info(league_id: str):
    """Get specific league information"""
    try:
        league_info = await yahoo_api.get_league_info(league_id)
        return league_info
    except Exception as e:
        logger.error(f"Error getting league info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/yahoo/players/{league_id}")
async def get_league_players(league_id: str):
    """Get all players in a league"""
    try:
        players = await yahoo_api.get_league_players(league_id)
        return {"players": players}
    except Exception as e:
        logger.error(f"Error getting league players: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/yahoo/player/{player_id}/stats")
async def get_player_stats(player_id: str, league_id: str = Query(...)):
    """Get detailed stats for a specific player"""
    try:
        player_stats = await yahoo_api.get_player_stats(player_id, league_id)
        return player_stats
    except Exception as e:
        logger.error(f"Error getting player stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/yahoo/player/{player_id}/history")
async def get_player_history(player_id: str, league_id: str = Query(...)):
    """Get historical performance data for a player"""
    try:
        history = await yahoo_api.get_player_history(player_id, league_id)
        return {"history": history}
    except Exception as e:
        logger.error(f"Error getting player history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/yahoo/team/{team_id}")
async def get_team_info(team_id: str, league_id: str = Query(...)):
    """Get team information and roster"""
    try:
        team_info = await yahoo_api.get_team_info(team_id, league_id)
        return team_info
    except Exception as e:
        logger.error(f"Error getting team info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/yahoo/league/{league_id}/stats")
async def get_league_stats(league_id: str):
    """Get comprehensive league statistics"""
    try:
        league_stats = await yahoo_api.get_league_stats(league_id)
        return league_stats
    except Exception as e:
        logger.error(f"Error getting league stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# AI Analysis Endpoints
@app.post("/ai/analyze-player")
async def analyze_player(player_id: str = Query(...), league_id: str = Query(...)):
    """Analyze a player using AI"""
    try:
        analysis = await ai_engine.analyze_player(player_id, league_id)
        return analysis
    except Exception as e:
        logger.error(f"Error analyzing player: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/predict-performance")
async def predict_performance(player_id: str = Query(...), league_id: str = Query(...)):
    """Predict player performance using AI"""
    try:
        prediction = await ai_engine.predict_performance(player_id, league_id)
        return prediction
    except Exception as e:
        logger.error(f"Error predicting performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/team-optimization")
async def optimize_team(league_id: str = Query(...), team_id: str = Query(...)):
    """Optimize team lineup using AI"""
    try:
        optimization = await ai_engine.optimize_team(league_id, team_id)
        return optimization
    except Exception as e:
        logger.error(f"Error optimizing team: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Desktop Database Endpoints
@app.get("/desktop/status")
async def desktop_database_status():
    """Check desktop database connection status"""
    try:
        is_connected = await unified_data.desktop_db.test_connection()
        
        if is_connected:
            stats = await unified_data.desktop_db.get_database_stats()
            return {
                "connected": True,
                "database": "fantasy_ai_local",
                "host": unified_data.desktop_db.desktop_url.split("@")[1].split("/")[0] if unified_data.desktop_db.desktop_url else None,
                "statistics": stats
            }
        else:
            return {
                "connected": False,
                "error": "Unable to connect to desktop database"
            }
    except Exception as e:
        logger.error(f"Error checking desktop database status: {e}")
        return {
            "connected": False,
            "error": str(e)
        }

@app.get("/desktop/players/{sport}")
async def get_desktop_players(
    sport: str,
    player_name: str = Query(None, description="Player name to search"),
    limit: int = Query(100, description="Number of results to return")
):
    """Get player data from desktop database"""
    try:
        players = await unified_data.desktop_db.get_player_stats(
            sport=sport.upper(),
            player_name=player_name,
            limit=limit
        )
        
        return {
            "sport": sport.upper(),
            "count": len(players),
            "players": players
        }
    except Exception as e:
        logger.error(f"Error getting desktop players: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/desktop/dfs-slate/{sport}")
async def get_dfs_slate(
    sport: str,
    platform: str = Query("draftkings", description="DFS platform"),
    date: str = Query(None, description="Slate date (YYYY-MM-DD)")
):
    """Get DFS slate data from desktop database"""
    try:
        from datetime import datetime
        
        slate_date = None
        if date:
            slate_date = datetime.strptime(date, "%Y-%m-%d").date()
            
        slate_data = await unified_data.get_dfs_slate(
            sport=sport.upper(),
            slate_date=slate_date,
            platform=platform
        )
        
        return slate_data
    except Exception as e:
        logger.error(f"Error getting DFS slate: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/desktop/injuries")
async def get_injury_reports():
    """Get current injury reports from desktop database"""
    try:
        injuries = await unified_data.desktop_db.get_injury_reports()
        
        # Group by sport
        by_sport = {}
        for injury in injuries:
            sport = injury["sport"]
            if sport not in by_sport:
                by_sport[sport] = []
            by_sport[sport].append(injury)
        
        return {
            "total_injuries": len(injuries),
            "by_sport": by_sport,
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting injury reports: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/unified/player/{player_name}")
async def get_unified_player_data(
    player_name: str,
    sport: str = Query(None, description="Sport (NFL, NBA, MLB, NHL)"),
    include_stats: bool = Query(True, description="Include recent stats"),
    include_projections: bool = Query(True, description="Include ML projections")
):
    """Get comprehensive player data from all sources"""
    try:
        player_data = await unified_data.get_player_data(
            player_name=player_name,
            sport=sport,
            include_stats=include_stats,
            include_projections=include_projections
        )
        
        return player_data
    except Exception as e:
        logger.error(f"Error getting unified player data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/unified/optimization/{sport}")
async def get_optimization_data(
    sport: str,
    contest_type: str = Query("main", description="Contest type"),
    date: str = Query(None, description="Contest date (YYYY-MM-DD)")
):
    """Get optimization data for lineup building"""
    try:
        from datetime import datetime
        
        contest_date = None
        if date:
            contest_date = datetime.strptime(date, "%Y-%m-%d").date()
            
        optimization_data = await unified_data.get_optimization_data(
            sport=sport.upper(),
            contest_type=contest_type,
            slate_date=contest_date
        )
        
        return optimization_data
    except Exception as e:
        logger.error(f"Error getting optimization data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 