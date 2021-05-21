import subprocess

import discord
from discord.opus import Encoder as OpusEncoder


class VirtualSource(discord.FFmpegAudio):

    def __init__(self):
        args = ['-f', 'dshow', '-i', 'audio=CABLE Output (VB-Audio Virtual Cable)', '-loglevel', 'warning', '-ar', '48000', '-f', 's16le', 'pipe:1']
        subprocess_kwargs = {
            'stdin': subprocess.DEVNULL
        }
        print(args)
        super().__init__(source='audio=CABLE Output (VB-Audio Virtual Cable)', args=args, **subprocess_kwargs)
    
    def read(self):
        ret = self._stdout.read(OpusEncoder.FRAME_SIZE)
        if len(ret) != OpusEncoder.FRAME_SIZE:
            return b''
        return ret

    def is_opus(self):
        return False
