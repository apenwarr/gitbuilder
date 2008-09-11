package Autobuilder;
require Exporter;
@ISA = qw(Exporter);
@EXPORT = qw(find_errors squish_log mtime catfile basename stripwhite 
    shorten git_describe);

use strict;

my $err_tail = "";
sub find_errors($)
{
	my $filename = shift;
	my $out = "";
    	my $warnings = 0;
    	my $testsfailed = 0;
	my @tail = ();
	
	open my $fh, "<$filename"
		or die("Can't open $filename: $!\n");
	while (defined(my $s = <$fh>)) {
	    	chomp $s;
		if ($s =~ /^\s*(\S*)\s*(hint|warning|error|fatal)\s*:\s*(.*)/i) {
			$out .= "$2: $1 $3<br>\n";
		    	$warnings++;
		} elsif ($s =~ /^!\s*(.*?)\s+(\S+)\s*$/) {
		        if ($2 ne "ok") {
			        $out .= "! $1   <b>$2</b><br>\n";
			        $testsfailed++;
                        }
		}
		push @tail, "$s<br>\n";
		if (@tail > 25) {
		    shift @tail;
		}
	}
	close $fh;
	$err_tail = "<p>\n\n<b>Last messages:</b><p>\n\n@tail\n";
        my @msg = ();
    	if ($warnings) {
	    	push @msg, "Warnings";
	}
    	if ($testsfailed) {
	    	push @msg, "Failures";
	}
    	if (!@msg) {
	    	push @msg, "ok";
	}
	return join("/", @msg), $out;
}

sub squish_log($)
{
	my $filename = shift;
	my ($msg, $out) = find_errors($filename);
        return $out . $err_tail;
}

sub mtime($)
{
	my $filename = shift @_;
	my ($dev,$ino,$mode,$nlink,$uid,$gid,$rdev,$size,
	    $atime,$mtime,$ctime,$blksize,$blocks) = stat($filename)
	    or die("stat $filename: $!\n");
	return $mtime;
}

sub catfile(@)
{
	my @list = ();
	foreach my $file (@_) {
		open my $fh, "<$file" or die("$file: $!\n");
		push @list, <$fh>;
		close $fh;
	}
	return join('', @list);
}

sub basename($)
{
	my $filename = shift @_;
	$filename =~ m{.*/([^/]+)}  &&  ($filename = $1);
	return $filename;
}

sub stripwhite($)
{
	my $s = shift @_;
	$s =~ s/^\s+//mg;
	$s =~ s/\s+$//mg;
	return $s;
}

sub shorten($$)
{
	my ($s, $len) = @_;
	if (length($s) > $len) {
		return substr($s, 0, $len) . "...";
	} else {
		return $s;
	}
}

sub git_describe($)
{
    my $commit = shift;
    if (-d '../build/.') {
	return stripwhite(
	    `cd ../build && git-describe --contains --all $commit`);
    } else {
	return stripwhite(catfile("describe/$commit"));
    }
}

1;
