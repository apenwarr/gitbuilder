#!/bin/bash

mkdir -p out/pass out/fail out/ignore

( cd build && git remote update )

if [ -n "$*" ]; then
	branches="$*"
else
	branches=$( (cd build && git-branch -r) )
fi
./branches.sh | while read commit branch; do
	ref=$(./next-rev.sh $branch)
	if [ -z "$ref" ]; then
		echo "$branch: already up to date."
		continue;
	fi
	echo "Building $branch: $ref"
	./run-build.sh $ref

		
		# only do one build per script invocation
		# exit $CODE
done

exit 0
