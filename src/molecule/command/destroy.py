#  Copyright (c) 2015-2018 Cisco Systems, Inc.
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.
"""Destroy Command Module."""
from __future__ import annotations

import logging
import os

import click

from molecule import util
from molecule.api import drivers
from molecule.command import base
from molecule.config import DEFAULT_DRIVER


LOG = logging.getLogger(__name__)
MOLECULE_PARALLEL = os.environ.get("MOLECULE_PARALLEL", False)


class Destroy(base.Base):
    """Destroy Command Class."""

    def execute(self, action_args=None):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, ARG002
        """Execute the actions necessary to perform a `molecule destroy` and returns None."""
        if self._config.command_args.get("destroy") == "never":
            msg = "Skipping, '--destroy=never' requested."
            LOG.warning(msg)
            return

        self._config.provisioner.destroy()
        self._config.state.reset()


@base.click_command_ex()
@click.pass_context
@click.option(
    "--scenario-name",
    "-s",
    default=base.MOLECULE_DEFAULT_SCENARIO_NAME,
    help=f"Name of the scenario to target. ({base.MOLECULE_DEFAULT_SCENARIO_NAME})",
)
@click.option(
    "--driver-name",
    "-d",
    type=click.Choice([str(s) for s in drivers()]),
    help=f"Name of driver to use. ({DEFAULT_DRIVER})",
)
@click.option(
    "--all/--no-all",
    "__all",
    default=MOLECULE_PARALLEL,
    help="Destroy all scenarios. Default is False.",
)
@click.option(
    "--parallel/--no-parallel",
    default=False,
    help="Enable or disable parallel mode. Default is disabled.",
)
def destroy(ctx, scenario_name, driver_name, __all, parallel):  # type: ignore[no-untyped-def] # pragma: no cover  # noqa: ANN001, ANN201
    """Use the provisioner to destroy the instances."""
    args = ctx.obj.get("args")
    subcommand = base._get_subcommand(__name__)  # noqa: SLF001
    command_args = {
        "parallel": parallel,
        "subcommand": subcommand,
        "driver_name": driver_name,
    }

    if __all:
        scenario_name = None

    if parallel:
        util.validate_parallel_cmd_args(command_args)

    base.execute_cmdline_scenarios(scenario_name, args, command_args)
