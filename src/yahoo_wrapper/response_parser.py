"""
Yahoo Fantasy Sports API Response Parser
Handles parsing of complex Yahoo API responses into clean Python objects
"""

import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

logger = logging.getLogger(__name__)


class YahooResponseParser:
    """Parse Yahoo Fantasy Sports API responses"""
    
    @staticmethod
    def extract_content(response: Dict[str, Any]) -> Dict[str, Any]:
        """Extract fantasy_content from response"""
        if isinstance(response, dict) and 'fantasy_content' in response:
            return response['fantasy_content']
        return response
    
    @staticmethod
    def parse_game(response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse game response"""
        content = YahooResponseParser.extract_content(response)
        
        if 'game' in content:
            game = content['game']
            return {
                'game_key': game.get('game_key', ''),
                'game_id': game.get('game_id', ''),
                'name': game.get('name', ''),
                'code': game.get('code', ''),
                'type': game.get('type', ''),
                'url': game.get('url', ''),
                'season': game.get('season', ''),
                'is_live_draft_lobby_active': game.get('is_live_draft_lobby_active', False),
                'is_game_over': game.get('is_game_over', False),
                'is_offseason': game.get('is_offseason', False)
            }
        return {}
    
    @staticmethod
    def parse_games_collection(response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse games collection response"""
        content = YahooResponseParser.extract_content(response)
        games = []
        
        if 'games' in content:
            games_data = content['games']
            for key, value in games_data.items():
                if isinstance(value, dict) and 'game' in value:
                    games.append(YahooResponseParser.parse_game({'game': value['game']}))
                    
        return games
    
    @staticmethod
    def parse_league(response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse league response"""
        content = YahooResponseParser.extract_content(response)
        
        if 'league' in content:
            league = content['league']
            return {
                'league_key': league.get('league_key', ''),
                'league_id': league.get('league_id', ''),
                'name': league.get('name', ''),
                'url': league.get('url', ''),
                'draft_status': league.get('draft_status', ''),
                'num_teams': league.get('num_teams', 0),
                'edit_key': league.get('edit_key', ''),
                'weekly_deadline': league.get('weekly_deadline', ''),
                'league_update_timestamp': league.get('league_update_timestamp', ''),
                'scoring_type': league.get('scoring_type', ''),
                'league_type': league.get('league_type', ''),
                'renew': league.get('renew', ''),
                'renewed': league.get('renewed', ''),
                'short_invitation_url': league.get('short_invitation_url', ''),
                'is_pro_league': league.get('is_pro_league', '0') == '1',
                'current_week': league.get('current_week', ''),
                'start_week': league.get('start_week', ''),
                'end_week': league.get('end_week', ''),
                'is_finished': league.get('is_finished', 0) == 1
            }
        return {}
    
    @staticmethod
    def parse_league_settings(response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse league settings"""
        content = YahooResponseParser.extract_content(response)
        
        if 'league' in content and 'settings' in content['league']:
            settings = content['league']['settings']
            return {
                'draft_type': settings.get('draft_type', ''),
                'is_auction_draft': settings.get('is_auction_draft', '0') == '1',
                'scoring_type': settings.get('scoring_type', ''),
                'uses_playoff': settings.get('uses_playoff', '1') == '1',
                'has_playoff_consolation_games': settings.get('has_playoff_consolation_games', False),
                'playoff_start_week': settings.get('playoff_start_week', ''),
                'uses_playoff_reseeding': settings.get('uses_playoff_reseeding', 0) == 1,
                'uses_lock_eliminated_teams': settings.get('uses_lock_eliminated_teams', 0) == 1,
                'num_playoff_teams': settings.get('num_playoff_teams', ''),
                'num_playoff_consolation_teams': settings.get('num_playoff_consolation_teams', 0),
                'uses_faab': settings.get('uses_faab', '0') == '1',
                'draft_time': settings.get('draft_time', ''),
                'draft_pick_time': settings.get('draft_pick_time', ''),
                'post_draft_players': settings.get('post_draft_players', ''),
                'max_teams': settings.get('max_teams', ''),
                'waiver_time': settings.get('waiver_time', ''),
                'trade_end_date': settings.get('trade_end_date', ''),
                'trade_ratify_type': settings.get('trade_ratify_type', ''),
                'trade_reject_time': settings.get('trade_reject_time', ''),
                'player_pool': settings.get('player_pool', ''),
                'cant_cut_list': settings.get('cant_cut_list', ''),
                'roster_positions': YahooResponseParser._parse_roster_positions(settings.get('roster_positions', [])),
                'stat_categories': YahooResponseParser._parse_stat_categories(settings.get('stat_categories', {})),
                'stat_modifiers': YahooResponseParser._parse_stat_modifiers(settings.get('stat_modifiers', {}))
            }
        return {}
    
    @staticmethod
    def _parse_roster_positions(positions_data: Any) -> List[Dict[str, Any]]:
        """Parse roster positions"""
        positions = []
        
        if isinstance(positions_data, list):
            for pos in positions_data:
                if isinstance(pos, dict):
                    positions.append({
                        'position': pos.get('position', ''),
                        'position_type': pos.get('position_type', ''),
                        'count': pos.get('count', 0)
                    })
        elif isinstance(positions_data, dict) and 'roster_position' in positions_data:
            # Handle when it's wrapped in roster_position
            for pos in positions_data.get('roster_position', []):
                positions.append({
                    'position': pos.get('position', ''),
                    'position_type': pos.get('position_type', ''),
                    'count': pos.get('count', 0)
                })
                
        return positions
    
    @staticmethod
    def _parse_stat_categories(categories_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse stat categories"""
        categories = {}
        
        if 'stats' in categories_data:
            stats_list = categories_data['stats']
            if isinstance(stats_list, list):
                for stat_group in stats_list:
                    if 'stat' in stat_group:
                        for stat in stat_group['stat']:
                            stat_id = str(stat.get('stat_id', ''))
                            categories[stat_id] = {
                                'stat_id': stat_id,
                                'name': stat.get('name', ''),
                                'display_name': stat.get('display_name', ''),
                                'sort_order': stat.get('sort_order', ''),
                                'position_type': stat.get('position_type', ''),
                                'is_only_display_stat': stat.get('is_only_display_stat', '0') == '1'
                            }
                            
        return categories
    
    @staticmethod
    def _parse_stat_modifiers(modifiers_data: Dict[str, Any]) -> Dict[str, float]:
        """Parse stat modifiers (scoring values)"""
        modifiers = {}
        
        if 'stats' in modifiers_data:
            stats_list = modifiers_data['stats']
            if isinstance(stats_list, list):
                for stat_group in stats_list:
                    if 'stat' in stat_group:
                        for stat in stat_group['stat']:
                            stat_id = str(stat.get('stat_id', ''))
                            value = stat.get('value', '0')
                            try:
                                modifiers[stat_id] = float(value)
                            except ValueError:
                                modifiers[stat_id] = 0.0
                                
        return modifiers
    
    @staticmethod
    def parse_team(response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse team response"""
        content = YahooResponseParser.extract_content(response)
        
        if 'team' in content:
            team = content['team']
            return {
                'team_key': team.get('team_key', ''),
                'team_id': team.get('team_id', ''),
                'name': team.get('name', ''),
                'url': team.get('url', ''),
                'team_logos': YahooResponseParser._parse_team_logos(team.get('team_logos', [])),
                'waiver_priority': team.get('waiver_priority', ''),
                'faab_balance': team.get('faab_balance', ''),
                'number_of_moves': team.get('number_of_moves', ''),
                'number_of_trades': team.get('number_of_trades', 0),
                'roster_adds': YahooResponseParser._parse_roster_adds(team.get('roster_adds', {})),
                'league_scoring_type': team.get('league_scoring_type', ''),
                'has_draft_grade': team.get('has_draft_grade', 0) == 1,
                'managers': YahooResponseParser._parse_managers(team.get('managers', [])),
                'is_owned_by_current_login': team.get('is_owned_by_current_login', 0) == 1
            }
        return {}
    
    @staticmethod
    def _parse_team_logos(logos_data: Any) -> List[Dict[str, str]]:
        """Parse team logos"""
        logos = []
        
        if isinstance(logos_data, list):
            for logo_item in logos_data:
                if 'team_logo' in logo_item:
                    logo = logo_item['team_logo']
                    logos.append({
                        'size': logo.get('size', ''),
                        'url': logo.get('url', '')
                    })
        elif isinstance(logos_data, dict) and 'team_logo' in logos_data:
            logo = logos_data['team_logo']
            logos.append({
                'size': logo.get('size', ''),
                'url': logo.get('url', '')
            })
            
        return logos
    
    @staticmethod
    def _parse_roster_adds(adds_data: Dict[str, Any]) -> Dict[str, int]:
        """Parse roster adds"""
        return {
            'coverage_type': adds_data.get('coverage_type', ''),
            'coverage_value': adds_data.get('coverage_value', 0),
            'value': adds_data.get('value', 0)
        }
    
    @staticmethod
    def _parse_managers(managers_data: Any) -> List[Dict[str, Any]]:
        """Parse team managers"""
        managers = []
        
        if isinstance(managers_data, list):
            for mgr_item in managers_data:
                if 'manager' in mgr_item:
                    mgr = mgr_item['manager']
                    managers.append({
                        'manager_id': mgr.get('manager_id', ''),
                        'nickname': mgr.get('nickname', ''),
                        'guid': mgr.get('guid', ''),
                        'is_commissioner': mgr.get('is_commissioner', '0') == '1',
                        'is_current_login': mgr.get('is_current_login', '0') == '1',
                        'email': mgr.get('email', ''),
                        'image_url': mgr.get('image_url', '')
                    })
        elif isinstance(managers_data, dict) and 'manager' in managers_data:
            mgr = managers_data['manager']
            managers.append({
                'manager_id': mgr.get('manager_id', ''),
                'nickname': mgr.get('nickname', ''),
                'guid': mgr.get('guid', ''),
                'is_commissioner': mgr.get('is_commissioner', '0') == '1',
                'is_current_login': mgr.get('is_current_login', '0') == '1',
                'email': mgr.get('email', ''),
                'image_url': mgr.get('image_url', '')
            })
            
        return managers
    
    @staticmethod
    def parse_player(response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse player response"""
        content = YahooResponseParser.extract_content(response)
        
        if 'player' in content:
            player = content['player']
            return YahooResponseParser._parse_player_data(player)
        return {}
    
    @staticmethod
    def _parse_player_data(player: Dict[str, Any]) -> Dict[str, Any]:
        """Parse individual player data"""
        return {
            'player_key': player.get('player_key', ''),
            'player_id': player.get('player_id', ''),
            'name': YahooResponseParser._parse_player_name(player.get('name', {})),
            'status': player.get('status', ''),
            'status_full': player.get('status_full', ''),
            'injury_note': player.get('injury_note', ''),
            'editorial_player_key': player.get('editorial_player_key', ''),
            'editorial_team_key': player.get('editorial_team_key', ''),
            'editorial_team_full_name': player.get('editorial_team_full_name', ''),
            'editorial_team_abbr': player.get('editorial_team_abbr', ''),
            'bye_weeks': YahooResponseParser._parse_bye_weeks(player.get('bye_weeks', {})),
            'uniform_number': player.get('uniform_number', ''),
            'display_position': player.get('display_position', ''),
            'headshot': YahooResponseParser._parse_headshot(player.get('headshot', {})),
            'image_url': player.get('image_url', ''),
            'is_undroppable': player.get('is_undroppable', '0') == '1',
            'position_type': player.get('position_type', ''),
            'eligible_positions': YahooResponseParser._parse_eligible_positions(player.get('eligible_positions', [])),
            'has_player_notes': player.get('has_player_notes', 0) == 1,
            'has_recent_player_notes': player.get('has_recent_player_notes', 0) == 1
        }
    
    @staticmethod
    def _parse_player_name(name_data: Dict[str, Any]) -> Dict[str, str]:
        """Parse player name"""
        return {
            'full': name_data.get('full', ''),
            'first': name_data.get('first', ''),
            'last': name_data.get('last', ''),
            'ascii_first': name_data.get('ascii_first', ''),
            'ascii_last': name_data.get('ascii_last', '')
        }
    
    @staticmethod
    def _parse_bye_weeks(bye_data: Dict[str, Any]) -> List[int]:
        """Parse bye weeks"""
        if 'week' in bye_data:
            week = bye_data['week']
            if isinstance(week, list):
                return [int(w) for w in week if str(w).isdigit()]
            elif str(week).isdigit():
                return [int(week)]
        return []
    
    @staticmethod
    def _parse_headshot(headshot_data: Dict[str, Any]) -> Dict[str, str]:
        """Parse player headshot"""
        return {
            'url': headshot_data.get('url', ''),
            'size': headshot_data.get('size', '')
        }
    
    @staticmethod
    def _parse_eligible_positions(positions_data: Any) -> List[str]:
        """Parse eligible positions"""
        positions = []
        
        if isinstance(positions_data, list):
            for pos_item in positions_data:
                if 'position' in pos_item:
                    positions.append(pos_item['position'])
        elif isinstance(positions_data, dict) and 'position' in positions_data:
            pos = positions_data['position']
            if isinstance(pos, list):
                positions = pos
            else:
                positions = [pos]
                
        return positions
    
    @staticmethod
    def parse_roster(response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse roster response"""
        content = YahooResponseParser.extract_content(response)
        
        if 'team' in content and 'roster' in content['team']:
            roster = content['team']['roster']
            return {
                'coverage_type': roster.get('coverage_type', ''),
                'week': roster.get('week', ''),
                'date': roster.get('date', ''),
                'is_editable': roster.get('is_editable', 0) == 1,
                'players': YahooResponseParser._parse_roster_players(roster.get('players', {}))
            }
        return {}
    
    @staticmethod
    def _parse_roster_players(players_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse roster players"""
        players = []
        
        for key, value in players_data.items():
            if isinstance(value, dict) and 'player' in value:
                player_data = value['player']
                player = YahooResponseParser._parse_player_data(player_data)
                
                # Add roster-specific data
                if 'selected_position' in player_data:
                    selected = player_data['selected_position']
                    player['selected_position'] = {
                        'coverage_type': selected.get('coverage_type', ''),
                        'date': selected.get('date', ''),
                        'week': selected.get('week', ''),
                        'position': selected.get('position', ''),
                        'is_flex': selected.get('is_flex', 0) == 1
                    }
                    
                players.append(player)
                
        return players
    
    @staticmethod
    def parse_transaction(response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse transaction response"""
        content = YahooResponseParser.extract_content(response)
        
        if 'transaction' in content:
            transaction = content['transaction']
            return {
                'transaction_key': transaction.get('transaction_key', ''),
                'transaction_id': transaction.get('transaction_id', ''),
                'type': transaction.get('type', ''),
                'status': transaction.get('status', ''),
                'timestamp': transaction.get('timestamp', ''),
                'players': YahooResponseParser._parse_transaction_players(transaction.get('players', {}))
            }
        return {}
    
    @staticmethod
    def _parse_transaction_players(players_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse transaction players"""
        players = []
        
        for key, value in players_data.items():
            if isinstance(value, dict) and 'player' in value:
                player = value['player']
                player_info = {
                    'player_key': player.get('player_key', ''),
                    'player_id': player.get('player_id', ''),
                    'name': YahooResponseParser._parse_player_name(player.get('name', {})),
                    'transaction_data': {}
                }
                
                if 'transaction_data' in player:
                    trans_data = player['transaction_data']
                    player_info['transaction_data'] = {
                        'type': trans_data.get('type', ''),
                        'source_type': trans_data.get('source_type', ''),
                        'source_team_key': trans_data.get('source_team_key', ''),
                        'destination_type': trans_data.get('destination_type', ''),
                        'destination_team_key': trans_data.get('destination_team_key', '')
                    }
                    
                players.append(player_info)
                
        return players