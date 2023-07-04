# SPDX-License-Identifier: BSD-3-Clause

"""
This module contains classes for OpenDSS objects that can be monitored.
"""

from __future__ import annotations

from typing import List, Optional, Sequence
from nptyping import Float, NDArray, Shape

import numpy as np
import pandas as pd

import dss_name
import dss_object

#===================================================================================================
#===================================================================================================
class Monitor(dss_object.ObjectMixin):
    """
    An OpenDSS monitor for recording measurements of an OpenDSS object.

    Attributes
    ----------
    command_add : str
        The OpenDSS command to run that will add the loadshape to the active circuit.
    name : dss_name.Name
        The name of the OpenDSS object.

    See Also
    --------
    dss_object.ObjectMixin
    """
    #-----------------------------------------------------------------------------------------------
    #-----------------------------------------------------------------------------------------------
    def __init__(
        self, dss: win32com.client.CDispatch, mode: int, target_object: dss_object.ObjectMixin,
        terminal: int
    ):
        """
        The designated initializer.

        Parameters
        ----------
        dss : win32com.client.CDispatch
            The OpenDSSEngine COM object.
        mode : int
            The monitor mode (see OpenDSS manual for valid modes). Note that some modes will have
            duplicate headers (such as mode 11, which uses the header "Deg" for all voltage and
            current phases), as of OpenDSS 9.5.1.1.
        target_object : dss_object.ObjectMixin
            The OpenDSS object to monitor.
        terminal : int
            The terminal of the OpenDSS object to monitor.
        """
        monitor_name = dss_name.Name(
            class_="monitor",
            element="-".join([
                f"{target_object.name.class_}_{target_object.name.element}",
                f"mode_{mode}",
                f"terminal_{terminal}"
            ])
        )

        self.command_add = " ".join([
            f"new {monitor_name.object}",
            f"element={target_object.name.object}",
            f"mode={mode}",
            f"terminal={terminal}"
        ])

        self._i_monitors = dss.ActiveCircuit.Monitors

        dss_object.ObjectMixin.__init__(self, dss=dss, name=monitor_name)

    #-----------------------------------------------------------------------------------------------
    #-----------------------------------------------------------------------------------------------
    def make_data(self) -> MonitorData:
        """
        Make a pandas data frame containing the monitor data.

        Returns
        -------
        dss_monitor.MonitorData
            The recorded measurement data from the monitor.
        """
        # Set this monitor as the active monitor via the COM interface.
        self._i_monitors.Name = self.name.element

        # The channel index starts at 1 rather than 0 when reading a channel through the COM
        # interface.
        channel_count = self._i_monitors.NumChannels
        channel_indices = list(range(1, channel_count + 1))

        hours = list(self._i_monitors.dblHour)
        sample_count = self._i_monitors.SampleCount

        # Add an extra column for the hours.
        data = np.zeros(shape=(sample_count, channel_count + 1), dtype=float)
        data[:, 0] = hours

        # Get the monitor data for each channel.
        for index in channel_indices:
            data[:, index] = np.array(self._i_monitors.Channel(index))

        channel_names = ["hours"] + list(self._i_monitors.Header)

        # Some of the channel names returned by the COM interface have an extra space in them. These
        # spaces are removed.
        channel_names = [name.replace(" ", "") for name in channel_names]

        data_md = MonitorData(
            channel_names=channel_names, data=data, monitor_name=self.name
        )

        return data_md

#===================================================================================================
#===================================================================================================
class MonitorData:
    """
    Data recorded by a monitor.

    Attributes
    ----------
    channel_names : list of str, (n_channel)
        The name of the channels.
    data : numpy.ndarray of float, (n_sample, n_channel)
        The measurement data recorded by the monitor.
    monitor_name: dss_name.Name
        The name of the monitor that made this data.
    """

    #-----------------------------------------------------------------------------------------------
    #-----------------------------------------------------------------------------------------------
    def __init__(
        self, channel_names: Sequence[str], data: NDArray[Shape["*,*"], Float],
        monitor_name: dss_name.Name
    ):
        """
        The designated initializer.

        Parameters
        ----------
        channel_names : list of str, (n_channel)
            The name of the channels.
        data : numpy.ndarray of float, (n_sample, n_channel)
            The measurement data recorded by the monitor.
        monitor_name: dss_name.Name
            The name of the monitor that made this data.
        """
        self.channel_names = channel_names
        self.data = data
        self.monitor_name = monitor_name

    #-----------------------------------------------------------------------------------------------
    #-----------------------------------------------------------------------------------------------
    def to_csv(self, folderpath: str, filename: Optional[str] = None):
        """
        Save the monitor data to a CSV file.

        Parameters
        ----------
        folderpath : str
            The path to the folder to save the file in.
        filename : optional of str, default=None
            The name of the file. If `None`, then the filename will be derived from the monitor's
            name.
        """
        filename = f"{self.monitor_name.element}.csv" if filename is None else filename
        header = ",".join(self.channel_names)
        
        np.savetxt(fname=f"{folderpath}/{filename}", X=self.data, delimiter=",", header=header)
