#!/usr/bin/perl -w
use strict;
use CGI qw/:standard/;
use POSIX qw(strftime);

use lib ".";
use Autobuilder;

my $url = url();
my $relative = url(-relative=>1);
$url =~ s{/$relative$}{};

print "Content-Type: text/xml\n";
print "\n";

print qq{<rss version='2.0'>
	<channel>
		<title>Autobuilder results</title>
		<link>$url/</link>
		<language>en-ca</language>
		<generator>CGI</generator>
		<docs>http://blogs.law.harvard.edu/tech/rss</docs>
};

for my $branch (sort { mtime($b) cmp mtime($a) } <refs/*>) {
	next if $branch =~ /~$/;
	my $branchbase = basename($branch);

	my $commit = stripwhite(catfile($branch));
	next if -f "ignore/$commit";
	
	my $filename;
	my $failed;
	if (-f "pass/$commit") {
		$filename = "pass/$commit";
		$failed = 0;
	} elsif (-f "fail/$commit") {
		$filename = "fail/$commit";
		$failed = 1;
	} else {
		#die("No commit $commit found!\n");
		next;
	}
	
        my $longstr = find_errors($filename);
	my $codestr = ($failed ? "Error during build!" : 
		($longstr ? "Warnings found!" : "Pass."));
		
	my $logcgi = "log.cgi?log=$commit";

	my $date = strftime("%a, %d %b %Y %H:%M:%S %z",
	               localtime(mtime($filename)));
	
	print qq{
	  <item>
		<title>$branchbase: $codestr</title>
		<pubDate>$date</pubDate>
		<link>$url/$logcgi</link>
		<guid isPermaLink='true'>$url/$logcgi</guid>
		<description>$codestr\n\n$longstr</description>
	  </item>
	};
}

print "</channel></rss>";
