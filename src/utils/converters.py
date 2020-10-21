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

import contextlib
import re
from datetime import timedelta
from typing import Final, NamedTuple, Optional, Sequence

import discord
from discord.ext import commands

from .formatting import humanize_timedelta
from .parsing import parse_timedelta

_discord_member_converter_instance: Final[
    commands.MemberConverter
] = commands.MemberConverter()
_id_regex: Final[re.Pattern] = re.compile(r"([0-9]{15,21})$")
_mention_regex: Final[re.Pattern] = re.compile(r"<@!?([0-9]{15,21})>$")
_role_mention_regex: Final[re.Pattern] = re.compile(r"^<@&([0-9]{15,21})>$")


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
    async def convert(cls, ctx, argument: str):

        argument = argument.strip().casefold()

        for number, opts in cls._valid_days.items():
            if argument in opts:
                return cls(number)

        raise commands.BadArgument(
            message="I didn't understand that input as a day of the week"
        )


class MemberOrID(NamedTuple):
    member: Optional[discord.Member]
    id: int

    @classmethod
    async def convert(cls, ctx, argument: str):

        with contextlib.suppress(Exception):
            m = await _discord_member_converter_instance.convert(ctx, argument)
            return cls(m, m.id)

        match = _id_regex.match(argument) or _mention_regex.match(argument)
        if match:
            return cls(None, int(match.group(1)))

        raise commands.BadArgument(message="That wasn't a member or member ID.")


class TimedeltaConverter(NamedTuple):
    arg: str
    delta: timedelta

    @classmethod
    async def convert(cls, ctx, argument: str):

        parsed = parse_timedelta(argument)
        if not parsed:
            raise commands.BadArgument(message="That wasn't a duration of time.")

        return cls(argument, parsed)

    def __str__(self):
        return humanize_timedelta(self.delta)


def resolve_as_roles(guild: discord.Guild, user_input: str) -> Sequence[discord.Role]:

    if match := (_id_regex.match(user_input) or _role_mention_regex.match(user_input)):
        # We assume that nobody will make a role with a name that is an ID
        # If someone reports this as a bug,
        # kindly tell them to change the name of the impacted role.
        if role := guild.get_role(int(match.group(1))):
            return (role,)

    casefolded_user_input = user_input.casefold()
    return tuple(r for r in guild.roles if r.name.casefold() == casefolded_user_input)
