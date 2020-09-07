#!/usr/bin/perl -w
use strict;
use lib "./out";
use Autobuilder;

$|=1;

my $mark = 0;
if (@ARGV>=1 && $ARGV[0] eq "--mark") {
    $mark = 1;
}

if (!$mark) {
    print STDERR 
          "WARNING: not updating last-seen pointers.  Try --mark if\n"
        . "  you don't want to see the same commits next time.\n";
}

my %skipmarks = ();

sub run_cmd(@)
{
    my @cmdline = @_;
    
    open(my $fh, "-|", @cmdline)
      or die("Can't run $cmdline[0]: $!\n");
    my @out = <$fh>;
    chomp @out;
    close $fh;
    return @out;
}

sub list_branches()
{
    my @out = ();
    foreach my $s (run_cmd('../branches.sh')) {
	my $print = $s;
	$print =~ s{^.*/}{};
	
	push @out, "$print $s";
    }
    
    my @out2 = ();
    foreach my $s (sort { lc($a) cmp lc($b) } @out)
    {
	my ($branchword, $branch) = split(" ", $s, 2);
	push @out2, $branch;
    }	  
    
    return @out2;
}

# returns revs from newest to oldest
sub changed_revs($)
{
    my $branch = shift;
    my @out = ();
    foreach my $rs (run_cmd('../changed-revs.sh', $branch))
    {
	my ($rev, $junk) = split(" ", $rs, 2);
	last if $skipmarks{$rev};
	push @out, $rev;
    }
    return @out;
}

sub revdetail($)
{
    my $rev = shift;
    
    my $who = "UNKNOWN";
    my $date = "UNKNOWN";
    my $log = "";
    my @filenames = ();
    
    my $inlog = 0;
    
    foreach my $line (run_cmd('../revdetail.sh', $rev)) {
	if ($inlog && $line =~ /^\S/) {
	    push @filenames, $line;
	} elsif ($line =~ /^author (.*) <(.*)> (\d+)/) {
	    $who = $2;
	    my $ticks = $3;
	    
	    $who =~ s/\@.*//;
	    
	    my @tm = localtime($ticks);
	    $date = sprintf("%04d-%02d-%02d %02d:%02d:%02d",
		1900+$tm[5], $tm[4]+1, $tm[3], 
		$tm[2], $tm[1], $tm[0]);
	} elsif ($line =~ /^$/) {
	    $inlog = 1;
	} elsif ($line =~ /^    (.*)/) {
	    $log .= "$1\n";
	    $inlog = 1;
	}
    }
    
    $log =~ s/^\s*git-svn-id:.*$//mg;
    $log =~ s/^\s*//;
    $log =~ s/\s*$//;
    $log =~ s/\n/<br>\n/g;
    
    return $rev, $who, $date, \@filenames, $log;
}

sub revformat(@)
{
    my ($rev, $who, $date, $_filenames, $log) = @_;
    my @filenames = @{$_filenames};
    
    my @out = ();
    
    my $commitlink = commitlink($rev, shorten($rev, 7, ""));
    my $filenames = join('<br>', sort @filenames);
    if ($filenames) {
        $filenames .= "<p>";
    }
    
    my ($warnmsg, $errs) = find_errors($rev);
    if ($warnmsg) {
	my $aburl = autobuilder_url();
	$warnmsg = sprintf("(Autobuilder: %s)<br>",
	    $aburl ? "<a href='$aburl/log.cgi?log=$rev'>$warnmsg</a>"
	           : $warnmsg);
    }
    
    push @out, qq{
	<div>
	  <span class='svtitle'>$commitlink by <b>$who</b></span>
	  <span class='svdate'>$date</span>
	  <ul>
	  <div class='svcommentary'>$warnmsg$filenames</div>
	  <div class='svtext'>$log</div>
	  </ul>
	</div>
    };

    return join('', @out);
}

sub nicebranch($)
{
    my $branch = shift;
    $branch =~ s{^remotes/}{};
    $branch =~ s{^origin/}{};
    return $branch;
}


# When we want to mark the most recent revision on a branch as being
# printed, we actually mark a few revisions starting from the most recent.
#
# We could mark them *all*, but that would be unnecessarily many marks.
#
# However, marking more than one helps with tags that are just slightly
# different (eg. a version number commit) from some other branch's history.
# It happens a lot with git-svn, because "made a copy" in svn is an extra
# commit, and that's how you make an svn tag.  Without our slightly funny
# behaviour here, listing all the commits in tag 1.0 wouldn't mark
# *anything* dirty in 1.0a, which is no good.
sub mark_rev(@)
{
    my @revs = @_;
    
    mkdir("lastlog");
    for (my $i = 0; $i < @revs && $i < 5; $i++) {
	my $rev = $revs[$i];
	$skipmarks{$rev} = 1;
	if ($mark) {
        	open my $fh, ">lastlog/$rev" 
	          or die("lastlog/$rev: $!\n");
        	close $fh;
        }
    }
}



my $style = catfile("changelog.css");
my $projname = project_name() || "Git project";
my @ltm = localtime();
my $title = sprintf("%s changes for %04d-%02d-%02d", $projname,
    $ltm[5]+1900, $ltm[4]+1, $ltm[3]);
print qq{<html>
      <head>
      <style type="text/css">
       $style
      </style>
      <title>$title</title>
      </head>
      <body>
};


my %changelogs = ();
my @branches = list_branches();

foreach my $branch (@branches)
{
    printf STDERR "%40s: ", $branch;
    my $nicebranch = nicebranch($branch);
    my @revs = changed_revs($branch);
    
    my $revcount = scalar(@revs);
    if (!$revcount) {
	print STDERR "  Empty.\n";
	next;
    }
    
    # otherwise, actually do the changelog
    my @log = ();
    
    push @log, qq{
	<a name="$branch">
	<h1>$nicebranch:</h1>
	<div class="listings">
    };
    
    print STDERR "  $revcount\n";
    if ($revcount > 25) {
	my $commitlink = commitlink($revs[0], shorten($revs[0], 7, ""));
	push @log, qq{
	    <div>
	      <span class='svtitle'>$commitlink</span>
	      <ul>
	      <span class='svtext'>Too many commits ($revcount) to print them all here.</span>
	      </ul>
	    </div>
	};
    } else {
	foreach my $rev (reverse @revs) {
	    push @log, revformat(revdetail($rev));
	}
    }
    
    $changelogs{$branch} = join('', @log);
    mark_rev(@revs);
}


if (keys %changelogs) {
    print "<h1>There were changes in these branches:</h1> <ul>\n";
    foreach my $branch (@branches) {
	next if !defined($changelogs{$branch});
	my $nicebranch = nicebranch($branch);
	print "<li><a name='toc-$branch'><a href='#$branch'>"
	  . "$nicebranch</a></a></li>\n";
    }
    print "</ul>";
    
    foreach my $branch (@branches) {
	next if !defined($changelogs{$branch});
	print $changelogs{$branch};
    }
} else {
    print "No recent changes.\n";
}


print "</body></html>\n\n";

exit 0;
