#!/usr/local/bin/perl

use lib '/space/usr/local/src/ensembl-36/ensembl/modules/';
use lib '/space/usr/local/src/bioperl-live/';

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

require 'getsession.pl';

my $get = new CGI;

#initialize the html page
print $get->header("text/html");

#connect to the database
my $dbh = pazar->new( 
	  	   -host          =>    DB_HOST,
                   -user          =>    DB_USER,
                   -pass          =>    DB_PASS,
                   -dbname        =>    DB_NAME,
		   -drv           =>    DB_DRV,
                   -globalsearch  =>    'yes');

my $projects=&select($dbh, "SELECT * FROM project WHERE upper(status)='OPEN' OR upper(status)='PUBLISHED'");

my @desc;
while (my $project=$projects->fetchrow_hashref) {
    push @desc, $project;
}
if ($loggedin eq 'true') {
    foreach my $proj (@projids) {
	my $restricted=&select($dbh, "SELECT * FROM project WHERE project_id='$proj' and upper(status)='RESTRICTED'");
	while (my $restr=$restricted->fetchrow_hashref) {
	    push @desc, $restr;
	}
    }
}

my %tf_project;
my %tf_subunit;
my $node=0;
foreach my $project (@desc) {
    $node++;
    my @funct_tfs = $dbh->get_all_complex_ids($project->{project_id});
    foreach my $funct_tf (@funct_tfs) {
	my $funct_name = $dbh->get_complex_name_by_id($funct_tf);
	push (@{$tf_project{$project->{project_name}}}, $funct_name);
	my $tf = $dbh->create_tf;
	my $tfcomplex = $tf->get_tfcomplex_by_id($funct_tf,'notargets');
	while (my $subunit=$tfcomplex->next_subunit) {
	    push (@{$tf_subunit{$project->{project_name}}{$funct_name}}, {
		accn => $subunit->get_transcript_accession($dbh),
		class => $subunit->get_class,
		family => $subunit->get_fam});
	}
    }
}
print "<head>
<title>PAZAR - TF List</title>
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

function autoPopulate(val)
{
    window.opener.document.tf_search.geneID.value=val;   ;
}
-->
    </script>
    </head>
    <body style=\"background-color: rgb(255, 255, 255);\" onload=\"coll_all();\" onblur=\"self.focus();\">
    <b><span style=\"font-size: 14pt;\">TF List sorted by project name:</span></b>

    <ul style=\"margin: 0pt; padding: 0pt; list-style-type: none;\">

    <a href=\"javascript:exp_all();\"><img src=\"../images/plus.gif\" alt=\"toggle\" border=\"0\"><small>Expand
    all</small></a>
    &nbsp; <a href=\"javascript:coll_all();\"><img src=\"../images/minus.gif\" alt=\"toggle\" border=\"0\"><small>Collapse
    all</small></a>
    <br><br><br>";

my $count=0;
my @proj_names=sort(keys %tf_project);
foreach my $proj_name (@proj_names) {

print " <li><a href=\"javascript:exp_coll($count);\"><img src=\"../images/minus.gif\" alt=\"toggle\" id=\"im_$count\" border=\"0\" height=\"11\" width=\"11\">$proj_name</a>
    <ul type=\"DISC\" id=\"sp_$count\" style=\"padding: 0pt; margin-left: 10pt; list-style-type: block;\">
    ";
$count++;
my @tfnames=sort(@{$tf_project{$proj_name}});
foreach my $tf_name (@tfnames) {

print "<li><a name='#$tf_name'><b>".$tf_name."</b><br>";

my @tfdatas=sort(@{$tf_subunit{$proj_name}{$tf_name}});
foreach my $tf_data (@tfdatas) {
if (!$tf_data->{class} || $tf_data->{class} eq '0') {
print "<a href=\"#$tf_name\" onClick=\"javascript:window.opener.document.tf_search.geneID.value='$tf_data->{accn}';window.opener.document.tf_search.ID_list.options[1].selected=true;window.opener.focus();\">".$tf_data->{accn}."</a><br>";
} elsif (!$tf_data->{family} || $tf_data->{family} eq '0') {
    print "<a href=\"#$tf_name\" onClick=\"javascript:window.opener.document.tf_search.geneID.value='$tf_data->{accn}';window.opener.document.tf_search.ID_list.options[1].selected=true;window.opener.focus();\">".$tf_data->{accn}."</a>   (".$tf_data->{class}.")<br>";
} else {
    print "<a href=\"#$tf_name\" onClick=\"javascript:window.opener.document.tf_search.geneID.value='$tf_data->{accn}';window.opener.document.tf_search.ID_list.options[1].selected=true;window.opener.focus();\">".$tf_data->{accn}."</a>   (".$tf_data->{class}.", ".$tf_data->{family}.")<br>";
}
}
print "</li>";
}
print "</ul></li><br>";
}
print "</ul></body></html>";


sub select {

    my ($dbh, $sql) = @_;
    my $sth=$dbh->prepare($sql);
    $sth->execute or die "$dbh->errstr\n";
    return $sth;
}
