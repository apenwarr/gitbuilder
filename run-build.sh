#!/bin/bash

if [ -z "$1" ]; then
	echo "Usage: $0 <commitid>" >&2
	echo "  Build the tree in build/ as of the given commitid."
	exit 1
fi

ref="$1"

mkdir -p out/fail out/pass
chmod 777 out/fail

log()
{
	(echo; echo ">>> $@") # log file
}

_run()
{
	log "Starting at: $(date)"
	commit="$1"
	log "Commit: $commit"
	
	cd build || return 10

	log "Removing submodules..."
	git submodule foreach git clean -q -f -x -d &&
	git submodule deinit --all --force &&
	git ls-files --others | (
		# 'git clean' refuses to delete sub-repositories (anything containing
		# a .git dir) and there's no way to change its mind, so we occasionally
		# have to do it the hard way.
		while read -r name; do
			rm -rf "./$name"
		done
	) || return 15

	log "Switching git branch..."
	git checkout --detach &&
	git reset --hard "$commit" 2>&1 | grep -v 'warning:' || return 20
	
	log "Cleaning..."
	git clean -q -f -x -d || return 30
	
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

go()
{
	echo $ref >out/.doing
	rm -f out/pass/$ref out/fail/$ref
	run $ref
	CODE=${PIPESTATUS[0]}
	
	# This whole program's output is being dumped in log.out.  Unix
	# lets us rename open files, so we can do that here.
	# FIXME: it would be cleaner if the caller renamed the output
	# file based on our result code, however.
	if [ "$CODE" = 0 ]; then
		echo PASS
		mv -v out/log out/pass/$ref
	else
		echo FAIL
		mv -v out/log out/fail/$ref
	fi

	echo "Done: $ref"
	rm -f out/.doing
	return $CODE
}

set -m
go &
XPID=$!
trap "echo 'Killing (SIGINT)';  kill -TERM -$XPID; exit 1" SIGINT
trap "echo 'Killing (SIGTERM)'; kill -TERM -$XPID; exit 1" SIGTERM
wait $XPID
# return exit code from previous command
