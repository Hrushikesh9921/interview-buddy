"""
Message renderer component for displaying chat messages with markdown.
"""
import streamlit as st
from typing import List, Dict
from services.chat_service import ChatMessage
from config.constants import MessageRole


def render_messages(messages: List[ChatMessage]) -> None:
    """
    Render a list of chat messages.
    
    Args:
        messages: List of ChatMessage objects
    """
    if not messages:
        st.info("💬 No messages yet. Start the conversation below!")
        return
    
    for message in messages:
        render_message(message)


def render_message(message: ChatMessage) -> None:
    """
    Render a single chat message.
    
    Args:
        message: ChatMessage object
    """
    # Determine message styling based on role
    if message.role == MessageRole.USER:
        render_user_message(message)
    elif message.role == MessageRole.ASSISTANT:
        render_assistant_message(message)
    elif message.role == MessageRole.SYSTEM:
        render_system_message(message)


def render_user_message(message: ChatMessage) -> None:
    """Render user message."""
    with st.chat_message("user", avatar="👤"):
        st.markdown(message.content)
        
        # Token badge and timestamp
        col1, col2 = st.columns([4, 1])
        with col2:
            if message.tokens > 0:
                st.caption(f"🎫 {message.tokens} tokens")


def render_assistant_message(message: ChatMessage) -> None:
    """Render assistant message with markdown support."""
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown(message.content)
        
        # Token badge and timestamp
        col1, col2 = st.columns([4, 1])
        with col2:
            if message.tokens > 0:
                st.caption(f"🎫 {message.tokens} tokens")


def render_system_message(message: ChatMessage) -> None:
    """Render system message."""
    st.info(f"ℹ️ {message.content}")


def render_message_input(
    placeholder: str = "Type your message here...",
    key: str = "message_input",
    disabled: bool = False,
    help_text: str = None
) -> str:
    """
    Render message input field.
    
    Args:
        placeholder: Placeholder text
        key: Unique key for the input
        disabled: Whether input is disabled
        help_text: Help text to display
    
    Returns:
        The input text
    """
    return st.chat_input(
        placeholder=placeholder,
        key=key,
        disabled=disabled
    )

