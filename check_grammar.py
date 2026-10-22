import language_tool_python

# LanguageTool එක load කරගැනීම (Remote API එක Pi 3 RAM එක ඉතිරි කරගන්න හොඳයි)
tool = language_tool_python.LanguageTool('en-US', remote_server='https://api.languagetool.org')

def get_grammar_errors(text: str):
    """
    පෙළෙහි ඇති සියලුම Grammar වැරදි සොයා list එකක් ලෙස ලබා දෙයි.
    """
    matches = tool.check(text)
    return matches