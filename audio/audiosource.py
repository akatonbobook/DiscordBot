import subprocess

import discord
from discord.opus import Encoder as OpusEncoder



class MyPCMVolumeTransformer(discord.PCMVolumeTransformer):

    def __init__(self, original, volume=1.0):
        super().__init__(original, volume)
        self.original = original
