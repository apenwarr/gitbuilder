#!c:\cygwin\bin\perl -w
use strict;
use CGI::Pretty qw/:standard *table start_ul end_ul start_li end_li/;

my $date = param('date');
$date =~ s/[^0-9\.]/_/g;
$date =~ s/^\./_/;

print header, start_html(
	-title => "$date Autobuilder log",
	-style => {-src => "log.css"}
);

print div({-style=>'float: right'}, a({-href=>"."}, "<< index"));
print h1("Autobuilder log for $date:");

open my $fh, "<log/log.$date"
	or die("Can't open file log/log.$date: $!\n");

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
    } elsif ($s =~ /^Project ".*"/) {
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
    } elsif ($s =~ /^: (warning|error|fatal) : ([^:]+): (.*)/) {
    	$class = $1;
    	$s = "$2:" . ul($3);
    }
    
    print div({-class=>$class}, $s);
}

close $fh;

