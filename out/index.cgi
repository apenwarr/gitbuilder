#!/usr/bin/perl -w
use strict;
use CGI qw/:standard *table start_ul/;

use lib ".";
use Autobuilder;

print header, start_html("Autobuilder results");

print Link({-rel=>"alternate", -title=>"Autobuilder results",
	-href=>"rss.cgi", -type=>"application/rss+xml"});

print h1("Autobuilder results");

print start_table();
print Tr(th("Branch"), th("Commit"), th("Result"), th("Details"));

my $rows = 0;

my @ = split("\n", `cat index`);

for my $
for my $filename (sort { $b cmp $a } (<pass/*>, <fail/*>)) {
	next if $filename =~ /~$/;

	my $runname = $filename;
	$runname =~ s{^result/result.(....)(..)(..)}{$1/$2/$3};

	my $failed = ($filename =~ /^pass/) ? 0 : 1;
	my $filebase = ($filename =~ m{.*/([^/]+)}) && $1;
	
	my ($dev,$ino,$mode,$nlink,$uid,$gid,$rdev,$size,
	    $atime,$mtime,$ctime,$blksize,$blocks) = stat($filename);

	my $codestr = ($failed ? "Error during build!" : 
		(find_errors($filename) ? "Warnings found!" : "Pass."));
		
	my $logcgi = "log.cgi?log=$filebase";

	print Tr(td($filename),
		 td($filebase),
		 td({bgcolor=>($failed ? "#ff6666" : "#66ff66")},
		    $failed ? b("FAIL") : "ok"),
		 td($codestr . " " . a({-href=>$logcgi}, "(Log)")));
}

print end_table();
exit 0;
