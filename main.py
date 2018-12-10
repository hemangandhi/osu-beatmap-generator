import subprocess as proc
from functools import reduce

import audioread as au

import beatmap as bm

def handle_file(path, out_path):
    with au.audio_open(path) as f:
        chan = f.channels
        rate = f.samplerate
        duration = f.duration
        #TODO: it might make sense to concat the buffers, depending on the time/buffer...
        note_states = reduce(lambda tbm, buf: tbm + bm.next_beatmap(buf, rate, tbm[-1][1], tbm[-1][0]), [(None, [None for i in range(chan)])], f)

    just_notes = [n[1] for n in note_states]
    sample_len = duration / len(just_notes)
    time = sample_len / 2
    hits = []
    down_hits = [None for i in range(chan)]
    for notes in just_notes[1:]:
        for i, n in enumerate(notes):
            #this heavily assumes that something isn't held down twice "in a row"
            #for different notes.
            if down_hits[i] is None and n is not None:
                down_hits[i] = time
            elif down_hits[i] is not None and n is None:
                hits.append((i, down_hits[i], time))
                down_hits[i] = None
            time += sample_len

    col_width = 512/chan
    beatmap_hits = map(lambda x: (x[0] * col_width + col_width / 2, 0, x[1], 128, 0, x[2]), hits)
    hit_objs = bm.CSVPart("Hit Objects", *beatmap_hits)
    default = bm.mk_default_metadata(path, 0, 3, "Auto beatmap for:" + path, "", "", "")
    bm.mk_beatmap(out_path, default + [hit_objs])
