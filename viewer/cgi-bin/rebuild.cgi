#!/usr/bin/perl -w
use strict;
use CGI qw/:standard/;
use lib "..";
use Autobuilder;

my $commit = param('log');
$commit =~ s/[^0-9A-Za-z]/_/g;
$commit =~ s/^\./_/;

unlink("../../out/pass/$commit");
unlink("../../out/fail/$commit");
unlink("../../out/errcache/$commit");

print redirect(-location=>"index.cgi");
