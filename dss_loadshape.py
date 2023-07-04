# SPDX-License-Identifier: BSD-3-Clause

"""
This module contains classes for custom OpenDSS load shapes.

An OpenDSS load shape is the equivalent of a load profile in other contexts.
"""

import enum

from typing import Callable, Optional
from nptyping import Float, NDArray, Shape

import win32com.client

import numpy as np
import scipy.interpolate

import dss_name
import dss_object

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

#===================================================================================================
#===================================================================================================
class Recurrence(enum.Enum):
    """
    Enums for the recurrance of a load shape.
    """
    DAILY = "daily"
    YEARLY = "yearly"

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

#===================================================================================================
#===================================================================================================
class LoadShape(dss_object.ObjectMixin):
    """
    A class for an OpenDSS load shape.

    Attributes
    ----------
    command_add : str
        The OpenDSS command to run that will add the loadshape to the active circuit.
    name : dss_name.Name
        The name of the OpenDSS object.
    profile_name : str
        The name of the external load profile.
    recurrence : dss_loadshape.Recurrence
        The recurrence of the load shape.
    values : numpy.ndarray of float, (n_timestep,)
        The load shape values. These will be in the range [0.0, 1.0].

    See Also
    --------
    dss_object.ObjectMixin
    """

    #-----------------------------------------------------------------------------------------------
    #-----------------------------------------------------------------------------------------------
    def __init__(
        self, dss: win32com.client.CDispatch, name: str, profile_name: str, recurrence: Recurrence,
        values: NDArray[Shape["*"], Float], hour_interval: float = 1.0,
        n_interpolate: Optional[int] = None
    ):
        """
        The designated initializer.

        Parameters
        ----------
        dss : win32com.client.CDispatch
            The OpenDSSEngine COM object.
        name : str
            The name of the OpenDSS object element.
        profile_name : str
            The name of the external load profile.
        recurrence : dss_loadshape.Recurrence
            The recurrence of the load shape.
        values : numpy.ndarray of float, (n_timestep,)
            The load shape values.
        hour_interval : float, default=1.0
            The hour interval for each timestep. The default value of 1.0 means that each timestep
            represents 1-hour. A value of 0.25 would mean that each timestep represents 15-minutes.
        n_interpolate: optional of int, default=None
            The number of timesteps to expand/compress the `values` to using linear interpolation
            for inbetween values and linear extrapolation for end values. For example, if
            `len(values) == 10` and `n_interpolate == 20`, then `values` will be expanded to
            have 20 timesteps. A value of `None` will result in no expansion/compression of
            `values`.
        """
        loadshape_name= dss_name.Name(class_="loadshape", element=name)
        self.values = values.copy()

        if n_interpolate is not None:
            make_interpolated_values = scipy.interpolate.interp1d(
                x=np.arange(len(values)), y=values, kind="linear", fill_value="extrapolate"
            )
            
            self.values = make_interpolated_values(
                np.arange(start=0, stop=len(values), step=(len(values) / n_interpolate))
            )

        # Scale the values to be in the range [0, 1].
        self.values = np.interp(x=self.values, xp=(self.values.min(), self.values.max()), fp=(0, 1))

        # Convert the load profile's values to a string of an OpenDSS array.
        array_string = _make_opendss_array_string(array=self.values)

        
        # Add the loadshape to the circuit.
        # NOTE: It's important to specify `npts` before any array properties (`hour`, `mult`,
        # etc). Not doing this will cause OpenDSS 9.2.0.1 to have a memory access violation when
        # running the simulation.
        self.command_add = " ".join([
            f"new {loadshape_name.object}",
            f"npts={self.values.size}",
            f"mult={array_string}",
            f"interval={hour_interval}"
        ])

        self.profile_name = profile_name
        self.recurrence = recurrence

        dss_object.ObjectMixin.__init__(self=self, dss=dss, name=loadshape_name)

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def _make_opendss_array_string(array: NDArray[Shape["*"], Float]) -> str:
    """
    Make an OpenDSS formated array string from a numpy array.

    Parameters
    ----------
    array : numpy.ndarray of float, (n_timestep,)
        The array to convert.
    """
    array_string = [str(value) for value in array]
    array_string = "[" + ", ".join(array_string) + "]"

    return array_string
