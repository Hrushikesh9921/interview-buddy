"""
Enhanced challenge display component for candidate interface.
"""
import streamlit as st
from typing import Dict, Optional


def render_challenge_panel(session_data: Dict):
    """
    Render enhanced challenge display in sidebar.
    
    Args:
        session_data: Dictionary with session data including challenge_id and challenge_text
    """
    if session_data.get("challenge_id"):
        # Load full challenge from DB
        from services import get_challenge_service
        from models import get_db_context
        
        challenge_service = get_challenge_service()
        with get_db_context() as db:
            challenge_obj = challenge_service.get_challenge(session_data["challenge_id"], db)
            
            # Convert to dict INSIDE the db context to avoid DetachedInstanceError
            if challenge_obj:
                challenge_data = {
                    "title": challenge_obj.title,
                    "description": challenge_obj.description,
                    "category": challenge_obj.category,
                    "difficulty": challenge_obj.difficulty,
                    "instructions": challenge_obj.instructions,
                    "starter_code": challenge_obj.starter_code,
                    "hints": challenge_obj.hints,
                    "tags": challenge_obj.tags,
                    "estimated_duration": challenge_obj.estimated_duration
                }
            else:
                challenge_data = None
        
        if challenge_data:
            # Render simplified info in sidebar
            st.markdown("### 📋 Challenge")
            
            # Title and metadata
            st.markdown(f"**{challenge_data['title']}**")
            
            # Metadata row
            category_str = challenge_data['category'].value.replace('_', ' ').title()
            difficulty_str = challenge_data['difficulty'].value.capitalize()
            
            metadata_parts = [category_str, difficulty_str]
            if challenge_data['estimated_duration']:
                duration_str = f"~{challenge_data['estimated_duration'] // 60} min"
                metadata_parts.append(duration_str)
            
            st.caption(" • ".join(metadata_parts))
            
            # Hints only (collapsible)
            if challenge_data['hints']:
                with st.expander("💡 Hints", expanded=False):
                    for i, hint in enumerate(challenge_data['hints'], 1):
                        st.markdown(f"{i}. {hint}")
        else:
            # Challenge not found (deleted?)
            st.warning("⚠️ Challenge not found")
    
    elif session_data.get("challenge_text"):
        # Legacy text-only challenge
        st.markdown("### 📋 Challenge")
        
        # Display in a styled box
        st.markdown(
            f'<div class="challenge-box">{session_data["challenge_text"]}</div>',
            unsafe_allow_html=True
        )
    
    else:
        # No challenge
        st.info("ℹ️ No challenge assigned for this session")


def get_challenge_data(session_data: Dict) -> Optional[Dict]:
    """
    Get full challenge data for rendering.
    
    Args:
        session_data: Dictionary with session data including challenge_id and challenge_text
        
    Returns:
        Dictionary with challenge data or None if no challenge
    """
    if session_data.get("challenge_id"):
        from services import get_challenge_service
        from models import get_db_context
        
        challenge_service = get_challenge_service()
        with get_db_context() as db:
            challenge_obj = challenge_service.get_challenge(session_data["challenge_id"], db)
            
            # Convert to dict INSIDE the db context to avoid DetachedInstanceError
            if challenge_obj:
                return {
                    "title": challenge_obj.title,
                    "description": challenge_obj.description,
                    "category": challenge_obj.category,
                    "difficulty": challenge_obj.difficulty,
                    "instructions": challenge_obj.instructions,
                    "starter_code": challenge_obj.starter_code,
                    "hints": challenge_obj.hints,
                    "tags": challenge_obj.tags,
                    "estimated_duration": challenge_obj.estimated_duration
                }
    elif session_data.get("challenge_text"):
        return {
            "title": "Custom Challenge",
            "instructions": session_data["challenge_text"],
            "description": session_data["challenge_text"]
        }
    
    return None


def render_challenge_instructions(session_data: Dict):
    """
    Render full challenge instructions in main content area.
    
    Args:
        session_data: Dictionary with session data including challenge_id and challenge_text
    """
    challenge_data = get_challenge_data(session_data)
    
    if not challenge_data:
        return
    
    # Render as collapsible expander
    with st.expander("📖 Problem Statement", expanded=True):
        if challenge_data.get('instructions'):
            st.markdown(challenge_data['instructions'])
        elif challenge_data.get('description'):
            st.markdown(challenge_data['description'])
        else:
            st.info("No problem statement available")

