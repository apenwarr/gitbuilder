## gitbuilder aggregator

This is a nicer and more cleaned up version of the gitbuilder.cgi script
http://tracker.newdream.net/issues/1655.

To use, copy the _js/url.js.in_ script to _js/urls.js_ customise this
script with your own urls. The serverUrl should point to a server side
script which acts as a proxy for the javascript.

## Issues

* There are some minor issues with ordering of the table, turn on async:
true will make the page run/load faster but it does not guarantee the
ordering.

* The hide/show buttons don't fully function as one would expect.

* Cross-domain scripting issues. If all the data files are stored on
the one machine there is no problem. If the urls.js script has a number
of different domains then a proxy is needed. The supplied request.php
file is a very simplistic implementation that does no checking at all.
