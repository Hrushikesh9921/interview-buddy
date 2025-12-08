"""
Session creation page.
"""
import streamlit as st
from services import SessionConfig, get_session_service
from config.settings import settings
from utils.logger import logger


def render():
    """Render the session creation page."""
    st.title("➕ Create Interview Session")
    st.markdown("Set up a new interview session for a candidate.")
    st.markdown("---")
    
    # Session creation form
    with st.form("session_create_form"):
        st.subheader("📋 Candidate Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            candidate_name = st.text_input(
                "Candidate Name *",
                placeholder="John Doe",
                help="Full name of the candidate"
            )
        
        with col2:
            candidate_email = st.text_input(
                "Candidate Email",
                placeholder="john@example.com",
                help="Email address (optional)"
            )
        
        st.markdown("---")
        st.subheader("⚙️ Session Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            time_limit_minutes = st.number_input(
                "Time Limit (minutes) *",
                min_value=1,
                max_value=180,
                value=60,
                step=1,
                help="Maximum duration for the interview"
            )
        
        with col2:
            token_budget = st.number_input(
                "Token Budget *",
                min_value=1000,
                max_value=200000,
                value=settings.default_token_budget,
                step=1000,
                help="Maximum tokens the candidate can use"
            )
        
        # Model selection
        model_options = ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"]
        model_name = st.selectbox(
            "AI Model *",
            options=model_options,
            index=0,
            help="OpenAI model to use for the interview"
        )
        
        st.markdown("---")
        st.subheader("📝 Challenge")
        
        challenge_text = st.text_area(
            "Challenge Description",
            placeholder="Enter the coding challenge or interview question here...\n\nExample:\nWrite a function that finds the two numbers in an array that add up to a target sum.",
            height=200,
            help="The challenge or problem the candidate should solve"
        )
        
        st.markdown("---")
        
        # Submit button
        submitted = st.form_submit_button(
            "🚀 Create Session",
            use_container_width=True,
            type="primary"
        )
    
    # Handle form submission
    if submitted:
        # Validation
        errors = []
        
        if not candidate_name or len(candidate_name.strip()) == 0:
            errors.append("Candidate name is required")
        
        if candidate_email and "@" not in candidate_email:
            errors.append("Invalid email address")
        
        if time_limit_minutes < 1:
            errors.append("Time limit must be at least 1 minute")
        
        if token_budget < 1000:
            errors.append("Token budget must be at least 1000")
        
        if errors:
            for error in errors:
                st.error(f"❌ {error}")
        else:
            # Create session
            try:
                service = get_session_service()
                
                config = SessionConfig(
                    candidate_name=candidate_name.strip(),
                    candidate_email=candidate_email.strip() if candidate_email else None,
                    time_limit=time_limit_minutes * 60,  # Convert to seconds
                    token_budget=token_budget,
                    model_name=model_name,
                    challenge_text=challenge_text.strip() if challenge_text else None
                )
                
                with st.spinner("Creating session..."):
                    from models import get_db_context
                    with get_db_context() as db:
                        session = service.create_session(config, db)
                        # Extract all data we need while db session is active
                        session_data = {
                            "id": session.id,
                            "candidate_name": session.candidate_name,
                            "candidate_email": session.candidate_email,
                            "time_limit": session.time_limit,
                            "token_budget": session.token_budget,
                            "model_name": session.model_name,
                            "challenge_text": session.challenge_text
                        }
                
                # Success!
                st.success("✅ Session created successfully!")
                
                # Display session details
                st.markdown("---")
                st.subheader("📊 Session Details")
                
                # Session ID and Direct Link (prominent display)
                st.markdown("### 🔑 Session ID")
                st.code(session_data["id"], language=None)
                
                # Direct candidate link
                st.markdown("### 🔗 Direct Candidate Link")
                candidate_url = f"http://localhost:8501/candidate?session_id={session_data['id']}"
                st.code(candidate_url, language=None)
                st.caption("⭐ Share this link with the candidate for instant access (no ID entry needed!)")
                
                # Session info
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Time Limit", f"{time_limit_minutes} min")
                
                with col2:
                    st.metric("Token Budget", f"{token_budget:,}")
                
                with col3:
                    st.metric("Model", model_name)
                
                # Candidate info
                st.markdown("---")
                st.markdown("**Candidate Information:**")
                st.write(f"- **Name:** {session_data['candidate_name']}")
                if session_data['candidate_email']:
                    st.write(f"- **Email:** {session_data['candidate_email']}")
                
                # Challenge
                if session_data['challenge_text']:
                    st.markdown("---")
                    st.markdown("**Challenge:**")
                    st.info(session_data['challenge_text'])
                
                # Next steps
                st.markdown("---")
                st.markdown("### 🎯 Next Steps")
                st.markdown("""
                **Option 1: Direct Link (Recommended)** ⭐
                1. Share the **Direct Candidate Link** above
                2. Candidate clicks the link and automatically joins
                3. Monitor progress from **Interviewer Dashboard**
                
                **Option 2: Manual Entry**
                1. Share the **Session ID** with the candidate
                2. Candidate navigates to **Candidate Interface** page
                3. Candidate enters the Session ID to join
                """)
                
                # Action buttons
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("➕ Create Another Session", use_container_width=True):
                        st.rerun()
                
                with col2:
                    if st.button("👔 Go to Dashboard", use_container_width=True):
                        st.info("Navigate to 'Interviewer Dashboard' from the sidebar")
                
                logger.info(f"Session {session_data['id']} created via UI")
                
            except Exception as e:
                st.error(f"❌ Error creating session: {str(e)}")
                logger.error(f"Error creating session: {e}", exc_info=True)
    
    # Help section
    with st.expander("ℹ️ Help & Tips"):
        st.markdown("""
        ### Creating a Session
        
        **Required Fields:**
        - **Candidate Name**: Full name of the person taking the interview
        - **Time Limit**: How long the candidate has to complete the challenge
        - **Token Budget**: Maximum AI tokens the candidate can use
        
        **Optional Fields:**
        - **Candidate Email**: For record-keeping and notifications
        - **Challenge**: The problem or question for the candidate to solve
        
        ### Recommended Settings
        
        **For Coding Interviews:**
        - Time Limit: 60-90 minutes
        - Token Budget: 30,000-50,000 tokens
        - Model: GPT-4 (best quality)
        
        **For Quick Assessments:**
        - Time Limit: 30 minutes
        - Token Budget: 15,000-20,000 tokens
        - Model: GPT-3.5-Turbo (faster, cheaper)
        
        ### Token Budget Guide
        
        - **10,000 tokens** ≈ 20-30 messages
        - **30,000 tokens** ≈ 60-90 messages
        - **50,000 tokens** ≈ 100-150 messages
        
        The actual number depends on message length and complexity.
        """)


if __name__ == "__main__":
    render()

