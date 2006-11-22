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
	      1 => "#BDE0DC");

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

my %gene_project;
my $node=0;
foreach my $project (@desc) {
    my $genes = &select($dbh, "SELECT * FROM gene_source WHERE project_id='$project->{project_id}'");
    if ($genes) {
	$node++;
	while (my $gene=$genes->fetchrow_hashref) {
	    my $found=0;
	    my $tsrs = &select($dbh, "SELECT * FROM tsr WHERE gene_source_id='$gene->{gene_source_id}'");
	    if ($tsrs) {
		while (my $tsr=$tsrs->fetchrow_hashref && $found==0) {
		    my $reg_seqs = &select($dbh, "SELECT distinct reg_seq.* FROM reg_seq, anchor_reg_seq, tsr WHERE reg_seq.reg_seq_id=anchor_reg_seq.reg_seq_id AND anchor_reg_seq.tsr_id='$tsr->{tsr_id}'");
		    if ($reg_seqs) {
			my @coords = $talkdb->get_ens_chr($gene->{db_accn});
			$coords[5]=~s/\[.*\]//g;
			$coords[5]=~s/\(.*\)//g;
			$coords[5]=~s/\.//g;
			my $species = $talkdb->current_org();
			$species = ucfirst($species)||'-';

			my $pazargeneid = write_pazarid($gene->{gene_source_id},'GS');
			my $gene_desc=$gene->{description};
			if ($gene_desc eq '0'||$gene_desc eq '') {$gene_desc='-';}
			push (@{$gene_project{$project->{project_name}}}, {
                            ID => $pazargeneid,
			    accn => $gene->{db_accn},
			    desc => $gene_desc,
			    ens_desc => $coords[5],
                            species => $species});
			$found++;
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
.genetabletitle {
padding-left: 5px;
padding-right: 5px;
width: 250px;
height: 10px;
text-align: center;
vertical-align: top;
background-color: #39aecb;
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
    <body style=\"background-color: rgb(255, 255, 255);\" onblur=\"self.focus();\">
    <b><span class=\"title1\">Gene List sorted by project name:</span></b><br>
   You can change the sorting options by clicking on the column headers.<br>
<table width='750'>";

foreach my $proj_name (keys %gene_project) {
my $div_id=$proj_name;
$div_id=~s/ /_/g;
my $style='display:none';
if ($param{opentable} eq $proj_name) {$style='display:block';}

print " <tr><td width='750'><a href=\"#$div_id\" onclick = \"showHide('$div_id');\">$proj_name</a></td></tr><tr><td width='750'>
<div id=\"$div_id\" style=\"$style\"><table width='750' class='summarytable'><tr>";
    print "<td class='genetabletitle' width='100'><form name=\"species_browse\" method=\"post\" action=\"http://www.pazar.info/cgi-bin/gene_list.cgi\" enctype=\"multipart/form-data\" target=\"_self\"><input type='hidden' name='BROWSE' value='species'><input type='hidden' name='opentable' value='$proj_name'><input type=\"submit\" class=\"submitLink\" value=\"Species\"></form></td>";
    print "<td class='genetabletitle' width='80'><form name=\"ID_browse\" method=\"post\" action=\"http://www.pazar.info/cgi-bin/gene_list.cgi\" enctype=\"multipart/form-data\" target=\"_self\"><input type='hidden' name='BROWSE' value='ID'><input type='hidden' name='opentable' value='$proj_name'><input type=\"submit\" class=\"submitLink\" value=\"PAZAR Gene ID\"></form></td>";
    print "<td class='genetabletitle' width='80'><form name=\"desc_browse\" method=\"post\" action=\"http://www.pazar.info/cgi-bin/gene_list.cgi\" enctype=\"multipart/form-data\" target=\"_self\"><input type='hidden' name='BROWSE' value='desc'><input type='hidden' name='opentable' value='$proj_name'><input type=\"submit\" class=\"submitLink\" value=\"Gene name\"><small>(user defined)</small></form></td>";
    print "<td class='genetabletitle' width='80'><form name=\"accn_browse\" method=\"post\" action=\"http://www.pazar.info/cgi-bin/gene_list.cgi\" enctype=\"multipart/form-data\" target=\"_self\"><input type='hidden' name='BROWSE' value='accn'><input type='hidden' name='opentable' value='$proj_name'><input type=\"submit\" class=\"submitLink\" value=\"EnsEMBL Gene ID\"></form></td>";
    print "<td class='genetabletitle' width='120'><form name=\"ens_desc_browse\" method=\"post\" action=\"http://www.pazar.info/cgi-bin/gene_list.cgi\" enctype=\"multipart/form-data\" target=\"_self\"><input type='hidden' name='BROWSE' value='ens_desc'><input type='hidden' name='opentable' value='$proj_name'><input type=\"submit\" class=\"submitLink\" value=\"EnsEMBL Gene Description\"></form></td>";
    print "</tr>";

    my @sorted;
    if ($param{BROWSE} eq 'species') {
	@sorted=sort {$a->{species} cmp $b->{species} or $a->{desc} cmp $b->{desc}} @{$gene_project{$proj_name}};
    } elsif ($param{BROWSE} eq 'ID') {
	@sorted=sort {$a->{ID} cmp $b->{ID}} @{$gene_project{$proj_name}};
    } elsif ($param{BROWSE} eq 'ens_desc') {
	@sorted=sort {$a->{ens_desc} cmp $b->{ens_desc} or $a->{species} cmp $b->{species}} @{$gene_project{$proj_name}};
    } elsif ($param{BROWSE} eq 'accn') {
	@sorted=sort {$a->{accn} cmp $b->{accn}} @{$gene_project{$proj_name}};
    } else {
	@sorted=sort {$a->{desc} cmp $b->{desc} or $a->{species} cmp $b->{species}} @{$gene_project{$proj_name}};
    }

foreach my $gene_data (@sorted) {

print "<tr><td class='basictd' width='100' bgcolor=\"$colors{$bg_color}\">$gene_data->{species}</td>";
print "<td class='basictd' width='80' bgcolor=\"$colors{$bg_color}\"><a href=\"#$gene_data->{accn}\" onClick=\"javascript:window.opener.document.gene_search.geneID.value='$gene_data->{accn}';window.opener.document.gene_search.ID_list.options[0].selected=true;window.opener.focus();window.close();\">$gene_data->{ID}</a></td>";
print "<td class='basictd' width='80' bgcolor=\"$colors{$bg_color}\">$gene_data->{desc}</td>";
print "<td class='basictd' width='80' bgcolor=\"$colors{$bg_color}\">$gene_data->{accn}</td>";
print "<td class='basictd' width='120' bgcolor=\"$colors{$bg_color}\">$gene_data->{ens_desc}</td>";
print "</tr>";

$bg_color =  1 - $bg_color;
}
print "</table><br></div></td></tr>";
}
print "</table></body></html>";




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
