#!/bin/bash

DATE=$(date "+%Y%m%d")

n=0
while [ $n = 0 -o -e "$LOG" -o -e "$RESULT" ]; do
	n=$(($n + 1))
	LOG="out/log/log.$DATE.$n"
	RESULT="out/result/result.$DATE.$n"
	BUILDDIR=build.tmp
done


log()
{
	(echo "$@") >&2
	(echo; echo ">>> $@") # log file
}

result()
{
	(echo "Result: " "$@") >&2
	(echo "$@") >&30
}

run()
{
	log "Starting at: $(date)"
	log "Log file is: '$LOG'"
	log "Result file is: '$RESULT'"

	log "Updating pristine subversion..."	
	svn cleanup .
	svn cleanup pristine
	svn cleanup pristine/*
	svn up pristine
	
	if [ -z "$DONTRECOPY" ]; then
		log "Deleting old $BUILDDIR..."
		rm -rf "$BUILDDIR"
		
		log "Copying to $BUILDDIR..."
		cp -a pristine "$BUILDDIR"
	fi
	
	log "Looking for projects..."
	cd "$BUILDDIR"
	for proj in */*.bpg; do
		DIR="$(dirname "$proj")"
		BASE="$(basename "$proj")"
		
		log "Building project '$BASE' in '$DIR'"
		
		(
			cd "$DIR"
			errfile="$(basename "$BASE" .bpg).err"
			if [ -r "$BASE" ]; then
				delphi32.exe /b "$BASE"
				code=$?
				log "Error code was $code."
				if [ "$code" = 0 ]; then
					codestr="ok"
				else
					codestr=$(tail -1 "$errfile")
				fi
				result "$code $proj  $codestr"
			fi
			
			echo
			echo "Log listing:"
			echo
			cat "$errfile"
			echo
			echo "End of log listing."
		)
	done
	
	log "Done at: $(date)"
}

run >>"$LOG" 30>>"$RESULT"

