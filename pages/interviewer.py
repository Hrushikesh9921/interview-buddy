"""
Interviewer dashboard page.
Phase 5: Interviewer Dashboard Foundation
"""
import streamlit as st
import time
from datetime import datetime
from typing import List, Dict

from models import get_db_context
from models.models import Session, SessionStatus
from services import get_session_service, get_timer_service
from utils.logger import logger


def render():
    """Render the interviewer dashboard."""
    st.title("👔 Interviewer Dashboard")
    st.markdown("Monitor and manage active interview sessions")
    
    # Initialize session state for selected session
    if "selected_session_id" not in st.session_state:
        st.session_state.selected_session_id = None
    
    # Auto-refresh toggle
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown("### 📊 Active Sessions")
    with col2:
        auto_refresh = st.checkbox("🔄 Auto-refresh", value=True, key="auto_refresh")
    with col3:
        if st.button("🔄 Refresh Now", use_container_width=True):
            st.rerun()
    
    # Get all active sessions within db context
    session_service = get_session_service()
    with get_db_context() as db:
        all_sessions = session_service.list_sessions(status=None, limit=100, db=db)
        
        # Filter active/paused sessions (only those that have started) and create simple dicts
        active_sessions = []
        for s in all_sessions:
            # Only show sessions that have been started (have start_time)
            if s.status != SessionStatus.COMPLETED and s.start_time is not None:
                # Get timer info while in session
                timer_service = get_timer_service()
                timer_info = timer_service.get_timer_info(s).to_dict()
                
                # Create a simple dict with all needed data
                session_data = {
                    "id": s.id,
                    "candidate_name": s.candidate_name,
                    "status": s.status,
                    "start_time": s.start_time,
                    "time_limit": s.time_limit,
                    "token_budget": s.token_budget,
                    "tokens_used": s.tokens_used,
                    "message_count": s.message_count,
                    "timer_info": timer_info
                }
                active_sessions.append(session_data)
    
    if not active_sessions:
        st.info("📭 No active sessions. Create a new session to get started.")
        if st.button("➕ Create New Session", type="primary"):
            st.switch_page("pages/session_create.py")
        return
    
    # Two-column layout: Sessions list on left, monitor on right
    st.markdown("---")
    
    col_left, col_right = st.columns([1, 2])
    
    # Left column: Sessions list
    with col_left:
        st.markdown("#### 📋 Sessions List")
        
        # Scrollable container
        for session in active_sessions:
            render_session_list_item(session)
    
    # Right column: Session monitor
    with col_right:
        if st.session_state.selected_session_id:
            render_session_monitor(st.session_state.selected_session_id)
        else:
            # Show placeholder when no session selected
            st.markdown("### 👈 Select a session to monitor")
            st.info("Click on any session from the list to view live conversation and metrics.")
    
    # Auto-refresh every 5 seconds if enabled
    if auto_refresh:
        time.sleep(5)
        st.rerun()


def render_session_list_item(session_data: Dict):
    """Render a compact session list item."""
    timer_info = session_data["timer_info"]
    
    # Determine status color
    if session_data["status"] == SessionStatus.ACTIVE:
        status_color = "#28a745"
        status_icon = "🟢"
    elif session_data["status"] == SessionStatus.PAUSED:
        status_color = "#fd7e14"
        status_icon = "🟡"
    else:
        status_color = "#6c757d"
        status_icon = "⚪"
    
    # Check if selected
    is_selected = st.session_state.selected_session_id == session_data["id"]
    
    # Time and token colors
    time_percentage = timer_info.get("percentage_used", 0)
    time_color = "#dc3545" if time_percentage > 90 else ("#fd7e14" if time_percentage > 75 else "#28a745")
    
    token_percentage = (session_data["tokens_used"] / session_data["token_budget"] * 100) if session_data["token_budget"] > 0 else 0
    token_color = "#dc3545" if token_percentage > 90 else ("#fd7e14" if token_percentage > 75 else "#28a745")
    
    # Compact card
    with st.container():
        if st.button(
            f"{status_icon} {session_data['candidate_name']}",
            key=f"select_{session_data['id']}",
            use_container_width=True,
            type="primary" if is_selected else "secondary"
        ):
            if is_selected:
                st.session_state.selected_session_id = None
            else:
                st.session_state.selected_session_id = session_data["id"]
            st.rerun()
        
        # Show compact metrics below button in one line
        st.markdown(f"""
            <div style="
                padding: 6px 8px;
                background-color: {'#e7f3ff' if is_selected else '#f8f9fa'};
                border-radius: 4px;
                margin-bottom: 10px;
                font-size: 11px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            ">
                <span><strong>⏱️</strong> <span style="color: {time_color}; font-weight: bold;">{timer_info.get('formatted_remaining', '00:00:00')}</span></span>
                <span><strong>🎫</strong> <span style="color: {token_color}; font-weight: bold;">{(session_data['token_budget'] - session_data['tokens_used']) // 1000}k</span></span>
                <span><strong>💬</strong> {session_data['message_count']}</span>
            </div>
        """, unsafe_allow_html=True)


