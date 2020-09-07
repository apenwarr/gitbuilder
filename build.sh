#!/bin/bash -x
#
# Copy this file to build.sh so that gitbuilder can run it.
#
# What happens is that gitbuilder will checkout the revision of your software
# it wants to build in the directory called gitbuilder/build/.  Then it
# does "cd build" and then "../build.sh" to run your script.
#
# You might want to run ./configure here, make, make test, etc.
#

#../maxtime 1800 ./do out/native/oss/cmd/tailscaled/tailscaled

set -e

if [ -x "do" ]; then
	REDO=./do
else
	export PATH=$HOME/src/redo/bin:$PATH
	REDO=redo
fi

git checkout origin/main -- git-fix-modules.sh git-stash-all.sh
./git-fix-modules.sh 2>fix-modules.err || true
if [ -x "git-stash-all.sh" ]; then
	./git-stash-all.sh
fi

git checkout origin/main -- go.toolchain.cmd.do check-redo-dirs.do

if [ -e "native.do" ]; then
	if [ -e "allconfig.do" ]; then
		$REDO -j10 allconfig
	fi
	$REDO native
else
	echo "No interesting .do files, skipping." >&2
fi

exit 0
