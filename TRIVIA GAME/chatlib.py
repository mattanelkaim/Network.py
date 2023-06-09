"""
IMPORTANT: server.pyc file works only with 3.8.2 version!
"""

NUM_OF_FIELDS = 3  # ADDED TO FURTHER CHECK VALIDITY OF MESSAGES
CMD_FIELD_LENGTH = 16  # Exact length of cmd field (in bytes)
LENGTH_FIELD_LENGTH = 4  # Exact length of length field (in bytes)
MAX_DATA_LENGTH = 10 ** LENGTH_FIELD_LENGTH - 1  # Max data field size
MSG_HEADER_LENGTH = CMD_FIELD_LENGTH + LENGTH_FIELD_LENGTH + 2
MAX_MSG_LENGTH = MSG_HEADER_LENGTH + MAX_DATA_LENGTH
DELIMITER = "|"
DATA_DELIMITER = "#"

# Protocol Messages
PROTOCOL_CLIENT = {
    "login_msg": "LOGIN",
    "logout_msg": "LOGOUT",
    "get_logged_msg": "LOGGED",
    "get_score_msg": "MY_SCORE",
    "get_highscore_msg": "HIGHSCORE",
    "get_question_msg": "GET_QUESTION",
    "send_answer_msg": "SEND_ANSWER"
}

PROTOCOL_SERVER = {
    "error_msg": "ERROR",
    "login_ok_msg": "LOGIN_OK",
    "all_logged_msg": "LOGGED_ANSWER",
    "my_score_ok_msg": "YOUR_SCORE",
    "highscore_ok_msg": "ALL_SCORE",
    "question_ok_msg": "YOUR_QUESTION",
    "no_questions_msg": "NO_QUESTIONS",
    "correct_answer_msg": "CORRECT_ANSWER",
    "wrong_answer_msg": "WRONG_ANSWER"
}

# Union of all protocol's commands
ALL_COMMANDS = set(PROTOCOL_CLIENT.values()) | set(PROTOCOL_SERVER.values())
ERROR_RETURN = None


def build_message(cmd: str, data: str) -> str | None:
    """
    Gets command name and data field, then creates a valid protocol message.
    Valid message: <cmd>:(whitespace:16)|<data_len>(whitespace/zeros:4)|<data>
    :param cmd: The command of the message
    :param data: The data of the message
    :return: Valid protocol message, or None if error occurred
    """
    data_len = len(data)  # Compute only once
    # Check length validity of cmd and data fields
    if len(cmd) > CMD_FIELD_LENGTH or data_len > MAX_DATA_LENGTH:
        return ERROR_RETURN

    # Add leading zeros until limit
    formatted_len = str(data_len).zfill(LENGTH_FIELD_LENGTH)
    # Add whitespace to the right cmd, until limit
    formatted_cmd = cmd.ljust(CMD_FIELD_LENGTH)

    return f"{formatted_cmd}{DELIMITER}{formatted_len}{DELIMITER}{data}"


def parse_message(msg: str) -> tuple[str, str] | tuple[None, None]:
    """
    Parses protocol message and returns command name and data field.
    Valid message: <cmd>:(whitespace:16)|<data_len>(whitespace/zeros:4)|<data>
    :param msg: The message to parse to cmd and data
    :return: cmd, data fields. If some error occurred, returns None, None
    """
    # First check type edge-case
    if not isinstance(msg, str):
        return ERROR_RETURN, ERROR_RETURN

    msg_parts = msg.split(DELIMITER)
    # Then check # of fields edge-case
    if len(msg_parts) != NUM_OF_FIELDS:
        return ERROR_RETURN, ERROR_RETURN

    cmd, length, data = msg_parts
    cmd_stripped, length_stripped = cmd.strip(), length.strip()
    data_len = len(data)  # Compute only once

    # First validate logic, then check lengths
    if cmd_stripped not in ALL_COMMANDS\
            or not length_stripped.isdigit()\
            or data_len != int(length_stripped) \
            \
            or len(cmd) != CMD_FIELD_LENGTH\
            or len(length) != LENGTH_FIELD_LENGTH\
            or data_len > MAX_DATA_LENGTH:
        return ERROR_RETURN, ERROR_RETURN

    return cmd_stripped, data  # Valid message


def split_data(msg: str, expected_fields: int) -> list[str] | list[None]:
    """
    Helper method. Gets a string and number of expected fields in it.
    Splits the string using protocol's data field delimiter (|#)
    and validates that there are correct number of fields.
    :param msg: The message to split
    :param expected_fields: The number of expected fields
    :return: list of fields if all ok. If some error occurred, returns [None]
    """
    fields = msg.split(DATA_DELIMITER)
    return fields if (len(fields) == expected_fields) else [ERROR_RETURN]


def join_data(msg_fields: list[str]) -> str:
    """
    Helper method. Gets a list, joins all of its fields to one string
    divided by the data delimiter.
    :param msg_fields: The data fields to join
    :return: A joined string that looks like cell1#cell2#cell3
    """
    return DATA_DELIMITER.join(msg_fields)
