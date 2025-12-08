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
    Render the resource panel with timer and token information in a compact single row.
    
    Args:
        timer_info: Dictionary with timer information
            - elapsed_seconds: int
            - remaining_seconds: int
            - formatted_remaining: str
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
    # Get status colors
    timer_color, timer_status = get_status_color_and_label(
        timer_info.get("percentage_used", 0),
        timer_info.get("is_expired", False)
    )
    
    token_percentage = token_info.get("percentage_used", 0)
    token_remaining = token_info.get("remaining", 0)
    token_color, token_status = get_status_color_and_label(
        token_percentage,
        token_remaining <= 0
    )
    
    # Format time string
    time_str = timer_info.get("formatted_remaining", "00:00:00")
    
    # Create compact single-row layout with custom CSS
    st.markdown(f"""
        <div style='
            background-color: #f0f2f6;
            padding: 10px 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            border: 1px solid #e0e0e0;
        '>
            <div style='display: flex; justify-content: space-between; align-items: center; font-size: 14px;'>
                <div style='display: flex; align-items: center; gap: 20px;'>
                    <div style='font-weight: bold; color: #555;'>📊 Resources:</div>
                    <div style='display: flex; align-items: center; gap: 8px;'>
                        <span style='font-weight: 500;'>⏱️</span>
                        <span style='font-size: 16px; font-weight: bold; font-family: monospace;'>{time_str}</span>
                        <span style='color: {timer_color}; font-weight: bold;'>● {timer_status}</span>
                    </div>
                    <div style='border-left: 2px solid #ccc; height: 20px;'></div>
                    <div style='display: flex; align-items: center; gap: 8px;'>
                        <span style='font-weight: 500;'>🎫</span>
                        <span style='font-size: 16px; font-weight: bold;'>{token_remaining:,}</span>
                        <span style='color: #666; font-size: 12px;'>/ {token_info.get("token_budget", 0):,}</span>
                        <span style='color: {token_color}; font-weight: bold;'>● {token_status}</span>
                    </div>
                </div>
                <div style='display: flex; gap: 15px; font-size: 12px; color: #666;'>
                    <div>Time: {timer_info.get("percentage_used", 0):.0f}%</div>
                    <div>Tokens: {token_percentage:.0f}%</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Show critical warnings only
    if show_warnings:
        render_compact_warnings(timer_info, token_info)


def get_status_color_and_label(percentage_used: float, is_exhausted: bool) -> tuple:
    """Get color and status label based on usage percentage."""
    if is_exhausted:
        return "#dc3545", "EXPIRED"
    elif percentage_used >= 90:
        return "#dc3545", "CRITICAL"
    elif percentage_used >= 75:
        return "#fd7e14", "LOW"
    elif percentage_used >= 50:
        return "#0d6efd", "ACTIVE"
    else:
        return "#28a745", "GOOD"


def render_compact_warnings(timer_info: Dict, token_info: Dict) -> None:
    """Render compact warning messages only for critical situations."""
    timer_percentage = timer_info.get("percentage_used", 0)
    token_percentage = token_info.get("percentage_used", 0)
    is_expired = timer_info.get("is_expired", False)
    is_exhausted = token_info.get("remaining", 0) <= 0
    
    # Only show critical warnings
    if is_expired:
        st.error("⏰ **Time's up!** Your session has expired.")
    elif is_exhausted:
        st.error("🎫 **Out of tokens!** Your token budget is exhausted.")
    elif timer_percentage >= 90 or token_percentage >= 90:
        warning_parts = []
        if timer_percentage >= 90:
            warning_parts.append("⏰ Less than 10% time remaining")
        if token_percentage >= 90:
            warning_parts.append("🎫 Less than 10% tokens remaining")
        st.warning(" | ".join(warning_parts))

