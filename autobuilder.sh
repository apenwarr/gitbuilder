#!/bin/bash
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

did_something=1
while [ -n "$did_something" ]; do
	( cd build && 
	  git remote show | xargs git remote prune && 
	  git remote update )
	did_something=
	for branch in $(./branches.sh); do
		ref=$(./next-rev.sh $branch)
		if [ -z "$ref" ]; then
			echo "$branch: already up to date."
			continue;
		fi
		if [ -e "out/pass/$ref" -o -e "out/fail/$ref" ]; then
			echo "$branch: weird, already built $ref!"
			continue
		fi
		did_something=1
		echo "Building $branch: $ref"
		set -m
		./runtee out/log ./run-build.sh $ref &
		XPID=$!
		trap "echo 'Killing (SIGINT)';  kill -TERM -$XPID; exit 1" SIGINT
		trap "echo 'Killing (SIGTERM)'; kill -TERM -$XPID; exit 1" SIGTERM
		wait; wait
	done
	
	sleep 5
done

exit 0
