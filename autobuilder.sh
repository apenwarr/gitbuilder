#!/bin/bash

DATE=$(date "+%Y%m%d")

log()
{
	(echo "$@") >&2
	(echo; echo ">>> $@") # log file
}

_run()
{
	log "Starting at: $(date)"

	log "Updating git..."
	cd src && 
	git fetch origin &&
	git checkout origin/master || return 1

	log "Cleaning..."
	git clean -n -x -d || return 2
	
	log "Building..."
	make 2>&1 || return 3
	
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

run >log.out
CODE=$?
mkdir -p out/pass out/fail
if [ "$CODE" = 0 ]; then
	echo PASS
	mv -v log.out out/pass/log-$DATE.txt
else
	echo FAIL
	mv -v log.out out/fail/log-$DATE.txt
fi

exit 0
