# SPDX-License-Identifier: BSD-3-Clause

"""
This script generates a synthetic dataset from an OpenDSS circuit.
"""

from typing import Sequence

import json
import os
import win32com.client

import dataclasses
from rich.progress import track

import numpy as np
import pyarrow.feather

import data_factory
import dss_command
import dss_load
import dss_loadshape
import dss_name
import dss_phase
import dss_monitor
import dss_transformer
import label_factory
import loadshape_factory

@dataclasses.dataclass
class _Parameters:
    circuit_name: str
    random_state: int
    sourcepath: str
    transformer_names: Sequence[str]

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def main(): # pylint: disable=too-many-locals
    """
    The main function.
    """
    # OpenDSS prefers full paths. Use the current directory of this script file.
    basepath = os.getcwd()

    #***********************************************************************************************
    # Initialize parameters for circuits.
    #***********************************************************************************************
    parameters_list = [
        _Parameters(
            circuit_name="ckt5", random_state=42,
            sourcepath=f"{basepath}/src/ckt5/Master_ckt5.dss",
            transformer_names=["MDV_SUB_1"]
        ),
        _Parameters(
            circuit_name="lvna", random_state=7331,
            sourcepath=f"{basepath}/src/LVTestCaseNorthAmerican/Master.dss",
            transformer_names=["1", "2"]
        )
    ]

    #***********************************************************************************************
    # Run the simulations.
    #***********************************************************************************************
    for parameters in parameters_list:
        print("-"*50)
        print(parameters.circuit_name)
        print("-"*50)

        #*******************************************************************************************
        # Load the circuit.
        #*******************************************************************************************
        dss = win32com.client.Dispatch("OpenDSSEngine.DSS")

        dss.Text.Command = "clearall"
        dss.Text.Command = f"redirect ({parameters.sourcepath})"
        
        #*******************************************************************************************
        # Get loads and make monitors.
        #*******************************************************************************************
        loads = [
            dss_load.Load(dss=dss, name=name)
        for name in track(dss.ActiveCircuit.Loads.AllNames, "Making loads...")]

        transformers = [
            dss_transformer.Transformer(dss=dss, name=name)
        for name in parameters.transformer_names]

        load_monitors = [
            dss_monitor.Monitor(dss=dss, mode=0, target_object=load, terminal=1)
        for load in track(loads, "Making load monitors...")]

        # Monitors for the primary side of the transformers.
        transformer_monitors_primary = [
            dss_monitor.Monitor(dss=dss, mode=0, target_object=transformer, terminal=1)
        for transformer in track(transformers, "Making transformer primary monitors...")]

        # Monitors for the secondary side of the transformers.
        transformer_monitors_secondary = [
            dss_monitor.Monitor(dss=dss, mode=0, target_object=transformer, terminal=2)
        for transformer in track(transformers, "Making transformer secondary monitors...")]

        #*******************************************************************************************
        # Make loadshapes for all the loads.
        #*******************************************************************************************
        rng = np.random.default_rng(seed=parameters.random_state)
        recurrence = dss_loadshape.Recurrence.YEARLY

        (edit_commands,
         loadshapes,
         random_states) = loadshape_factory.make_ercot_iqr_random_loadshapes(
            dss=dss, ercot_loadprofile_path=f"{basepath}/profiles/ercot-2021-load_profiles.feather",
            loads=loads, recurrence=recurrence, rng=rng
        )

        #*******************************************************************************************
        # Add the monitors and loadshapes to the active circuit.
        #*******************************************************************************************
        _ = [dss_command.run(dss=dss, cmd=monitor.command_add) for monitor in load_monitors]

        _ = [
            dss_command.run(dss=dss, cmd=monitor.command_add)
        for monitor in transformer_monitors_primary]

        _ = [
            dss_command.run(dss=dss, cmd=monitor.command_add)
        for monitor in transformer_monitors_secondary]

        _ = [dss_command.run(dss=dss, cmd=loadshape.command_add) for loadshape in loadshapes]
        _ = [dss_command.run(dss=dss, cmd=command) for command in edit_commands]

        #*******************************************************************************************
        # Run simulation plan.
        #*******************************************************************************************
        print("Running simulation...")

        n_timestep = len(loadshapes[0].values)

        dss.Text.Command = " ".join([
            "set",
            f"mode={recurrence.value}",
            f"number={n_timestep}",
            #"stepsize=1h",
            "maxcontroliter=100"
        ])

        dss.Text.Command = "solve"

        #*******************************************************************************************
        # Save data.
        #*******************************************************************************************
        print("Saving data...")

        folderpath = f"{basepath}/data"
        circuit_name = parameters.circuit_name

        (data_df, channel_map) = data_factory.make_load_voltage_magnitude_data(
            loads=loads, monitors=load_monitors
        )

        loadshape_df = data_factory.make_loadshape_data(loadshapes=loadshapes)

        labels_df = label_factory.make_load_labels(
            loads=loads, loadshapes=loadshapes, random_states=random_states
        )

        sub_data_df = data_factory.make_transformer_voltage_magnitude_data(
            monitors_primary=transformer_monitors_primary,
            monitors_secondary=transformer_monitors_secondary, transformers=transformers
        )

        pyarrow.feather.write_feather(
            df=data_df, dest=f"{folderpath}/{circuit_name}-load-voltage_magnitudes-raw.feather"
        )

        pyarrow.feather.write_feather(
            df=labels_df, dest=f"{folderpath}/{circuit_name}-labels.feather"
        )

        pyarrow.feather.write_feather(
            df=loadshape_df, dest=f"{folderpath}/{circuit_name}-loadshapes.feather"
        )

        pyarrow.feather.write_feather(
            df=sub_data_df,
            dest=f"{folderpath}/{circuit_name}-transformer-voltage_magnitudes-raw.feather"
        )

        filepath_channel_map = f"{folderpath}/{circuit_name}-channel_map-load.json" 

        with open(file=filepath_channel_map, mode="w", encoding="utf8") as handle:
            json.dump(obj=channel_map, fp=handle, indent=4)

    print("*"*50)
    print("done!")
    print("*"*50)

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
