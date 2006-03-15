#!/usr/local/bin/perl

use lib '/space/usr/local/src/ensembl-36/ensembl/modules/';
use lib '/space/usr/local/src/bioperl-live/';

use strict;

use pazar;
use pazar::talk;

use CGI qw(:standard);
use CGI::Carp qw(fatalsToBrowser);
#use CGI::Debug( report => 'everything', on => 'anything' );

use constant DB_DRV  => 'mysql';
use constant DB_NAME => $ENV{PAZAR_name};
use constant DB_USER => $ENV{PAZAR_pubuser};
use constant DB_PASS => $ENV{PAZAR_pubpass};
use constant DB_HOST => $ENV{PAZAR_host};

my $get = new CGI;

#initialize the html page
print $get->header("text/html");

#connect to the database
my $dbh = pazar->new( 
		      -host    =>    DB_HOST,
		      -user    =>    DB_USER,
		      -pass    =>    DB_PASS,
		      -dbname  =>    DB_NAME,
		      -drv     =>    DB_DRV);

my $talkdb = pazar::talk->new(DB=>'ensembl',USER=>$ENV{ENS_USER},PASS=>$ENV{ENS_PASS},HOST=>$ENV{ENS_HOST},DRV=>'mysql');

my %gene_project;
my $projects=&select($dbh, "SELECT * FROM project WHERE status='open' OR status='published'");
if ($projects) {
    my $node=0;
    while (my $project=$projects->fetchrow_hashref) {
	my $genes = &select($dbh, "SELECT * FROM gene_source WHERE project_id='$project->{project_id}'");
	if ($genes) {
	    $node++;
	    while (my $gene=$genes->fetchrow_hashref) {
		my $tsrs = &select($dbh, "SELECT * FROM tsr WHERE gene_source_id='$gene->{gene_source_id}'");
		if ($tsrs) {
		    while (my $tsr=$tsrs->fetchrow_hashref) {
			my $reg_seqs = &select($dbh, "SELECT distinct reg_seq.* FROM reg_seq, anchor_reg_seq, tsr WHERE reg_seq.reg_seq_id=anchor_reg_seq.reg_seq_id AND anchor_reg_seq.tsr_id='$tsr->{tsr_id}'");
			if ($reg_seqs) {
			    my @coords = $talkdb->get_ens_chr($gene->{db_accn});
			    my @desc = split('\[',$coords[5]);
			    push (@{$gene_project{$project->{project_name}}}, {
				accn => $gene->{db_accn},
				desc => $gene->{description},
				ens_desc => $desc[0]});
			}
		    }
		}
	    }
	}
    }

    print "<head>
<title>PAZAR - Gene List</title>
<script type=\"text/javascript\">
<!--
function exp_coll(ind)
{
    s = document.getElementById(\"sp_\" + ind);
    i = document.getElementById(\"im_\" + ind);
    if (s.style.display == 'none')
{
    s.style.display = 'block';
    i.src = \"../images/minus.gif\";
}
else if (s.style.display == 'block')
{
    s.style.display = 'none';
    i.src = \"../images/plus.gif\";
}
}
function exp(ind)
{
    s = document.getElementById(\"sp_\" + ind);
    i = document.getElementById(\"im_\" + ind);
    if (!(s && i)) return false;
    s.style.display = 'block';
    i.src = \"../images/minus.gif\";
}
function coll(ind)
{
    s = document.getElementById(\"sp_\" + ind);
    i = document.getElementById(\"im_\" + ind);
    if (!(s && i)) return false;
    s.style.display = 'none';
    i.src = \"../images/plus.gif\";
}
function coll_all()
{";

for (my $i=0; $i<$node; $i++) {
print "coll($i);";
}
print "
}
function exp_all()
{";
for (my $i=0; $i<$node; $i++) {
print "exp($i);";
}
print "
}
-->
    </script>
    </head>
    <body style=\"background-color: rgb(255, 255, 255);\" onload=\"coll_all();\" onblur=\"self.focus();\">
    <b><span style=\"font-size: 14pt;\">Gene List sorted by project name:</span></b>

    <ul style=\"margin: 0pt; padding: 0pt; list-style-type: none;\">

    <a href=\"javascript:exp_all();\"><img src=\"../images/plus.gif\" alt=\"toggle\" border=\"0\"><small>Expand
    all</small></a>
    &nbsp; <a href=\"javascript:coll_all();\"><img src=\"../images/minus.gif\" alt=\"toggle\" border=\"0\"><small>Collapse
    all</small></a>
    <br><br><br>";

my $count=0;
foreach my $proj_name (keys %gene_project) {

print " <li><a href=\"javascript:exp_coll($count);\"><img src=\"../images/minus.gif\" alt=\"toggle\" id=\"im_$count\" border=\"0\" height=\"11\" width=\"11\">$proj_name</a>
    <ul type=\"DISC\" id=\"sp_$count\" style=\"padding: 0pt; margin-left: 10pt; list-style-type: block;\">
    ";
$count++;
foreach my $gene_data (@{$gene_project{$proj_name}}) {
if ($gene_data->{desc} && $gene_data->{desc} ne '0') {
print "    <li><b>EnsEMBL stable ID: </b>".$gene_data->{accn}."<br>"."<b>Annotator Description: </b>".$gene_data->{desc}."<br>"."<b>EnsEMBL Description: </b>".$gene_data->{ens_desc}."</li>";
} else {
print "    <li><b>EnsEMBL stable ID: </b>".$gene_data->{accn}."<br>"."<b>EnsEMBL Description: </b>".$gene_data->{ens_desc}."</li>";
}
}
print "</ul></li><br>";
}}
print "</ul></body></html>";




sub select {

    my ($dbh, $sql) = @_;
    my $sth=$dbh->prepare($sql);
    $sth->execute or die "$dbh->errstr\n";
    return $sth;
}
