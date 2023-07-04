# SPDX-License-Identifier: BSD-3-Clause

"""
This module contains a class for representing an OpenDSS object.
"""

from typing import Any, Dict

import win32com.client

import dss_command
import dss_name

#===================================================================================================
#===================================================================================================
class ObjectMixin:
    """
    This mixin adds functionality/attributes for an OpenDSS object.

    Attributes
    ----------
    name : dss_name.Name
        The name of the OpenDSS object.
    """
    
    #-----------------------------------------------------------------------------------------------
    #-----------------------------------------------------------------------------------------------
    def __init__(self, dss: win32com.client.CDispatch, name: dss_name.Name):
        """
        The designated initializer.

        Parameters
        ----------
        dss : win32com.client.CDispatch
            The OpenDSSEngine COM object.
        name : dss_name.Name
            The name of the OpenDSS object.
        """
        self._dss = dss
        self.name = name

    #-----------------------------------------------------------------------------------------------
    #-----------------------------------------------------------------------------------------------
    def get_property(self, key: str) -> str:
        """
        Get a property of the OpenDSS object, as shown in the OpenDSS manual.

        Parameters
        ----------
        key : str
            The name of the OpenDSS property to get. See the OpenDSS manual for the available
            properties for the given object.

        Returns
        -------
        str
            The desired property of the OpenDSS object as a string.
        """
        result = dss_command.run(dss=self._dss, cmd=f"? {self.name.object}.{key}")

        # NOTE: If the object doesn't exist, then an OpenDSS error dialog will appear. We cannot
        # capture this event here.
        if "property unknown" in result.lower():
            raise KeyError(
                f"Key `{key}` is invalid. See the OpenDSS manual for valid property keys."
            )

        return result
