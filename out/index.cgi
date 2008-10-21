#!/usr/bin/perl -w
use strict;
use CGI qw/:standard *table start_ul start_div end_div/;
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
	if (/^\:(.*)/) {
	    my ($topcommit, $newbranch) = split(" ", $1, 2);
	    if ($branch) {
		$revs{$branch} = join("\n", @list);
	    }
	    push @branches, "$topcommit $newbranch";
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
	return run_cmd("../branches.sh", "-v");
    } else {
	return @branches;
    }
}


sub list_branches()
{
    my @out = ();
    foreach my $line (_list_branches())
    {
        my ($commit, $branch) = split(" ", $line, 2);
        my $branchword = $branch;
        $branchword =~ s{^.*/}{};
        push @out, "$branchword $branch $commit";
    }
    return @out;
}

my $title = "Autobuilder results";
my $project_name = project_name();
if ($project_name) {
    $title .= " for $project_name";
}

print header(-type => 'text/html; charset=utf-8'),
      start_html(
	-title => $title,
	-style => {-src => "index.css"}
);

print Link({-rel=>"alternate", -title=>$title,
	-href=>"rss.cgi", -type=>"application/rss+xml"});

print div({-class=>"logo"}, "compiled by ",
    a({-href=>"http://github.com/apenwarr/gitbuilder/"},
      "<b>git</b>builder"));

print h1($title,
    a({-href=>"rss.cgi",-title=>"Subscribe via RSS"},
      img({-src=>"feed-icon-28x28.png",-alt=>"[RSS]"})),
);

my @branchlist = list_branches();

sub branch_age($)
{
    my ($branchword, $branch, $topcommit) = split(" ", shift, 3);
    if (-f "fail/$topcommit") {
        return -M "fail/$topcommit";
    } elsif (-f "pass/$topcommit") {
        return -M "pass/$topcommit";
    } else {
        return -1;
    }
}

sub fixbranchprint($)
{
    my $branchprint = shift;
    $branchprint =~ s{^origin/}{};
    $branchprint =~ s{(.*/)?(.*)}{$1<b>$2</b>};
    return $branchprint;
}

sub status_to_statcode($)
{
    my $status = shift;
    if ($status eq "ok") {
        return "ok";
    } elsif ($status eq "BUILDING") {
        return "pending";
    } elsif ($status eq "(Pending)") {
        return "pending";
    } elsif ($status =~ m{^W[^/]*$}) {
        return "warn";
    } else {
        # some kind of FAIL marker by default
        return "err";
    }
}

print start_div({id=>"most_recent"}),
    "Most Recent:",
    start_ul({id=>"most_recent_list"});
for my $bpb (sort { branch_age($a) <=> branch_age($b) } @branchlist) {
    my ($branchword, $branch, $topcommit) = split(" ", $bpb, 3);
    my $branchprint = fixbranchprint($branch);
    my $fn;
    
    next if (-f "ignore/$topcommit");
    
    if (-f "fail/$topcommit") {
        $fn = "fail/$topcommit";
    } elsif (-f "pass/$topcommit") {
        $fn = "pass/$topcommit";
    }
    my $statcode;
    if ($fn) {
        my ($warnmsg, $errs) = find_errors($fn);
        $statcode = status_to_statcode($warnmsg);
    } else {
        $statcode = "pending";
    }
    print li(a({href=>"#$branch"}, 
        span({class=>"status branch status-$statcode"}, $branchprint)));
    
    last if (branch_age($bpb) > 30);
}
print end_ul, end_div;


print start_table({class=>"results",align=>"center"});
print Tr({class=>"resultheader"},
    th({style=>'text-align: right'}, "Branch"),
    th("Status"), th("Commit"), th("Who"), th("Result"), th(""));
    
sub spacer()
{
    return Tr({class=>"spacer"}, td({colspan=>6}, ""));
}

my $last_ended_in_spacer = 0;
for my $bpb (sort { lc($a) cmp lc($b) } @branchlist) {
    our ($branchword, $branch, $topcommit) = split(" ", $bpb, 3);
    our $branchprint = fixbranchprint($branch);

    our $last_was_pending = 0;
    our $print_pending = 1;
    
    my @branchout = ();
    
    sub do_pending_dots(\@)
    {
        my $_branchout = shift;
	if ($last_was_pending > $print_pending) {
	    $last_was_pending -= $print_pending;
	    $print_pending = 0;
	    push @{$_branchout}, Tr(
	        td($branchprint),
		td({class=>"status"}, "...$last_was_pending..."),
		td(""), td(""), td(""));
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
	my $commitlink = commitlink($commit, shorten($commit, 7, ""));
	$comment =~ s/^\s*-?\s*//;
	
        sub pushrow(\@$$$$$$)
        {
            my ($_branchout, $status, $commitlink,
                $email, $codestr, $comment, $logcgi) = @_;
                
            my $statcode = status_to_statcode($status);
            
            do_pending_dots(@{$_branchout});
            push @{$_branchout},
                Tr({class=>"result"},
                    td({class=>"branch"},
                        $branchprint),
                    td({class=>"status status-$statcode"}, $status),
                    td({class=>"commit"}, $commitlink),
                    td({class=>"committer"}, $email),
                    td({class=>"details"},
                        a({class=>"hyper", name=>$branch}, "") . div(
                        span({class=>"codestr"},
                          $logcgi ? a({-href=>$logcgi}, $codestr) : $codestr),
                        span({class=>"comment"}, $comment)))
                    );
            $branchprint = "";
        }
        
	if (-f "pass/$commit") {
	    $filename = "pass/$commit";
	    $failed = 0;
	    # fall through
	} elsif (-f "fail/$commit") {
	    $filename = "fail/$commit";
	    $failed = 1;
	    # fall through
	} elsif ($commit eq $currently_doing) {
	    # currently building this one
	    pushrow(@branchout, "BUILDING", 
	            $commitlink, $email, "", $comment, "");
	    next;
	} elsif ($last_was_pending == 0 && $print_pending) {
	    # first pending in a group: print (Pending)
	    pushrow(@branchout, "(Pending)",
	            $commitlink, $email, "", $comment, "");
	    $last_was_pending = 1;
	    next;
	} else {
	    # no info yet: just count, don't print
	    $last_was_pending++;
	    next;
	}
	    
	my ($warnmsg, $errs) = find_errors($filename);
	my $status = ($warnmsg eq "ok") ? "ok" 
	    : ($warnmsg =~ /^Warnings\(\d+\)$/) ? "Warn" : "FAIL";
	pushrow(@branchout, $status,
                $commitlink, $email, $warnmsg, $comment, $logcgi);
    }
    
    do_pending_dots(@branchout);
    
    if (@branchout > 1) {
        if (!$last_ended_in_spacer) {
            print spacer;
        }
        print @branchout, spacer;
        $last_ended_in_spacer = 1;
    } else {
        print @branchout;
        $last_ended_in_spacer = 0;
    }
}

print end_table();
print div({class=>"extraspace"}, "&nbsp;");
print end_html;
exit 0;
