#!/bin/bash
 
for i in /root/*.sh; do
        BASENAME=$(basename "$i")
        if [[ ! "$BASENAME" =~ ^[0-9] ]]; then
                continue
        fi
        if [[ -x "$i" ]]; then
                "$i"
        fi
done
