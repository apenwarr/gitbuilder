#!/bin/bash

if [ -z "$1" ]; then
	echo "Usage: $0 <commitid>" >&2
	echo "  Build the tree in build/ as of the given commitid."
	exit 1
fi

ref="$1"

mkdir -p out/fail out/pass

log()
{
	# (echo "$@") >&2
	(echo; echo ">>> $@") # log file
}

_run()
{
	log "Starting at: $(date)"
	commit="$1"
	log "Commit: $commit"
	
	cd build || return 10

	log "Switching git branch..."
	git checkout "$commit" &&
	git reset --hard HEAD || return 20
	
	log "Cleaning..."
	git clean -f -x -d || return 30
	
	log "Building..."
	../build.sh 2>&1 || return 40
	
	log "Done at: $(date)"
	return 0
}

run()
{
	( _run "$@" )
	CODE=$?
	log "Result code: $CODE"
	return $CODE
}

run $ref | perl -pe 's/\r/\n/g; s/\n+/\n/g;' \
	| grep -v '^[-\\:A-Za-z0-9_().]* *$' \
	| tee log.out
CODE=${PIPESTATUS[0]}
if [ "$CODE" = 0 ]; then
	echo PASS
	mv -v log.out out/pass/$ref
else
	echo FAIL
	mv -v log.out out/fail/$ref
fi
