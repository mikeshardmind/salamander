#   Copyright 2020-present Michael Hall
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

import os
import pathlib
import sys
from typing import Optional

import toml

from src.bot import BehaviorFlags, Salamander
from src import ipc_layer as ipcl


def get_conf() -> Optional[BehaviorFlags]:

    path = pathlib.Path("config.toml")

    if not (path.exists() and path.is_file()):
        return None

    raw_data = toml.load(path)

    no_serpent = raw_data.pop("no_serpent", False)
    no_basilisk = raw_data.pop("no_basilisk", False)

    ext_dict = raw_data.pop("exts", None)
    about_text = raw_data.pop("about_text", None)

    # TODO: probably move this later to allow multiple bots in same proc to have different addresses here.
    if hydra_subscribe_addr := raw_data.pop("hydra_subscribe_addr", ""):
        ipcl.MULTICAST_SUBSCRIBE_ADDR.set(hydra_subscribe_addr)
    if hydra_remote_recv_addr := raw_data.pop("hydra_remote_recv_addr", ""):
        ipcl.PULL_REMOTE_ADDR.set(hydra_remote_recv_addr)

    if ext_dict:
        exts = tuple(
            (
                *(f"src.extensions.{name}" for name in ext_dict.pop("core", ())),
                *(f"src.contrib_extensions.{name}" for name in ext_dict.pop("contrib", ())),
                *(f"src.local_extensions.{name}" for name in ext_dict.pop("local", ())),
                *ext_dict.pop("global", ()),
            )
        )
    else:
        exts = ()

    return BehaviorFlags(
        no_serpent=no_serpent,
        no_basilisk=no_basilisk,
        initial_exts=exts,
        about_text=about_text,
    )


def main():

    if TOKEN := os.environ.get("SALAMANDER_TOKEN", None):
        Salamander.run_with_wrapping(TOKEN, config=get_conf())
    else:
        sys.exit("No token?")


if __name__ == "__main__":
    main()
