# VELMARA — The Poster for a Place That Isn't There

[![make.fun](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539)
[![rank](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539/Djebrix/poster-place-that-isnt-there/rank.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539)
[![reward](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539/Djebrix/poster-place-that-isnt-there/reward.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539)

A travel poster for **Velmara**, a place that does not exist — a chain of
floating isles above a sea of cloud, where the sea falls *upward*.

## The place

Velmara's one landmark is the white tower on the largest isle, its gold spire
catching the last light of a sun that never quite sets. Waterfalls arc off
the islands' edges and rise into the sky. Below, nothing but cloud.

## The program

`main.py` (Python 3.13, Pillow only) draws the whole poster in code — sky
gradient, low sun, floating islands with terraced rock, the tower, upward
waterfalls, cloud sea, and the set type — and writes one image to
`/output/entry.png` (1024×1024 PNG, well under 1 MiB).

No network, no downloaded or copied images, fully deterministic: two runs
produce byte-identical output.

## Run it

```sh
python3 main.py
```

Competition: https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539
