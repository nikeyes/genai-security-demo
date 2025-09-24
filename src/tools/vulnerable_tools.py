import os


def read_log(filename: str) -> str:
    """
    Reads and returns the content of a specified log file.
    IMPORTANT! Should only be used to read files with '.log' extension.
    For example: 'system.log' or 'application.log'.
    """
    print(f"🤖 DEBUG: The tool has been called with argument: '{filename}'")

    # --- THE VULNERABLE LINE ---
    # The function builds a shell command by concatenating text without validating input.
    # This is a Command Injection vulnerability.
    command = f'cat {filename}'

    print(f"🐚 DEBUG: Executing the following shell command: '{command}'")

    # We use os.popen to capture the command output and return it to the LLM
    # os.system() would also work but doesn't capture output as easily.
    with os.popen(command) as p:
        result = p.read()
    return result
