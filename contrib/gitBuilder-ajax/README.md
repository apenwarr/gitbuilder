## gitbuilder aggregator

This is a nicer and more cleaned up version of the gitbuilder.cgi script
http://tracker.newdream.net/issues/1655.

## Issues

* There are some minor issues with ordering of the table, turn on async:
true will make the page run/load faster but it does not guarantee the
ordering.

* The hide/show buttons don't fully function as one would expect.

* Cross-domain scripting issues. If all the data files are stored on
the one machine there is no problem. If the urls.js script has a number
of different domains then a proxy is needed.
