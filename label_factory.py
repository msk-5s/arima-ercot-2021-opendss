# SPDX-License-Identifier: BSD-3-Clause

"""
This module contains factory functions for making labels.
"""

from typing import Optional, Sequence

from rich.progress import track

import pandas as pd

import dss_load
import dss_loadshape

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def make_load_labels(
    loads: Sequence[dss_load.Load], loadshapes: Sequence[dss_loadshape.LoadShape],
    random_states: Optional[Sequence[int]] = None
) -> pd.DataFrame:
    """
    Make labels for loads.

    Parameters
    ----------
    loads : list of dss_load.Load
        The loads to make labels for.
    loadshapes : list of dss_loadshape.LoadShape
        The load shapes of the loads.
    random_states : optional list of int, default=None
        The random states associated with each load.

    Returns
    -------
    pandas.DataFrame
        The labels for the loads.
    """
    labels = {
        "base_kv": [],
        "connection": [],
        "load_name": [],
        "loadshape_name": [],
        "meter_count": [],
        "phase_count": [],
        "phase_name": [],
        "phase_value": [],
        "profile_name": [],
        "random_state": []
    }

    for (load, loadshape, random_state) in track(
        zip(loads, loadshapes, random_states), "Making load labels...", total=len(loads)
    ):
        labels["load_name"].append(load.name.object)
        labels["loadshape_name"].append(loadshape.name.object)
        labels["base_kv"].append(load.get_property(key="kv"))
        labels["connection"].append(load.connection.name.lower())
        labels["meter_count"].append(load.meter_count)
        labels["phase_count"].append(load.phase_count)
        labels["phase_name"].append(load.phase.name)
        labels["phase_value"].append(load.phase.value)
        labels["profile_name"].append(loadshape.profile_name)
        labels["random_state"].append(random_state)

    labels_df = pd.DataFrame(labels)

    return labels_df
