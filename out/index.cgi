#!/usr/bin/perl -w
use strict;
use CGI qw/:standard *table start_ul/;
use POSIX qw(strftime);

use lib ".";
use Autobuilder;

print header, start_html(
	-title => "Autobuilder results",
	-style => {-src => "index.css"}
);

print Link({-rel=>"alternate", -title=>"Autobuilder results",
	-href=>"rss.cgi", -type=>"application/rss+xml"});

print h1("Autobuilder results");

print start_table();
print Tr(th("Branch"), th("Date"), th("Commit"), th("Result"), th("Details"));

for my $branch (sort <refs/*>) {
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
	
	my ($dev,$ino,$mode,$nlink,$uid,$gid,$rdev,$size,
	    $atime,$mtime,$ctime,$blksize,$blocks) = stat($filename)
	    	or die("stat $filename: $!\n");

	my $codestr = ($failed ? "Error during build!" : 
		(find_errors($filename) ? "Warnings found!" : "Pass."));
		
	my $logcgi = "log.cgi?log=$commit";

	print Tr(td($branchbase),
		 td(strftime("%Y-%m-%d", localtime($mtime))),
		 td(shorten($commit, 7)),
		 td({bgcolor=>($failed ? "#ff6666" : "#66ff66")},
		    $failed ? b("FAIL") : "ok"),
		 td($codestr . " " . a({-href=>$logcgi}, "(Log)")));
}

print end_table();
exit 0;
