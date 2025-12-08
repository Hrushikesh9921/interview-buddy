"""
Resource panel component for displaying timer and token information.
"""
import streamlit as st
from typing import Dict, Optional


def render_resource_panel(
    timer_info: Dict,
    token_info: Dict,
    show_warnings: bool = True
) -> None:
    """
    Render the resource panel with timer and token information.
    
    Args:
        timer_info: Dictionary with timer information
            - elapsed_seconds: int
            - remaining_seconds: int
            - time_limit: int
            - state: str
            - is_expired: bool
            - percentage_used: float
        token_info: Dictionary with token information
            - tokens_used: int
            - token_budget: int
            - percentage_used: float
            - remaining: int
        show_warnings: Whether to show warning messages
    """
    st.markdown("### 📊 Resources")
    
    # Create two columns for timer and tokens
    col1, col2 = st.columns(2)
    
    with col1:
        render_timer_display(timer_info, show_warnings)
    
    with col2:
        render_token_display(token_info, show_warnings)
    
    # Show warnings if needed
    if show_warnings:
        render_warnings(timer_info, token_info)


def render_timer_display(timer_info: Dict, show_warnings: bool = True) -> None:
    """Render timer display."""
    st.markdown("#### ⏱️ Time")
    
    # Format time
    remaining = timer_info.get("remaining_seconds", 0)
    time_limit = timer_info.get("time_limit", 0)
    percentage_used = timer_info.get("percentage_used", 0)
    is_expired = timer_info.get("is_expired", False)
    
    # Determine color based on percentage
    if is_expired:
        color = "red"
        status = "EXPIRED"
    elif percentage_used >= 90:
        color = "red"
        status = "CRITICAL"
    elif percentage_used >= 75:
        color = "orange"
        status = "LOW"
    elif percentage_used >= 50:
        color = "blue"
        status = "RUNNING"
    else:
        color = "green"
        status = "GOOD"
    
    # Format remaining time
    hours = remaining // 3600
    minutes = (remaining % 3600) // 60
    seconds = remaining % 60
    
    if hours > 0:
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        time_str = f"{minutes:02d}:{seconds:02d}"
    
    # Display metric
    st.metric(
        label="Remaining",
        value=time_str,
        delta=f"{100 - percentage_used:.0f}% left",
        delta_color="normal" if not is_expired else "off"
    )
    
    # Progress bar
    progress_value = min(1.0, percentage_used / 100)
    st.progress(progress_value)
    
    # Status badge
    st.markdown(f"<span style='color: {color}; font-weight: bold;'>● {status}</span>", unsafe_allow_html=True)


def render_token_display(token_info: Dict, show_warnings: bool = True) -> None:
    """Render token display."""
    st.markdown("#### 🎫 Tokens")
    
    tokens_used = token_info.get("tokens_used", 0)
    token_budget = token_info.get("token_budget", 0)
    remaining = token_info.get("remaining", 0)
    percentage_used = token_info.get("percentage_used", 0)
    is_exhausted = remaining <= 0
    
    # Determine color based on percentage
    if is_exhausted:
        color = "red"
        status = "EXHAUSTED"
    elif percentage_used >= 90:
        color = "red"
        status = "CRITICAL"
    elif percentage_used >= 75:
        color = "orange"
        status = "LOW"
    elif percentage_used >= 50:
        color = "blue"
        status = "MODERATE"
    else:
        color = "green"
        status = "GOOD"
    
    # Display metric
    st.metric(
        label="Remaining",
        value=f"{remaining:,}",
        delta=f"{100 - percentage_used:.0f}% left",
        delta_color="normal" if not is_exhausted else "off"
    )
    
    # Progress bar
    progress_value = min(1.0, percentage_used / 100)
    st.progress(progress_value)
    
    # Status badge
    st.markdown(f"<span style='color: {color}; font-weight: bold;'>● {status}</span>", unsafe_allow_html=True)
    
    # Usage details
    st.caption(f"Used: {tokens_used:,} / {token_budget:,}")


def render_warnings(timer_info: Dict, token_info: Dict) -> None:
    """Render warning messages if thresholds are reached."""
    timer_percentage = timer_info.get("percentage_used", 0)
    token_percentage = token_info.get("percentage_used", 0)
    is_expired = timer_info.get("is_expired", False)
    is_exhausted = token_info.get("remaining", 0) <= 0
    
    # Critical warnings
    if is_expired:
        st.error("⏰ **Time's up!** Your session has expired.")
        return
    
    if is_exhausted:
        st.error("🎫 **Out of tokens!** Your token budget is exhausted.")
        return
    
    # High priority warnings
    if timer_percentage >= 90 or token_percentage >= 90:
        warning_msg = ""
        if timer_percentage >= 90:
            warning_msg += "⏰ **Less than 10% time remaining!** "
        if token_percentage >= 90:
            warning_msg += "🎫 **Less than 10% tokens remaining!** "
        
        st.warning(warning_msg.strip())
        return
    
    # Medium priority warnings
    if timer_percentage >= 75 or token_percentage >= 75:
        info_msg = ""
        if timer_percentage >= 75:
            remaining = timer_info.get("remaining_seconds", 0)
            minutes = remaining // 60
            info_msg += f"⏱️ About {minutes} minutes left. "
        if token_percentage >= 75:
            remaining_tokens = token_info.get("remaining", 0)
            info_msg += f"🎫 About {remaining_tokens:,} tokens left. "
        
        st.info(info_msg.strip())

