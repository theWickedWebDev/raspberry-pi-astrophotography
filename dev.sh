#!/usr/bin/env bash
find . -name '*.py' | entr -cr python3 src/main.py


# for new files, you can make it like:


# while true; do find . -name '*.py' | entr -cdr python src/main.py --virtual; done
 
# but it's not perfect... it can be hard to make it stop if you do it that way
# with the -d and without the while might be an ok compromise
# with the -d, entr will watch for new files and just exit if it sees one