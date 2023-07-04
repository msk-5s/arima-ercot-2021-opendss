# SPDX-License-Identifier: BSD-3-Clause

"""
This module contains a classes for an OpenDSS transformer.
"""

import win32com

import dss_name
import dss_object

#===================================================================================================
#===================================================================================================
class Transformer(dss_object.ObjectMixin):
    """
    This class represents an OpenDSS Transformer class.

    Attributes
    ----------
    name : str
        The name of the OpenDSS object element.

    See Also
    --------
    dss_object.ObjectMixin
    """

    #-----------------------------------------------------------------------------------------------
    #-----------------------------------------------------------------------------------------------
    def __init__(self, dss: win32com.client.CDispatch, name: str):
        """
        The designated initializer.

        Parameters
        ----------
        dss : win32com.client.CDispatch
            The OpenDSSEngine COM object.
        name : str
            The name of the transformer object element.
        """
        load_name = dss_name.Name(class_="transformer", element=name)

        dss_object.ObjectMixin.__init__(self, dss=dss, name=load_name)
