#!c:\cygwin\bin\perl -w
use strict;
use CGI qw/:standard *table start_ul/;

print header, start_html("Autobuilder results");

print Link({-rel=>"alternate", -title=>"Autobuilder results",
	-href=>"rss.cgi", -type=>"application/rss+xml"});

print h1("Autobuilder results");

print start_table();
print Tr(th("Run"), th("Project"), th("Result"), th("Details"));

my $rows = 0;

for my $filename (sort { $b cmp $a } <result/result.*>) {
	next if $filename =~ /~$/;

	my $logname = $filename;
	$logname =~ s{^result/result}{log/log};
	
	my $runname = $filename;
	$runname =~ s{^result/result.(....)(..)(..)}{$1/$2/$3};

	open my $fh, "<$filename"
		or die("open $filename: $!\n");
		
	my $did_one = 0;
	while (<$fh>) {
		chomp;
		my ($code, $proj, $codestr) = split(/\s+/, $_, 3);
		# print "$code--$proj--$codestr\n", br;
		print Tr(td($runname),
			 td($proj),
			 td({bgcolor=>($code==0 ? "#66ff66" : "#ff6666")},
			    $code==0 ? "ok" : b("FAIL")),
			 td($codestr . " " . a({-href=>$logname}, "(Log)")));
		$did_one = 1;
		$rows++;
	}
	close $fh;
	
	if (!$did_one) {
		print Tr(td($runname),
			 td("NONE"),
			 td({bgcolor=>"#ffff00"}, b("FAIL")),
			 td("Missing - no result codes generated?!"
			 	 . " " . a({-href=>$logname}, "(Log)")));
		$rows++;
	}
	
	last if $rows > 100;
}
