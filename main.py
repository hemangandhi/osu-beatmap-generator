import subprocess as proc
from functools import reduce

import audioread as au

import beatmap as bm

def handle_file(path, out_path, channels):
    with au.audio_open(path) as f:
        chan = channels or f.channels
        rate = f.samplerate
        duration = f.duration * 1000

        def reducer(tbm, buf):
            print(tbm[-1])
            return tbm + [bm.next_hits(buf, rate, tbm[-1][1], tbm[-1][0])]
        #TODO: it might make sense to concat the buffers, depending on the time/buffer...
        note_states = reduce(reducer, bm.flat_map_file(f), [(None, [None for i in range(chan)])])

    just_notes = [n[1] for n in note_states]
    sample_len = duration / len(just_notes)
    print(sample_len)
    print(1/sample_len)
    time = sample_len / 2
    hits = []
    down_hits = [None for i in range(chan)]
    for notes in just_notes[1:]:
        for i, n in enumerate(notes):
            #this heavily assumes that something isn't held down twice "in a row"
            #for different notes.
            if down_hits[i] is None and n is not None:
                down_hits[i] = int(time)
            elif down_hits[i] is not None and n is None:
                hits.append((i, down_hits[i], int(time)))
                down_hits[i] = None
            time += sample_len

    col_width = 512/chan
    beatmap_hits = map(lambda x: (int(x[0] * col_width + col_width / 2), 0, x[1], 128, 0, x[2]), hits)
    hit_objs = bm.CSVPart("Hit Objects", *beatmap_hits)
    default = bm.mk_default_metadata(path, 0, 3, "Auto beatmap for " + path, "", "", "")
    bm.mk_beatmap(out_path, *(default + [hit_objs]))

if __name__ == "__main__":
    import sys
    handle_file("tests/a-ha - Take On Me (Official Music Video).mp3", "out.osu", sys.argv[1] if len(sys.argv) >= 2 else 4)
