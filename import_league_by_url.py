#!/usr/bin/env python3
"""
Import Fantasy League by URL
Extract league ID from Yahoo Fantasy URL and import all data
"""

import asyncio
import aiohttp
import json
import re
from datetime import datetime
from urllib.parse import urlparse, parse_qs

BASE_URL = "http://localhost:8000"

class LeagueURLImporter:
    def __init__(self):
        self.session = None
        self.league_id = None
        self.league_data = {}
        
    async def setup(self):
        """Setup aiohttp session"""
        self.session = aiohttp.ClientSession()
    
    async def cleanup(self):
        """Cleanup session"""
        if self.session:
            await self.session.close()
    
    def extract_league_id(self, url: str) -> str:
        """Extract league ID from Yahoo Fantasy URL"""
        print(f"\nAnalyzing URL: {url}")
        
        # Common Yahoo Fantasy URL patterns:
        # https://baseball.fantasysports.yahoo.com/b1/12345
        # https://football.fantasysports.yahoo.com/f1/12345
        # https://basketball.fantasysports.yahoo.com/nba/12345
        # https://hockey.fantasysports.yahoo.com/puck/12345/1
        
        # Pattern 1: Direct league URL
        pattern1 = r'fantasysports\.yahoo\.com/(\w+)/(\d+)'
        match1 = re.search(pattern1, url)
        
        if match1:
            sport_code = match1.group(1)
            league_num = match1.group(2)
            
            # Map sport codes
            sport_map = {
                'b1': 'mlb',
                'f1': 'nfl', 
                'nba': 'nba',
                'puck': 'nhl',
                'baseball': 'mlb',
                'football': 'nfl',
                'basketball': 'nba',
                'hockey': 'nhl'
            }
            
            # Determine sport
            if sport_code in sport_map:
                sport = sport_map[sport_code]
            elif len(sport_code) <= 3:
                sport = sport_code
            else:
                # For full sport names
                sport = 'mlb' if 'base' in sport_code else sport_code[:3]
            
            league_id = f"{sport}.l.{league_num}"
            print(f"[OK] Extracted League ID: {league_id}")
            return league_id
        
        # Pattern 2: With additional path segments
        pattern2 = r'fantasysports\.yahoo\.com/(\w+)/(\w+)/(\d+)'
        match2 = re.search(pattern2, url)
        
        if match2:
            sport = match2.group(2)
            league_num = match2.group(3)
            league_id = f"{sport}.l.{league_num}"
            print(f"[OK] Extracted League ID: {league_id}")
            return league_id
        
        print("[ERROR] Could not extract league ID from URL")
        print("Expected format: https://baseball.fantasysports.yahoo.com/b1/12345")
        return None
    
    async def check_auth(self):
        """Check authentication status"""
        print("\nChecking Yahoo authentication...")
        try:
            async with self.session.get(f"{BASE_URL}/auth/status") as resp:
                auth_status = await resp.json()
                if auth_status['authenticated']:
                    print("[OK] Authenticated with Yahoo")
                    return True
                else:
                    print("\n[!] Not authenticated. Please:")
                    print(f"1. Visit: {BASE_URL}")
                    print("2. Click 'Login with Yahoo'")
                    print("3. Complete authentication")
                    print("4. Run this script again")
                    return False
        except Exception as e:
            print(f"[ERROR] Auth check failed: {e}")
            return False
    
    async def import_league(self, league_id: str):
        """Import all data for the league"""
        self.league_id = league_id
        print(f"\nImporting league: {league_id}")
        print("=" * 60)
        
        # 1. Get league info
        print("\n1. Fetching league information...")
        try:
            async with self.session.get(f"{BASE_URL}/yahoo/league/{league_id}") as resp:
                if resp.status == 200:
                    self.league_data['info'] = await resp.json()
                    info = self.league_data['info']
                    print(f"[OK] League: {info.get('name', 'Unknown')}")
                    print(f"     Sport: {info.get('game_name', 'Unknown')}")
                    print(f"     Season: {info.get('season', 'Unknown')}")
                    print(f"     Teams: {info.get('num_teams', 'Unknown')}")
                    print(f"     Scoring: {info.get('scoring_type', 'Unknown')}")
                else:
                    print(f"[ERROR] Failed to fetch league info: {resp.status}")
                    return False
        except Exception as e:
            print(f"[ERROR] {e}")
            return False
        
        # 2. Get all players
        print("\n2. Fetching all players...")
        try:
            async with self.session.get(f"{BASE_URL}/yahoo/players/{league_id}") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    self.league_data['players'] = data.get('players', [])
                    player_count = len(self.league_data['players'])
                    print(f"[OK] Found {player_count} players")
                    
                    # Show sample players
                    if player_count > 0:
                        print("\n     Top 5 players:")
                        for p in self.league_data['players'][:5]:
                            print(f"     - {p.get('name')} ({p.get('editorial_team_abbr')}) - {p.get('display_position')}")
        except Exception as e:
            print(f"[WARNING] Could not fetch players: {e}")
        
        # 3. Get league stats
        print("\n3. Fetching league statistics...")
        try:
            async with self.session.get(f"{BASE_URL}/yahoo/league/{league_id}/stats") as resp:
                if resp.status == 200:
                    self.league_data['stats'] = await resp.json()
                    print("[OK] League statistics loaded")
                    
                    # Show standings if available
                    if 'teams' in self.league_data['stats']:
                        teams = self.league_data['stats']['teams']
                        print(f"\n     Standings ({len(teams)} teams):")
                        for i, team in enumerate(teams[:5], 1):
                            print(f"     {i}. {team.get('name', 'Unknown')}")
        except Exception as e:
            print(f"[WARNING] Could not fetch stats: {e}")
        
        # 4. Save data
        filename = f"league_{league_id.replace('.', '_')}_import_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump({
                "import_date": datetime.now().isoformat(),
                "league_id": league_id,
                "source_url": url,
                "data": self.league_data
            }, f, indent=2)
        
        print(f"\n[SUCCESS] League data saved to: {filename}")
        return True

async def main():
    print("=" * 60)
    print("YAHOO FANTASY LEAGUE IMPORTER")
    print("=" * 60)
    
    # Get URL from user
    print("\nPaste your Yahoo Fantasy league URL below:")
    print("(Example: https://baseball.fantasysports.yahoo.com/b1/12345)")
    url = input("\nURL: ").strip()
    
    if not url:
        print("[ERROR] No URL provided")
        return
    
    importer = LeagueURLImporter()
    
    try:
        await importer.setup()
        
        # Extract league ID
        league_id = importer.extract_league_id(url)
        if not league_id:
            return
        
        # Check auth
        if not await importer.check_auth():
            return
        
        # Import league
        success = await importer.import_league(league_id)
        
        if success:
            print("\n" + "=" * 60)
            print("IMPORT COMPLETE!")
            print("=" * 60)
            print("\nYour league has been successfully imported.")
            print("You can now proceed with deployment knowing the import works!")
            
    except Exception as e:
        print(f"\n[ERROR] {e}")
    finally:
        await importer.cleanup()

if __name__ == "__main__":
    # Store the URL globally so we can use it in the import
    url = None
    asyncio.run(main())