"""
Interview Buddy - Main Application
AI-powered interview practice platform with resource tracking.
"""
import streamlit as st
from config import settings
from utils.logger import logger


def main():
    """Main application entry point."""
    
    # Page configuration
    st.set_page_config(
        page_title=settings.app_name,
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better styling
    st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 2rem;
        }
        .welcome-text {
            font-size: 1.2rem;
            text-align: center;
            margin-bottom: 2rem;
        }
        .feature-card {
            background-color: #f0f2f6;
            padding: 1.5rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
        }
        .stButton>button {
            width: 100%;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Sidebar navigation
    with st.sidebar:
        st.title("🎯 Navigation")
        st.markdown("---")
        
        # Navigation options
        page = st.radio(
            "Go to:",
            [
                "🏠 Home",
                "➕ Create Session",
                "👤 Candidate Interface",
                "👔 Interviewer Dashboard",
                "📊 Analytics",
                "📜 Session History",
                "⚙️ Settings"
            ],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.caption(f"v{settings.app_version}")
        
        # API key status
        if settings.validate_openai_key():
            st.success("✅ OpenAI API Connected")
        else:
            st.error("❌ OpenAI API Key Missing")
            st.caption("Please set OPENAI_API_KEY in .env file")
    
    # Main content based on navigation
    if page == "🏠 Home":
        show_home_page()
    elif page == "➕ Create Session":
        show_create_session_page()
    elif page == "👤 Candidate Interface":
        show_candidate_page()
    elif page == "👔 Interviewer Dashboard":
        show_interviewer_page()
    elif page == "📊 Analytics":
        show_analytics_page()
    elif page == "📜 Session History":
        show_history_page()
    elif page == "⚙️ Settings":
        show_settings_page()


def show_home_page():
    """Display the home page."""
    st.markdown('<div class="main-header">🎯 Interview Buddy</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="welcome-text">AI-Powered Interview Practice with Resource Tracking</div>',
        unsafe_allow_html=True
    )
    
    # Welcome message
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.subheader("👤 For Candidates")
        st.markdown("""
        - **Practice** coding interviews with AI assistance
        - **Track** your time and token usage
        - **Learn** with guided hints and feedback
        - **Review** your conversation history
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.subheader("👔 For Interviewers")
        st.markdown("""
        - **Monitor** candidate progress in real-time
        - **Control** session parameters
        - **Analyze** performance metrics
        - **Export** session transcripts
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Getting started
    st.subheader("🚀 Getting Started")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("**Step 1**\n\nCreate a new interview session")
    
    with col2:
        st.info("**Step 2**\n\nShare session ID with candidate")
    
    with col3:
        st.info("**Step 3**\n\nMonitor and analyze performance")
    
    st.markdown("---")
    
    # Quick actions
    st.subheader("⚡ Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("➕ Create New Session", use_container_width=True):
            st.info("Navigate to 'Create Session' from the sidebar")
    
    with col2:
        if st.button("👤 Join as Candidate", use_container_width=True):
            st.info("Navigate to 'Candidate Interface' from the sidebar")
    
    with col3:
        if st.button("👔 Interviewer Dashboard", use_container_width=True):
            st.info("Navigate to 'Interviewer Dashboard' from the sidebar")


def show_create_session_page():
    """Display session creation page (placeholder)."""
    st.title("➕ Create Interview Session")
    st.info("📝 Session creation interface will be implemented in Phase 2")
    st.markdown("---")
    st.markdown("""
    **Features to be implemented:**
    - Candidate information input
    - Time limit configuration
    - Token budget settings
    - Challenge selection
    - Session ID generation
    """)


def show_candidate_page():
    """Display candidate interface page (placeholder)."""
    st.title("👤 Candidate Interface")
    st.info("💬 Chat interface will be implemented in Phase 3")
    st.markdown("---")
    st.markdown("""
    **Features to be implemented:**
    - Real-time chat with AI
    - Timer countdown display
    - Token usage tracking
    - Challenge display
    - Message history
    """)


def show_interviewer_page():
    """Display interviewer dashboard page (placeholder)."""
    st.title("👔 Interviewer Dashboard")
    st.info("📊 Dashboard will be implemented in Phase 5")
    st.markdown("---")
    st.markdown("""
    **Features to be implemented:**
    - Active sessions list
    - Real-time monitoring
    - Session controls
    - Resource metrics
    - Conversation view
    """)


def show_analytics_page():
    """Display analytics page (placeholder)."""
    st.title("📊 Analytics")
    st.info("📈 Analytics dashboard will be implemented in Phase 8")
    st.markdown("---")
    st.markdown("""
    **Features to be implemented:**
    - Performance metrics
    - Token usage graphs
    - Time utilization charts
    - Efficiency scores
    - Data export
    """)


def show_history_page():
    """Display session history page (placeholder)."""
    st.title("📜 Session History")
    st.info("🗂️ Session history will be implemented in Phase 9")
    st.markdown("---")
    st.markdown("""
    **Features to be implemented:**
    - Session search and filter
    - Session replay
    - Export functionality
    - Performance comparison
    """)


def show_settings_page():
    """Display settings page."""
    st.title("⚙️ Settings")
    
    st.subheader("🔧 Configuration")
    
    # Display current settings
    with st.expander("OpenAI Configuration", expanded=True):
        st.text(f"Model: {settings.openai_model}")
        st.text(f"Max Tokens: {settings.openai_max_tokens}")
        st.text(f"Temperature: {settings.openai_temperature}")
        st.text(f"API Key: {'✅ Set' if settings.validate_openai_key() else '❌ Not Set'}")
    
    with st.expander("Session Defaults"):
        st.text(f"Default Duration: {settings.default_session_duration}s ({settings.default_session_duration // 60} minutes)")
        st.text(f"Default Token Budget: {settings.default_token_budget:,}")
        st.text(f"Max Message Length: {settings.max_message_length}")
    
    with st.expander("Application Info"):
        st.text(f"App Name: {settings.app_name}")
        st.text(f"Version: {settings.app_version}")
        st.text(f"Debug Mode: {settings.debug}")
        st.text(f"Log Level: {settings.log_level}")
        st.text(f"Database: {settings.database_url}")
    
    st.markdown("---")
    st.caption("💡 To change settings, edit the .env file and restart the application")


if __name__ == "__main__":
    try:
        logger.info("Starting Interview Buddy application")
        main()
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        st.error(f"An error occurred: {e}")

