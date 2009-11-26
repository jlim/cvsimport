#!/usr/bin/perl
use pazar;
use pazar::gene;
use pazar::talk;
use pazar::reg_seq;
use HTML::Template;
use CGI qw(:standard);
use CGI::Carp qw(fatalsToBrowser);
my $pazar_cgi       = $ENV{PAZAR_CGI};
my $pazar_html      = $ENV{PAZAR_HTML};
my $pazarcgipath    = $ENV{PAZARCGIPATH};
my $pazarhtdocspath = $ENV{PAZARHTDOCSPATH};
our $searchtab = "tfs";
my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");
my $temptail = HTML::Template->new(filename => "tail.tmpl");
$template->param(TITLE => "Search for Transcription Factors (TFs) | PAZAR");
$template->param(PAZAR_HTML          => $pazar_html);
$template->param(PAZAR_CGI           => $pazar_cgi);
$template->param(ONLOAD_FUNCTION     => "init();");
$template->param(JAVASCRIPT_FUNCTION => qq{ });
my $intro = qq{
	<div class="p20to p5bo">
		<span class="welcometext">Welcome to PAZAR!</span>
	</div>
	<div class="welcomeintro"><span class="b">PAZAR is your one stop shopping experience for transcription factors and regulatory sequence annotations.</span> It is a software framework for the construction and maintenance of regulatory sequence data annotations; a framework which allows multiple boutique databases to function independently within a larger system (or information mall). Our goal is to be the public repository for regulatory data. <a target="publication" href="$pazar_cgi/overview.pl#publications">View our publications &raquo;</a><br><a target="webinar" href="http://cmmt.na3.acrobat.com/p24235926">View our first information webinar held on Nov 24th 2009</a></div>};


require "$pazarcgipath/searchbox.pl";
require "$pazarcgipath/getsession.pl";
if ($loggedin eq "true") {
	$template->param(LOGOUT => qq{<span class="b">You are signed in as $info{first} $info{last}.</span> <a href="$pazar_cgi/logout.pl" class="b">Sign out</a>});
} else {
	$template->param(LOGOUT => qq{<a href="$pazar_cgi/login.pl"><span class="b">Sign in</span></a>});
}
print "Content-Type: text/html\n\n", $template->output;
print "$bowz.$intro";

