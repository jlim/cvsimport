#!/usr/bin/perl

use pazar;
use pazar::talk;
use HTML::Template;

use CGI qw(:standard);
use CGI::Carp qw(fatalsToBrowser);

# use CGI::Debug(report => "everything", on => "anything");

my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};
my $pazarhtdocspath = $ENV{PAZARHTDOCSPATH};

use constant DB_DRV  => $ENV{PAZAR_drv};
use constant DB_NAME => $ENV{PAZAR_name};
use constant DB_USER => $ENV{PAZAR_pubuser};
use constant DB_PASS => $ENV{PAZAR_pubpass};
use constant DB_HOST => $ENV{PAZAR_host};

my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");
my $temptail = HTML::Template->new(filename => "tail.tmpl");
$template->param(TITLE => "List of target genes | PAZAR");
$template->param(JAVASCRIPT_FUNCTION => qq{ });
$template->param(PAZAR_HTML => $pazar_html);
$template->param(PAZAR_CGI => $pazar_cgi);
$template->param(ONLOAD_FUNCTION => "");

my $pazarcgipath = $ENV{PAZARCGIPATH};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazar_cgi = $ENV{PAZAR_CGI};

require "$pazarcgipath/getsession.pl";

my $get = new CGI;
my %param = %{$get->Vars};

my $dbh = pazar->new( 
	-host => DB_HOST,
	-user => DB_USER,
	-pass => DB_PASS,
	-dbname => DB_NAME,
	-drv => DB_DRV,
	-globalsearch => "yes");

my $talkdb = pazar::talk->new(
	DB =>"ensembl",
	USER =>$ENV{ENS_USER},
	PASS =>$ENV{ENS_PASS},
	HOST =>$ENV{ENS_HOST},
	DRV =>"mysql");

my $bg_color = 0;
my %colors = (
	0 => "#fffff0",
	1 => "#BDE0DC");

my $projects = &select($dbh, qq{SELECT * FROM project WHERE upper(status)="OPEN" OR upper(status)="PUBLISHED"});
our %sqlcache;
my @desc;
while (my $project = $projects->fetchrow_hashref) {
	push @desc, $project;
}
if ($loggedin eq "true") {
	foreach my $proj (@projids) {
		my $restricted = &select($dbh, qq{SELECT * FROM project WHERE project_id="$proj" AND upper(status)="RESTRICTED"});
		while (my $restr = $restricted->fetchrow_hashref) {
			push @desc, $restr;
		}
	}
}

my %gene_project;
my %marker_project;

my $mh = $dbh->prepare(qq{SELECT count(distinct db_accn) FROM marker WHERE project_id=?}) || die DBI::errstr;
my $gh = $dbh->prepare(qq{SELECT count(distinct db_accn) FROM gene_source a, tsr b WHERE a.project_id=? AND a.gene_source_id=b.gene_source_id}) || die DBI::errstr;
foreach my $project (@desc) {
	$gh->execute($project->{project_id}) || die DBI::errstr;
	my $cnt = $gh->fetchrow_array;
	$mh->execute($project->{project_id}) || die DBI::errstr;
	my $mcnt = $mh->fetchrow_array;
	$gene_project{$project->{project_name}}{CNT} = $cnt;
	$gene_project{$project->{project_name}}{ID} = $project->{project_id};
	$marker_project{$project->{project_name}}{CNT} = $mcnt;
	$marker_project{$project->{project_name}}{ID} = $project->{project_id};
}
if ($loggedin eq "true") {
	$template->param(LOGOUT => qq{<span class="b">You are signed in as $info{first} $info{last}.</span> <a href="$pazar_cgi/logout.pl" class="b">Sign out</a>});
} else {
	$template->param(LOGOUT => qq{<a href="$pazar_cgi/login.pl"><span class="b">Sign in</span></a>});
}
print "Content-Type: text/html\n\n", $template->output;
print qq{
	<div class="docp">
		<div class="float-r b txt-grey">PAZAR Database</div>
		<a href="$pazar_cgi/gene_search.cgi" class="b">&laquo; Return to gene search</a>
		<div class="clear-r"></div>
	</div>
	<h1>List of target genes</h1>};

my @proj_names = sort(keys %gene_project);
foreach my $proj_name (@proj_names) {
	my $div_id = $proj_name;
	$div_id =~ s/ /_/g;
	my $style = "display: none";
	if ($param{opentable} eq $proj_name) {
		$style = "display: block";
	}
	my $mdiv_id = $proj_name . "markers";
	$mdiv_id =~ s/ /_/g;
	my $mstyle = "display: none";
	if ($param{opentable} eq $proj_name . "markers") {
		$mstyle = "display: block";
	}
	my $nuberg = $gene_project{$proj_name}{CNT};
	my $geneid = $marker_project{$proj_name}{ID};
	my $marker = $marker_project{$proj_name}{CNT};
	print qq{
		<div class="blklk" onclick="showHideGeneList('$div_id');">$proj_name ($nuberg genes)</div>
		<div class="p20lo"><div id="$div_id" style="$style" loaded="no" project_id="$geneid" genes="$nuberg"></div></div>
		<div class="blklk" onclick="showHideGeneList('$mdiv_id');">$proj_name markers ($marker genes)</div>
		<div class="p20lo"><div id="$mdiv_id" style="$mstyle" loaded="no" project_id="$geneid" genes="$marker"></div></div>};
}

sub select {
	my ($dbh,$sql,$cache) = @_;
	my $sth;
	if ($cache) {
		unless ($sqlcache{$sql}) {
			$sth = $dbh->prepare($sql);
			$sqlcache{$sql} = $sth;
		}
	} else {
		$sth = $dbh->prepare($sql);
	}
	$sth->execute or die "$dbh->errstr\n";
	return $sth;
}
sub write_pazarid {
    my $id = shift;
    my $type = shift;
    my $id7d = sprintf "%07d", $id;
    my $pazarid = $type . $id7d;
    return $pazarid;
}