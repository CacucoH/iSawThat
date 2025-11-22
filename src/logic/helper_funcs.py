"""
    Misc helper funcs that my be useful
"""
import re

def message_sanitize(msg: str) -> str:
    """Replace all special md characters and links"""
    msg = msg.replace('*', '') \
              .replace('_', '') \
              .replace('~', '') \
              .replace('`', '')

    # Remove MD-like links and create plain text
    msg = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', msg)
    return msg


def correct_word_spell(timedelta_days: str) -> str:
    """Corrects suffixes for russian words, depending on numbers"""
    base = "дн"
    if timedelta_days[-1] == '1':
        base += 'я'
    else:
        base += 'ей' 
    
    return base