# SPDX-License-Identifier: BSD-3-Clause

"""
This module contains classes and functions for running a command in OpenDSS.
"""

import win32com

from typing import Callable

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def run(dss:win32com.client.CDispatch, cmd: str) -> str:
    """
    Run an OpenDSS command via the COM interface and return the results of the command as a string.
    This function exists as a helper function to simplify running an OpenDSS command and retrieving
    the result.

    Parameters
    ----------
    dss : win32com.client.CDispatch
        The OpenDSSEngine COM object.
    cmd : str
        The OpenDSS command to run.

    Returns
    -------
    str
        The result of the OpenDSS command.
    """
    dss.Text.Command = cmd
    result = str(dss.Text.Result)

    return result
