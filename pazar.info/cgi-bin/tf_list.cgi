#!/usr/local/bin/perl

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
my %param = %{$get->Vars};

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

my $talkdb = pazar::talk->new(DB=>'ensembl',USER=>$ENV{ENS_USER},PASS=>$ENV{ENS_PASS},HOST=>$ENV{ENS_HOST},DRV=>'mysql');

my $bg_color = 0;
my %colors = (0 => "#fffff0",
	      1 => "#FFB5AF");

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
foreach my $project (@desc) {
    my @funct_tfs = $dbh->get_all_complex_ids($project->{project_id});
    foreach my $funct_tf (@funct_tfs) {
	my $funct_name = $dbh->get_complex_name_by_id($funct_tf);
	my $tf = $dbh->create_tf;
	my $tfcomplex = $tf->get_tfcomplex_by_id($funct_tf,'notargets');
	my $pazartfid = write_pazarid($funct_tf,'TF');
	my @accns;
	my @classes;
	my @species;
	while (my $subunit=$tfcomplex->next_subunit) {
	    my $fam=!$subunit->get_fam?'':'/'.$subunit->get_fam;
	    my $class=!$subunit->get_class?'':$subunit->get_class.$fam;
	    push @classes,$class;
	    my $sub_accn=$subunit->get_transcript_accession($dbh);
	    push @accns,$sub_accn;
	    my @coords = $talkdb->get_ens_chr($sub_accn);
	    my $species = $talkdb->current_org();
	    $species = ucfirst($species)||'-';
	    push @species,$species;
	}
	push (@{$tf_project{$project->{project_name}}}, {
                tfname => $funct_name,
		accn => \@accns,
		class => \@classes,
                species => \@species,
                ID => $pazartfid});
    }
}
print "<head>
<title>PAZAR - TF List</title>
<script type=\"text/javascript\">
<!--
function showHide(inputID) {
	theObj = document.getElementById(inputID)
	theDisp = theObj.style.display == \"none\" ? \"block\" : \"none\"
	theObj.style.display = theDisp
}

-->
    </script>
<STYLE type=\"text/css\">
.title1 {
font-weight: bold;
font-size: 18px;
}
.summarytable {
border: 2px solid black;
border-collapse: collapse;
}
.tftabletitle {
padding-left: 5px;
padding-right: 5px;
width: 250px;
height: 10px;
text-align: center;
vertical-align: top;
background-color: #e65656;
border: 1px solid black;
}
.basictd {
padding-left: 5px;
padding-right: 5px;
text-align: left;
vertical-align: top;
border: 1px solid black;
}
.submitLink {
background-color: transparent;
text-decoration: underline;
font-size: 14px;
border: none;
cursor: pointer;
cursor: hand;
  }
</style>
    </head>
    <body style=\"background-color: rgb(255, 255, 255);\" onload=\"coll_all();\" onblur=\"self.focus();\">
    <b><span class=\"title1\">TF List sorted by project name:</span></b><br>
   You can change the sorting options by clicking on the column headers.<br>
<table width='750'><ul>";

