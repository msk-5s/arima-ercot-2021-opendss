# SPDX-License-Identifier: BSD-3-Clause

"""
This module contains classes for OpenDSS objects that can have a phase connection.
"""

import enum

import win32com

import dss_command
import dss_connection
import dss_name

#===================================================================================================
#===================================================================================================
class Phase(enum.Enum):
    """
    Enums for the phase of a load.
    """
    A = 0
    B = 1
    C = 2
    AB = 3
    AC = 4
    BC = 5
    ABC = 6

#===================================================================================================
#===================================================================================================
class PhaseMixin:
    """
    This mixin adds functionality/attributes for an OpenDSS power conversion object that has a
    single-sided phase connection (on the `bus1` property of the object).

    Attributes
    ----------
    connection : dss_connection.Connection
        The type of `connection` that the object is connected to.
    phase : phase.Phase
        The phase of the object.
    phase_count : int
        The number of phases that the object is connected to.
    """
    
    #-----------------------------------------------------------------------------------------------
    #-----------------------------------------------------------------------------------------------
    def __init__(self, dss: win32com.client.CDispatch, name: dss_name.Name):
        """
        The designated initializer.

        Parameters
        ----------
        dss : win32com.client.CDispatch
            The OpenDSSEngine COM object.
        name: dss_name.Name
            The name of the OpenDSS object.
        """
        self.connection = dss_connection.string_to_connection(
            a_string=dss_command.run(dss=dss, cmd=f"? {name.object}.conn")
        )

        self.phase = object_name_to_phase(dss=dss, name=name)
        self.phase_count = int(dss_command.run(dss=dss, cmd=f"? {name.object}.phases"), base=10)

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def object_name_to_phase(dss: win32com.client.CDispatch, name: dss_name.Name) -> Phase:
    """
    Take an OpenDSS's object name and determine its phase.

    Assumptions:
        - The ordering of connections doesn't matter for line-to-line connections.
        - The object is only connected at `bus1`.
        - There are only at most 3 terminal connections. OpenDSS allows specifying an additional
          terminal connection for the neutral (it is not required to be specified, however, the
          code could always be updated to handle this case, if desired).

    Parameters
    ----------
    dss : win32com.client.CDispatch
        The OpenDSSEngine COM object.
    name : dss_name.Name
        The name of the OpenDSS object to get the phase of.

    Returns
    -------
    Phase
        The appropriate `Phase` enum.
    """
    phase_count = int(dss_command.run(dss=dss, cmd=f"? {name.object}.phases"), base=10)

    phase = None

    if phase_count == 3:
        phase = Phase.ABC
    else:
        bus1 = dss_command.run(dss=dss, cmd=f"? {name.object}.bus1")
        substrings = bus1.split(".")
        terminals = {int(x, base=10) for x in substrings[1:]}

        # NOTE: line-to-line connections are 1-phase connections (higher voltage by sqrt(3)).
        phase_mapping = {
            Phase.A: {1},
            Phase.B: {2},
            Phase.C: {3},
            Phase.AB: {1, 2},
            Phase.AC: {1, 3},
            Phase.BC: {2, 3}
        }

        # Since `terminals` is a set, we want to find the index of the matching set in
        # `phase_mapping`.
        index = list(phase_mapping.values()).index(terminals)
        phase = list(phase_mapping.keys())[index]

    return phase
