from __future__ import annotations

from typing import TYPE_CHECKING

from ... import Command, controllersConfig
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext

class OdcommanderGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        commandArray = ["od-commander"]

        return Command.Command(array=commandArray,env={
            "SDL_GAMECONTROLLERCONFIG": controllersConfig.generateSdlGameControllerConfig(playersControllers)
        })

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "odcommander",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"] }
        }
