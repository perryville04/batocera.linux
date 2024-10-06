from __future__ import annotations

from configparser import ConfigParser
from pathlib import Path
from typing import TYPE_CHECKING

from ... import Command, controllersConfig
from ...batoceraPaths import CONFIGS, SAVES, SCREENSHOTS, mkdir_if_not_exists
from ...utils.buildargs import parse_args
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext


class EDuke32Generator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "eduke32",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"], "menu": "KEY_ESC", "pause": "KEY_ESC", "save_state": "KEY_F8", "restore_state": "KEY_F9" }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        rom_path = Path(rom)
        # Core is either eduke32 or fury
        core = system.config["core"]
        config_dir = CONFIGS / f"{core}"
        saves_dir = SAVES / f"{core}"
        config_file = config_dir / f"{core}.cfg"
        # A script file with console commands that are always ran when the game starts
        script_file = config_dir / "autoexec.cfg"

        mkdir_if_not_exists(config_dir)
        mkdir_if_not_exists(saves_dir)

        if not config_file.exists():
            with config_file.open('x'):
                pass

        parser = ConfigParser(interpolation=None)
        # Override optionxform to stop implicit case conversions
        parser.optionxform = str
        # Configuration options found here: https://wiki.eduke32.com/wiki/Configuration_file_options
        # NB: Not all configuration options listed actually work e.g. showFPS, etc.
        # NB: In eduke32 configs, booleans must be integers
        with config_file.open("r") as config:
            parser.read_file(config)
        if not parser.has_section("Screen Setup"):
            parser.add_section("Screen Setup")
        parser.set("Screen Setup", "ScreenWidth", str(gameResolution["width"]))
        parser.set("Screen Setup", "ScreenHeight", str(gameResolution["height"]))
        # The game should always be fullscreen
        parser.set("Screen Setup", "ScreenMode", "1")
        with config_file.open("w") as config:
            parser.write(config)
        with script_file.open("w") as script:
            script.write(
                f'// This file is automatically generated by eduke32Generator.py\n'
                f'bind "F12" "screenshot"\n'
                f'screenshot_dir "{SCREENSHOTS}"\n'
                f'r_showfps "{1 if system.getOptBoolean("showFPS") else 0}"\n'
                f'echo BATOCERA\n'  # Easy check when debugging
            )
        launch_args: list[str | Path] = [
            core,
            "-cfg", config_file,
            "-nologo" if system.getOptBoolean("nologo") else ""
        ]
        if core == "fury":
            launch_args += [
                "-gamegrp", rom_path.name,
                "-j", rom_path.parent,
            ]
        else:
            result = parse_args(launch_args, rom_path)
            if not result.okay:
                raise Exception(result.message)
        return Command.Command(
            array=launch_args,
            env={
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            }
        )
