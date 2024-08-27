# SPDX-FileCopyrightText: 2018 Carter Nelson for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`analog_in`
==============================
AnalogIn for single-ended and
differential ADC readings.

* Author(s): Carter Nelson, adapted from MCP3xxx original by Brent Rubell
"""

try:
    from typing import Optional
    from .ads1x15 import ADS1x15
except ImportError:
    pass

_ADS1X15_DIFF_CHANNELS = {(0, 1): 0, (0, 3): 1, (1, 3): 2, (2, 3): 3}
_ADS1X15_PGA_RANGE = {2 / 3: 6.144, 1: 4.096, 2: 2.048, 4: 1.024, 8: 0.512, 16: 0.256}


class AnalogIn:
    """AnalogIn Mock Implementation for ADC Reads.

    :param ADS1x15 ads: The ads object.
    :param int positive_pin: Required pin for single-ended.
    :param int negative_pin: Optional pin for differential reads.
    """

    def __init__(
        self, ads: ADS1x15, positive_pin: int, negative_pin: Optional[int] = None
    ):
        self._ads = ads
        self._pin_setting = positive_pin
        self._negative_pin = negative_pin
        self.is_differential = False
        if negative_pin is not None:
            pins = (self._pin_setting, self._negative_pin)
            if pins not in _ADS1X15_DIFF_CHANNELS:
                raise ValueError(
                    "Differential channels must be one of: {}".format(
                        list(_ADS1X15_DIFF_CHANNELS.keys())
                    )
                )
            self._pin_setting = _ADS1X15_DIFF_CHANNELS[pins]
            self.is_differential = True

    def status(self):
        """
        human readable summary of dac channel
        >>> chan.str()
        'AIN0( voltage: 0.0000v, raw_value:     0/65535, is_differential: False )' # single ended
        'AIN3P->4N (voltage: 0.0000v, raw_value:     0/65535, is_differential: True)' # differential
        """
        # ch_name = self._dac._channel_index_map[self.channel_index]
        if self.is_differential == False:
            ch_name = self._pin_setting
        else:
            ch_name = f"{self._pin_setting}P->{self._negative_pin}N"
        summary = (
            f"AIN{ch_name}( "
            + f"voltage: {self.voltage:.4f}v, "
            + f"value:{self.value:5}/65535, "
            + f"is_differential: {self.is_differential} )"
        )

        return summary

    def __repr__(self):
        return self.status()

    def __str__(self):
        return self.status()

    @property
    def value(self) -> int:
        """The value on the analog pin between 0 and 65535
        inclusive (16-bit). (read-only)

        Even if the underlying analog to digital converter (ADC) is
        lower resolution, the value is 16-bit.
        """
        return self._ads.read(
            self._pin_setting, is_differential=self.is_differential
        ) << (16 - self._ads.bits)

    @property
    def voltage(self) -> float:
        """Returns the voltage from the ADC pin as a floating point value."""
        volts = self.value * _ADS1X15_PGA_RANGE[self._ads.gain] / 32767
        return volts
