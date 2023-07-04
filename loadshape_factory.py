# SPDX-License-Identifier: BSD-3-Clause

"""
This script contains factory functions for making loadshapes.
"""

from typing import List, Sequence, Tuple

from rich.progress import track
import win32com

import numpy as np
import pyarrow.feather
import scipy.stats

import dss_load
import dss_loadshape
import dss_phase
import loadshape_prototype

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def make_ercot_iqr_random_loadshapes(
    dss: win32com.client.CDispatch, ercot_loadprofile_path: str, loads: Sequence[dss_load.Load],
    recurrence: dss_loadshape.Recurrence, rng: np.random.Generator
) -> Tuple[List[dss_loadshape.LoadShape], List[int]]:
    """
    Make a loadshape using the `loadshape_prototype.IqrRandomLoadshapePrototype` for each load using
    the ERCOT load profiles.

    Parameters
    ----------
    dss : win32com.client.CDispatch
        The OpenDSSEngine COM object.
    loads : list of dss_load.Load
        The loads to make loadshapes for.
    recurrence : dss_loadshape.Recurrence
        The recurrence of the load shape.
    rng : numpy.random.Generator
        The random number generator to use to generate a unique random state for each load.

    Returns
    -------
    loadshape_tuples : list of tuple of (str, dss_loadshape.LoadShape)
        Each tuple will contain an OpenDSS command for editing any attribute of the loadshape as
        well as the loadshape itself.
        The loadshape for each of the `loads`.
    random_states : list of int
        The random state used to generate randomness for each load.
    """
    random_states = [rng.integers(np.iinfo(np.int32).max) for _ in range(len(loads))]

    # See `ercot.py` for the valid load profile names.
    single_wye = [
        "BUSLOLF_SCENT", "BUSLOPV_SCENT", "BUSLOWD_SCENT", "BUSLODG_SCENT", "RESLOWR_SCENT",
        "RESHIWR_SCENT", "RESLOPV_SCENT", "RESHIPV_SCENT", "RESLOWD_SCENT", "RESHIWD_SCENT",
        "RESLODG_SCENT", "RESHIDG_SCENT"
    ]

    single_delta = ["BUSMEDLF_SCENT", "BUSMEDPV_SCENT", "BUSMEDWD_SCENT", "BUSMEDDG_SCENT"]

    triple = ["BUSHILF_SCENT", "BUSHIPV_SCENT", "BUSHIWD_SCENT", "BUSHIDG_SCENT"]

    phase_profile_mapping = {
        dss_phase.Phase.A: single_wye,
        dss_phase.Phase.B: single_wye,
        dss_phase.Phase.C: single_wye,
        dss_phase.Phase.AB: single_delta,
        dss_phase.Phase.AC: single_delta,
        dss_phase.Phase.BC: single_delta,
        dss_phase.Phase.ABC: triple
    }

    profiles_df = pyarrow.feather.read_feather(source=ercot_loadprofile_path)

    make_values = lambda iqr, n_timestep, random_state: scipy.stats.norm.rvs(
        loc=0.0, scale=(0.1 * iqr), size=n_timestep, random_state=random_state
    )

    prototype = loadshape_prototype.IqrRandomLoadShapePrototype(
        dss=dss, make_values=make_values, phase_profile_mapping=phase_profile_mapping,
        profiles_df=profiles_df, recurrence=recurrence
    )

    loadshape_tuples = [
        prototype.clone(load=load, random_state=random_state)
    for (load, random_state) in track(
        zip(loads, random_states), "Making loadshapes...", total=len(loads)
    )]

    edit_commands = [_tuple[0] for _tuple in loadshape_tuples]
    loadshapes = [_tuple[1] for _tuple in loadshape_tuples]

    return (edit_commands, loadshapes, random_states)
