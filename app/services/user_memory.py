"""User memory service for storing preferences and personal information."""
import json
from pathlib import Path
from typing import Optional
from datetime import datetime

class UserMemoryService:
    """Stores and retrieves user preferences and information."""
    
    def __init__(self, memory_file: Optional[Path] = None):
        if memory_file is None:
            memory_file = Path.home() / ".config" / "sonet" / "user_memory.json"
        
        memory_file.parent.mkdir(parents=True, exist_ok=True)
        self.memory_file = memory_file
        self.memory = self._load_memory()
    
    def _load_memory(self) -> dict:
        """Load memory from file."""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
            except:
                return {"preferences": {}, "facts": [], "interactions": []}
        return {"preferences": {}, "facts": [], "interactions": []}
    
    def _save_memory(self):
        """Save memory to file."""
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, indent=2)
    
    def add_preference(self, key: str, value: str):
        """Add or update user preference."""
        self.memory["preferences"][key] = {
            "value": value,
            "updated_at": datetime.now().isoformat()
        }
        self._save_memory()
    
    def add_fact(self, fact: str):
        """Add a fact about the user."""
        self.memory["facts"].append({
            "fact": fact,
            "learned_at": datetime.now().isoformat()
        })
        self._save_memory()
    
    def record_interaction(self, topic: str, context: str):
        """Record an interaction for context."""
        self.memory["interactions"].append({
            "topic": topic,
            "context": context,
            "timestamp": datetime.now().isoformat()
        })
        # Keep only last 50 interactions
        if len(self.memory["interactions"]) > 50:
            self.memory["interactions"] = self.memory["interactions"][-50:]
        self._save_memory()
    
    def get_memory_context(self) -> str:
        """Get formatted memory context for AI."""
        context = "USER MEMORY AND PREFERENCES:\n\n"
        
        if self.memory["preferences"]:
            context += "Preferences:\n"
            for key, data in self.memory["preferences"].items():
                context += f"- {key}: {data['value']}\n"
            context += "\n"
        
        if self.memory["facts"]:
            context += "Known facts about user:\n"
            for fact_data in self.memory["facts"][-10:]:  # Last 10 facts
                context += f"- {fact_data['fact']}\n"
            context += "\n"
        
        if self.memory["interactions"]:
            context += "Recent topics discussed:\n"
            for interaction in self.memory["interactions"][-5:]:  # Last 5
                context += f"- {interaction['topic']}\n"
            context += "\n"
        
        return context if len(context) > 50 else ""
    
    def extract_and_store(self, user_message: str, ai_response: str):
        """Extract preferences/facts from conversation (to be called by AI)."""
        # This will be enhanced by AI to extract information
        # For now, just record the interaction
        self.record_interaction(
            topic=user_message[:100],
            context=ai_response[:200]
        )
