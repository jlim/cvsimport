#!/usr/bin/perl
use pazar;
use pazar::talk;

use CGI qw(:standard);
use CGI::Carp qw(fatalsToBrowser);

# use CGI::Debug(report => "everything", on => "anything");

use constant DB_DRV  => $ENV{PAZAR_drv};
use constant DB_NAME => $ENV{PAZAR_name};
use constant DB_USER => $ENV{PAZAR_pubuser};
use constant DB_PASS => $ENV{PAZAR_pubpass};
use constant DB_HOST => $ENV{PAZAR_host};

my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazarcgipath = $ENV{PAZARCGIPATH};

require "$pazarcgipath/getsession.pl";

my $get = new CGI;
my %param = %{$get->Vars};

print $get->header("text/html");
my $refer = $ENV{"HTTP_REFERER"};
$refer =~ s/#[_\w\d]+$//;
unless ($ENV{SERVER_NAME} =~ (/\w+\.cmmt\.ubc\.ca/||/pazar.info/) ) {
	print qq{<div class="emp">This method is not allowed. Please contact the system administrators for assistance.</div>};
	exit();
}

my $dbh = pazar->new( 
	-host => DB_HOST,
	-user => DB_USER,
	-pass => DB_PASS,
	-dbname => DB_NAME,
	-drv => DB_DRV,
	-globalsearch => "yes");

my $talkdb = pazar::talk->new(
	DB=>"ensembl",
	USER=>$ENV{ENS_USER},
	PASS=>$ENV{ENS_PASS},
	HOST=>$ENV{ENS_HOST},
	DRV=>"mysql");

my $bg_color = 0;
my %colors = (
	0 => "#fffff0",
	1 => "#BDE0DC");

my $project = $param{project_id};
my $table = $param{table};
my $gh;

if ($table eq "marker") {
	$gh = $dbh->prepare(qq{SELECT * FROM marker where project_id="$project"}) || die DBI::errstr;
} else {
	$gh = $dbh->prepare(qq{SELECT * FROM gene_source a, tsr b WHERE a.project_id="$project" AND a.gene_source_id=b.gene_source_id}) || die DBI::errstr;
}

my %gene_project;
$gh->execute() || die DBI::errstr;
while (my $gene = $gh->fetchrow_hashref) {
	my @coords = $talkdb->get_ens_chr($gene->{db_accn});
	$coords[5] =~ s/\[.*\]//g;
	$coords[5] =~ s/\(.*\)//g;
	$coords[5] =~ s/\.//g;
	my $species = $talkdb->current_org();
	$species = ucfirst($species) || "-";
	my $pazargeneid = "";
	if ($table eq "marker") {
		$pazargeneid = write_pazarid($gene->{marker_id},"MK");
	} else {
		$pazargeneid = write_pazarid($gene->{gene_source_id},"GS");
	}
	my $gene_desc = $gene->{description};
	if ($gene_desc eq "0" || $gene_desc eq "") {
		$gene_desc = "-";
	}
	push (@{$gene_project{$project->{project_name}}}, {
		ID => $pazargeneid,
		accn => $gene->{db_accn},
		desc => $gene_desc,
		ens_desc => $coords[5],
		species => $species});
	}
	my @proj_names = sort(keys %gene_project);
	foreach my $proj_name (@proj_names) {
		my $div_id = $proj_name;
		$div_id =~ s/ /_/g;
		my $style = "display: none";
		if ($param{opentable} eq $proj_name) {
			$style = "display: block";
		}
		print qq{
				<table class="summarytable w100p m20bo" class="sortable">
					<thead>
						<tr>
							<th class="gdtt w160">Species</th>
							<th class="gdtt w120">PAZAR gene ID</th>
							<th class="gdtt w100">Gene name</th>
							<th class="gdtt w160">Ensembl gene ID</th>
							<th class="gdtt">Description</th>
						</tr>
					</thead>
					<tbody>};
		my @sorted;
		if ($param{BROWSE} eq "species") {
			@sorted = sort {lc($a->{species}) cmp lc($b->{species}) or lc($a->{desc}) cmp lc($b->{desc})} @{$gene_project{$proj_name}};
		} elsif ($param{BROWSE} eq "ID") {
			@sorted = sort {$a->{ID} cmp $b->{ID}} @{$gene_project{$proj_name}};
		} elsif ($param{BROWSE} eq "ens_desc") {
			@sorted = sort {lc($a->{ens_desc}) cmp lc($b->{ens_desc}) or lc($a->{species}) cmp lc($b->{species})} @{$gene_project{$proj_name}};
		} elsif ($param{BROWSE} eq "accn") {
			@sorted = sort {$a->{accn} cmp $b->{accn}} @{$gene_project{$proj_name}};
		} else {
			@sorted = sort {lc($a->{desc}) cmp lc($b->{desc}) or lc($a->{species}) cmp lc($b->{species})} @{$gene_project{$proj_name}};
		}
		foreach my $gene_data (@sorted) {
			my $gd_endc = $gene_data->{ens_desc};
			my $gd_spec = $gene_data->{species};
			my $gd_accn = $gene_data->{accn};
			my $gd_desc = $gene_data->{desc};
			my $gd_gnid = $gene_data->{ID};
			if (length($gd_endc) > 30) {
				$gd_endc =~ s/\'/\&\#39\;/g;
				$gd_endc = qq{<div onclick="popup(this,'$gd_endc','rt');" class="popup">} . substr($gd_endc,0,28) . "..." . qq{</div>};
			}
			if (length($gd_desc) > 14) {
				$gd_desc =~ s/\'/\&\#39\;/g;
				$gd_desc = qq{<div onclick="popup(this,'$gd_desc','rt');" class="popup">} . substr($gd_desc,0,12) . "..." . qq{</div>};
			}
			print qq{
				<tr style="background-color: $colors{$bg_color};">
					<td class="btd">$gd_spec</td>
					<td class="btd"><a href="$pazar_cgi/gene_search.cgi?searchtab=genes&amp;ID_list=PAZAR_gene&amp;geneID=$gd_gnid">$gd_gnid</a></td>
					<td class="btd">$gd_desc</td>
					<td class="btd">$gd_accn</td>
					<td class="btd">$gd_endc</td>
				</tr>};
			$bg_color =  1 - $bg_color;
		}
		print qq{</tbody></table>};
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