my $dbh = pazar->new(
    -host         => $ENV{PAZAR_host},
    -user         => $ENV{PAZAR_pubuser},
    -pass         => $ENV{PAZAR_pubpass},
    -dbname       => $ENV{PAZAR_name},
    -drv          => $ENV{PAZAR_drv},
    -globalsearch => "yes"
);
my %unsort_proj;
my $checkl_proj;
my $checkl_proj_public;
my $projects = &select($dbh,qq{SELECT * FROM project WHERE status="open" OR status="published"});
my @desc;
while (my $project = $projects->fetchrow_hashref) {
 	my $proj_rw = $project->{project_name};
 	my $proj_lc = lc($proj_rw);
	$unsort_proj{$proj_lc} = $proj_rw;
}
if ($loggedin eq "true") {
	foreach my $proj (@projids) {
		my $restricted = &select($dbh,qq{SELECT * FROM project WHERE project_id="$proj" and upper(status)="RESTRICTED"});
		while (my $restr = $restricted->fetchrow_hashref) {
		 	my $proj_rw = $restr->{project_name};
 			my $proj_lc = lc($proj_rw);
 			$proj_lc = qq{RESTRICTED_} . $proj_lc;
			$unsort_proj{$proj_lc} = $proj_rw;
		}
	}
}
foreach my $projname (sort(keys %unsort_proj)) {
	my $pn = $unsort_proj{$projname};
	my $public = 0;
	if ($projname =~ /^RESTRICTED_/) {
		$projname =~ s/^RESTRICTED_//g;
		$public = 1;
	}
	my $pd = &select($dbh,qq{SELECT status, description, project_id FROM project WHERE project_name="$projname"});
	my ($sta,$des,$pid) = $pd->fetchrow_array;
	my $tnb = &select($dbh,qq{SELECT count(funct_tf_id) FROM funct_tf WHERE project_id="$pid"});
	my $tfnb = $tnb->fetchrow_array || "0";
	my $mnb = &select($dbh,qq{SELECT count(distinct db_accn) FROM marker WHERE project_id="$pid"});
	my $markernb = $mnb->fetchrow_array || "0";
	my $rnb = &select($dbh,qq{SELECT count(reg_seq_id) FROM reg_seq WHERE project_id="$pid"});
	my $regseqnb = $rnb->fetchrow_array || "0";
	my $cnb = &select($dbh,qq{SELECT count(construct_id) FROM construct WHERE project_id="$pid"});
	my $constrnb = $cnb->fetchrow_array || "0";
	my $totalseq = $regseqnb + $constrnb;
	my $gnb = &select($dbh,qq{SELECT count(distinct db_accn) FROM gene_source a, tsr b 
		WHERE a.project_id="$pid" and a.gene_source_id=b.gene_source_id});
	my $genenb = $gnb->fetchrow_array || "0";
		my $totmrk = $genenb + $markernb;
	my $mnb = &select($dbh,qq{SELECT count(matrix_id) FROM matrix WHERE project_id="$pid"});
	my $matrixnb = $mnb->fetchrow_array || "0";
	$des =~ s/\n/ /g;
	$des =~ s/<[^>]*>/ /g;
	if ($matrixnb > 0) {
		$matrixnb = &pnum($matrixnb);
	} else {
		$matrixnb = "&bull;";
	}
	$totalseq = &pnum($totalseq);
	$totmrk = &pnum($totmrk);
	$tfnb = &pnum($tfnb);
	if ($public == 1) {
		$checkl_proj_public .= qq{
			<div class="p5bo p10lo">
				<div class="pde">
					<div class="pp-pro">$matrixnb</div>
					<div class="pp-seq">$totalseq</div>
					<div class="pp-gns">$totmrk</div>
					<div class="pp-tfs">$tfnb</div>
					<div class="float-l p10ro"><a class="b" href="$pazar_cgi/project.pl?project_name=$pn">$pn</a></div>
					$des
				</div>
				<div class="clear-l"></div>
			</div>};
	} else {
		$checkl_proj .= qq{
			<div class="p5bo p10lo">
				<div class="pde">
					<div class="pp-pro">$matrixnb</div>
					<div class="pp-seq">$totalseq</div>
					<div class="pp-gns">$totmrk</div>
					<div class="pp-tfs">$tfnb</div>
					<div class="float-l p10ro"><a class="b" href="$pazar_cgi/project.pl?project_name=$pn">$pn</a></div>
					$des
				</div>
				<div class="clear-l"></div>
			</div>};
	}
}
if ($checkl_proj_public) {
	print qq{
	<h2>
		<div class="pp-pro">Profiles</div>
		<div class="pp-seq">Seqs</div>
		<div class="pp-gns">Genes</div>
		<div class="pp-tfs">TFs</div>
		My restricted projects
	</h2>
	$checkl_proj_public};
}
print qq{
	<h2>
		<div class="pp-pro">Profiles</div>
		<div class="pp-seq">Seqs</div>
		<div class="pp-gns">Genes</div>
		<div class="pp-tfs">TFs</div>
		Public projects
	</h2>
	$checkl_proj
	<div class="p20to p10lo small b txt-grey">&bull; Transcription factor binding profiles can be generated dynamically in this project.</div>};
sub select {
	my ($dbh, $sql) = @_;
	my $sth = $dbh->prepare($sql);
	$sth->execute or die qq{$dbh->errstr\n};
	return $sth;
}
sub pnum {
	my $num = shift;
	my @aum = split(//,$num);
	my $fnu;
	while (@aum) {
		my $len = @aum;
		if ($len > 3) {
			$fnu = pop(@aum) . $fnu;
			$fnu = pop(@aum) . $fnu;
			$fnu = pop(@aum) . $fnu;
			$fnu = "," . $fnu;
		} else {
			while (@aum) {
				$fnu = pop(@aum) . $fnu;
			}
		}
	}
	return $fnu;
}
print $temptail->output;