#!/usr/bin/env python3
"""
Import YOUR Specific Fantasy League
Interactive script to find and import your league data
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configuration
BASE_URL = "http://localhost:8000"

class MyLeagueImporter:
    def __init__(self):
        self.session = None
        self.all_leagues = []
        self.selected_league = None
        self.league_data = {}
    
    async def setup(self):
        """Setup aiohttp session"""
        self.session = aiohttp.ClientSession()
    
    async def cleanup(self):
        """Cleanup session"""
        if self.session:
            await self.session.close()
    
    async def check_auth(self):
        """Check if authenticated"""
        print("\nChecking authentication status...")
        try:
            async with self.session.get(f"{BASE_URL}/auth/status") as resp:
                auth_status = await resp.json()
                if auth_status['authenticated']:
                    print("[OK] You are authenticated with Yahoo!")
                    return True
                else:
                    print("\n[!] You need to authenticate first:")
                    print(f"1. Open your browser and go to: {BASE_URL}")
                    print("2. Click 'Login with Yahoo'")
                    print("3. Complete the authentication")
                    print("4. Then run this script again")
                    return False
        except Exception as e:
            print(f"[ERROR] Could not check auth status: {e}")
            print("Make sure the server is running: python scripts/start.py")
            return False
    
    async def fetch_all_leagues(self):
        """Fetch ALL your leagues"""
        print("\nFetching ALL your fantasy leagues...")
        print("-" * 60)
        
        try:
            async with self.session.get(f"{BASE_URL}/yahoo/leagues") as resp:
                data = await resp.json()
                self.all_leagues = data.get("leagues", [])
                
                if not self.all_leagues:
                    print("[!] No leagues found. Make sure you have active fantasy leagues.")
                    return False
                
                print(f"\nFound {len(self.all_leagues)} total league(s):\n")
                
                # Display all leagues with numbers
                for idx, league in enumerate(self.all_leagues, 1):
                    print(f"{idx}. {league.get('name', 'Unknown League')}")
                    print(f"   Sport: {league.get('game_name', 'Unknown')}")
                    print(f"   League ID: {league.get('league_id', 'Unknown')}")
                    print(f"   Season: {league.get('season', league.get('year', 'Unknown'))}")
                    print(f"   Teams: {league.get('num_teams', 'Unknown')}")
                    print()
                
                return True
                
        except Exception as e:
            print(f"[ERROR] Failed to fetch leagues: {e}")
            return False
    
    async def select_league(self):
        """Let user select which league to import"""
        while True:
            try:
                print("-" * 60)
                choice = input("\nEnter the number of the league you want to import (or 'q' to quit): ").strip()
                
                if choice.lower() == 'q':
                    return False
                
                league_num = int(choice)
                if 1 <= league_num <= len(self.all_leagues):
                    self.selected_league = self.all_leagues[league_num - 1]
                    print(f"\n[OK] Selected: {self.selected_league['name']}")
                    return True
                else:
                    print(f"[!] Please enter a number between 1 and {len(self.all_leagues)}")
            
            except ValueError:
                print("[!] Please enter a valid number")
    
    async def import_league_details(self):
        """Import detailed league information"""
        league_id = self.selected_league['league_id']
        league_name = self.selected_league['name']
        
        print(f"\nImporting details for: {league_name}")
        print("=" * 60)
        
        # 1. Get league info
        print("\n1. Fetching league information...")
        try:
            async with self.session.get(f"{BASE_URL}/yahoo/league/{league_id}") as resp:
                self.league_data['info'] = await resp.json()
                print("[OK] League info loaded")
                
                # Display key info
                info = self.league_data['info']
                print(f"   - Scoring Type: {info.get('scoring_type', 'Unknown')}")
                print(f"   - Current Week: {info.get('current_week', 'Unknown')}")
                print(f"   - Draft Status: {info.get('draft_status', 'Unknown')}")
        except Exception as e:
            print(f"[ERROR] Failed to get league info: {e}")
        
        # 2. Get teams/standings
        print("\n2. Fetching teams and standings...")
        try:
            # Try to get from league stats endpoint
            async with self.session.get(f"{BASE_URL}/yahoo/league/{league_id}/stats") as resp:
                stats_data = await resp.json()
                if 'teams' in stats_data:
                    self.league_data['teams'] = stats_data['teams']
                    print(f"[OK] Found {len(stats_data['teams'])} teams")
                    
                    # Show standings
                    print("\n   Current Standings:")
                    for i, team in enumerate(stats_data.get('teams', [])[:5], 1):
                        print(f"   {i}. {team.get('name', 'Unknown Team')}")
        except Exception as e:
            print(f"[WARNING] Could not fetch team standings: {e}")
        
        # 3. Get players
        print("\n3. Fetching all players...")
        try:
            async with self.session.get(f"{BASE_URL}/yahoo/players/{league_id}") as resp:
                data = await resp.json()
                players = data.get("players", [])
                self.league_data['players'] = players
                print(f"[OK] Found {len(players)} players")
                
                # Show top players
                print("\n   Sample Players:")
                for player in players[:5]:
                    print(f"   - {player.get('name', 'Unknown')} ({player.get('editorial_team_abbr', 'FA')}) - {player.get('display_position', 'Unknown')}")
        except Exception as e:
            print(f"[ERROR] Failed to get players: {e}")
        
        # 4. Save imported data
        print("\n4. Saving league data...")
        filename = f"my_league_{league_id.replace('.', '_')}_import.json"
        
        with open(filename, 'w') as f:
            json.dump({
                "import_date": datetime.now().isoformat(),
                "league": self.selected_league,
                "data": self.league_data
            }, f, indent=2)
        
        print(f"[OK] League data saved to: {filename}")
        
        return True
    
    async def display_summary(self):
        """Display import summary"""
        print("\n" + "=" * 60)
        print("IMPORT COMPLETE!")
        print("=" * 60)
        
        print(f"\nLeague: {self.selected_league['name']}")
        print(f"Sport: {self.selected_league['game_name']}")
        print(f"Season: {self.selected_league.get('season', 'Unknown')}")
        
        if 'info' in self.league_data:
            print(f"\nLeague Details:")
            print(f"- Scoring Type: {self.league_data['info'].get('scoring_type')}")
            print(f"- Number of Teams: {self.league_data['info'].get('num_teams')}")
            
        if 'players' in self.league_data:
            print(f"\nPlayers Imported: {len(self.league_data['players'])}")
            
        print("\n[SUCCESS] Your league has been successfully imported!")
        print("\nNext steps:")
        print("1. Review the imported data in the JSON file")
        print("2. The league is now ready for AI analysis")
        print("3. You can deploy to production with confidence!")

async def main():
    """Run the interactive league importer"""
    print("=" * 60)
    print("IMPORT YOUR FANTASY LEAGUE")
    print("=" * 60)
    print("\nThis will help you import YOUR specific fantasy league.")
    
    importer = MyLeagueImporter()
    
    try:
        await importer.setup()
        
        # Step 1: Check authentication
        if not await importer.check_auth():
            return
        
        # Step 2: Fetch all leagues
        if not await importer.fetch_all_leagues():
            return
        
        # Step 3: Let user select their league
        if not await importer.select_league():
            print("\nImport cancelled.")
            return
        
        # Step 4: Import the selected league
        await importer.import_league_details()
        
        # Step 5: Show summary
        await importer.display_summary()
        
    except KeyboardInterrupt:
        print("\n\nImport cancelled by user.")
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
    finally:
        await importer.cleanup()

if __name__ == "__main__":
    # Make sure server is running
    print("\nIMPORTANT: Make sure the server is running!")
    print("If not, open another terminal and run: python scripts/start.py")
    input("\nPress Enter when ready to continue...")
    
    asyncio.run(main())