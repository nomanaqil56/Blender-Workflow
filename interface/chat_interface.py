"""User chat loop formatter and prompt handler."""

from storage.conversation_store import conversation_store
from core.logger import logger

class ChatInterface:
    def format_agent_response(self, text: str) -> str:
        conversation_store.add_message("assistant", text)
        return f"\n[AI Studio Agent]: {text}\n"

    def format_user_prompt(self, text: str) -> str:
        conversation_store.add_message("user", text)
        return f"\n[User]: {text}"

chat_interface = ChatInterface()
