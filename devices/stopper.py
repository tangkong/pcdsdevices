"""
Generic X-Ray Stoppers
"""
############
# Standard #
############
import logging
from copy import copy
from enum import Enum

###############
# Third Party #
###############


##########
# Module #
##########
from .state         import pvstate_class
from .lclsdevice    import LCLSDevice             as Device
from .lclssignal    import LCLSEpicsSignal        as EpicsSignal
from .lclssignal    import LCLSEpicsSignalRO      as EpicsSignalRO
from .lclscomponent import LCLSComponent          as C
from .lclscomponent import LCLSFormattedComponent as FC


logger = logging.getLogger(__name__)


class Commands(Enum):
    """
    Command aliases for ``CMD``
    """
    close_stopper = 0
    open_stopper  = 1 


PPS = pvstate_class('PPS',
                    {'summary' : {'pvname' : '',
                                        0  : 'out',
                                        1  : 'unknown',
                                        2  : 'unknown',
                                        3  : 'unknown',
                                        4  : 'in'}},
                    doc='MPS Summary of Stopper state')


Limits = pvstate_class('Limits',
                       {'open_limit'  : {'pvname' :':OPEN',
                                          0       : 'defer',
                                          1       : 'out'},
                       'closed_limit' : {'pvname' :':CLOSE',
                                          0       : 'defer',
                                          1       : 'in'}},
                       doc='State description of Stopper limits')


class PPSStopper(Device):
    """
    PPS Stopper

    Control of this device only available to PPS systems. This class merely
    interprets the summary of limit switches to let the controls system know
    the current position
    """
    summary = C(PPS, '')

    def __init__(self, prefix, *, name=None,
                 read_attrs=None, ioc=None,
                 mps=None, **kwargs):

        if not read_attrs:
            read_attrs = ['summary']

        super().__init__(prefix, ioc=ioc,
                         read_attrs=read_attrs,
                         name=name)


class Stopper(Device):
    """
    Controls Stopper

    Similar to the :class:`.GateValve`, the Stopper class provides basic
    support for Controls stoppers i.e stoppers that can be commanded from
    outside the PPS system
    """
    command   = C(EpicsSignal, ':CMD')
    limits    = C(Limits, '')

    commands  = Commands
    
    def __init__(self, prefix, *, name=None,
                 read_attrs=None, ioc=None,
                 mps=None, **kwargs):

        #Configure read attributes
        if read_attrs is None:
            read_attrs = ['limits']

        super().__init__(prefix, ioc=ioc,
                         read_attrs=read_attrs,
                         name=name)
    
    def open(self):
        """
        Remove the stopper from the beam
        """
        self.command.put(self.commands.open_stopper)


    def close(self):
        """
        Close the stopper
        """
        self.command.put(self.commands.close_stopper)
