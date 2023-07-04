# SPDX-License-Identifier: BSD-3-Clause

"""
This module contains classes for OpenDSS objects that can have a connection.
"""

import enum

#===================================================================================================
#===================================================================================================
class Connection(enum.Enum):
    """
    Enums for the types of connections.
    """
    WYE = 0
    DELTA = 1

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def string_to_connection(a_string: str) -> Connection:
    """
    Converts a string of the connection type to the appropriate `Connection` enum.

    Parameters
    ----------
    a_string : str
        The `conn` property string to convert.

    Returns
    -------
    dss_connection.Connection
        The appropriate connection enum.
    """
    # These valid types are drawn from the OpenDSS manual. Everything is converted to lowercase.
    valid_wyes = ["wye", "y", "ln"]
    valid_deltas = ["delta", "d", "ll"]

    connection = None

    if a_string.lower() in valid_wyes:
        connection = Connection.WYE
    elif a_string.lower() in valid_deltas:
        connection = Connection.DELTA

    if connection is None:
        raise KeyError(f"'{a_string}' is an invalid connection type.")

    return connection
