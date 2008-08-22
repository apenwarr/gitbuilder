#!/bin/bash
DIR=$(dirname $0)
cd "$DIR/build"

../revlist.sh "$@" | (
	pass=
	fail=
	pending=
	while read commit junk; do
		if [ -e ../out/pass/$commit ]; then
			# only a maximum of one pass is ever received
			pass=$commit
		elif [ -e ../out/fail/$commit ]; then
			# there might be more than one fail; we want the
			# last one
			fail=$commit
		elif [ -z "$pending" -a -z "$fail" ]; then
			# and we only want the first pending build,
			# and only if it's *not* following a failed build
			pending=$commit
		fi
	done
	
	# if a pending build came before the first failed build, then we need to
	# build it first.
	if [ -n "$pending" ]; then
		echo $pending
	elif [ -n "$fail" -a -n "$pass" ]; then
		git rev-list --first-parent --bisect $fail ^$pass
	elif [ -n "$fail" ]; then
		git rev-list --first-parent --bisect $fail
	fi

	# if we don't print anything at all, it means there's nothing to build!
)

