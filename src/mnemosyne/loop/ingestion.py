import json
import os
from typing import List, Dict, Any
from datetime import datetime
from ..core.schemas import Comment, AuthorType, IntentType, EmotionalIntensity
from ..core.semantic import SemanticEngine

class CommentIngestor:
    """
    V0 Comment Ingestor. 
    Classifies raw comment data based on heuristics.
    """
    def __init__(self):
        self.semantic = SemanticEngine()
    
    def ingest_from_file(self, file_path: str, post_id: str) -> List[Comment]:
        if not os.path.exists(file_path):
            return []
            
        with open(file_path, "r") as f:
            raw_data = json.load(f)
            
        comments = []
        for raw in raw_data:
            comment = self._classify(raw, post_id)
            comments.append(comment)
        return comments

    def _classify(self, raw: Dict[str, Any], post_id: str) -> Comment:
        text = raw.get("text", "")
        author = raw.get("author", "anonymous")
        author_type = AuthorType(raw.get("author_type", "unknown"))
        timestamp_str = raw.get("timestamp")
        timestamp = datetime.fromisoformat(timestamp_str) if timestamp_str else datetime.utcnow()
        
        # Heuristic Intent Classification
        intent = IntentType.PRAISE
        if "?" in text:
            intent = IntentType.QUESTION
        elif any(word in text.lower() for word in ["bad", "wrong", "fail", "slow", "fatigue", "skeptical"]):
            intent = IntentType.CRITIQUE
        elif len(text.split()) < 3:
            intent = IntentType.SPAM
            
        # Topic Cluster Heuristic (lightweight)
        topic_cluster = "general"
        if any(word in text.lower() for word in ["memory", "brain", "continuity"]):
            topic_cluster = "architecture"
        elif any(word in text.lower() for word in ["employee", "people", "humans"]):
            topic_cluster = "operations"
            
        # Emotional Intensity Heuristic
        intensity = EmotionalIntensity.LOW
        if "!" in text or any(word in text.lower() for word in ["love", "hate", "amazing", "terrible", "urgent"]):
            intensity = EmotionalIntensity.HIGH
        elif len(text) > 100:
            intensity = EmotionalIntensity.MEDIUM
            
        return Comment(
            id=f"cmt_{hash(text + str(timestamp))}",
            post_id=post_id,
            author=author,
            author_type=author_type,
            embedding=self.semantic.encode(text), # V1 Semantic Embedding
            content=text,
            intent=intent,
            topic_cluster=topic_cluster,
            emotional_intensity=intensity,
            timestamp=timestamp
        )
