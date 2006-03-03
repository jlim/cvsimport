#!/usr/local/bin/perl

use lib '/space/usr/local/src/ensembl-36/ensembl/modules/';
use lib '/space/usr/local/src/bioperl-1.5.0/';
use strict;

use pazar;

use CGI qw(:standard);
use CGI::Carp qw(fatalsToBrowser);
#use CGI::Debug( report => 'everything', on => 'anything' );

use constant DB_DRV  => 'mysql';
use constant DB_NAME => $ENV{PAZAR_name};
use constant DB_USER => $ENV{PAZAR_pubuser};
use constant DB_PASS => $ENV{PAZAR_pubpass};
use constant DB_HOST => $ENV{PAZAR_host};

my $get = new CGI;
my $action = $get->param('submit');

#initialize the html page
print $get->header("text/html");

#connect to the database
my $dbh = pazar->new( 
	  	   -host    =>    DB_HOST,
                   -user    =>    DB_USER,
                   -pass    =>    DB_PASS,
                   -dbname  =>    DB_NAME,
		   -drv     =>    DB_DRV);

my $projects=&select($dbh, "SELECT * FROM project");
my %tf_project;
my %tf_subunit;
if ($projects) {
    my $node=0;
    while (my $project=$projects->fetchrow_hashref) {
	$node++;
	my @funct_tfs = $dbh->get_all_tfs($project->{project_id});
	foreach my $funct_tf (@funct_tfs) {
	    my $funct_name = $dbh->get_complex_name_by_id($funct_tf);
	    push (@{$tf_project{$project->{project_name}}}, $funct_name);
	    my @tf_subunits = $dbh->get_subunit_by_complex($funct_tf);
	    foreach my $subunit (@tf_subunits) {
		push (@{$tf_subunit{$funct_name}}, {
		    accn => $subunit->{transcript},
		    class => $subunit->{class},
		    family => $subunit->{family}});
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
foreach my $proj_name (keys %tf_project) {

print " <li><a href=\"javascript:exp_coll($count);\"><img src=\"../images/minus.gif\" alt=\"toggle\" id=\"im_$count\" border=\"0\" height=\"11\" width=\"11\">$proj_name</a>
    <ul type=\"DISC\" id=\"sp_$count\" style=\"padding: 0pt; margin-left: 10pt; list-style-type: block;\">
    ";
$count++;
foreach my $tf_name (@{$tf_project{$proj_name}}) {

print "<li><b>".$tf_name."</b><br>";

foreach my $tf_data (@{$tf_subunit{$tf_name}}) {
if (!$tf_data->{class} || $tf_data->{class} eq '0') {
print $tf_data->{accn}."<br>";
} elsif (!$tf_data->{family} || $tf_data->{family} eq '0') {
print $tf_data->{accn}."   ".$tf_data->{class}."<br>";
} else {
print $tf_data->{accn}."   ".$tf_data->{class}."/".$tf_data->{family}."<br>";
}
}
print "</li>";
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
