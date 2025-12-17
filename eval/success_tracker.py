# eval/success_tracker.py
"""Success rate tracking system"""
import json
import os
from typing import Dict, List
from datetime import datetime
from collections import defaultdict

class SuccessTracker:
    """Tracks success rates of attacks over time"""
    
    def __init__(self, db_path="data/success_tracker.json"):
        self.db_path = db_path
        self.data = self._load_data()
    
    def _load_data(self) -> Dict:
        """Load tracking data from file"""
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r") as f:
                    return json.load(f)
            except:
                pass
        return {
            "attacks": {},
            "strategies": {},
            "models": {},
            "timeline": [],
        }
    
    def _save_data(self):
        """Save tracking data to file"""
        os.makedirs(os.path.dirname(self.db_path) or ".", exist_ok=True)
        with open(self.db_path, "w") as f:
            json.dump(self.data, f, indent=2)
    
    def record_attack_result(self, attack_id: str, success: bool, model: str, strategy: str = None):
        """Record result of an attack"""
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        # Track by attack_id
        if attack_id not in self.data["attacks"]:
            self.data["attacks"][attack_id] = {
                "success": 0,
                "total": 0,
                "first_seen": timestamp,
                "last_seen": timestamp,
            }
        
        self.data["attacks"][attack_id]["total"] += 1
        self.data["attacks"][attack_id]["last_seen"] = timestamp
        if success:
            self.data["attacks"][attack_id]["success"] += 1
        
        # Track by strategy
        if strategy:
            if strategy not in self.data["strategies"]:
                self.data["strategies"][strategy] = {"success": 0, "total": 0}
            self.data["strategies"][strategy]["total"] += 1
            if success:
                self.data["strategies"][strategy]["success"] += 1
        
        # Track by model
        if model not in self.data["models"]:
            self.data["models"][model] = {"success": 0, "total": 0}
        self.data["models"][model]["total"] += 1
        if success:
            self.data["models"][model]["success"] += 1
        
        # Timeline entry
        self.data["timeline"].append({
            "timestamp": timestamp,
            "attack_id": attack_id,
            "success": success,
            "model": model,
            "strategy": strategy,
        })
        
        # Keep timeline to last 1000 entries
        if len(self.data["timeline"]) > 1000:
            self.data["timeline"] = self.data["timeline"][-1000:]
        
        self._save_data()
    
    def get_attack_success_rate(self, attack_id: str) -> float:
        """Get success rate for specific attack"""
        if attack_id not in self.data["attacks"]:
            return 0.0
        attack = self.data["attacks"][attack_id]
        if attack["total"] == 0:
            return 0.0
        return attack["success"] / attack["total"]
    
    def get_strategy_success_rate(self, strategy: str) -> float:
        """Get success rate for strategy"""
        if strategy not in self.data["strategies"]:
            return 0.0
        strat = self.data["strategies"][strategy]
        if strat["total"] == 0:
            return 0.0
        return strat["success"] / strat["total"]
    
    def get_model_success_rate(self, model: str) -> float:
        """Get success rate against specific model"""
        if model not in self.data["models"]:
            return 0.0
        model_data = self.data["models"][model]
        if model_data["total"] == 0:
            return 0.0
        return model_data["success"] / model_data["total"]
    
    def get_top_attacks(self, n: int = 10) -> List[Dict]:
        """Get top N most successful attacks"""
        attacks = []
        for attack_id, data in self.data["attacks"].items():
            if data["total"] > 0:
                success_rate = data["success"] / data["total"]
                attacks.append({
                    "attack_id": attack_id,
                    "success_rate": success_rate,
                    "total": data["total"],
                    "success": data["success"],
                })
        
        attacks.sort(key=lambda x: x["success_rate"], reverse=True)
        return attacks[:n]
    
    def get_top_strategies(self, n: int = 5) -> List[Dict]:
        """Get top N most successful strategies"""
        strategies = []
        for strategy, data in self.data["strategies"].items():
            if data["total"] > 0:
                success_rate = data["success"] / data["total"]
                strategies.append({
                    "strategy": strategy,
                    "success_rate": success_rate,
                    "total": data["total"],
                    "success": data["success"],
                })
        
        strategies.sort(key=lambda x: x["success_rate"], reverse=True)
        return strategies[:n]
    
    def get_recent_trends(self, days: int = 7) -> Dict:
        """Get trends over last N days"""
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        recent = [
            entry for entry in self.data["timeline"]
            if datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00")) > cutoff
        ]
        
        if not recent:
            return {"success_rate": 0.0, "total": 0, "success": 0}
        
        success_count = sum(1 for e in recent if e["success"])
        return {
            "success_rate": success_count / len(recent),
            "total": len(recent),
            "success": success_count,
        }




