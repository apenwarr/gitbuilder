#!/bin/bash

DATE=$(date "+%Y%m%d")

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
	make 2>&1 || return 40
	
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

getref()
{
	(cd build && git-rev-list --no-walk "$1")
}

mkdir -p out/pass out/fail out/refs

( cd build && git remote update )

if [ -n "$*" ]; then
	branches="$*"
else
	branches=$( (cd build && git-branch -r) )
fi
for branch in $branches; do
	nicebranch=$(echo $branch | sed -e 's,.*/,,' -e 's/[^A-Za-z0-9]/_/g')
	ref=$(getref $branch)
	echo "$branch ($nicebranch) -> $ref"

	if [ ! -e "out/pass/$ref" -a ! -e "out/fail/$ref" ]; then
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
		
		echo $ref >out/refs/$nicebranch
		
		# only do one build per script invocation
		# exit $CODE
	else
		echo $ref >out/refs/$nicebranch
	fi
done

exit 0
