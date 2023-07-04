# SPDX-License-Identifier: BSD-3-Clause

"""
This module contains a classes for an OpenDSS load.
"""

import win32com

import dss_name
import dss_object
import dss_phase

#===================================================================================================
#===================================================================================================
_meter_counts = {
    dss_phase.Phase.A: 1,
    dss_phase.Phase.B: 1,
    dss_phase.Phase.C: 1,
    dss_phase.Phase.AB: 2,
    dss_phase.Phase.AC: 2,
    dss_phase.Phase.BC: 2,
    dss_phase.Phase.ABC: 3,
}

#===================================================================================================
#===================================================================================================
class Load(dss_object.ObjectMixin, dss_phase.PhaseMixin):
    """
    This class represents an OpenDSS Load class.

    Attributes
    ----------
    connection : dss_connection.Connection
        The type of `connection` that the object is connected to.
    meter_count : int
        The number of meters connected to the load. In OpenDSS, a line-to-line delta connected load
        will be considered a single-phase load, but will have two meter readings (as recorded by a
        monitor). This means that `meter_count == 2` while `phase_count == 1`.
    name : str
        The name of the OpenDSS object element.
    phase : dss_phase.Phase
        The phase of the object.
    phase_count : int
        The number of phases that the object is connected to.

    See Also
    --------
    dss_object.ObjectMixin
    dss_phase.PhaseMixin
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
            The name of the load object element.
        """
        load_name = dss_name.Name(class_="load", element=name)

        dss_object.ObjectMixin.__init__(self, dss=dss, name=load_name)
        dss_phase.PhaseMixin.__init__(self, dss=dss, name=load_name)
        
        self.meter_count = _meter_counts[self.phase]
