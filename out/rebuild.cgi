#!/usr/bin/perl -w
use strict;
use CGI::Pretty qw/:standard/;
use lib ".";
use Autobuilder;

my $commit = param('log');
$commit =~ s/[^0-9A-Za-z]/_/g;
$commit =~ s/^\./_/;

unlink("pass/$commit");
unlink("fail/$commit");
unlink("errcache/$commit");

print redirect(-location=>".");
