# SPDX-License-Identifier: BSD-3-Clause

"""
This module contains factory functions for making data.
"""

from typing import Sequence

from rich.progress import track

import numpy as np
import pandas as pd
import pyarrow.feather

import dss_connection
import dss_load
import dss_loadshape
import dss_monitor
import dss_transformer
import label_factory
import simulator

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def make_transformer_voltage_magnitude_data(
    monitors_primary: Sequence[dss_monitor.Monitor],
    monitors_secondary: Sequence[dss_monitor.Monitor], 
    transformers: Sequence[dss_transformer.Transformer]
) -> pd.DataFrame:
    """
    Make voltage magnitude data from the `transformers`.

    Parameters
    ----------
    monitors_primary : list of dss_monitor.Monitor
        The corresponding monitor for the primary side of each transformer.
    monitors_secondary : list of dss_monitor.Monitor
        The corresponding monitor for the secondary side of each transformer.
    transformers : list of dss_transformer.Transformer
        The transformers to make voltage magnitude data from.

    Returns
    -------
    pandas.DataFrame
        The transformer voltage magnitude data.
    """
    data = {}

    # We use this delimiter to separate the transformer's object name from the channel name and
    # winding side.
    delimiter = simulator.parameters.delimiter

    for (transformer, monitor_primary, monitor_secondary) in track(
        zip(transformers, monitors_primary, monitors_secondary), 
        "Making transformer voltage magnitude data...", total=len(transformers)
    ):
        data_primary_md = monitor_primary.make_data()
        data_secondary_md = monitor_secondary.make_data()

        for channel_name in ["V1", "V2", "V3"]:
            channel_index_primary = data_primary_md.channel_names.index(channel_name)
            channel_index_secondary = data_secondary_md.channel_names.index(channel_name)

            data[f"{transformer.name.object}{delimiter}primary{delimiter}{channel_name}"] = \
            data_primary_md.data[:, channel_index_primary]

            data[f"{transformer.name.object}{delimiter}secondary{delimiter}{channel_name}"] = \
            data_secondary_md.data[:, channel_index_secondary]

    data_df = pd.DataFrame(data)

    return data_df

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def make_load_voltage_magnitude_data(
    loads: Sequence[dss_load.Load], monitors: Sequence[dss_monitor.Monitor]
) -> pd.DataFrame:
    """
    Make voltage magnitude data from the `loads`.

    Parameters
    ----------
    loads : list of dss_load.Load
        The loads to make voltage magnitude data from.
    monitors : list of dss_monitor.Monitor
        The corresponding monitor for each load.

    Returns
    -------
    data_df : pandas.DataFrame
        The load voltage magnitude data.
    channel_map : list of tuple of (str, list of int)
        The list of channel indices for each meter. These mappings are used to aggregate multiple
        meter channels. The tuple will contain (meter_name, list of channel_indices), where the
        indices are the columns in the returned data_df.
    """
    data = {}

    # We use this delimiter to separate the load's object name from the channel name.
    delimiter = simulator.parameters.delimiter

    for (load, monitor) in track(
        zip(loads, monitors), "Making load voltage magnitude data...", total=len(loads)
    ):
        data_md = monitor.make_data()
        channel_names = ["V1", "V2", "V3"][:load.meter_count]

        for channel_name in channel_names:
            channel_index = data_md.channel_names.index(channel_name)

            data[f"{load.name.object}{delimiter}{channel_name}"] = data_md.data[:, channel_index]

    data_df = pd.DataFrame(data)

    channel_map = {}

    for (i, meter_name) in enumerate(data_df.columns):
        # Loads will only have two items split by the delimiter.
        (load_name, _) = meter_name.split(simulator.parameters.delimiter)
        
        if load_name not in channel_map:
            channel_map[load_name] = []

        channel_map[load_name].append(i)

    return (data_df, channel_map)

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def make_loadshape_data(loadshapes: Sequence[dss_loadshape.LoadShape]) -> pd.DataFrame:
    """
    Make the load shape data.

    Parameters
    ----------
    loadshapes : list of dss_loadshape.LoadShape
        The load shapes of the loads.

    Returns
    -------
    pandas.DataFrame
        The loadshape data.
    """
    data = {}

    for loadshape in track(loadshapes, "Making load shape data..."):
        data[loadshape.name.object] = loadshape.values

    data_df = pd.DataFrame(data)

    return data_df
