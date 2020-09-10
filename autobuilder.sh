#!/bin/bash
set -e
DIR="$(dirname $0)"
cd "$DIR"

if [ ! -d build/. ]; then
	echo >&2
	echo "We need a directory named build/ in this directory." >&2
	echo "You should 'git clone' the project you want to test," >&2
	echo "like this:" >&2
	echo >&2
	echo "    git clone /path/to/myproject.git build" >&2
	echo >&2
	exit 2
fi

if [ -e build.sh -a ! -x build.sh ]; then
	chmod a+x build.sh
fi

if [ ! -x build.sh ]; then
	echo >&2
	echo "We need an executable file named build.sh in this directory" >&2
	echo "in order to run the autobuilder." >&2
	echo >&2
	echo "Try copying build.sh.example as a starting point." >&2
	echo >&2
	exit 1
fi

mkdir -p out/pass out/fail out/ignore out/errcache
chmod a+w out/errcache

build() {
	local ref="$1"

	if [ -z "$ref" ]; then
		echo "$branch: already up to date."
		return
	fi
	if [ -e "out/pass/$ref" -o -e "out/fail/$ref" ]; then
		return
	fi
	did_something=1
	echo "Building $branch: $ref"
	set -m
	./runtee out/log ./run-build.sh $ref || true &
	XPID=$!
	trap "echo 'Killing (SIGINT)';  kill -TERM -$XPID; exit 1" SIGINT
	trap "echo 'Killing (SIGTERM)'; kill -TERM -$XPID; exit 1" SIGTERM
	wait; wait
}

did_something=1
while [ -n "$did_something" ]; do
	( cd build && 
	  git remote show | ../maxtime 60 xargs git remote prune &&
	  ../maxtime 60 git remote update )
	did_something=

	# Build top of every branch first of all
	branches=$(./branches.sh)
	for branch in $branches; do
		xref=$(cd build && git rev-parse "$branch~0")
		build "$xref"
	done

	# Only then do we try bisecting other branches
	for branch in $branches; do
		xref=$(./next-rev.sh $branch)
		build "$xref"
	done
	
	sleep 5
done

exit 0
