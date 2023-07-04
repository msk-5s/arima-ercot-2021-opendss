# SPDX-License-Identifier: BSD-3-Clause

"""
This module contains the abstract base class for a prototype.
"""

import abc

from typing import Mapping

#===================================================================================================
#===================================================================================================
class Prototype(abc.ABC):
    """
    The abstract base class for a prototype.
    """

    #-----------------------------------------------------------------------------------------------
    #-----------------------------------------------------------------------------------------------
    @abc.abstractmethod
    def clone(self, **kwargs: Mapping[str, any]) -> any:
        """
        Make a clone of the prototype.

        Parameters
        ----------
        **kwargs : dict of {str, any}
            See concrete implementations.

        Returns
        -------
        any
            A clone of the prototype.
        """
