# `fbterm` background generator

This program cooperates with [my version](https://github.com/Goheeca/fbterm/releases) of `fbterm`, in which the background is grabbed from a shared memory segment and it's rendered with `SIGIO`.

## How to use

`python3 main.py PATH_TO_BACKGROUND [ARG]...`

* `PATH_TO_BACKGROUND` -- the same as in the environment variable `FBTERM_BACKGROUND_IMAGE_PATH`
* `ARG`s (arbitrary) -- these arguments are available in the `setup()` method in `__feed__.py`
