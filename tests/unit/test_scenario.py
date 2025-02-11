#  Copyright (c) 2015-2018 Cisco Systems, Inc.  # noqa: D100
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
from __future__ import annotations

import os
import shutil

from pathlib import Path

import pytest

from molecule import config, scenario, util


# NOTE(retr0h): The use of the `patched_config_validate` fixture, disables
# config.Config._validate from executing.  Thus preventing odd side-effects
# throughout patched.assert_called unit tests.
@pytest.fixture()
def _instance(patched_config_validate, config_instance: config.Config):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN202, ARG001
    return scenario.Scenario(config_instance)


def test_prune(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, PT019, D103
    e_dir = _instance.ephemeral_directory
    # prune data also includes files in the scenario inventory dir,
    # which is "<e_dir>/inventory" by default.
    # items are created in listed order, directories first, safe before pruned
    prune_data = {
        # these files should not be pruned
        "safe_files": ["state.yml", "ansible.cfg", "inventory/ansible_inventory.yml"],
        # these directories should not be pruned
        "safe_dirs": ["inventory"],
        # these files should be pruned
        "pruned_files": ["foo", "bar", "inventory/foo", "inventory/bar"],
        # these directories should be pruned, including empty subdirectories
        "pruned_dirs": ["baz", "roles", "inventory/baz", "roles/foo"],
    }

    for directory in prune_data["safe_dirs"] + prune_data["pruned_dirs"]:
        # inventory dir should already exist, and its existence is
        # required by the assertions below.
        if directory == "inventory":
            continue
        os.mkdir(os.path.join(e_dir, directory))  # noqa: PTH102, PTH118

    for file in prune_data["safe_files"] + prune_data["pruned_files"]:
        util.write_file(os.path.join(e_dir, file), "")  # noqa: PTH118

    _instance.prune()

    for safe_file in prune_data["safe_files"]:
        assert os.path.isfile(os.path.join(e_dir, safe_file))  # noqa: PTH113, PTH118

    for safe_dir in prune_data["safe_dirs"]:
        assert os.path.isdir(os.path.join(e_dir, safe_dir))  # noqa: PTH112, PTH118

    for pruned_file in prune_data["pruned_files"]:
        assert not os.path.isfile(os.path.join(e_dir, pruned_file))  # noqa: PTH113, PTH118

    for pruned_dir in prune_data["pruned_dirs"]:
        assert not os.path.isdir(os.path.join(e_dir, pruned_dir))  # noqa: PTH112, PTH118


def test_config_member(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, PT019, D103
    assert isinstance(_instance.config, config.Config)


def test_scenario_init_calls_setup(patched_scenario_setup, _instance):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, PT019, D103
    patched_scenario_setup.assert_called_once_with()


def test_scenario_name_property(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, PT019, D103
    assert _instance.name == "default"


def test_ephemeral_directory_property(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, PT019, D103
    assert os.access(_instance.ephemeral_directory, os.W_OK)


def test_scenario_inventory_directory_property(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, PT019, D103
    ephemeral_directory = _instance.config.scenario.ephemeral_directory
    e_dir = os.path.join(ephemeral_directory, "inventory")  # noqa: PTH118

    assert e_dir == _instance.inventory_directory


def test_check_sequence_property(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, PT019, D103
    sequence = [
        "dependency",
        "cleanup",
        "destroy",
        "create",
        "prepare",
        "converge",
        "check",
        "cleanup",
        "destroy",
    ]

    assert sequence == _instance.check_sequence


def test_converge_sequence_property(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, PT019, D103
    sequence = ["dependency", "create", "prepare", "converge"]

    assert sequence == _instance.converge_sequence


def test_create_sequence_property(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, PT019, D103
    sequence = ["dependency", "create", "prepare"]

    assert sequence == _instance.create_sequence


def test_dependency_sequence_property(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, PT019, D103
    assert _instance.dependency_sequence == ["dependency"]


def test_destroy_sequence_property(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, PT019, D103
    assert _instance.destroy_sequence == ["dependency", "cleanup", "destroy"]


def test_idempotence_sequence_property(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, PT019, D103
    assert _instance.idempotence_sequence == ["idempotence"]


def test_prepare_sequence_property(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, PT019, D103
    assert _instance.prepare_sequence == ["prepare"]


def test_side_effect_sequence_property(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, PT019, D103
    assert _instance.side_effect_sequence == ["side_effect"]


def test_syntax_sequence_property(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, PT019, D103
    assert _instance.syntax_sequence == ["syntax"]


def test_test_sequence_property(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, PT019, D103
    sequence = [
        "dependency",
        "cleanup",
        "destroy",
        "syntax",
        "create",
        "prepare",
        "converge",
        "idempotence",
        "side_effect",
        "verify",
        "cleanup",
        "destroy",
    ]

    assert sequence == _instance.test_sequence


def test_verify_sequence_property(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, PT019, D103
    assert _instance.verify_sequence == ["verify"]


def test_sequence_property_with_invalid_subcommand(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, PT019, D103
    _instance.config.command_args = {"subcommand": "invalid"}

    assert _instance.sequence == []


def test_setup_creates_ephemeral_and_inventory_directories(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, PT019, D103
    ephemeral_dir = _instance.config.scenario.ephemeral_directory
    inventory_dir = _instance.config.scenario.inventory_directory
    shutil.rmtree(ephemeral_dir)
    _instance._setup()

    assert os.path.isdir(ephemeral_dir)  # noqa: PTH112
    assert os.path.isdir(inventory_dir)  # noqa: PTH112


def test_ephemeral_directory():  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    # assure we can write to ephemeral directory
    assert os.access(scenario.ephemeral_directory("foo/bar"), os.W_OK)


def test_ephemeral_directory_overridden_via_env_var(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Confirm ephemeral_directory is overridden by MOLECULE_EPHEMERAL_DIRECTORY.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
        tmp_path: Pytest tmp_path fixture.
    """
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("MOLECULE_EPHEMERAL_DIRECTORY", "foo/bar")

    assert os.access(scenario.ephemeral_directory("foo/bar"), os.W_OK)


def test_ephemeral_directory_overridden_via_env_var_uses_absolute_path(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Confirm MOLECULE_EPHEMERAL_DIRECTORY uses absolute path.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
        tmp_path: Pytest tmp_path fixture.
    """
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("MOLECULE_EPHEMERAL_DIRECTORY", "foo/bar")

    assert Path(scenario.ephemeral_directory()).is_absolute()
