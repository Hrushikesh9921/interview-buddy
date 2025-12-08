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
from components.shared.message_renderer import render_messages, render_message_input
from utils.logger import logger


def render():
    """Render the candidate chat interface."""
    # Session initialization
    if "candidate_session_id" not in st.session_state:
        st.session_state.candidate_session_id = None
    
    if "last_refresh" not in st.session_state:
        st.session_state.last_refresh = time.time()
    
    # Check for session_id in URL query parameters
    query_params = st.query_params
    if "session_id" in query_params and not st.session_state.candidate_session_id:
        url_session_id = query_params["session_id"]
        # Validate the session exists
        try:
            with get_db_context() as db:
                session = db.query(Session).filter(Session.id == url_session_id).first()
                if session and session.status != SessionStatus.COMPLETED:
                    st.session_state.candidate_session_id = url_session_id
                    # Start session if needed
                    session_service = get_session_service()
                    if session.status == SessionStatus.CREATED:
                        session_service.start_session(url_session_id, db)
                    st.rerun()
        except Exception as e:
            logger.error(f"Error loading session from URL: {e}")
    
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
        
        # Add custom CSS for isolated candidate interface
        st.markdown("""
            <style>
            /* HIDE ALL NAVIGATION - Candidate should NOT see other pages */
            [data-testid="stSidebarNav"] {
                display: none !important;
            }
            
            /* Hide Navigation header */
            [data-testid="stSidebar"] h1,
            [data-testid="stSidebar"] [data-testid="stHeading"] {
                display: none !important;
            }
            
            /* Hide the collapse arrow for sidebar */
            [data-testid="collapsedControl"] {
                display: none !important;
            }
            
            /* Hide Deploy button and menu */
            [data-testid="stHeader"] {
                display: none !important;
            }
            
            header[data-testid="stHeader"] {
                display: none !important;
            }
            
            /* Hide top banner/toolbar */
            .stDeployButton {
                display: none !important;
            }
            
            /* Proper chat area layout with padding */
            .main .block-container {
                padding-top: 1.5rem;
                padding-bottom: 1rem;
                padding-left: 2.5rem;
                padding-right: 2.5rem;
                max-width: 100%;
            }
            
            /* Better spacing for chat content */
            .main .block-container > div {
                gap: 1rem;
            }
            
            /* Chat messages styling */
            [data-testid="stChatMessageContainer"] {
                padding: 1rem 0;
            }
            
            /* Chat input styling */
            [data-testid="stChatInput"] {
                margin-top: 1rem;
            }
            
            /* Improve message spacing */
            .stChatMessage {
                margin-bottom: 1rem;
            }
            
            /* Better alignment for chat area */
            section[data-testid="stVerticalBlock"] > div {
                gap: 1rem;
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
            
            # Timer with auto-decrement and progress bar
            timer_percentage = timer_info.get("percentage_used", 0)
            timer_color = "#28a745" if timer_percentage < 75 else ("#fd7e14" if timer_percentage < 90 else "#dc3545")
            remaining_seconds = timer_info.get("remaining_seconds", 0)
            timer_html = f"""
                <div style='margin: 10px 0;'>
                    <strong>⏱️ Time Remaining:</strong><br>
                    <span id='timer-display' style='font-size: 24px; font-family: monospace; color: {timer_color};'>
                        {timer_info.get("formatted_remaining", "00:00:00")}
                    </span><br>
                    <div style='width: 100%; background-color: #e0e0e0; border-radius: 10px; height: 8px; margin: 8px 0;'>
                        <div id='timer-progress' style='width: {100 - timer_percentage}%; background-color: {timer_color}; height: 100%; border-radius: 10px; transition: width 1s linear, background-color 0.3s;'></div>
                    </div>
                    <small style='color: #666;'><span id='timer-percentage'>{timer_percentage:.0f}</span>% used</small>
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
                            
                            let percentageUsed = ((timeLimit - remainingSeconds) / timeLimit * 100);
                            let percentageRemaining = 100 - percentageUsed;
                            
                            // Determine color
                            let color = '#28a745';
                            if (percentageUsed >= 90) {{
                                color = '#dc3545';
                            }} else if (percentageUsed >= 75) {{
                                color = '#fd7e14';
                            }}
                            
                            let timerDisplay = document.getElementById('timer-display');
                            if (timerDisplay) {{
                                timerDisplay.textContent = formattedTime;
                                timerDisplay.style.color = color;
                            }}
                            
                            let percentageDisplay = document.getElementById('timer-percentage');
                            if (percentageDisplay) {{
                                percentageDisplay.textContent = Math.round(percentageUsed);
                            }}
                            
                            let progressBar = document.getElementById('timer-progress');
                            if (progressBar) {{
                                progressBar.style.width = percentageRemaining + '%';
                                progressBar.style.backgroundColor = color;
                            }}
                        }}
                    }}
                    
                    // Update timer every second
                    setInterval(updateTimer, 1000);
                </script>
            """
            components.html(timer_html, height=100)
            
            # Get timer warning from service
            timer_service = get_timer_service()
            with get_db_context() as db:
                session_obj = db.query(Session).filter(Session.id == session_id).first()
                timer_warning = timer_service.get_warning_message(session_obj)
            
            if timer_warning:
                st.warning(timer_warning)
            
            # Tokens with progress bar
            token_percentage = token_info.get("percentage_used", 0)
            token_color = "#28a745" if token_percentage < 75 else ("#fd7e14" if token_percentage < 90 else "#dc3545")
            st.markdown(f"""
                <div style='margin: 10px 0;'>
                    <strong>🎫 Tokens Remaining:</strong><br>
                    <span style='font-size: 20px; color: {token_color};'>
                        {token_info.get("remaining", 0):,} / {token_info.get("token_budget", 0):,}
                    </span><br>
                    <div style='width: 100%; background-color: #e0e0e0; border-radius: 10px; height: 8px; margin: 8px 0;'>
                        <div style='width: {100 - token_percentage}%; background-color: {token_color}; height: 100%; border-radius: 10px;'></div>
                    </div>
                    <small style='color: #666;'>{token_percentage:.0f}% used</small>
                </div>
            """, unsafe_allow_html=True)
            
            # Get token warning and estimated queries from service
            from services import get_token_service
            token_service = get_token_service()
            with get_db_context() as db:
                token_warning = token_service.get_warning_message(session_id, db)
                estimated_queries = token_service.estimate_queries_remaining(session_id, db)
            
            if token_warning:
                st.warning(token_warning)
            
            if estimated_queries is not None and estimated_queries > 0:
                st.info(f"📊 Estimated queries remaining: **~{estimated_queries}**")
            
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