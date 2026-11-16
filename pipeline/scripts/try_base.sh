#!/bin/bash
# try_base.sh O_SLUG BASE_SLUG : lyrics from released song, align, report
cd /home/claude/songs/$1 || exit 1
[ -f lyrics.txt ] || { echo "# $(sed -n "s/^[0-9]*\t$1\t[^\t]*\t//p" ../list.tsv) - from released lyrics, checked against vocal"; grep -v '^#' ../$2/lyrics.txt | sed 's/^@[0-9.]* //'; } > lyrics.txt
python3 /home/claude/scripts/align.py lyrics.txt words_mix.json,words_voc.json aligned.json 2>&1 | head -1
python3 /home/claude/scripts/align.py lyrics.txt words_mix.json,words_voc.json aligned.json 2>&1 | grep -E "^ +[0-9]" | awk '{d=$2-$1; if (d>9 || d<0.5) n++} END{print "odd lines:", n+0, "of", NR}'
