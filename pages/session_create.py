"""
Session creation page.
"""
import streamlit as st
from services import SessionConfig, get_session_service
from config.settings import settings
from utils.logger import logger
from models import get_db_context


def render():
    """Render the session creation page."""
    st.title("➕ Create Interview Session")
    st.markdown("Set up a new interview session for a candidate.")
    st.markdown("---")
    
    # Candidate Information
    st.subheader("📋 Candidate Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        candidate_name = st.text_input(
            "Candidate Name *",
            placeholder="John Doe",
            help="Full name of the candidate",
            key="candidate_name_input"
        )
    
    with col2:
        candidate_email = st.text_input(
            "Candidate Email",
            placeholder="john@example.com",
            help="Email address (optional)",
            key="candidate_email_input"
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
            help="Maximum duration for the interview",
            key="time_limit_input"
        )
    
    with col2:
        token_budget = st.number_input(
            "Token Budget *",
            min_value=1000,
            max_value=200000,
            value=settings.default_token_budget,
            step=1000,
            help="Maximum tokens the candidate can use",
            key="token_budget_input"
        )
    
    # Model selection
    model_options = ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"]
    model_name = st.selectbox(
        "AI Model *",
        options=model_options,
        index=0,
        help="OpenAI model to use for the interview",
        key="model_select"
    )
    
    # Challenge mode selection (OUTSIDE form to allow dynamic rendering)
    st.markdown("---")
    st.subheader("📝 Challenge Selection")
    challenge_mode = st.radio(
        "Challenge Source",
        options=["📚 Template Library", "✏️ Custom Challenge"],
        horizontal=True,
        key="challenge_mode_select",
        help="Select from pre-built templates or create your own challenge"
    )
    
    # Template selection (OUTSIDE form for dynamic preview)
    selected_challenge_id = None
    challenge_text = None
    
    if challenge_mode == "📚 Template Library":
        from services import get_challenge_service
        from config.constants import ChallengeCategory, ChallengeDifficulty
        
        challenge_service = get_challenge_service()
        with get_db_context() as db:
            all_templates_objs = challenge_service.get_all_templates(db)
            
            # Convert to dicts to avoid detached instance errors
            all_templates = []
            for t in all_templates_objs:
                template_dict = {
                    "id": t.id,
                    "title": t.title,
                    "description": t.description,
                    "category": t.category,
                    "difficulty": t.difficulty,
                    "instructions": t.instructions,
                    "starter_code": t.starter_code,
                    "test_cases": t.test_cases,
                    "hints": t.hints,
                    "estimated_duration": t.estimated_duration,
                    "tags": t.tags
                }
                all_templates.append(template_dict)
        
        if not all_templates:
            st.warning("⚠️ No challenge templates found. Run `python scripts/setup_challenges.py` to load templates.")
            st.info("For now, use Custom Challenge mode.")
        else:
            # Category and difficulty filters
            col_cat, col_diff = st.columns(2)
            
            with col_cat:
                categories = ["ALL"] + [c.value.replace('_', ' ').title() for c in ChallengeCategory]
                selected_category = st.selectbox(
                    "Category",
                    categories,
                    help="Filter by challenge category",
                    key="template_category"
                )
            
            with col_diff:
                difficulties = ["ALL"] + [d.value.capitalize() for d in ChallengeDifficulty]
                selected_difficulty = st.selectbox(
                    "Difficulty",
                    difficulties,
                    help="Filter by difficulty level",
                    key="template_difficulty"
                )
            
            # Filter templates
            filtered_templates = all_templates
            
            if selected_category != "ALL":
                cat_value = selected_category.replace(' ', '_').upper()
                filtered_templates = [t for t in filtered_templates if t["category"].value.upper() == cat_value]
            
            if selected_difficulty != "ALL":
                diff_value = selected_difficulty.upper()
                filtered_templates = [t for t in filtered_templates if t["difficulty"].value.upper() == diff_value]
            
            if filtered_templates:
                template_options = {
                    f"{c['title']} ({c['category'].value.replace('_', ' ').title()} - {c['difficulty'].value.capitalize()})": c['id'] 
                    for c in filtered_templates
                }
                
                selected_template_name = st.selectbox(
                    "Select Challenge Template *",
                    options=list(template_options.keys()),
                    help="Choose a challenge from the library",
                    key="template_selector"
                )
                
                selected_challenge_id = template_options[selected_template_name]
                selected_challenge = next(c for c in filtered_templates if c["id"] == selected_challenge_id)
                
                # Show preview
                with st.expander("📖 Challenge Preview", expanded=True):
                    st.markdown(f"**{selected_challenge['title']}**")
                    st.markdown(selected_challenge['description'])
                    
                    # Show metadata
                    col_meta1, col_meta2 = st.columns(2)
                    with col_meta1:
                        st.caption(f"**Category:** {selected_challenge['category'].value.replace('_', ' ').title()}")
                        st.caption(f"**Difficulty:** {selected_challenge['difficulty'].value.capitalize()}")
                    with col_meta2:
                        if selected_challenge['estimated_duration']:
                            duration_min = selected_challenge['estimated_duration'] // 60
                            st.caption(f"**Estimated Time:** {duration_min} minutes")
                        if selected_challenge['tags']:
                            st.caption(f"**Tags:** {', '.join(selected_challenge['tags'][:3])}")
                    
                    # Show instructions preview
                    if selected_challenge['instructions']:
                        st.markdown("**Instructions Preview:**")
                        preview_text = selected_challenge['instructions'][:300]
                        if len(selected_challenge['instructions']) > 300:
                            preview_text += "..."
                        st.text(preview_text)
            else:
                st.warning(f"No templates match your filters ({selected_category}, {selected_difficulty})")
                st.info("Try selecting 'ALL' or use Custom Challenge mode.")
    elif challenge_mode == "✏️ Custom Challenge":
        # Custom challenge text area
        challenge_text = st.text_area(
            "Challenge Description *",
            placeholder="Enter the coding challenge or interview question here...\n\nExample:\nWrite a function that finds the two numbers in an array that add up to a target sum.",
            height=200,
            help="The challenge or problem the candidate should solve",
            key="custom_challenge_input"
        )
    
    st.markdown("---")
    
    # Submit button
    submitted = st.button("🚀 Create Session", type="primary", use_container_width=True, key="create_session_btn")
    
    # Handle session creation
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
        
        # Validate challenge selection
        if not selected_challenge_id and (not challenge_text or len(challenge_text.strip()) == 0):
            errors.append("Please select a challenge template or provide a custom challenge description")
        
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
                    challenge_id=selected_challenge_id,  # Use challenge_id if template selected
                    challenge_text=challenge_text.strip() if challenge_text else None  # Legacy field for custom
                )
                
                with st.spinner("Creating session..."):
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

