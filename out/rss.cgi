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

my $title = "Autobuilder";
my $project_name = project_name();
if ($project_name) {
    # use the shortest name possible because some RSS readers don't leave much
    # room for the name.  Also make sure the critical text comes at the start.
    $title = "$project_name Builder";
}

print qq{<rss version='2.0' xmlns:atom="http://www.w3.org/2005/Atom">
	<channel>
		<title>$title</title>
		<description>Autobuilder results via gitbuilder</description>
		<link>$url</link>
		<atom:link href="$url/rss.cgi" rel="self" type="application/rss+xml" />
		<language>en-ca</language>
		<generator>CGI</generator>
		<docs>http://blogs.law.harvard.edu/tech/rss</docs>
};

my @all = (glob("pass/*"), glob("fail/*"));
my $i = 0;
for my $path (sort { mtime($b) cmp mtime($a) } @all) {
    last if ++$i > 20;
    my $commit = basename($path);
    my $name = git_describe($commit);
    $name =~ s{^remotes/}{};
    $name =~ s{^origin/}{};
    
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
    
    my ($warnmsg, $errs) = find_errors($filename);
    my $codestr = $warnmsg;
    $codestr =~ s/([A-Z])[a-z]*/$1/g;
    
    my $longstr = "$commit\n\n" . squish_log($filename);
    $longstr =~ s/\&/\&amp;/g;
    $longstr =~ s/</&lt;/g;
    
    my $logcgi = "log.cgi?log=$commit";
    
    my $mtime = mtime($filename);
    my $date = strftime("%a, %d %b %Y %H:%M:%S %z",
	localtime($mtime));
    
    print qq{
	<item>
	  <title>$codestr: $name</title>
	  <pubDate>$date</pubDate>
	  <link>$url/$logcgi</link>
	  <guid isPermaLink='true'>$url/$logcgi#$mtime</guid>
	  <description>$warnmsg\n\n$longstr</description>
	</item>
    };
}

print "</channel></rss>";
