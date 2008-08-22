#!/bin/bash

mkdir -p out/pass out/fail out/ignore

( cd build && git remote update )

if [ -n "$*" ]; then
	branches="$*"
else
	branches=$( (cd build && git-branch -r) )
fi

did_something=1
while [ -n "$did_something" ]; do
	did_something=
	for branch in $(./branches.sh | sed 's/^[0-9a-f]* //'); do
		ref=$(./next-rev.sh $branch)
		if [ -z "$ref" ]; then
			echo "$branch: already up to date."
			continue;
		fi
		did_something=1
		echo "Building $branch: $ref"
		./run-build.sh $ref
	done
	
	sleep 5
done

exit 0
