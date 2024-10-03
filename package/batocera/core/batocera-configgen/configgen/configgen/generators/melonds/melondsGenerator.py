from __future__ import annotations

import codecs
from typing import TYPE_CHECKING, Final

from ... import Command
from ...batoceraPaths import BIOS, CHEATS, CONFIGS, ROMS, SAVES, mkdir_if_not_exists
from ...utils.logger import get_logger
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext

eslog = get_logger(__name__)

_MELONDS_SAVES: Final = SAVES / "melonds"
_MELONDS_ROMS: Final = ROMS / "nds"
_MELONDS_CHEATS: Final = CHEATS / "melonDS"
_MELONDS_CONFIG: Final = CONFIGS / "melonDS"

class MelonDSGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "melonds",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"] }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        # Verify the save path exists
        mkdir_if_not_exists(_MELONDS_SAVES)
        # Verify the cheat path exist
        mkdir_if_not_exists(_MELONDS_CHEATS)
        # Config path
        mkdir_if_not_exists(_MELONDS_CONFIG)
        # Config file
        configFileName = _MELONDS_CONFIG / "melonDS.ini"
        f = codecs.open(str(configFileName), "w", encoding="utf_8_sig")

        # [Set config defaults]
        f.write("WindowWidth={}\n".format(gameResolution["width"]))
        f.write("WindowHeight={}\n".format(gameResolution["height"]))
        f.write("WindowMax=1\n")
        # Hide mouse after 5 seconds
        f.write("MouseHide=1\n")
        f.write("MouseHideSeconds=5\n")
        # Set bios locations
        f.write("ExternalBIOSEnable=1\n")
        f.write(f"BIOS9Path={BIOS / 'bios9.bin'}\n")
        f.write(f"BIOS7Path={BIOS / 'bios7.bin'}\n")
        f.write(f"FirmwarePath={BIOS / 'firmware.bin'}\n")
        f.write(f"DSiBIOS9Path={BIOS / 'dsi_bios9.bin'}\n")
        f.write(f"DSiBIOS7Path={BIOS / 'dsi_bios7.bin'}\n")
        f.write(f"DSiFirmwarePath={BIOS / 'dsi_firmware.bin'}\n")
        f.write(f"DSiNANDPath={BIOS / 'dsi_nand.bin'}\n")
        # Set save locations
        f.write(f"DLDIFolderPath={_MELONDS_SAVES}\n")
        f.write(f"DSiSDFolderPath={_MELONDS_SAVES}\n")
        f.write(f"MicWavPath={_MELONDS_SAVES}\n")
        f.write(f"SaveFilePath={_MELONDS_SAVES}\n")
        f.write(f"SavestatePath={_MELONDS_SAVES}\n")
        # Cheater!
        f.write(f"CheatFilePath={_MELONDS_CHEATS}\n")
        # Roms
        f.write(f"LastROMFolder={_MELONDS_ROMS}\n")
        # Audio
        f.write("AudioInterp=1\n")
        f.write("AudioBitrate=2\n")
        f.write("AudioVolume=256\n")
        # For Software Rendering
        f.write("Threaded3D=1\n")

        # [User selected options]
        # MelonDS only has OpenGL or Software - use OpenGL if not selected
        if system.isOptSet("melonds_renderer"):
            f.write("3DRenderer={}\n".format(system.config["melonds_renderer"]))
        else:
            f.write("3DRenderer=1\n")
        if system.isOptSet("melonds_framerate"):
            f.write("LimitFPS={}\n".format(system.config["melonds_framerate"]))
        else:
            f.write("LimitFPS=1\n")
        if system.isOptSet("melonds_resolution"):
            f.write("GL_ScaleFactor={}\n".format(system.config["melonds_resolution"]))
        else:
            f.write("GL_ScaleFactor=1\n")
        if system.isOptSet("melonds_polygons"):
            f.write("GL_BetterPolygons={}\n".format(system.config["melonds_polygons"]))
        else:
            f.write("GL_BetterPolygons=0\n")
        if system.isOptSet("melonds_rotation"):
            f.write("ScreenRotation={}\n".format(system.config["melonds_rotation"]))
        else:
            f.write("ScreenRotation=0\n")
        if system.isOptSet("melonds_screenswap"):
            f.write("ScreenSwap={}\n".format(system.config["melonds_screenswap"]))
        else:
            f.write("ScreenSwap=0\n")
        if system.isOptSet("melonds_layout"):
            f.write("ScreenLayout={}\n".format(system.config["melonds_layout"]))
        else:
            f.write("ScreenLayout=0\n")
        if system.isOptSet("melonds_screensizing"):
            f.write("ScreenSizing={}\n".format(system.config["melonds_screensizing"]))
        else:
            f.write("ScreenSizing=0\n")
        if system.isOptSet("melonds_scaling"):
            f.write("IntegerScaling={}\n".format(system.config["melonds_scaling"]))
        else:
            f.write("IntegerScaling=0\n")
        # Cheater!
        if system.isOptSet("melonds_cheats"):
            f.write("EnableCheats={}\n".format(system.config["melonds_cheats"]))
        else:
            f.write("EnableCheats=0\n")
        if system.isOptSet("melonds_osd"):
            f.write("ShowOSD={}\n".format(system.config["melonds_osd"]))
        else:
            f.write("ShowOSD=1\n")
        if system.isOptSet("melonds_console"):
            f.write("ConsoleType={}\n".format(system.config["melonds_console"]))
        else:
            f.write("ConsoleType=0\n")

        # Map controllers
        melonDSMapping = {
        "a":        "Joy_A",
        "b":        "Joy_B",
        "select":   "Joy_Select",
        "start":    "Joy_Start",
        "right":    "Joy_Right",
        "left":     "Joy_Left",
        "up":       "Joy_Up",
        "down":     "Joy_Down",
        "pagedown": "Joy_R",
        "pageup":   "Joy_L",
        "x":        "Joy_X",
        "y":        "Joy_Y"
        }

        val = -1
        for controller, pad in sorted(playersControllers.items()):
            # Only use Player 1 controls
            if pad.player != "1":
                continue
            for index in pad.inputs:
                input = pad.inputs[index]
                if input.name not in melonDSMapping:
                    continue
                option = melonDSMapping[input.name]
                # Workaround - SDL numbers?
                val = input.id
                if val == "0":
                    if option == "Joy_Up":
                        val = 257
                    elif option == "Joy_Down":
                        val = 260
                    elif option == "Joy_Left":
                        val = 264
                    elif option == "Joy_Right":
                        val = 258
                eslog.debug(f"Name: {option} - Var: {val}")
                f.write(f"{option}={val}\n")
        # Always set ID to 0
        f.write("JoystickID=0\n")

        # Now write the ini file
        f.close()

        commandArray = ["/usr/bin/melonDS", "-f", rom]
        return Command.Command(array=commandArray, env={"XDG_CONFIG_HOME":CONFIGS, \
            "XDG_DATA_HOME":SAVES, "QT_QPA_PLATFORM":"xcb"})
