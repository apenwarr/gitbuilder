#!/bin/bash
DIR=$(dirname $0)
cd "$DIR/build"

bisect()
{
	(git rev-list --first-parent --bisect-all "$@" ||
	 git rev-list --first-parent "$@" ) |
		while read x y; do
			[ -e ../out/pass/$x -o -e ../out/fail/$x ] && continue
			echo $x
			exit 0
		done
}

../revlist.sh "$@" | (
	pass=
	firstfail=
	fail=
	pending=
	while read commit junk; do
		if [ -e "../out/pass/$commit" ]; then
			# only a maximum of one pass is ever received
			pass=$commit
		elif [ -e "../out/fail/$commit" ]; then
			# there might be more than one fail; we want the
			# last one, so that we can figure out where things
			# started to go wrong.
			fail=$commit
			[ -n "$firstfail" ] || firstfail=$commit
		elif [ -z "$pending" -a -z "$fail" ]; then
			# and we only want the first pending build,
			# and only if it's *not* following a failed build
			pending=$commit
		fi
		last=$commit
	done
	
	if [ -n "$pending" ]; then
		# if a pending build came before the first failed build,
		# then we need to build it first.
		echo "$pending"
	elif [ -n "$fail" ]; then
		# If there were no passing tests, just use the last one as
		# a reference.
		[ -n "$pass" ] || pass=$last

		# First, we want to bisect to find the *last* failure before
		# the first pass. That is, the commit where failures were
		# introduced.
		try=$(bisect "$fail^" "^$pass")

		# But if there's nothing left to try (we tested it already),
		# let's keep building the other commits in between, just in
		# case one of the intermediate ones passes. (This can happen
		# if commits are failing for two different reasons, sigh.)
		if [ -z "$try" ]; then
			try=$(bisect "$firstfail^" "^$pass")
		fi
		if [ -n "$try" ]; then
			echo "$try"
		fi
	fi

	# if we don't print anything at all, it means there's nothing to build!
)
