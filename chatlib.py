# In some GIVEN functions, msg and data are opposite to each other for some reason
from typing import Union  # To type hint
# import time  # To measure performance

NUM_OF_FIELDS = 3  # ADDED TO FURTHER CHECK VALIDITY OF MESSAGES
CMD_FIELD_LENGTH = 16  # Exact length of cmd field (in bytes)
LENGTH_FIELD_LENGTH = 4  # Exact length of length field (in bytes)
MAX_DATA_LENGTH = 10 ** LENGTH_FIELD_LENGTH - 1  # Max possible size of data field
MSG_HEADER_LENGTH = CMD_FIELD_LENGTH + 1 + LENGTH_FIELD_LENGTH + 1
MAX_MSG_LENGTH = MSG_HEADER_LENGTH + MAX_DATA_LENGTH
DELIMITER = "|"
DATA_DELIMITER = "#"

# Protocol Messages
PROTOCOL_CLIENT = {
    "login_msg": "LOGIN",
    "logout_msg": "LOGOUT"
}  # Add more commands if needed

PROTOCOL_SERVER = {
    "login_ok_msg": "LOGIN_OK",
    "login_failed_msg": "ERROR"
}  # Add more commands if needed

# ADDED TO FURTHER CHECK VALIDITY OF MESSAGES: union of all commands
ALL_COMMANDS = set(PROTOCOL_CLIENT.values()) | set(PROTOCOL_SERVER.values())
ERROR_RETURN = None


def build_message(cmd: str, data: str) -> Union[str, None]:
    """
    Gets command name (str) and data field (str) and creates a valid protocol message.
    Valid message: <cmd>:(whitespace:16)|<data_len>(whitespace/zeros:4)|<data>
    :param cmd: The command of the message
    :type cmd: str
    :param data: The data of the message
    :type data: str
    :return: Valid protocol message, or None if error occurred
    :rtype: Union[str, None]
    """
    data_len = len(data)  # Compute only once
    # Check length validity of cmd and data fields
    if len(cmd) > CMD_FIELD_LENGTH or data_len > MAX_DATA_LENGTH:
        return ERROR_RETURN

    formatted_len = str(data_len).zfill(LENGTH_FIELD_LENGTH)  # Add leading zeros until limit
    formatted_cmd = cmd.ljust(CMD_FIELD_LENGTH)  # Add whitespace to the right cmd, until limit

    return f"{formatted_cmd}{DELIMITER}{formatted_len}{DELIMITER}{data}"


def parse_message(msg: str) -> Union[tuple[str, str], tuple[None, None]]:
    """
    Parses protocol message and returns command name and data field.
    Valid message: <cmd>:(whitespace:16)|<data_len>(whitespace/zeros:4)|<data>
    :param msg: The message to parse to cmd and data
    :type msg: str
    :return: cmd, data fields. If some error occurred, returns None, None
    :rtype: Union[tuple[str, str], tuple[None, None]]
    """
    # First check type edge-case
    if not isinstance(msg, str):
        return ERROR_RETURN, ERROR_RETURN

    msg_parts = msg.split(DELIMITER)
    # Then check # of fields edge-case
    if len(msg_parts) != NUM_OF_FIELDS:
        return ERROR_RETURN, ERROR_RETURN

    cmd, length, data = msg_parts
    cmd_stripped = cmd.strip()
    length_stripped = length.strip()
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


def split_data(msg: str, expected_fields: int) -> Union[list[str], list[None]]:
    """
    Helper method. gets a string and number of expected fields in it. Splits the string
    using protocol's data field delimiter (|#) and validates that there are correct number of fields.
    :param msg: The message to split
    :type msg: str
    :param expected_fields: The number of expected separators (not fields)
    :type expected_fields: int
    :return: list of fields if all ok. If some error occurred, returns [None]
    :rtype: Union[list[str], list[None]]
    """
    fields = msg.split(DATA_DELIMITER)
    return fields if len(fields) == expected_fields + 1 else [ERROR_RETURN]


def join_data(msg_fields: list[str]) -> str:
    """
    Helper method. Gets a list, joins all of its fields to one string divided by the data delimiter.
    :param msg_fields: The data fields to join
    :type msg_fields: list
    :return: A joined string that looks like cell1#cell2#cell3
    :rtype: str
    """
    return DATA_DELIMITER.join(msg_fields)


def main():
    # t1 = time.perf_counter()
    # for _ in range(1_000_000):
    #     build_message("LOGIN", "aaaa#bbbb")
    # t2 = time.perf_counter()
    # print(f"1 took {t2 - t1} seconds.")

    print(parse_message("ERROR           |0015|Error Occurred!"))


if __name__ == '__main__':
    main()
