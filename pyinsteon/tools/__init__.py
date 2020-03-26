"""Command line tools to interact with the Insteon devices."""
import os
from .. import async_connect, async_close, devices
from .tools_base import ToolsBase
from .config import ToolsConfig
from .aldb import ToolsAldb
from .cmd import CmdTools
from ..managers.link_manager import async_enter_linking_mode, async_enter_unlinking_mode


class InsteonCmd(ToolsBase):
    """Command class to test interactivity."""

    async def do_connect(self, *args, **kwargs):
        """Connect to the Insteon modem.

        Usage:
            connect device
            connect host username [hub_version [port]]
        """
        args = args[0].split()
        try:
            self.username = args[1]
            self.host = args[0]
        except IndexError:
            try:
                self.device = args[0]
            except IndexError:
                pass
            params = self.device
        else:
            try:
                self.hub_version = int(args[2])
                self.port = int(args[3])
            except (ValueError, IndexError):
                self.hub_version = None
                self.port = None

        password = await self._get_connection_params()

        if password:
            params = f"{self.host} {self.username} {'*' * len(password)} {self.hub_version} {self.port}"
        self._log_command(f"connect {params}")
        try:
            await async_connect(
                device=self.device,
                host=self.host,
                port=self.port,
                username=self.username,
                password=password,
                hub_version=self.hub_version,
            )
        except ConnectionError:
            self._log_stdout("Connection failed. Please review connection information.")

    async def do_disconnect(self, *args, **kwargs):
        """Close the connection to the modem.

        Usage:
            disconnect
        """
        self._log_command("disconnect")
        await async_close()

    async def do_load_devices(self, *args, **kwargs):
        """Load the devices.

        Usage:
            load_devices workdir id_devices

        workdir: Directory where the saved device file is located (Enter . for current directory)
        id_devices: Option for handling unknown devices
            0 - Do not ID devices
            1 - ID unknown devices only (default)
            2 - ID all devices
        """

        args = args[0].split()
        try:
            if args[0] != "":
                self.workdir = args[0]
                if self.workdir == ".":
                    self.workdir = os.getcwd()
        except IndexError:
            pass

        if not self.workdir:
            self.workdir = await self._get_workdir()

        try:
            id_devices = int(args[1])
        except (IndexError, ValueError):
            id_devices = None
        if id_devices not in [0, 1, 2]:
            id_devices = await self._get_int(
                "Identify devices (0=None, 1=Unknown Only, 2=All", 1, [0, 1, 2]
            )
        self._log_command(f"load_devices {self.workdir} {id_devices}")
        await devices.async_load(workdir=self.workdir, id_devices=id_devices)
        self._log_stdout(f"Total devices: {len(devices)}")

    async def do_manage_aldb(self, *args, **kwargs):
        """Manage device All-Link database."""
        self._log_command("manage_aldb")
        await self._call_next_menu(ToolsAldb, "aldb")

    async def do_manage_config(self, *args, **kwargs):
        """Manage operational flags and extended properties."""
        self._log_command("manage_config")
        await self._call_next_menu(ToolsConfig, "config")

    async def do_commands(self, *args, **kwargs):
        """Execute device commands."""
        self._log_command("tests")
        await self._call_next_menu(CmdTools, "commands")

    async def do_add_device(self, *args, **kwargs):
        """Add a device."""
        self._log_command("add_device")
        self._log_stdout(
            "Press the set button on the device. Linking will occur in the background."
        )
        await async_enter_linking_mode(is_controller=True, group=0)

    async def do_remove_device(self, *args, **kwargs):
        """Add a device."""
        self._log_command("remove_device")
        self._log_stdout(
            "Press the set button on the device. Unlinking will occur in the background."
        )
        await async_enter_unlinking_mode(group=0)

    async def do_exit(self, *args, **kwargs):
        """Exit the current menu.

        Usage:
            exit
        """
        self._log_command("exit")
        await self.do_log_to_file("n")
        return -1


def tools():
    """Start insteon tools."""
    InsteonCmd.start()