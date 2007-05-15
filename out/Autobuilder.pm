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
		if ($s =~ /: (warning|error|fatal) : (.*)/) {
			$out .= "<p>$1: $2</p>\n";
		}
	}
	close $fh;
	return $out;
}


1;
