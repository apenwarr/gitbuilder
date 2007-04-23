#!c:\cygwin\bin\perl -w
use strict;
use CGI qw/:standard/;
use File::stat;
use POSIX qw(strftime);

my $url = url();
my $relative = url(-relative=>1);
$url =~ s{/$relative$}{};

print "Content-Type: text/xml\n";
print "\n";

print qq{<rss version='2.0'>
	<channel>
		<title>Autobuilder results</title>
		<link>$url/</link>
		<language>en-ca</language>
		<generator>CGI</generator>
		<docs>http://blogs.law.harvard.edu/tech/rss</docs>
};

my $rows = 0;

for my $filename (sort { $b cmp $a } <result/result.*>) {
	next if $filename =~ /~$/;

	my $logname = $filename;
	$logname =~ s{^result/result}{log/log};
	
	my $runname = $filename;
	$runname =~ s{^result/result.(....)(..)(..)}{$1/$2/$3};
	
	my $st = stat($filename);
	my $date = strftime("%a, %d %b %Y %H:%M:%S %z",
		localtime($st->mtime));

	open my $fh, "<$filename"
		or die("open $filename: $!\n");
		
	my $did_one = 0;
	while (<$fh>) {
		chomp;
		my ($code, $proj, $codestr) = split(/\s+/, $_, 3);
		print qq{
		  <item>
			<title>$proj: $codestr</title>
			<pubDate>$date</pubDate>
			<link>$url/$logname</link>
			<guid isPermaLink='true'>$url/$logname</guid>
			<description>$codestr</description>
		  </item>
		};
		$did_one = 1;
		$rows++;
	}
	close $fh;
	
	if (!$did_one) {
		my $codestr = "Missing - no result codes generated?!";
		print qq{
		  <item>
			<title>NONE: $codestr</title>
			<pubDate>$date</pubDate>
			<link>$url/$logname</link>
			<guid isPermaLink='true'>$url/$logname</guid>
			<description>$codestr</description>
		  </item>
		};
		$rows++;
	}
	
	last if $rows > 20;
}

print "</channel></rss>";
