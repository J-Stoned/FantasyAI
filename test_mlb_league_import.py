#!/usr/bin/env python3
"""
Test MLB League Import Functionality
Tests the complete flow from OAuth to league data import
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime
from typing import Dict, List, Any

# Configuration
BASE_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}

class MLBLeagueImportTester:
    def __init__(self):
        self.session = None
        self.auth_status = None
        self.leagues = []
        self.selected_league = None
        self.test_results = {
            "oauth": False,
            "leagues_fetched": False,
            "mlb_league_found": False,
            "league_data_imported": False,
            "players_imported": False,
            "stats_imported": False
        }
    
    async def setup(self):
        """Setup aiohttp session"""
        self.session = aiohttp.ClientSession()
    
    async def cleanup(self):
        """Cleanup session"""
        if self.session:
            await self.session.close()
    
    async def test_oauth_status(self):
        """Test OAuth authentication status"""
        print("\n[1/6] Testing OAuth Status...")
        print("-" * 50)
        
        try:
            async with self.session.get(f"{BASE_URL}/auth/status") as resp:
                self.auth_status = await resp.json()
                print(f"Authentication Status: {self.auth_status['authenticated']}")
                print(f"Has Access Token: {self.auth_status['has_access_token']}")
                print(f"Has Refresh Token: {self.auth_status['has_refresh_token']}")
                
                if not self.auth_status['authenticated']:
                    print("\n[WARNING] Not authenticated!")
                    print("Please complete OAuth flow first:")
                    print(f"1. Visit: {BASE_URL}/auth/login")
                    print("2. Complete Yahoo authentication")
                    print("3. Run this test again")
                    return False
                
                self.test_results["oauth"] = True
                print("[OK] OAuth authentication successful!")
                return True
                
        except Exception as e:
            print(f"[ERROR] OAuth status check failed: {e}")
            return False
    
    async def test_fetch_leagues(self):
        """Fetch user's fantasy leagues"""
        print("\n[2/6] Fetching Your Fantasy Leagues...")
        print("-" * 50)
        
        try:
            async with self.session.get(f"{BASE_URL}/yahoo/leagues") as resp:
                data = await resp.json()
                self.leagues = data.get("leagues", [])
                
                print(f"Total leagues found: {len(self.leagues)}")
                
                # Filter for MLB leagues
                mlb_leagues = []
                for league in self.leagues:
                    print(f"\nLeague: {league.get('name', 'Unknown')}")
                    print(f"  - ID: {league.get('league_id')}")
                    print(f"  - Game: {league.get('game_name', 'Unknown')}")
                    print(f"  - Season: {league.get('season', 'Unknown')}")
                    print(f"  - Year: {league.get('season_year', league.get('year', 'Unknown'))}")
                    
                    # Check if it's MLB (game_code might be 'mlb')
                    # Also check league_id, game_code, or game_key
                    league_str = str(league).lower()
                    if any(sport in league_str for sport in ['mlb', 'baseball']):
                        mlb_leagues.append(league)
                        print("  [MLB LEAGUE FOUND!]")
                    elif '2025' in str(league.get('season', '')) or '2025' in str(league.get('year', '')):
                        # Check if it might be MLB based on season
                        if 'football' not in league_str and 'basketball' not in league_str:
                            print("  [Possible MLB league based on 2025 season]")
                
                if mlb_leagues:
                    self.test_results["leagues_fetched"] = True
                    self.test_results["mlb_league_found"] = True
                    self.selected_league = mlb_leagues[0]  # Select first MLB league
                    print(f"\n[OK] Found {len(mlb_leagues)} MLB league(s)!")
                    print(f"Selected: {self.selected_league['name']}")
                    return True
                else:
                    print("\n[WARNING] No MLB leagues found in your account")
                    print("Available leagues are from other sports")
                    return False
                    
        except Exception as e:
            print(f"[ERROR] Failed to fetch leagues: {e}")
            return False
    
    async def test_import_league_data(self):
        """Import detailed league data"""
        if not self.selected_league:
            print("\n[3/6] Skipping league data import - no MLB league selected")
            return False
            
        print(f"\n[3/6] Importing MLB League Data...")
        print("-" * 50)
        print(f"League: {self.selected_league['name']}")
        
        try:
            league_id = self.selected_league['league_id']
            async with self.session.get(f"{BASE_URL}/yahoo/league/{league_id}") as resp:
                league_data = await resp.json()
                
                print("\nLeague Details:")
                print(f"  - Name: {league_data.get('name')}")
                print(f"  - Scoring Type: {league_data.get('scoring_type')}")
                print(f"  - Current Week: {league_data.get('current_week')}")
                print(f"  - Total Teams: {league_data.get('num_teams')}")
                print(f"  - League URL: {league_data.get('url')}")
                
                # Check for settings
                if 'settings' in league_data:
                    print("\nLeague Settings:")
                    settings = league_data['settings']
                    print(f"  - Draft Type: {settings.get('draft_type')}")
                    print(f"  - Max Teams: {settings.get('max_teams')}")
                    print(f"  - Roster Positions: {settings.get('roster_positions', [])[:5]}...")
                
                self.test_results["league_data_imported"] = True
                print("\n[OK] League data imported successfully!")
                return True
                
        except Exception as e:
            print(f"[ERROR] Failed to import league data: {e}")
            return False
    
    async def test_import_players(self):
        """Import league players"""
        if not self.selected_league:
            print("\n[4/6] Skipping player import - no MLB league selected")
            return False
            
        print(f"\n[4/6] Importing MLB Players...")
        print("-" * 50)
        
        try:
            league_id = self.selected_league['league_id']
            async with self.session.get(f"{BASE_URL}/yahoo/players/{league_id}") as resp:
                data = await resp.json()
                players = data.get("players", [])
                
                print(f"Total players found: {len(players)}")
                
                # Show first 10 players
                print("\nSample Players:")
                for i, player in enumerate(players[:10]):
                    print(f"\n{i+1}. {player.get('name', 'Unknown')}")
                    print(f"   - ID: {player.get('player_id')}")
                    print(f"   - Team: {player.get('editorial_team_abbr')}")
                    print(f"   - Position: {player.get('display_position')}")
                    print(f"   - Status: {player.get('status')}")
                
                if players:
                    self.test_results["players_imported"] = True
                    print(f"\n[OK] Imported {len(players)} players!")
                    return True
                else:
                    print("\n[WARNING] No players found")
                    return False
                    
        except Exception as e:
            print(f"[ERROR] Failed to import players: {e}")
            return False
    
    async def test_import_stats(self):
        """Import league statistics"""
        if not self.selected_league:
            print("\n[5/6] Skipping stats import - no MLB league selected")
            return False
            
        print(f"\n[5/6] Importing MLB League Statistics...")
        print("-" * 50)
        
        try:
            league_id = self.selected_league['league_id']
            async with self.session.get(f"{BASE_URL}/yahoo/league/{league_id}/stats") as resp:
                stats_data = await resp.json()
                
                print("League Statistics Overview:")
                
                # Display available stats
                if 'teams' in stats_data:
                    print(f"\nTeam Statistics Available: {len(stats_data['teams'])} teams")
                    
                if 'stat_categories' in stats_data:
                    print(f"\nStat Categories:")
                    for cat in stats_data['stat_categories'][:10]:
                        print(f"  - {cat.get('display_name', cat.get('name', 'Unknown'))}")
                
                if 'standings' in stats_data:
                    print(f"\nStandings Available: Yes")
                
                self.test_results["stats_imported"] = True
                print("\n[OK] League statistics imported!")
                return True
                
        except Exception as e:
            print(f"[ERROR] Failed to import stats: {e}")
            return False
    
    async def generate_report(self):
        """Generate final test report"""
        print("\n[6/6] MLB League Import Test Report")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for v in self.test_results.values() if v)
        
        print(f"\nTest Results: {passed_tests}/{total_tests} passed")
        print("-" * 50)
        
        for test_name, passed in self.test_results.items():
            status = "[PASS]" if passed else "[FAIL]"
            print(f"{status} {test_name.replace('_', ' ').title()}")
        
        print("\nSummary:")
        if passed_tests == total_tests:
            print("[SUCCESS] All tests passed! Ready for deployment.")
            print("\nYour MLB league data can be successfully imported.")
            print("The OAuth flow and Yahoo API integration are working correctly.")
        else:
            print("[WARNING] Some tests failed. Please fix issues before deployment.")
            
            if not self.test_results["oauth"]:
                print("\n1. Complete OAuth authentication first")
            elif not self.test_results["mlb_league_found"]:
                print("\n1. No MLB leagues found in your Yahoo account")
                print("2. Make sure you have an active MLB fantasy league")
        
        # Save detailed results
        with open("mlb_import_test_results.json", "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "test_results": self.test_results,
                "league_info": self.selected_league,
                "auth_status": self.auth_status
            }, f, indent=2)
        
        print(f"\nDetailed results saved to: mlb_import_test_results.json")

async def main():
    """Run MLB league import tests"""
    print("MLB Fantasy League Import Test Suite")
    print("=" * 50)
    print("This will test importing your MLB fantasy league data")
    print("Make sure the server is running at http://localhost:8000")
    
    input("\nPress Enter to start testing...")
    
    tester = MLBLeagueImportTester()
    
    try:
        await tester.setup()
        
        # Run tests in sequence
        if await tester.test_oauth_status():
            if await tester.test_fetch_leagues():
                await tester.test_import_league_data()
                await tester.test_import_players()
                await tester.test_import_stats()
        
        # Generate report
        await tester.generate_report()
        
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    asyncio.run(main())