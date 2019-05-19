#!/bin/bash

SHM="$1"
SHM_PATH="/dev/shm"

if [ -z $SHM ]; then
    exit 1
fi

feeder () {
    if ! ./main.py $SHM; then
        rm "$SHM_PATH$SHM"
    fi
}

wait_for_file() {
    if ! [ -f "$1" ]; then
        (echo $BASHPID; inotifywait -m "$(dirname "$1")" -e create) | {
            read notifier
            while read path action file; do
                echo $path $action $file
                if [ "$file" == "$(basename "$1")" ]; then
                    kill $notifier
                    break
                fi
            done
        }
    fi
}

while true; do
    wait_for_file "$SHM_PATH$SHM"
    feeder
done
