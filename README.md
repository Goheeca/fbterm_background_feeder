# `fbterm` background generator

This program cooperates with [my version](https://github.com/Goheeca/fbterm/releases) of `fbterm`, in which the background is grabbed from a shared memory segment and it's rendered with `SIGIO`.

## How to use

`python3 main.py PATH_TO_BACKGROUND [PID]`

* `PATH_TO_BACKGROUND` -- the same as in the environment variable `FBTERM_BACKGROUND_IMAGE_PATH`
* `PID` (optional) -- the pid of the fbterm instance; if it's not provided, it's read from the shared memory where it's initially placed by `fbterm`.
