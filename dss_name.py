# SPDX-License-Identifier: BSD-3-Clause

"""
This module contains a class for representing an OpenDSS object name.
"""

#===================================================================================================
#===================================================================================================
class Name:
    """
    The name of an OpenDSS object.

    The terms 'object, 'class' and 'element' are used to be consistent with the terminology in the
    OpenDSS manual.

    Attributes
    ----------
    class_ : str
        The name of the object's class (e.g. Load, Line, Transformer, etc.).
    element : str
        The name of the object's class instance (e.g. MDV201_1144260FUSE-1B0, etc.).
    """

    #-----------------------------------------------------------------------------------------------
    #-----------------------------------------------------------------------------------------------
    def __init__(self, class_: str, element: str):
        """
        The designated initializer.

        Parameters
        ----------
        class_ : str
            The name of the object's class (e.g. Load, Line, Transformer, etc.).
        element : str
            The name of the object's class instance (e.g. MDV201_1144260FUSE-1B0, etc.).
        """
        self.class_ = class_
        self.element = element

    #-----------------------------------------------------------------------------------------------
    #-----------------------------------------------------------------------------------------------
    def __str__(self) -> str:
        """
        Make the class `print`able.
        """
        return self.object

    #-----------------------------------------------------------------------------------------------
    #-----------------------------------------------------------------------------------------------
    @property
    def object(self) -> str:
        """
        Get the object's full name.

        Returns
        -------
        str
            The full name of the object.
        """
        return f"{self.class_}.{self.element}"
