#!/usr/bin/perl
# Imported from http://tracker.newdream.net/issues/1655
# Author: Sage Weil
#
# It's just a quick perl hack. What it really should do is make javascript
# and <div>s to fetch the results for each builder in parallel.
#
print "Content-type: text/html\n\n";

my @urls = (
        'http://ceph.newdream.net/gitbuilder-amd64/',
        'http://ceph.newdream.net/gitbuilder-i386/',
        'http://ceph.newdream.net/gitbuilder-deb-amd64/',
#        'http://ceph.newdream.net/gitbuilder-deb-i386/',
        'http://ceph.newdream.net/gitbuilder-gcov-amd64/',
        'http://ceph.newdream.net/gitbuilder-notcmalloc-amd64/',
        'http://ceph.newdream.net/gitbuilder-kernel-amd64/',

);

sub summarize_gitbuilder {
        my ($url, $raw) = @_;
        my ($b) = $raw =~ /(<div id="most_recent">.*)/;
        my ($c) = split(/<\/div>/, $b);
        $c =~ s/Most Recent://;
        $c =~ s/<a href="#/<a href="$url#/g;
        return $c . '</div>';
}

print "<html>\n";
print "<head>\n";
print "<title>Ceph gitbuilders</title><link rel=\"stylesheet\" type=\"text/css\" href=\"gitbuilder.css\" />";
print "<META HTTP-EQUIV=\"REFRESH\" CONTENT=\"600\">\n";
print "</head>\n";
print "<body>";
print "<table>";
for my $url (@urls) {
        my $raw = `curl -s $url`;
        my $summary = summarize_gitbuilder($url, $raw);
        #print $summary;
        print "<tr><td align=left id=\"most_recent\" nowrap=\"nowrap\"><a href=\"$url\">$url</a></td><td>$summary</td></tr>\n";
}
print "</table>";
print "</body></html>\n";
