"""
Candidate chat interface page.
"""
import streamlit as st
import streamlit.components.v1 as components
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
    # Session initialization
    if "candidate_session_id" not in st.session_state:
        st.session_state.candidate_session_id = None
    
    if "last_refresh" not in st.session_state:
        st.session_state.last_refresh = time.time()
    
    # If no session, show session ID input
    if not st.session_state.candidate_session_id:
        st.title("👤 Candidate Interface")
        render_session_join()
        return
    
    # Load and display session (no title here to save space)
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
        
        # Get timer and token info
        with get_db_context() as db:
            session = db.query(Session).filter(Session.id == session_id).first()
            timer_service = get_timer_service()
            timer_info = timer_service.get_timer_info(session).to_dict()
            
            token_info = {
                "tokens_used": session.tokens_used,
                "token_budget": session.token_budget,
                "remaining": session.token_budget - session.tokens_used,
                "percentage_used": (session.tokens_used / session.token_budget * 100) if session.token_budget > 0 else 0,
                "input_tokens": session.input_tokens,
                "output_tokens": session.output_tokens
            }
        
        # Add custom CSS for better layout
        st.markdown("""
            <style>
            /* Hide navigation links */
            [data-testid="stSidebarNav"] {
                display: none;
            }
            
            /* Full width layout - remove ALL padding */
            .main .block-container {
                padding-top: 0.5rem;
                padding-bottom: 0rem;
                padding-left: 0rem;
                padding-right: 0rem;
                max-width: 100%;
            }
            
            /* Customize sidebar for resources */
            [data-testid="stSidebar"] {
                background-color: #f8f9fa;
            }
            
            [data-testid="stSidebar"] > div:first-child {
                padding: 12px;
                padding-top: 0.5rem;
            }
            
            /* Reduce top spacing in sidebar headings */
            [data-testid="stSidebar"] h3 {
                margin-top: 0rem;
                padding-top: 0rem;
            }
            
            /* Challenge styling in sidebar */
            .challenge-box {
                background-color: white;
                padding: 12px;
                border-radius: 6px;
                border-left: 3px solid #0d6efd;
                margin: 15px 0;
                font-size: 13px;
                line-height: 1.5;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Use native Streamlit sidebar for Resources and Challenge (always visible!)
        with st.sidebar:
            # Header with candidate name
            st.markdown(f"### 👤 {session_data['candidate_name']}")
            
            if st.button("🚪 Leave Session", use_container_width=True, key="leave_btn"):
                st.session_state.candidate_session_id = None
                st.rerun()
            
            st.markdown("---")
            
            # Resources section
            st.markdown("#### 📊 Resources")
            
            # Timer with auto-decrement using HTML component
            timer_color = "#28a745" if timer_info.get("percentage_used", 0) < 75 else ("#fd7e14" if timer_info.get("percentage_used", 0) < 90 else "#dc3545")
            remaining_seconds = timer_info.get("remaining_seconds", 0)
            timer_html = f"""
                <div style='margin: 10px 0;'>
                    <strong>⏱️ Time Remaining:</strong><br>
                    <span id='timer-display' style='font-size: 24px; font-family: monospace; color: {timer_color};'>
                        {timer_info.get("formatted_remaining", "00:00:00")}
                    </span><br>
                    <small style='color: #666;'><span id='timer-percentage'>{timer_info.get("percentage_used", 0):.0f}</span>% used</small>
                </div>
                <script>
                    let remainingSeconds = {remaining_seconds};
                    let timeLimit = {timer_info.get("time_limit", 0)};
                    
                    function updateTimer() {{
                        if (remainingSeconds > 0) {{
                            remainingSeconds--;
                            
                            let hours = Math.floor(remainingSeconds / 3600);
                            let minutes = Math.floor((remainingSeconds % 3600) / 60);
                            let seconds = remainingSeconds % 60;
                            
                            let formattedTime = 
                                String(hours).padStart(2, '0') + ':' + 
                                String(minutes).padStart(2, '0') + ':' + 
                                String(seconds).padStart(2, '0');
                            
                            let timerDisplay = document.getElementById('timer-display');
                            if (timerDisplay) {{
                                timerDisplay.textContent = formattedTime;
                                
                                // Update color based on percentage
                                let percentageUsed = ((timeLimit - remainingSeconds) / timeLimit * 100);
                                if (percentageUsed < 75) {{
                                    timerDisplay.style.color = '#28a745';
                                }} else if (percentageUsed < 90) {{
                                    timerDisplay.style.color = '#fd7e14';
                                }} else {{
                                    timerDisplay.style.color = '#dc3545';
                                }}
                            }}
                            
                            let percentageDisplay = document.getElementById('timer-percentage');
                            if (percentageDisplay) {{
                                percentageDisplay.textContent = Math.round((timeLimit - remainingSeconds) / timeLimit * 100);
                            }}
                        }}
                    }}
                    
                    // Update timer every second
                    setInterval(updateTimer, 1000);
                </script>
            """
            components.html(timer_html, height=80)
            
            # Tokens
            token_color = "#28a745" if token_info.get("percentage_used", 0) < 75 else ("#fd7e14" if token_info.get("percentage_used", 0) < 90 else "#dc3545")
            st.markdown(f"""
                <div style='margin: 10px 0;'>
                    <strong>🎫 Tokens Remaining:</strong><br>
                    <span style='font-size: 20px; color: {token_color};'>
                        {token_info.get("remaining", 0):,} / {token_info.get("token_budget", 0):,}
                    </span><br>
                    <small style='color: #666;'>{token_info.get("percentage_used", 0):.0f}% used</small>
                </div>
            """, unsafe_allow_html=True)
            
            # Token breakdown explanation
            with st.expander("ℹ️ Token calculation", expanded=False):
                st.markdown(f"""
                **Why is the total higher than individual messages?**
                
                Each API call includes:
                - System prompt (challenge description)
                - **All previous messages** (entire conversation)
                - Your new message
                - AI's response
                
                **Your session breakdown:**
                - 📥 Input tokens (prompts): **{token_info.get("input_tokens", 0):,}**
                - 📤 Output tokens (AI responses): **{token_info.get("output_tokens", 0):,}**
                - 📊 Total consumed: **{token_info.get("tokens_used", 0):,}**
                
                💡 *The cost grows with each exchange because OpenAI needs the full context!*
                """)
            
            st.markdown("---")
            
            # Challenge section (SECURE - no XSS vulnerability!)
            if session_data["challenge_text"]:
                st.markdown("#### 📝 Challenge")
                # Using st.info() to safely display user input without XSS risk
                st.info(session_data["challenge_text"])
        
        # Main content area: Chat
        st.markdown("## 💬 Chat")
        
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
        
        # Status indicator (no manual refresh needed)
        st.caption(f"💡 Last updated: {time.strftime('%H:%M:%S')}")
        
    except Exception as e:
        st.error(f"❌ Error loading chat interface: {e}")
        logger.error(f"Error in chat interface: {e}", exc_info=True)
        
        if st.button("🔄 Retry"):
            st.rerun()


if __name__ == "__main__":
    render()