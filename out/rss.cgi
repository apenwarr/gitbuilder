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

print qq{<rss version='2.0' xmlns:atom="http://www.w3.org/2005/Atom">
	<channel>
		<title>Autobuilder results</title>
		<description>Autobuilder results</description>
		<link>$url</link>
		<atom:link href="$url/rss.cgi" rel="self" type="application/rss+xml" />
		<language>en-ca</language>
		<generator>CGI</generator>
		<docs>http://blogs.law.harvard.edu/tech/rss</docs>
};

my @all = (glob("pass/*"), glob("fail/*"));
my $i = 0;
for my $path (sort { mtime($b) cmp mtime($a) } @all) {
    last if ++$i > 10;
    my $commit = basename($path);
    my $name = git_describe($commit);
    
    my $filename;
    my $failed;
    if (-f "pass/$commit") {
	$filename = "pass/$commit";
	$failed = 0;
    } elsif (-f "fail/$commit") {
	$filename = "fail/$commit";
	$failed = 1;
    } else {
	die("No commit $commit found?!\n");
	next;
    }
    
    my $longstr = find_errors($filename);
    $longstr =~ s/\&/\&amp;/g;
    $longstr =~ s/</&lt;/g;
    
    my $codestr = ($failed ? "ERRORS" : 
	($longstr ? "WARNINGS" : "ok"));
    
    my $logcgi = "log.cgi?log=$commit";
    
    my $date = strftime("%a, %d %b %Y %H:%M:%S %z",
	localtime(mtime($filename)));
    
    print qq{
	<item>
	  <title>$codestr $name</title>
	  <pubDate>$date</pubDate>
	  <link>$url/$logcgi</link>
	  <guid isPermaLink='true'>$url/$logcgi</guid>
	  <description>$codestr\n\n$longstr</description>
	</item>
    };
}

print "</channel></rss>";