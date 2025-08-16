import json
import os
from typing import List, Dict, Any

class DataManager:
    def __init__(self):
        """Initialize data manager and ensure data directory exists"""
        self.data_dir = 'data'
        self.ensure_data_directory()
        self.initialize_data_files()
    
    def ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def initialize_data_files(self):
        """Initialize all data files with empty arrays if they don't exist"""
        files = ['clubs.json', 'players.json', 'matches.json', 'transfers.json']
        for file in files:
            filepath = os.path.join(self.data_dir, file)
            if not os.path.exists(filepath):
                with open(filepath, 'w') as f:
                    json.dump([], f)
    
    def load_data(self, filename: str) -> List[Dict[Any, Any]]:
        """Load data from a JSON file"""
        filepath = os.path.join(self.data_dir, filename)
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def save_data(self, filename: str, data: List[Dict[Any, Any]]):
        """Save data to a JSON file"""
        filepath = os.path.join(self.data_dir, filename)
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving data to {filename}: {e}")
    
    def load_clubs(self) -> List[Dict[Any, Any]]:
        """Load clubs data"""
        return self.load_data('clubs.json')
    
    def save_clubs(self, clubs: List[Dict[Any, Any]]):
        """Save clubs data"""
        self.save_data('clubs.json', clubs)
    
    def load_players(self) -> List[Dict[Any, Any]]:
        """Load players data"""
        return self.load_data('players.json')
    
    def save_players(self, players: List[Dict[Any, Any]]):
        """Save players data"""
        self.save_data('players.json', players)
    
    def load_matches(self) -> List[Dict[Any, Any]]:
        """Load matches data"""
        return self.load_data('matches.json')
    
    def save_matches(self, matches: List[Dict[Any, Any]]):
        """Save matches data"""
        self.save_data('matches.json', matches)
    
    def load_transfers(self) -> List[Dict[Any, Any]]:
        """Load transfers data"""
        return self.load_data('transfers.json')
    
    def save_transfers(self, transfers: List[Dict[Any, Any]]):
        """Save transfers data"""
        self.save_data('transfers.json', transfers)
    
    def get_next_id(self, data: List[Dict[Any, Any]]) -> int:
        """Get the next available ID for a new record"""
        if not data:
            return 1
        return max(item.get('id', 0) for item in data) + 1
    
    def find_by_id(self, data: List[Dict[Any, Any]], record_id: int) -> Dict[Any, Any]:
        """Find a record by its ID"""
        return next((item for item in data if item.get('id') == record_id), None)
    
    def remove_by_id(self, data: List[Dict[Any, Any]], record_id: int) -> List[Dict[Any, Any]]:
        """Remove a record by its ID"""
        return [item for item in data if item.get('id') != record_id]
    
    def backup_all_data(self) -> Dict[str, Any]:
        """Create a complete backup of all data"""
        return {
            'clubs': self.load_clubs(),
            'players': self.load_players(),
            'matches': self.load_matches(),
            'transfers': self.load_transfers()
        }
    
    def restore_from_backup(self, backup_data: Dict[str, Any]) -> bool:
        """Restore data from a backup"""
        try:
            if 'clubs' in backup_data:
                self.save_clubs(backup_data['clubs'])
            if 'players' in backup_data:
                self.save_players(backup_data['players'])
            if 'matches' in backup_data:
                self.save_matches(backup_data['matches'])
            if 'transfers' in backup_data:
                self.save_transfers(backup_data['transfers'])
            return True
        except Exception as e:
            print(f"Error restoring from backup: {e}")
            return False