def render_session_card(session_data: Dict):
    """Render a session card with key information."""
    timer_info = session_data["timer_info"]
    
    # Determine card color based on status
    if session_data["status"] == SessionStatus.ACTIVE:
        status_color = "#28a745"
        status_icon = "🟢"
    elif session_data["status"] == SessionStatus.PAUSED:
        status_color = "#fd7e14"
        status_icon = "🟡"
    else:
        status_color = "#6c757d"
        status_icon = "⚪"
    
    # Card styling
    is_selected = st.session_state.selected_session_id == session_data["id"]
    border_color = "#0d6efd" if is_selected else "#dee2e6"
    border_width = "3px" if is_selected else "1px"
    
    # Create card
    with st.container():
        st.markdown(f"""
            <div style="
                border: {border_width} solid {border_color};
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 15px;
                background-color: {'#f8f9fa' if is_selected else 'white'};
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            ">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <h4 style="margin: 0; color: #333;">{status_icon} {session_data["candidate_name"]}</h4>
                    <span style="color: {status_color}; font-weight: bold; font-size: 12px;">
                        {session_data["status"].value.upper()}
                    </span>
                </div>
                <p style="margin: 5px 0; font-size: 12px; color: #666;">
                    <strong>Session ID:</strong> {session_data["id"][:8]}...
                </p>
                <p style="margin: 5px 0; font-size: 12px; color: #666;">
                    <strong>Started:</strong> {session_data["start_time"].strftime('%Y-%m-%d %H:%M:%S') if session_data["start_time"] else 'Not started'}
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Metrics row
        col1, col2, col3 = st.columns(3)
        
        with col1:
            time_color = "#dc3545" if timer_info.get("percentage_used", 0) > 90 else ("#fd7e14" if timer_info.get("percentage_used", 0) > 75 else "#28a745")
            st.markdown(f"""
                <div style="text-align: center;">
                    <div style="font-size: 20px; font-weight: bold; color: {time_color};">
                        {timer_info.get('formatted_remaining', '00:00:00')}
                    </div>
                    <div style="font-size: 11px; color: #666;">Time Left</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            token_percentage = (session_data["tokens_used"] / session_data["token_budget"] * 100) if session_data["token_budget"] > 0 else 0
            token_color = "#dc3545" if token_percentage > 90 else ("#fd7e14" if token_percentage > 75 else "#28a745")
            st.markdown(f"""
                <div style="text-align: center;">
                    <div style="font-size: 20px; font-weight: bold; color: {token_color};">
                        {session_data["token_budget"] - session_data["tokens_used"]:,}
                    </div>
                    <div style="font-size: 11px; color: #666;">Tokens Left</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
                <div style="text-align: center;">
                    <div style="font-size: 20px; font-weight: bold; color: #0d6efd;">
                        {session_data["message_count"]}
                    </div>
                    <div style="font-size: 11px; color: #666;">Messages</div>
                </div>
            """, unsafe_allow_html=True)
        
        # Action button
        if st.button(
            "👁️ Monitor Session" if not is_selected else "✓ Monitoring",
            key=f"select_{session_data['id']}",
            use_container_width=True,
            type="primary" if is_selected else "secondary"
        ):
            if is_selected:
                st.session_state.selected_session_id = None
            else:
                st.session_state.selected_session_id = session_data["id"]
            st.rerun()


def render_session_monitor(session_id: str):
    """Render detailed session monitoring view."""
    st.markdown("### 🔍 Session Monitor")
    
    # Get session details
    with get_db_context() as db:
        session = db.query(Session).filter(Session.id == session_id).first()
        
        if not session:
            st.error("Session not found")
            st.session_state.selected_session_id = None
            st.rerun()
            return
        
        # Session header
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"#### 👤 {session.candidate_name}")
            st.caption(f"Session ID: `{session.id}`")
        
        with col2:
            if st.button("❌ Close Monitor", use_container_width=True):
                st.session_state.selected_session_id = None
                st.rerun()
        
        # Tabs for different views
        tab1, tab2, tab3 = st.tabs(["💬 Conversation", "📊 Metrics", "⚙️ Controls"])
        
        with tab1:
            render_conversation_view(session, db)
        
        with tab2:
            render_metrics_view(session)
        
        with tab3:
            render_controls_view(session, db)


