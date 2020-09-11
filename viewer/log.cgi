#!/usr/bin/perl -w
use strict;
use CGI qw/:standard *table start_ul end_ul start_li end_li/;
use lib ".";
use Autobuilder;

my $commit = param('log');
$commit =~ s/[^0-9A-Za-z]/_/g;
$commit =~ s/^\./_/;

print header(-type => 'text/html; charset=utf-8'),
      start_html(
	-title => "$commit - Autobuilder log",
	-style => [
		{-src => "/bootstrap.css"},
		{-src => "/bootstrap-responsive.css"},
		{-src => "/docs.css"},
		{-src => "/log.css"},],
);

print div({-style=>'float: right'}, a({-href=>"."}, "<< index"));
my $name = git_describe($commit);
my $commitlink = commitlink($commit, $commit);
print h1("Autobuilder log for <b><u>$name</u></b> ($commitlink):");

my $fn;
if (-f "../out/pass/$commit") {
    $fn = "../out/pass/$commit";
} elsif (-f "../out/fail/$commit") {
    $fn = "../out/fail/$commit";
} else {
    print h2("No log with that id.");
    exit 1;
}

open my $fh, "<$fn"
	or die("$fn: $!\n");

my $in = 0;
my $ignore_warnings = 0;
while (defined(my $s = <$fh>))
{
    chomp $s;

    $s =~ s/^\s+//g;
    $s =~ s/\s+$//g;
    
    $s =~ s{c:\\build\\tmp\\}{}ig;
    $s =~ s{c:\\cygwin\\.*tmp\\}{}ig;

    $s =~ s{^c:\\.*\\dcc32.exe}{...\\dcc32.exe}i;
    $s =~ s{^c:\\.*Borland.Delphi.Targets[^:]*: }{: }gi;
    
    my $class='debug';
    if ($s eq "") {
	print p($s);
        next;
    } elsif ($s =~ /--START-IGNORE-WARNINGS/) {
        $ignore_warnings++;
    } elsif ($s =~ /--STOP-IGNORE-WARNINGS/) {
        $ignore_warnings--;
    } elsif ($s =~ /^>>>/) {
    	$class = "buildscript";
    	if ($in) {
    	    print end_ul;
    	    $in = 0;
    	}
    } elsif ($s =~ /^Project ".*"/ || $s =~ /^---/ || $s =~ /^-->/
              || $s =~ /^Testing ".*" in .*:\s*/) {
    	$class = "msbuild";
    	if ($in) {
    	    print end_ul;
    	}
        if ($s =~ /^Project "(.*)" is building "(.*)"/) {
    	    print div({-class=>'msbuild'}, "Building $2:");
    	} else {
    	    print div({-class=>'msbuild'}, $s);
    	}
    	print start_ul;
    	$in = 1;
    	next;
    } elsif ($s =~ /^\s*(\S*)\s*(hint|warning|error|fatal)\s*:\s*(.*)/i) {
    	my $xclass = lc $2;
    	$s = ul("$2: $1 $3");
        if ($ignore_warnings <= 0 || $xclass !~ /(hint|warning)/i) {
            $class = $xclass;
        }
    } elsif ($s =~ /^(\s*.*\.go:\d+:\d+: .*)/i) {
        # errors from go compiler
        $class = "error";
        $s = ul($1);
    } elsif ($s =~ /^(FAIL(\t.*\d+s|$))/) {
        # errors from go tests
        $class = "error";
        $s = ul($1);
    } elsif ($s =~ /^\s*(make: \*\*\* .*)/) {
        # errors from GNU make
        $class = "error";
        $s = ul($1);
    } elsif ($s =~ /^(redo  \s*\S.* \(exit .*)/) {
        # errors from redo build system
        $class = "error";
        $s = ul($1);
    } elsif ($s =~ /^(redo  \s*\S.*)/) {
        $class = "redo";
        $s = $1;
    } elsif ($s =~ /^!\s*(.*?)\s+(\S+)\s*$/) {
        $class = ($2 ne "ok") ? 'error' : 'buildscript';
    }
    
    print div({-class=>$class}, $s);
}

close $fh;
