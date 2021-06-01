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

# temporary? Add a go compiler to our PATH in case the build script doesn't
# extract one like it should.
# TODO(apenwarr): Maybe make this only apply for older commits?
export PATH=$PATH:$HOME/.cache/tailscale-go/bin

git checkout origin/main -- git-fix-modules.sh git-stash-all.sh
./git-fix-modules.sh 2>fix-modules.err || true
if [ -x "git-stash-all.sh" ]; then
	./git-stash-all.sh
fi

git checkout origin/main -- go.toolchain.cmd.do check-redo-dirs.do

if [ -n "$(git rev-list e2a65fda59e9056b7 ^HEAD | head -n1)" ]; then
	# predates the commit that fixed mobileconfig keychain access.
	# Without this, it was broken on headless macOS and tests fail,
	# which is not that interesting.
	rm -f mobileconfig/*_test.go
fi

if [ -e "test.do" ]; then
	if [ -e "allconfig.do" ]; then
		$REDO -j10 allconfig
	fi
	
	# Need to build these sequentially since xcode can't handle being
	# executed in parallel, sigh.
	for d in archive-macos archive-ios test-ios-size; do
		if [ -e "xcode/$d.do" ]; then
			../maxtime 120 $REDO xcode/$d
		fi
	done
	
	# Can't actually redo 'test' because the xcode tests require
	# a macOS GUI to run. Hmm...
	../maxtime 1800 $REDO -j8 qtest world
else
	echo "No interesting .do files, skipping." >&2
fi

exit 0