def render_conversation_view(session: Session, db):
    """Render the conversation view."""
    from services import get_chat_service
    
    st.markdown("#### 💬 Live Conversation")
    
    chat_service = get_chat_service()
    messages = chat_service.get_conversation(session.id, db)
    
    if not messages:
        st.info("No messages yet in this session")
        return
    
    # Display messages
    for msg in messages:
        if msg.role.value == "user":
            st.markdown(f"""
                <div style="background: #e3f2fd; padding: 10px; border-radius: 8px; margin: 10px 0;">
                    <strong>👤 Candidate:</strong><br>
                    {msg.content}
                    <br><small style="color: #666;">🎫 {msg.tokens} tokens | {msg.created_at.strftime('%H:%M:%S')}</small>
                </div>
            """, unsafe_allow_html=True)
        elif msg.role.value == "assistant":
            st.markdown(f"""
                <div style="background: #f1f8e9; padding: 10px; border-radius: 8px; margin: 10px 0;">
                    <strong>🤖 AI:</strong><br>
                    {msg.content[:500]}{'...' if len(msg.content) > 500 else ''}
                    <br><small style="color: #666;">🎫 {msg.tokens} tokens | {msg.created_at.strftime('%H:%M:%S')}</small>
                </div>
            """, unsafe_allow_html=True)


def render_metrics_view(session: Session):
    """Render the metrics view."""
    st.markdown("#### 📊 Session Metrics")
    
    timer_service = get_timer_service()
    timer_info = timer_service.get_timer_info(session).to_dict()
    
    # Time metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("⏱️ Time Limit", f"{session.time_limit} min")
        st.metric("⏳ Time Elapsed", f"{timer_info.get('elapsed_seconds', 0) // 60} min")
        st.metric("⏰ Time Remaining", timer_info.get('formatted_remaining', '00:00:00'))
    
    with col2:
        st.metric("🎫 Token Budget", f"{session.token_budget:,}")
        st.metric("📊 Tokens Used", f"{session.tokens_used:,}")
        st.metric("💰 Tokens Remaining", f"{session.token_budget - session.tokens_used:,}")
    
    with col3:
        st.metric("💬 Messages", session.message_count)
        st.metric("📥 Input Tokens", f"{session.input_tokens:,}")
        st.metric("📤 Output Tokens", f"{session.output_tokens:,}")
    
    # Progress bars
    st.markdown("---")
    st.markdown("##### Progress")
    
    time_percentage = timer_info.get('percentage_used', 0)
    # Ensure percentage is between 0 and 100
    time_progress = min(max(time_percentage / 100, 0.0), 1.0)
    st.progress(time_progress, text=f"Time Used: {time_percentage:.1f}%")
    
    token_percentage = (session.tokens_used / session.token_budget * 100) if session.token_budget > 0 else 0
    # Ensure percentage is between 0 and 100
    token_progress = min(max(token_percentage / 100, 0.0), 1.0)
    st.progress(token_progress, text=f"Tokens Used: {token_percentage:.1f}%")


def render_controls_view(session: Session, db):
    """Render the session controls view."""
    st.markdown("#### ⚙️ Session Controls")
    
    st.warning("⚠️ **Warning:** These actions will affect the candidate's active session.")
    
    st.markdown("---")
    
    # End Session
    st.markdown("##### 🛑 End Session")
    st.markdown("Permanently end this interview session. The candidate will be notified.")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("🛑 End Session", type="primary", use_container_width=True, key="end_session_btn"):
            st.session_state.show_end_confirmation = True
            st.rerun()
    
    # Confirmation dialog
    if st.session_state.get("show_end_confirmation", False):
        st.markdown("---")
        st.error("### ⚠️ Confirm End Session")
        st.markdown(f"Are you sure you want to end the session for **{session.candidate_name}**?")
        st.markdown("This action cannot be undone.")
        
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("✅ Yes, End It", type="primary", use_container_width=True):
                # End the session
                session_service = get_session_service()
                session_service.end_session(session.id, db)
                
                st.success(f"✅ Session ended for {session.candidate_name}")
                st.session_state.show_end_confirmation = False
                st.session_state.selected_session_id = None
                time.sleep(2)
                st.rerun()
        
        with col2:
            if st.button("❌ Cancel", use_container_width=True):
                st.session_state.show_end_confirmation = False
                st.rerun()


if __name__ == "__main__":
    render()
