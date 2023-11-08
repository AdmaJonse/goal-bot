"""
This module defines the Period class.
"""

REGULATION = "REG"
OVERTIME = "OT"
SHOOTOUT = "SHO"


class Period:
    """
    The team class. This class contains the various names that can be used for a team and
    provides methods for querying these names.
    """

    def __init__(self, data):
        self._number      : int = data["number"]
        self._period_type : str = data["periodType"]

    def __eq__(self, other):
        return (isinstance(self, Period) and
                isinstance(other, Period) and
                self.number == other.number and
                self.period_type == other.period_type)

    def __str__(self):
        """
        Return a string representation of the period.
        """

        # default in case of funky data
        period_string = "The period"

        if self.is_regulation:

            if self.number == 1:
                period_string = "The first period"
            elif self.number == 2:
                period_string = "The second period"
            elif self.number == 3:
                period_string = "The third period"

        elif self.is_overtime:

            period_string = "The OT period"

        elif self.is_shootout:

            period_string = "The shootout"

        return period_string

    @property
    def number(self):
        """
        Getter for the period number.
        """
        return self._number

    @number.setter
    def number(self, number):
        """
        Setter for the period number.
        """
        self._number = number

    @property
    def period_type(self):
        """
        Getter for the period type.
        """
        return self._period_type

    @period_type.setter
    def period_type(self, period_type):
        """
        Setter for the period type.
        """
        self._period_type = period_type

    @property
    def is_regulation(self) -> bool:
        """
        Return a boolean indicating whether or not this is a period in regulation.
        """
        return self.period_type == REGULATION

    @property
    def is_overtime(self) -> bool:
        """
        Return a boolean indicating whether or not this is a period in overtime.
        """
        return self.period_type == OVERTIME

    @property
    def is_shootout(self) -> bool:
        """
        Return a boolean indicating whether or not this is a shootout.
        """
        return self.period_type == SHOOTOUT

    @property
    def ordinal(self) -> str:
        """
        Return an ordinal string representation of the period from the given event.
        """
        period_string = ""

        if self.is_regulation:

            if self.number == 1:
                period_string = "1st"
            elif self.number == 2:
                period_string = "2nd"
            elif self.number == 3:
                period_string = "3rd"

        elif self.is_overtime:

            if self.number == 4:
                period_string = "OT"
            elif self.number == 5:
                period_string = "2OT"
            elif self.number == 6:
                period_string = "3OT"
            elif self.number == 7:
                period_string = "4OT"
            else:
                period_string = "OT"

        elif self.is_shootout:

            period_string = "SO"

        return period_string
