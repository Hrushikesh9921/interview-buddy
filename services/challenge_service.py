"""
Challenge service for managing interview challenges and templates.
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import or_

from models import get_db_context, Challenge
from config.constants import ChallengeCategory, ChallengeDifficulty
from utils.logger import logger


class ChallengeConfig:
    """Configuration for creating a challenge."""
    
    def __init__(
        self,
        title: str,
        description: str,
        category: ChallengeCategory,
        difficulty: ChallengeDifficulty,
        instructions: Optional[str] = None,
        starter_code: Optional[str] = None,
        test_cases: Optional[List[Dict]] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        is_template: bool = False,
        estimated_duration: Optional[int] = None
    ):
        self.title = title
        self.description = description
        self.category = category
        self.difficulty = difficulty
        self.instructions = instructions
        self.starter_code = starter_code
        self.test_cases = test_cases or []
        self.tags = tags or []
        self.metadata = metadata or {}
        self.is_template = is_template
        self.estimated_duration = estimated_duration


class ChallengeService:
    """Service for managing interview challenges."""
    
    def __init__(self):
        """Initialize challenge service."""
        pass
    
    def create_challenge(
        self,
        config: ChallengeConfig,
        db: Optional[DBSession] = None
    ) -> Challenge:
        """
        Create a new challenge.
        
        Args:
            config: Challenge configuration
            db: Database session (optional)
            
        Returns:
            Created Challenge object
        """
        if db:
            return self._create_challenge_with_db(config, db)
        
        with get_db_context() as db:
            return self._create_challenge_with_db(config, db)
    
    def _create_challenge_with_db(
        self,
        config: ChallengeConfig,
        db: DBSession
    ) -> Challenge:
        """Internal method to create challenge with database session."""
        # Validate config
        if not config.title or not config.title.strip():
            raise ValueError("Challenge title is required")
        
        if not config.description or not config.description.strip():
            raise ValueError("Challenge description is required")
        
        # Create challenge
        challenge = Challenge(
            title=config.title.strip(),
            description=config.description.strip(),
            category=config.category,
            difficulty=config.difficulty,
            instructions=config.instructions.strip() if config.instructions else None,
            starter_code=config.starter_code.strip() if config.starter_code else None,
            test_cases=config.test_cases,
            tags=config.tags,
            metadata=config.metadata,
            is_template=config.is_template,
            estimated_duration=config.estimated_duration
        )
        
        db.add(challenge)
        db.flush()
        
        logger.info(f"Created challenge: {challenge.title} ({challenge.id})")
        
        return challenge
    
    def get_challenge(
        self,
        challenge_id: str,
        db: Optional[DBSession] = None
    ) -> Optional[Challenge]:
        """
        Get a challenge by ID.
        
        Args:
            challenge_id: Challenge ID
            db: Database session (optional)
            
        Returns:
            Challenge object or None
        """
        if db:
            return self._get_challenge_with_db(challenge_id, db)
        
        with get_db_context() as db:
            return self._get_challenge_with_db(challenge_id, db)
    
    def _get_challenge_with_db(
        self,
        challenge_id: str,
        db: DBSession
    ) -> Optional[Challenge]:
        """Internal method to get challenge with database session."""
        challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
        return challenge
    
    def update_challenge(
        self,
        challenge_id: str,
        updates: Dict[str, Any],
        db: Optional[DBSession] = None
    ) -> Challenge:
        """
        Update a challenge.
        
        Args:
            challenge_id: Challenge ID
            updates: Dictionary of fields to update
            db: Database session (optional)
            
        Returns:
            Updated Challenge object
        """
        if db:
            return self._update_challenge_with_db(challenge_id, updates, db)
        
        with get_db_context() as db:
            return self._update_challenge_with_db(challenge_id, updates, db)
    
    def _update_challenge_with_db(
        self,
        challenge_id: str,
        updates: Dict[str, Any],
        db: DBSession
    ) -> Challenge:
        """Internal method to update challenge with database session."""
        challenge = self._get_challenge_with_db(challenge_id, db)
        
        if not challenge:
            raise ValueError(f"Challenge not found: {challenge_id}")
        
        # Update allowed fields
        allowed_fields = [
            'title', 'description', 'category', 'difficulty', 'instructions',
            'starter_code', 'test_cases', 'tags', 'metadata', 'is_template',
            'estimated_duration'
        ]
        
        for key, value in updates.items():
            if key in allowed_fields:
                setattr(challenge, key, value)
        
        db.flush()
        
        logger.info(f"Updated challenge: {challenge.title} ({challenge.id})")
        
        return challenge
    
    def delete_challenge(
        self,
        challenge_id: str,
        db: Optional[DBSession] = None
    ) -> bool:
        """
        Delete a challenge.
        
        Args:
            challenge_id: Challenge ID
            db: Database session (optional)
            
        Returns:
            True if deleted, False if not found
        """
        if db:
            return self._delete_challenge_with_db(challenge_id, db)
        
        with get_db_context() as db:
            return self._delete_challenge_with_db(challenge_id, db)
    
    def _delete_challenge_with_db(
        self,
        challenge_id: str,
        db: DBSession
    ) -> bool:
        """Internal method to delete challenge with database session."""
        challenge = self._get_challenge_with_db(challenge_id, db)
        
        if not challenge:
            return False
        
        db.delete(challenge)
        db.flush()
        
        logger.info(f"Deleted challenge: {challenge.title} ({challenge.id})")
        
        return True
    
    def get_all_templates(
        self,
        db: Optional[DBSession] = None
    ) -> List[Challenge]:
        """
        Get all challenge templates.
        
        Args:
            db: Database session (optional)
            
        Returns:
            List of Challenge objects marked as templates
        """
        if db:
            return self._get_all_templates_with_db(db)
        
        with get_db_context() as db:
            return self._get_all_templates_with_db(db)
    
    def _get_all_templates_with_db(self, db: DBSession) -> List[Challenge]:
        """Internal method to get all templates with database session."""
        templates = db.query(Challenge).filter(
            Challenge.is_template == True
        ).order_by(
            Challenge.category,
            Challenge.difficulty,
            Challenge.title
        ).all()
        
        return templates
    
    def list_templates(
        self,
        category: Optional[ChallengeCategory] = None,
        difficulty: Optional[ChallengeDifficulty] = None,
        db: Optional[DBSession] = None
    ) -> List[Challenge]:
        """
        List challenge templates with optional filtering.
        
        Args:
            category: Filter by category (optional)
            difficulty: Filter by difficulty (optional)
            db: Database session (optional)
            
        Returns:
            List of Challenge objects
        """
        if db:
            return self._list_templates_with_db(category, difficulty, db)
        
        with get_db_context() as db:
            return self._list_templates_with_db(category, difficulty, db)
    
    def _list_templates_with_db(
        self,
        category: Optional[ChallengeCategory],
        difficulty: Optional[ChallengeDifficulty],
        db: DBSession
    ) -> List[Challenge]:
        """Internal method to list templates with database session."""
        query = db.query(Challenge).filter(Challenge.is_template == True)
        
        if category:
            query = query.filter(Challenge.category == category)
        
        if difficulty:
            query = query.filter(Challenge.difficulty == difficulty)
        
        templates = query.order_by(
            Challenge.category,
            Challenge.difficulty,
            Challenge.title
        ).all()
        
        return templates
    
    def get_by_category(
        self,
        category: ChallengeCategory,
        db: Optional[DBSession] = None
    ) -> List[Challenge]:
        """
        Get challenges by category.
        
        Args:
            category: Challenge category
            db: Database session (optional)
            
        Returns:
            List of Challenge objects
        """
        return self.list_templates(category=category, db=db)
    
    def get_by_difficulty(
        self,
        difficulty: ChallengeDifficulty,
        db: Optional[DBSession] = None
    ) -> List[Challenge]:
        """
        Get challenges by difficulty.
        
        Args:
            difficulty: Challenge difficulty
            db: Database session (optional)
            
        Returns:
            List of Challenge objects
        """
        return self.list_templates(difficulty=difficulty, db=db)
    
    def search_challenges(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        db: Optional[DBSession] = None
    ) -> List[Challenge]:
        """
        Search challenges by title or description.
        
        Args:
            query: Search query
            filters: Optional filters (category, difficulty, is_template)
            db: Database session (optional)
            
        Returns:
            List of matching Challenge objects
        """
        if db:
            return self._search_challenges_with_db(query, filters or {}, db)
        
        with get_db_context() as db:
            return self._search_challenges_with_db(query, filters or {}, db)
    
    def _search_challenges_with_db(
        self,
        query: str,
        filters: Dict[str, Any],
        db: DBSession
    ) -> List[Challenge]:
        """Internal method to search challenges with database session."""
        search_query = db.query(Challenge)
        
        # Text search
        if query and query.strip():
            search_term = f"%{query.strip()}%"
            search_query = search_query.filter(
                or_(
                    Challenge.title.ilike(search_term),
                    Challenge.description.ilike(search_term)
                )
            )
        
        # Apply filters
        if filters.get('category'):
            search_query = search_query.filter(Challenge.category == filters['category'])
        
        if filters.get('difficulty'):
            search_query = search_query.filter(Challenge.difficulty == filters['difficulty'])
        
        if 'is_template' in filters:
            search_query = search_query.filter(Challenge.is_template == filters['is_template'])
        
        challenges = search_query.order_by(Challenge.title).all()
        
        return challenges
    
    def get_challenge_stats(
        self,
        challenge_id: str,
        db: Optional[DBSession] = None
    ) -> Dict[str, Any]:
        """
        Get statistics for a challenge.
        
        Args:
            challenge_id: Challenge ID
            db: Database session (optional)
            
        Returns:
            Dictionary with challenge statistics
        """
        if db:
            return self._get_challenge_stats_with_db(challenge_id, db)
        
        with get_db_context() as db:
            return self._get_challenge_stats_with_db(challenge_id, db)
    
    def _get_challenge_stats_with_db(
        self,
        challenge_id: str,
        db: DBSession
    ) -> Dict[str, Any]:
        """Internal method to get challenge stats with database session."""
        from models.models import Session as SessionModel
        
        challenge = self._get_challenge_with_db(challenge_id, db)
        
        if not challenge:
            raise ValueError(f"Challenge not found: {challenge_id}")
        
        # Count sessions using this challenge
        session_count = db.query(SessionModel).filter(
            SessionModel.challenge_id == challenge_id
        ).count()
        
        # Count completed sessions
        from config.constants import SessionStatus
        completed_count = db.query(SessionModel).filter(
            SessionModel.challenge_id == challenge_id,
            SessionModel.status == SessionStatus.COMPLETED
        ).count()
        
        return {
            "challenge_id": challenge.id,
            "title": challenge.title,
            "total_sessions": session_count,
            "completed_sessions": completed_count,
            "completion_rate": (completed_count / session_count * 100) if session_count > 0 else 0
        }


# Global service instance
_challenge_service: Optional[ChallengeService] = None


def get_challenge_service() -> ChallengeService:
    """Get or create the global challenge service instance."""
    global _challenge_service
    if _challenge_service is None:
        _challenge_service = ChallengeService()
    return _challenge_service

