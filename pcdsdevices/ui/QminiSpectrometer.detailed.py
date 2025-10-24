from __future__ import annotations

import logging
import re

import pydm
from pydm import Display
from pydm.widgets import (PyDMByteIndicator, PyDMEnumComboBox, PyDMLabel,
                          PyDMLineEdit, PyDMPushButton, PyDMWaveformPlot)
from typhos import utils

from pcdsdevices.widgets.qmini import QMiniBase

logger = logging.getLogger(__name__)


class QminiSpectrometerDetailedUI(Display, utils.TyphosBase, QMiniBase):
    """
    Custom widget for managing the SmarAct detailed screen
    """
    def __init__(self, parent=None, ui_filename='QminiSpectrometer.detailed.ui', **kwargs):
        super().__init__(parent=parent, ui_filename=ui_filename)

    def add_device(self, device):
        """Typhos hook for adding a new device."""
        super().add_device(device)
        # Gotta make sure to destroy this screen if you were handed an empty device
        if device is None:
            self.ui.device_name_label.setText("(no device)")
            return

        self.fix_pvs()

    def fix_pvs(self):
        """
        Once typhos links the device, expand the macros in the buttons and
        indicators.
        """
        if not self.device:
            print('No device set!')
            return

        def expand_prefix(channel):
            """
            containerize the macro expansion because plot objects are weird
            """
            result = ''

            if re.search(r'\{prefix\}', _channel):
                result = _channel.replace('${prefix}',
                                          self.device.prefix)
            return result

        object_names = self.find_pydm_names()

        for obj in object_names:
            _widget = getattr(self, obj)

            # setting the channels in waveform plots is weird since you cannot
            # explicitly set the x and y channels. `addChannel` adds a curve??
            if isinstance(_widget,
                          PyDMWaveformPlot):
                _widget.addChannel(
                    y_channel=f'ca://{self.device.prefix}:SPECTRUM',
                    x_channel=f'ca://{self.device.prefix}:WAVELENGTHS',
                    color='black',
                    lineStyle=1,
                    lineWidth=2,
                    redraw_mode=pydm.widgets.waveformplot.WaveformCurveItem.REDRAW_ON_Y,
                    yAxisName='Intensity',
                    name='Intensity (a.u.)'
                )

            # standard channel macro expansion
            else:
                _channel = getattr(_widget, 'channel')

                if not _channel:
                    _channel = ''

                _widget.set_channel(expand_prefix(_channel))

    def find_pydm_names(self) -> list[str]:
        """
        Find the object names for all PyDM objects using findChildren

        Returns
        ------------
        result : list[str]
            1D list of object names
        """
        _button = PyDMPushButton
        _byte = PyDMByteIndicator
        _label = PyDMLabel
        _line_edit = PyDMLineEdit
        _combo_box = PyDMEnumComboBox
        _plot = PyDMWaveformPlot

        result = []

        for obj_type in [_button, _byte, _label, _line_edit, _combo_box, _plot]:
            result += [obj.objectName() for obj in self.findChildren(obj_type)]

        _omit = ['save_spectra']

        return [obj for obj in result if obj not in _omit]
