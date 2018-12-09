
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
import numpy.rfft as rfft

def next_hits(buf, rate, duration, channels, prev):
    data = np.frombuffer(buf, dtype=np.int16)
    p = 20 * np.log10(np.abs(rfft.rfft(data)))
    f = np.linspace(0, rate/2, len(p))
    sorted_idx = sorted(list(range(len(p))), key = lambda i: p[i])
    sorted_f = [f[i] for i in sorted_idx]

    pop_idx = 0
    new_chans = []
    for channel, note in enumerate(prev):
        if note == None:
            new_chans.append(sorted_idx[pop_idx])
            pop_idx += 1
