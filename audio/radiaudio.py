import subprocess

import discord
from discord.opus import Encoder as OpusEncoder

import src.radiko as radiko


class RadiSource(discord.FFmpegAudio):

    def __init__(self, identifier):
        self.client = radiko.Radiko()
        source = self.client.get_stream(identifier)
        args = ['-i', source, '-f', 's16le', '-ac', '2', '-loglevel', 'warning', 'pipe:1']
        subprocess_kwargs = {
            'stdin': subprocess.DEVNULL
        }
        super().__init__(source, args=args, **subprocess_kwargs)

    def read(self):
        ret = self._stdout.read(OpusEncoder.FRAME_SIZE)
        if len(ret) != OpusEncoder.FRAME_SIZE:
            return b''
        return ret

    def is_opus(self):
        return False

    def select(self, identifier):
        """局を選択する関数
        """
        self.client.select_station(identifier)