my @proj_names=sort(keys %tf_project);
foreach my $proj_name (@proj_names) {
my $div_id=$proj_name;
$div_id=~s/ /_/g;
my $style='display:none';
if ($param{opentable} eq $proj_name) {$style='display:block';}
    
    print " <tr><td width='750'><li><a href=\"#$div_id\" onclick = \"showHide('$div_id');\">$proj_name</a></li></td></tr><tr><td width='750'>
<div id=\"$div_id\" style=\"$style\"><table width='750' class='summarytable'><tr>";
    print "<td class='tftabletitle' width='100'><form name=\"species_browse\" method=\"post\" action=\"http://www.pazar.info/cgi-bin/tf_list.cgi\" enctype=\"multipart/form-data\" target=\"_self\"><input type='hidden' name='BROWSE' value='species'><input type='hidden' name='opentable' value='$proj_name'><input type=\"submit\" class=\"submitLink\" value=\"Species\"></form></td>";
    print "<td class='tftabletitle' width='80'><form name=\"ID_browse\" method=\"post\" action=\"http://www.pazar.info/cgi-bin/tf_list.cgi\" enctype=\"multipart/form-data\" target=\"_self\"><input type='hidden' name='BROWSE' value='ID'><input type='hidden' name='opentable' value='$proj_name'><input type=\"submit\" class=\"submitLink\" value=\"PAZAR TF ID\"></form></td>";
    print "<td class='tftabletitle' width='80'><form name=\"desc_browse\" method=\"post\" action=\"http://www.pazar.info/cgi-bin/tf_list.cgi\" enctype=\"multipart/form-data\" target=\"_self\"><input type='hidden' name='BROWSE' value='desc'><input type='hidden' name='opentable' value='$proj_name'><input type=\"submit\" class=\"submitLink\" value=\"TF name\"><small>(user defined)</small></form></td>";
    print "<td class='tftabletitle' width='80'><form name=\"accn_browse\" method=\"post\" action=\"http://www.pazar.info/cgi-bin/tf_list.cgi\" enctype=\"multipart/form-data\" target=\"_self\"><input type='hidden' name='BROWSE' value='accn'><input type='hidden' name='opentable' value='$proj_name'><input type=\"submit\" class=\"submitLink\" value=\"EnsEMBL Transcript ID\"></form></td>";
    print "<td class='tftabletitle' width='120'><form name=\"ens_desc_browse\" method=\"post\" action=\"http://www.pazar.info/cgi-bin/tf_list.cgi\" enctype=\"multipart/form-data\" target=\"_self\"><input type='hidden' name='BROWSE' value='class'><input type='hidden' name='opentable' value='$proj_name'><input type=\"submit\" class=\"submitLink\" value=\"TF Class/Family\"></form></td>";
    print "</tr>";

    my @sorted;
    if ($param{BROWSE} eq 'species') {
	@sorted=sort {$a->{species}->[0] cmp $b->{species}->[0] or $a->{tfname} cmp $b->{tfname}} @{$tf_project{$proj_name}};
    } elsif ($param{BROWSE} eq 'ID') {
	@sorted=sort {$a->{ID} cmp $b->{ID}} @{$tf_project{$proj_name}};
    } elsif ($param{BROWSE} eq 'class') {
	@sorted=sort {$a->{class}->[0] cmp $b->{class}->[0] or $a->{species}->[0] cmp $b->{species}->[0]} @{$tf_project{$proj_name}};
    } elsif ($param{BROWSE} eq 'accn') {
	@sorted=sort {$a->{accn}->[0] cmp $b->{accn}->[0]} @{$tf_project{$proj_name}};
    } else {
	@sorted=sort {$a->{tfname} cmp $b->{tfname} or $a->{species}->[0] cmp $b->{species}->[0]} @{$tf_project{$proj_name}};
    }

foreach my $tf_data (@sorted) {
my $classes=join('<br>',@{$tf_data->{class}});
my $accns=join('<br>',@{$tf_data->{accn}});
my $spec=join('<br>',@{$tf_data->{species}});
print "<tr><td class='basictd' width='100' bgcolor=\"$colors{$bg_color}\">$spec</td>";
print "<td class='basictd' width='80' bgcolor=\"$colors{$bg_color}\"><a href=\"#$tf_data->{tfname}\" onClick=\"javascript:window.opener.document.tf_search.geneID.value='$tf_data->{tfname}';window.opener.document.tf_search.ID_list.options[5].selected=true;window.opener.focus();window.close();\">$tf_data->{ID}</a></td>";
print "<td class='basictd' width='80' bgcolor=\"$colors{$bg_color}\">$tf_data->{tfname}</td>";
print "<td class='basictd' width='80' bgcolor=\"$colors{$bg_color}\">$accns</td>";
print "<td class='basictd' width='120' bgcolor=\"$colors{$bg_color}\">$classes</td>";
print "</tr>";

$bg_color =  1 - $bg_color;
}
print "</table><br></div></td></tr>";
}
print "</ul></table></body></html>";



sub select {

    my ($dbh, $sql) = @_;
    my $sth=$dbh->prepare($sql);
    $sth->execute or die "$dbh->errstr\n";
    return $sth;
}

sub write_pazarid {
    my $id=shift;
    my $type=shift;
    my $id7d = sprintf "%07d",$id;
    my $pazarid=$type.$id7d;
    return $pazarid;
}
