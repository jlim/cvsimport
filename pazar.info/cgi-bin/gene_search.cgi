#!/usr/local/bin/perl

use lib '/space/usr/local/src/ensembl-36/ensembl/modules/';

use strict;

use regdb;

use CGI qw(:standard);
use CGI::Carp qw(fatalsToBrowser);
use CGI::Debug( report => 'everything', on => 'anything' );

# BEGIN {
#             use CGI::Carp qw(carpout);
#             open(LOG, ">>/usr/local/apache/pazar.info/cgi-bin/cgi-logs/mycgi-log") or
#               die("Unable to open mycgi-log: $!\n");
#             carpout(LOG);
#           }

use constant DB_DRV  => 'mysql';
use constant DB_NAME => 'pazar';
use constant DB_USER => 'pazar_rw';
use constant DB_PASS => 'pazar_rwpass';
use constant DB_HOST => 'napa.cmmt.ubc.ca';

my $get = new CGI;
my $action = $get->param('submit');

#initialize the html page
print $get->header("text/html");

#connect to the database
my $dbh = regdb->new( 
	  	   -host    =>    DB_HOST,
                   -user    =>    DB_USER,
                   -pass    =>    DB_PASS,
                   -dbname  =>    DB_NAME,
		   -drv     =>    DB_DRV);

#View Gene List
if ($action eq 'View Gene List') {
    my %gene_project;
    my $projects=&select($dbh, "SELECT * FROM project");
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
				push (@{$gene_project{$project->{project_name}}}, {
				    accn => $gene->{db_accn},
				    desc => $gene->{description}});
			    }
			}
		    }
		}
	    }
	}

	print "<head>
  <title>PAZAR - search by gene</title>
  <script type=\"text/javascript\">
<!--
function exp_coll(ind)
{
    s = document.getElementById(\"sp_\" + ind);
    i = document.getElementById(\"im_\" + ind);
    if (s.style.display == 'none')
{
    s.style.display = 'block';
    i.src = \"images/minus.gif\";
}
else if (s.style.display == 'block')
{
    s.style.display = 'none';
    i.src = \"images/plus.gif\";
}
}
function exp(ind)
{
    s = document.getElementById(\"sp_\" + ind);
    i = document.getElementById(\"im_\" + ind);
    if (!(s && i)) return false;
    s.style.display = 'block';
    i.src = \"images/minus.gif\";
}
function coll(ind)
{
    s = document.getElementById(\"sp_\" + ind);
    i = document.getElementById(\"im_\" + ind);
    if (!(s && i)) return false;
    s.style.display = 'none';
    i.src = \"images/plus.gif\";
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


    <body style=\"background-color: rgb(255, 255, 255);\">

    <center>
    <table width=\"600\">

    <tbody>

    <tr>

    <td width=\"600\">
    <center>
    <p><b><i><span style=\"font-size: 20pt;\">PAZAR</span></i></b><b><span style=\"font-size: 14pt;\"> </span></b><b><span style=\"font-size: 20pt;\"><i>-</i> Search by Gene
    </span></b></p>
    </center>

    <hr><br><br><br>
    <body style=\"background-color: rgb(255, 255, 255);\" onload=\"coll_all();\">

    <ul style=\"margin: 0pt; padding: 0pt; list-style-type: none;\">

    <a href=\"javascript:exp_all();\"><img src=\"images/plus.gif\" alt=\"toggle\" border=\"0\">Expand
    all</a>
    &nbsp; <a href=\"javascript:coll_all();\"><img src=\"images/minus.gif\" alt=\"toggle\" border=\"0\">Collapse
    all</a>
    <p class=\"MsoNormal\" style=\"margin-left: 0.5in; text-indent: -0.5in;\"><b><span style=\"font-size: 14pt;\">Genes available within each project:</span></b></p>
    <ul style=\"margin: 0pt; padding: 0pt; list-style-type: none;\">";

my $count=0;
foreach my $proj_name (keys %gene_project) {

print " <li><a href=\"javascript:exp_coll($count);\"><img src=\"images/minus.gif\" alt=\"toggle\" id=\"im_$count\" border=\"0\" height=\"11\" width=\"11\">$proj_name</a>
    <ul class=\"zzul\" id=\"sp_$count\" style=\"padding: 0pt; margin-left: 10pt; list-style-type: none;\">
    ";
$count++;
foreach my $gene_data (@{$gene_project{$proj_name}}) {
if ($gene_data->{desc} && $gene_data->{desc} ne '0') {
print "    <li><span class=\"zzspace\">&nbsp;&nbsp;".$gene_data->{accn}."\t"."Description: ".$gene_data->{desc}."</span></li>";
} else {
print "    <li><span class=\"zzspace\">&nbsp;&nbsp;".$gene_data->{accn}."</span></li>";
}
}
print "</ul></li>";
}
print "</ul>";
}

} elsif ($action eq 'Submit') {
print "<head>
    <title>PAZAR - search by gene</title>
    </head>


    <body style=\"background-color: rgb(255, 255, 255);\">

    <center>
    <table width=\"600\">

    <tbody>

    <tr>

    <td width=\"600\">
    <center>
    <p><b><i><span style=\"font-size: 20pt;\">PAZAR</span></i></b><b><span style=\"font-size: 14pt;\"> </span></b><b><span style=\"font-size: 20pt;\"><i>-</i> Search by Gene
    </span></b></p>
    </center>

    <hr><br><br><br>";

my $gene = $get->param('geneID');

if (!$gene) {
    print "<big>Please provide a gene ID!</big>\n";

}
my $reg_seqs = regdb->get_psms_by_accn($gene);
}

print "</td></tr></tbody></table></center></body></html>";



sub select {

    my ($dbh, $sql) = @_;
    my $sth=$dbh->prepare($sql);
    $sth->execute or die "$dbh->errstr\n";
    return $sth;
}
