package Autobuilder;
require Exporter;
@ISA = qw(Exporter);
@EXPORT = qw(find_errors);

use strict;


sub find_errors($)
{
	my $filename = shift;
	my $out = "";
	
	open my $fh, "<$filename"
		or die("Can't open $filename: $!\n");
	while (defined(my $s = <$fh>)) {
		if ($s =~ /\s(hint|warning|error|fatal)\s*: (.*)/i) {
			$out .= "<p>$1: $2</p>\n";
		}
	}
	close $fh;
	return $out;
}


1;
