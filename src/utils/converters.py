#   Copyright 2020 Michael Hall
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from __future__ import annotations

from discord.ext import commands

from ..bot import SalamanderContext


class Weekday:

    _valid_days = {
        0: ("monday", "m", "mon"),
        1: ("tuesday", "t", "tu", "tue", "tues"),
        2: ("wednesday", "w", "wed"),
        3: ("thursday", "th", "r", "thu", "thur", "thurs"),
        4: ("friday", "f", "fri"),
        5: ("saturday", "sat", "sa", "s"),
        6: ("sunday", "sun", "su", "u"),
    }

    def __init__(self, number: int):
        self.number: int = number

    def as_string(self):
        return self._valid_days[self.number][0].title()

    def __repr__(self):
        return f"<Weekday({self.number})>"

    def __str__(self):
        return self.as_string()

    @classmethod
    async def convert(cls, ctx: SalamanderContext, argument: str):

        argument = argument.strip().casefold()

        for number, opts in cls._valid_days.items():
            if argument in opts:
                return cls(number)

        raise commands.BadArgument(
            message="I didn't understand that input as a day of the week"
        )