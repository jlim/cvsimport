#!/usr/local/bin/perl

use lib '/space/usr/local/src/ensembl-36/ensembl/modules/';
use lib '/space/usr/local/src/bioperl-1.5.0/';

use strict;

use regdb;

use CGI qw(:standard);
use CGI::Carp qw(fatalsToBrowser);
#use CGI::Debug( report => 'everything', on => 'anything' );

use constant DB_DRV  => 'mysql';
use constant DB_NAME => $ENV{REGDB_name};
use constant DB_USER => $ENV{REGDB_pubuser};
use constant DB_PASS => $ENV{REGDB_pubpass};
use constant DB_HOST => $ENV{REGDB_host};

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
<body style=\"background-color: rgb(255, 255, 255);\" onload=\"coll_all();\">
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
print "    <li>".$gene_data->{accn}."<br>"."Description: ".$gene_data->{desc}."</li>";
} else {
print "    <li>".$gene_data->{accn}."</li>";
}
}
print "</ul></li><br>";
}
print "</ul>";
}



sub select {

    my ($dbh, $sql) = @_;
    my $sth=$dbh->prepare($sql);
    $sth->execute or die "$dbh->errstr\n";
    return $sth;
}
