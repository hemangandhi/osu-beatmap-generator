
class FilePart:
    def __init__(self, name, **params):
        self.params = params
        self.name = name
    def __iter__(self):
        return iter(self.params)
    def __getitem__(self, item):
        return self.params[item]
    def __setitem__(self, item, val):
        self.params[item] = val
    def serialize(self, file):
        file.write("[{}]\n".format(self.name))
        for p in self:
            file.write("{}: {}\n".format(p, self[p]))

class CSVPart(FilePart):
    def __init__(self, name, *pts):
        FilePart.__init__(self, name)
        self.points = list(pts)
    def serialize(self, file):
        FilePart.serialize(self, file)
        for pt in self.points:
            file.write(",".join(map(str, pt)) + '\n')
    def add_row(self, idx, row):
        self.points.insert(idx, row)

def mk_beatmap(path, *parts):
    with open(path, 'w') as f:
        for p in parts:
            p.serialize(f)

def mk_default_metadata(audio_file, lead_in, mode, title, artist, map_id, map_set):
    general = FilePart("General", **{"AudioFilename": audio_file, "AudioLeadIn": lead_in, "Mode": mode})
    editor = FilePart("Editor")
    metadata = FilePart("Metadata", **{"Title": title, "Artist": artist, "Creator": "Osu! Beat Gen", "BeatmapID": map_id, "BeatmapSetID": map_set})
    #TODO: tune
    difficulty = FilePart("Difficulty")
    events = FilePart("Events")
    tp = CSVPart("Timing Points")
    colors = FilePart("Colours")
    return [general, editor, metadata, difficulty, events, tp, colors]

import numpy as np
import numpy.fft as rfft

def flat_map_file(file, split=2):
    for buf in file:
        data = np.frombuffer(buf, dtype=np.int16)
        yield from np.array_split(data, split)

def bag_notes(buf, rate):
    NOTE_TOLERANCE = 1

    data = buf
    #f is the note and p it's "volume" (I think it's actually like decibels)
    p = 20 * np.log10(np.abs(rfft.rfft(data)))
    max_p = p.max()
    f = np.linspace(0, rate/2, len(p))

    freq_to_vol = dict()
    for note, vol in zip(f, p):
        for known_note in freq_to_vol:
            if abs(known_note - note) < NOTE_TOLERANCE:
                freq_to_vol[known_note] = max(freq_to_vol[known_note], vol)
                break
        else:
            freq_to_vol[note] = vol

    return freq_to_vol, max_p


def next_hits(buf, rate, prev, prev_max_p):
    #TODO: is the number of channels a good heuristic on notes?
    P_DROPOFF = 10 #TODO: tune
    MIN_P = 0 #TODO: tune

    freq_to_vol, max_p = bag_notes(buf, rate)

    if (prev_max_p is not None and prev_max_p - max_p >= P_DROPOFF) or max_p < MIN_P:
        return max_p, [None for i in prev]

    #grab all the notes from the last state that are still playing
    sorted_notes = sorted(list(freq_to_vol.keys()), key=lambda n: freq_to_vol[n], reverse=True)
    is_still_playing = lambda i: prev[i] is not None and\
            0 <= sorted_notes.index(prev[i]) < len(prev)
    still_playing = list(filter(is_still_playing, range(len(prev))))

    chans = []
    rem_idx = 0
    for i, n in enumerate(prev):
        if i in still_playing:
            chans.append(n)
        elif n is None and rem_idx < len(sorted_notes):
            #TODO: may be add a threshold
            chans.append(sorted_notes[rem_idx])
            rem_idx += 1
        else:
            chans.append(None)
    return max_p, chans
