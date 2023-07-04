# SPDX-License-Identifier: BSD-3-Clause

"""
The module contains classes for loadshape prototypes.
"""

from typing import Callable, Mapping, Optional, Sequence
from nptyping import Float, NDArray, Shape

import win32com

import dss_load
import dss_loadshape
import dss_phase
import numpy as np
import pandas as pd
import prototype
import scipy.stats

#===================================================================================================
#===================================================================================================
class IqrRandomLoadShapePrototype(prototype.Prototype):
    """
    This class clones a loadshape that is a linear combination of an external load profile and some
    random values scaled by the Interquartile Range (IQR) of the external load profile
    (zero-centered).
    """

    #-----------------------------------------------------------------------------------------------
    #-----------------------------------------------------------------------------------------------
    def __init__(
        self, dss: win32com.client.CDispatch,
        make_values: Callable[[int, int, int], NDArray[Shape["*"], Float]],
        phase_profile_mapping: Mapping[dss_phase.Phase, Sequence[str]], profiles_df: pd.DataFrame,
        recurrence: dss_loadshape.Recurrence, hour_interval: float = 1.0,
        n_interpolate: Optional[int] = None
    ):
        """
        The designated initializer.

        Parameters
        ----------
        dss : win32com.client.CDispatch
            The OpenDSSEngine COM object.
        make_values : callable of (iqr: float, n_timestep: int, random_state: int)
            -> NDArray[Shape["*"], Float]
            A function that generates `n_timestep` random values. The `iqr` of a zero-centered
            profile is used as a multiplier to scale the range of the random values.
        phase_profile_mapping: dict of {dss_phase.Phase: list of str}
            A mapping of load phase to a corresponding list of column names of profiles that can be
            assigned to that phase. These are the column names of profiles in the `profiles` data
            frame.
        profiles_df : pandas.DataFrame
            The data frame of load profiles.
        recurrence : dss_loadshape.Recurrence
            The recurrence of the load shape.
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
        self._dss = dss
        self._make_values = make_values
        self._phase_profile_mapping = phase_profile_mapping
        self._profiles_df = profiles_df
        self._recurrence = recurrence
        self._hour_interval = hour_interval
        self._n_interpolate = n_interpolate

    #-----------------------------------------------------------------------------------------------
    #-----------------------------------------------------------------------------------------------
    def clone(self, **kwargs: Mapping[str, any]) -> any:
        """
        Make a clone of the prototype.

        Parameters
        ----------
        **kwargs : dict of {str, any}
            load : dss_load.Load
                The load to attach the loadshape to.
            random_state : int
                The random state to use for pseudorandomness.

        Returns
        -------
        command_edit : str
            The OpenDSS command to edit any attributes of the loadshape in the active circuit.
        dss_loadshape.LoadShape
            A clone of the prototype.
        """
        load = kwargs["load"]
        random_state = kwargs["random_state"]

        #*******************************************************************************************
        # Make the loadshape based on the appropriate load profile.
        #*******************************************************************************************
        profile_names = self._phase_profile_mapping[load.phase]
        rng = np.random.default_rng(seed=random_state)
        profile_index = rng.integers(low=0, high=len(profile_names))
        profile_name = profile_names[profile_index]
        profile = self._profiles_df.loc[:, profile_name].to_numpy(dtype=float)
        
        # Center the profile before calculating the Interquartile Range (IQR).
        iqr = scipy.stats.iqr(x=(profile - np.mean(profile)))

        random_values = self._make_values(
            iqr=iqr, n_timestep=len(profile), random_state=random_state
        )
        
        values = profile + random_values

        #*******************************************************************************************
        # Make the loadshape and add it to the OpenDSS circuit.
        #*******************************************************************************************
        loadshape = dss_loadshape.LoadShape(
            dss=self._dss,
            name=f"load_{load.name.element}_{profile_name}",
            profile_name=profile_name,
            recurrence=self._recurrence,
            values=values,
            hour_interval=self._hour_interval,
            n_interpolate=self._n_interpolate
        )

        command_edit = "=".join([
            f"{load.name.object}.{loadshape.recurrence.value}",
            f"{loadshape.name.element}"
        ])

        return (command_edit, loadshape)

#===================================================================================================
#===================================================================================================
class RandomLoadShapePrototype(prototype.Prototype):
    """
    This class clones a loadshape that is composed of random values.
    """

    #-----------------------------------------------------------------------------------------------
    #-----------------------------------------------------------------------------------------------
    def __init__(
        self, dss: win32com.client.CDispatch,
        make_values: Callable[[int, int], NDArray[Shape["*"], Float]], n_timestep: int, 
        recurrence: dss_loadshape.Recurrence, hour_interval: float = 1.0
    ):
        """
        The designated initializer.

        Parameters
        ----------
        dss : win32com.client.CDispatch
            The OpenDSSEngine COM object.
        make_values : callable of (n_timestep: int, random_state: int) -> NDArray[Shape["*"], Float]
            A function that generates `n_timestep` random values.
        n_timestep : int
            The number of timesteps to randomly generate.
        recurrence : dss_loadshape.Recurrence
            The recurrence of the load shape.
        hour_interval : float, default=1.0
            The hour interval for each timestep. The default value of 1.0 means that each timestep
            represents 1-hour. A value of 0.25 would mean that each timestep represents 15-minutes.
        """
        self._dss = dss
        self._make_values = make_values
        self._recurrence = recurrence
        self._n_timestep = n_timestep
        self._hour_interval = hour_interval

    #-----------------------------------------------------------------------------------------------
    #-----------------------------------------------------------------------------------------------
    def clone(self, **kwargs: Mapping[str, any]) -> any:
        """
        Make a clone of the prototype.

        Parameters
        ----------
        **kwargs : dict of {str, any}
            load : dss_load.Load
                The load to attach the loadshape to.
            random_state : int
                The random state to use for pseudorandomness.

        Returns
        -------
        command_edit : str
            The OpenDSS command to edit any attributes of the loadshape in the active circuit.
        dss_loadshape.LoadShape
            A clone of the prototype.
        """
        load = kwargs["load"]
        random_state = kwargs["random_state"]

        loadshape = dss_loadshape.LoadShape(
            dss=self._dss,
            name=f"load_{load.name.element}",
            profile_name=str(random_state),
            recurrence=self._recurrence,
            values=self._make_values(n_timestep=self._n_timestep, random_state=random_state),
            hour_interval=self._hour_interval,
            n_interpolate=None
        )

        command_edit = "=".join([
            f"{load.name.object}.{loadshape.recurrence.value}",
            f"{loadshape.name.element}"
        ])

        return (command_edit, loadshape)
