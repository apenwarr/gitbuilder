#!/usr/bin/perl -w
use strict;
use CGI::Pretty qw/:standard/;
use lib ".";
use Autobuilder;

my $commit = param('log');
$commit =~ s/[^0-9A-Za-z]/_/g;
$commit =~ s/^\./_/;

my $fn;
$fn = "fail/$commit";
if (-f $fn) {
    unlink($fn);
}

print redirect(-location=>".");
