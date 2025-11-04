import os
import sys

# Allow imports from project root when running this file directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Classes.chat_classes import OpenAIChat


def get_chat(system_message=None, 
             model_name: str = "gpt-4o-mini-2024-07-18", 
             temperature: float = 0.2):
    """Return a single preconfigured OpenAIChat instance.

    Override model_name/temperature as needed.
    """
    return OpenAIChat(
        model_name=model_name,
        temperature=temperature,
        system_message=system_message,
    )

__all__ = ["get_chat"]





"""
links to the other chat models of OpenAI

def get_chats(system_message):
    chats = {}

    chats['openAI_mini'] = OpenAIChat(
        model_name = "gpt-4.1-mini-2025-04-14",
        temperature=0.2,
        system_message = system_message
    )


    chats['openAI_full'] = OpenAIChat(
        model_name = "gpt-4.1-2025-04-14",
        temperature=0.2,
        system_message = system_message
    )

    chats['openAI_gpt5_full'] = OpenAIChat(
        model_name = "gpt-5-2025-08-07",
        temperature=1,
        system_message = system_message
    )


"""