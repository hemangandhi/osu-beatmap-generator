import subprocess as proc
from functools import reduce

import audioread as au

import beatmap as bm

def handle_file(path):
    with au.audio_open(path) as f:
        chan = f.channels
        rate = f.samplerate
        duration = f.duration
        reduce(lambda bm, buf: next_beatmap(bm, buf, chan, rate, duration), [], f)
