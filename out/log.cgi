#!/usr/bin/perl -w
use strict;
use CGI::Pretty qw/:standard *table start_ul end_ul start_li end_li/;
use lib ".";
use Autobuilder;

my $commit = param('log');
$commit =~ s/[^0-9A-Za-z]/_/g;
$commit =~ s/^\./_/;

print header, start_html(
	-title => "$commit - Autobuilder log",
	-style => {-src => "log.css"}
);

print div({-style=>'float: right'}, a({-href=>"."}, "<< index"));
my $name = git_describe($commit);
print h1("Autobuilder log for <b><u>$name</u></b> ($commit):");

my $fn;
if (-f "pass/$commit") {
    $fn = "pass/$commit";
} elsif (-f "fail/$commit") {
    $fn = "fail/$commit";
} else {
    print h2("No log with that id.");
    exit 1;
}

open my $fh, "<$fn"
	or die("$fn: $!\n");

my $in = 0;
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
        next;
    } elsif ($s =~ /^_+$/) {
    	# print hr;
    	next;
    } elsif ($s =~ /^>>>/) {
    	$class = "buildscript";
    	if ($in) {
    	    print end_ul;
    	    $in = 0;
    	}
    } elsif ($s =~ /^Project ".*"/ || $s =~ /^---/ || $s =~ /^-->/) {
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
    } elsif ($s =~ /(hint|warning|error|fatal)\s*:\s*(.*)/i) {
    	$class = lc $1;
    	$s = ul("$1: $2");
    }
    
    print div({-class=>$class}, $s);
}

close $fh;

