"""
Candidate chat interface page.
"""
import streamlit as st
import asyncio
from typing import Optional
import time

from models import get_db_context
from models.models import Session, SessionStatus
from services import get_chat_service, get_timer_service, get_session_service
from components.candidate.resource_panel import render_resource_panel
from components.shared.message_renderer import render_messages, render_message_input
from utils.logger import logger


def render():
    """Render the candidate chat interface."""
    st.title("👤 Candidate Interface")
    
    # Session initialization
    if "candidate_session_id" not in st.session_state:
        st.session_state.candidate_session_id = None
    
    if "last_refresh" not in st.session_state:
        st.session_state.last_refresh = time.time()
    
    # If no session, show session ID input
    if not st.session_state.candidate_session_id:
        render_session_join()
        return
    
    # Load and display session
    render_chat_interface()


def render_session_join():
    """Render session join interface."""
    st.markdown("### 🔐 Join Interview Session")
    st.markdown("Enter your Session ID to join the interview.")
    
    with st.form("join_session_form"):
        session_id = st.text_input(
            "Session ID",
            placeholder="e.g., 12345678-1234-1234-1234-123456789abc",
            help="Get this ID from your interviewer"
        )
        
        submitted = st.form_submit_button("Join Session", use_container_width=True, type="primary")
    
    if submitted:
        if not session_id or len(session_id.strip()) == 0:
            st.error("❌ Please enter a Session ID")
            return
        
        # Validate and join session
        try:
            with get_db_context() as db:
                session = db.query(Session).filter(Session.id == session_id.strip()).first()
                
                if not session:
                    st.error("❌ Session not found. Please check your Session ID.")
                    return
                
                if session.status == SessionStatus.COMPLETED:
                    st.error("❌ This session has already been completed.")
                    return
                
                # Join session
                st.session_state.candidate_session_id = session.id
                
                # Start session if not already started
                session_service = get_session_service()
                if session.status == SessionStatus.CREATED:
                    with get_db_context() as db:
                        session_service.start_session(session.id, db)
                    st.success("✅ Session started!")
                else:
                    st.success("✅ Joined session successfully!")
                
                st.rerun()
                
        except Exception as e:
            st.error(f"❌ Error joining session: {e}")
            logger.error(f"Error joining session: {e}", exc_info=True)


def render_chat_interface():
    """Render the main chat interface."""
    session_id = st.session_state.candidate_session_id
    
    try:
        with get_db_context() as db:
            session = db.query(Session).filter(Session.id == session_id).first()
            
            if not session:
                st.error("❌ Session not found")
                st.session_state.candidate_session_id = None
                st.rerun()
                return
            
            # Extract session data
            session_data = {
                "id": session.id,
                "candidate_name": session.candidate_name,
                "status": session.status,
                "challenge_text": session.challenge_text,
                "time_limit": session.time_limit,
                "token_budget": session.token_budget,
                "tokens_used": session.tokens_used,
                "start_time": session.start_time,
                "message_count": session.message_count
            }
        
        # Header with candidate name
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"### Welcome, {session_data['candidate_name']}!")
        with col2:
            if st.button("🚪 Leave Session", use_container_width=True):
                st.session_state.candidate_session_id = None
                st.rerun()
        
        st.markdown("---")
        
        # Get timer and token info
        with get_db_context() as db:
            session = db.query(Session).filter(Session.id == session_id).first()
            timer_service = get_timer_service()
            timer_info = timer_service.get_timer_info(session).to_dict()
            
            token_info = {
                "tokens_used": session.tokens_used,
                "token_budget": session.token_budget,
                "remaining": session.token_budget - session.tokens_used,
                "percentage_used": (session.tokens_used / session.token_budget * 100) if session.token_budget > 0 else 0
            }
        
        # Add custom CSS for sticky resource panel
        st.markdown("""
            <style>
            /* Make the resource panel sticky */
            [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
                position: sticky;
                top: 0;
                z-index: 999;
                background-color: white;
                padding-top: 10px;
                padding-bottom: 5px;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Resource panel (will be sticky due to CSS)
        render_resource_panel(timer_info, token_info)
        
        st.markdown("---")
        
        # Chat interface (NO challenge panel shown)
        st.markdown("### 💬 Chat")
        
        # Check if chat should be disabled
        is_expired = timer_info.get("is_expired", False)
        is_exhausted = token_info.get("remaining", 0) <= 0
        is_completed = session_data["status"] == SessionStatus.COMPLETED
        
        chat_disabled = is_expired or is_exhausted or is_completed
        
        # Display messages
        chat_service = get_chat_service()
        with get_db_context() as db:
            messages = chat_service.get_conversation(session_id, db)
        
        render_messages(messages)
        
        # Message input
        if chat_disabled:
            if is_expired:
                st.warning("⏰ **Session expired.** Chat is disabled.")
            elif is_exhausted:
                st.warning("🎫 **Token budget exhausted.** Chat is disabled.")
            elif is_completed:
                st.info("✅ **Session completed.** Chat is disabled.")
            
            # Disabled input
            render_message_input(disabled=True, placeholder="Chat is disabled")
        else:
            # Active input
            user_message = render_message_input(
                placeholder="Type your message here...",
                key="candidate_message_input"
            )
            
            if user_message:
                # Send message
                with st.spinner("🤖 AI is thinking..."):
                    with get_db_context() as db:
                        success, ai_message, error = asyncio.run(
                            chat_service.send_message(session_id, user_message, db)
                        )
                    
                    if success:
                        st.rerun()
                    else:
                        st.error(f"❌ {error}")
        
        # Auto-refresh indicator
        st.markdown("---")
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()
        
        st.caption(f"💡 Last updated: {time.strftime('%H:%M:%S')}")
        
    except Exception as e:
        st.error(f"❌ Error loading chat interface: {e}")
        logger.error(f"Error in chat interface: {e}", exc_info=True)
        
        if st.button("🔄 Retry"):
            st.rerun()


if __name__ == "__main__":
    render()
