#!/usr/bin/perl -w
use strict;
use CGI qw/:standard *table start_ul/;
use POSIX qw(strftime);

use lib ".";
use Autobuilder;

my @branches = ();
my %revs = ();

sub load_revcache()
{
    open my $fh, "<revcache" 
        or return; # try to survive without it, then
    my $branch;
    my @list;
    while (<$fh>) {
	chomp;
	if (/^\:(\S+)/) {
	    my $newbranch = $1;
	    if ($branch) {
		$revs{$branch} = join("\n", @list);
	    }
	    push @branches, $newbranch;
	    $branch = $newbranch;
	    @list = ();
	} else {
	    push @list, $_;
	}
    }
    if ($branch) {
	$revs{$branch} = join("\n", @list);
    }
    close $fh;
}
load_revcache();

my $currently_doing = (-f '.doing') && stripwhite(catfile(".doing")) || "";

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

sub revs_for_branch($)
{
    my $branch = shift;
    if (-x '../revlist.sh') {
	return run_cmd("../revlist.sh", $branch);
    } else {
	return split("\n", $revs{$branch});
    }
}

sub _list_branches()
{
    if (-x '../branches.sh') {
	return run_cmd("../branches.sh");
    } else {
	return @branches;
    }
}


sub list_branches()
{
    my @out = ();
    foreach my $branch (_list_branches())
    {
        my $branchword = $branch;
        $branchword =~ s{^.*/}{};
        push @out, "$branchword $branch";
    }
    return @out;
}


print header(-type => 'text/html; charset=utf-8'),
      start_html(
	-title => "Autobuilder results",
	-style => {-src => "index.css"}
);

print Link({-rel=>"alternate", -title=>"Autobuilder results",
	-href=>"rss.cgi", -type=>"application/rss+xml"});

print div({-class=>"logo"}, "compiled by ",
    a({-href=>"http://github.com/apenwarr/gitbuilder/"},
      "<b>git</b>builder"));

print h1("Autobuilder results", 
    a({-href=>"rss.cgi",-title=>"Subscribe via RSS"},
      img({-src=>"feed-icon-28x28.png",-alt=>"[RSS]"})),
);

print start_table();
print Tr(th("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"),
    th("Result"), th("Commit"), th("Who"), th("Details"));

for my $bpb (sort { lc($a) cmp lc($b) } list_branches()) {
    my ($branchword, $branch) = split(" ", $bpb, 2);
    my $branchprint = $branch;
    $branchprint =~ s{^origin/}{};

    our $last_was_pending = 0;
    our $print_pending = 1;
    
    sub do_pending_dots()
    {
	if ($last_was_pending > $print_pending) {
	    $last_was_pending -= $print_pending;
	    $print_pending = 0;
	    print Tr(td($branchprint),
		td("...$last_was_pending..."), td(""), td(""), td(""));
	    $branchprint = "";
	}
	$last_was_pending = 0;
    }
    
    foreach my $rev (revs_for_branch($branch)) {
	my ($commit, $email, $comment) = split(" ", $rev, 3);
	
	my $filename;
	my $failed;
	my $logcgi = "log.cgi?log=$commit";
	$email =~ s/\@.*//;
	
	if (-f "pass/$commit") {
	    $filename = "pass/$commit";
	    $failed = 0;
	} elsif (-f "fail/$commit") {
	    $filename = "fail/$commit";
	    $failed = 1;
	} elsif ($commit eq $currently_doing) {
	    do_pending_dots();
	    print Tr(td($branchprint),
		td({bgcolor=>'#ffff66'}, "BUILDING"),
		td(shorten($commit, 7)),
		td($email),
		td($comment));
	    $branchprint = "";
	    next;
	} elsif ($last_was_pending == 0 && $print_pending) {
	    print Tr(td($branchprint),
		td("(Pending)"),
		td(shorten($commit, 7)),
		td($email),
		td($comment));
	    $last_was_pending = 1;
	    $branchprint = "";
	    next;
	} else {
	    $last_was_pending++;
	    next;
	}
	    
	do_pending_dots();
	
	my ($warnmsg, $errs) = find_errors($filename);
	my $codestr = ($failed ? "Errors" : $warnmsg);
	print Tr(td($branchprint),
	    td({bgcolor=>($failed ? "#ff6666" : "#66ff66")},
		$failed ? b("FAIL") : "ok"),
	    td(shorten($commit, 7)),
	    td($email),
	    td(a({-href=>$logcgi}, "$codestr") . " $comment"));
	$branchprint = "";
    }
    
    do_pending_dots();
    
    if (!$branchprint) {
	print Tr(td({colspan=>5}, hr));
    }
}

print end_table();
print end_html;
exit 0;
