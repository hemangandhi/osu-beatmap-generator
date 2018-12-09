
class FilePart:
    def __init__(self, part_name, **params):
        self.params = params
        self.name = name
    def __iter__(self):
        return iter(self.params)
    def __getitem__(self, item):
        return self.params[item]
    def __setitem__(self, item, val):
        self.params[item] = val
    def serialize(self, file):
        file.writeLine("[{}]".format(self.name))
        for p in self:
            file.writeLine("{}: {}".format(p, self[p]))

class CSVPart(FilePart):
    def __init__(self, name, *pts):
        super(self, name)
        self.points = list(pts)
    def serialize(self, file):
        super.serialize(self, file)
        for pt in self.points:
            file.writeLine(",".join(map(str, pt)))
    def add_row(self, idx, row):
        self.points.insert(idx, row)

def mk_beatmap(path, *parts):
    with open(path, 'w') as f:
        for p in parts:
            p.serialize(f)

import numpy as np
import numpy.fft as rfft

def next_hits(buf, rate, duration, channels, prev, prev_max_p):
    #TODO: is the number of channels a good heuristic on notes?
    P_DROPOFF = 100 #TODO: tune
    MIN_P = 100 #TODO: tune

    data = np.frombuffer(buf, dtype=np.int16)
    #f is the note and p it's "volume" (I think it's actually like decibels)
    p = 20 * np.log10(np.abs(rfft.rfft(data)))
    #TODO: standardise length?
    f = np.linspace(0, rate/2, len(p))
    freq_to_vol = dict(zip(f, p))

    max_p = p.max()
    if prev_max_p - max_p >= P_DROPOFF or max_p < MIN_P:
        return max_p, [None for i in range(channels)]

    #grab all the notes from the last state that are still playing
    still_playing = filter(lambda i: freq_to_vol[i] > MIN_P, range(channels))
