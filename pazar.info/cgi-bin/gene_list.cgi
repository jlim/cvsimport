#!/usr/local/bin/perl

use pazar;
use pazar::talk;

use CGI qw(:standard);
use CGI::Carp qw(fatalsToBrowser);
#use CGI::Debug( report => 'everything', on => 'anything' );

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
our %sqlcache;
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

my $gh=$dbh->prepare("SELECT * FROM gene_source WHERE project_id=?")||die DBI::errstr;
my $tsrs=$dbh->prepare("SELECT * FROM tsr WHERE gene_source_id=?")||die DBI::errstr;
my %gene_project;
foreach my $project (@desc) {
     $gh->execute($project->{project_id})||die DBI::errstr;
	while (my $gene=$gh->fetchrow_hashref) {
	    my $found=0;
	    $tsrs->execute($gene->{gene_source_id})||die DBI::errstr;
		while (my $tsr=$tsrs->fetchrow_hashref && $found==0) {
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

    print "<head>
<title>PAZAR - Gene List</title>
<script type=\"text/javascript\">
function showHide(inputID) {
	theObj = document.getElementById(inputID)
	theDisp = theObj.style.display == \"none\" ? \"block\" : \"none\"
	theObj.style.display = theDisp
}
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
.genedetailstabletitle {
padding-left: 5px;
padding-right: 5px;
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
<table width='750'><ul>";

my @proj_names=sort(keys %gene_project);
foreach my $proj_name (@proj_names) {
my $div_id=$proj_name;
$div_id=~s/ /_/g;
my $style='display:none';
if ($param{opentable} eq $proj_name) {$style='display:block';}

print " <tr><td width='750'><li><a href=\"#$div_id\" onclick = \"showHide('$div_id');\">$proj_name</a></li></td></tr><tr><td width='750'>
<div id=\"$div_id\" style=\"$style\"><table width='750' class='summarytable'><tr>";
    print "<td class='genedetailstabletitle' width='100'><form name=\"species_browse\" method=\"post\" action=\"$pazar_cgi/gene_list.cgi\" enctype=\"multipart/form-data\" target=\"_self\"><input type='hidden' name='BROWSE' value='species'><input type='hidden' name='opentable' value='$proj_name'><input type=\"submit\" class=\"submitLink\" value=\"Species\"></form></td>";
    print "<td class='genedetailstabletitle' width='80'><form name=\"ID_browse\" method=\"post\" action=\"$pazar_cgi/gene_list.cgi\" enctype=\"multipart/form-data\" target=\"_self\"><input type='hidden' name='BROWSE' value='ID'><input type='hidden' name='opentable' value='$proj_name'><input type=\"submit\" class=\"submitLink\" value=\"PAZAR Gene ID\"></form></td>";
    print "<td class='genedetailstabletitle' width='80'><form name=\"desc_browse\" method=\"post\" action=\"$pazar_cgi/gene_list.cgi\" enctype=\"multipart/form-data\" target=\"_self\"><input type='hidden' name='BROWSE' value='desc'><input type='hidden' name='opentable' value='$proj_name'><input type=\"submit\" class=\"submitLink\" value=\"Gene name\"><small>(user defined)</small></form></td>";
    print "<td class='genedetailstabletitle' width='80'><form name=\"accn_browse\" method=\"post\" action=\"$pazar_cgi/gene_list.cgi\" enctype=\"multipart/form-data\" target=\"_self\"><input type='hidden' name='BROWSE' value='accn'><input type='hidden' name='opentable' value='$proj_name'><input type=\"submit\" class=\"submitLink\" value=\"EnsEMBL Gene ID\"></form></td>";
    print "<td class='genedetailstabletitle' width='120'><form name=\"ens_desc_browse\" method=\"post\" action=\"$pazar_cgi/gene_list.cgi\" enctype=\"multipart/form-data\" target=\"_self\"><input type='hidden' name='BROWSE' value='ens_desc'><input type='hidden' name='opentable' value='$proj_name'><input type=\"submit\" class=\"submitLink\" value=\"EnsEMBL Gene Description\"></form></td>";
    print "</tr>";

    my @sorted;
    if ($param{BROWSE} eq 'species') {
	@sorted=sort {lc($a->{species}) cmp lc($b->{species}) or lc($a->{desc}) cmp lc($b->{desc})} @{$gene_project{$proj_name}};
    } elsif ($param{BROWSE} eq 'ID') {
	@sorted=sort {$a->{ID} cmp $b->{ID}} @{$gene_project{$proj_name}};
    } elsif ($param{BROWSE} eq 'ens_desc') {
	@sorted=sort {lc($a->{ens_desc}) cmp lc($b->{ens_desc}) or lc($a->{species}) cmp lc($b->{species})} @{$gene_project{$proj_name}};
    } elsif ($param{BROWSE} eq 'accn') {
	@sorted=sort {$a->{accn} cmp $b->{accn}} @{$gene_project{$proj_name}};
    } else {
	@sorted=sort {lc($a->{desc}) cmp lc($b->{desc}) or lc($a->{species}) cmp lc($b->{species})} @{$gene_project{$proj_name}};
    }

foreach my $gene_data (@sorted) {

print "<tr><td class='basictd' width='100' bgcolor=\"$colors{$bg_color}\">$gene_data->{species}</td>";
print "<td class='basictd' width='80' bgcolor=\"$colors{$bg_color}\"><a href=\"#$gene_data->{accn}\" onClick=\"javascript:window.opener.document.gene_search.geneID.value='$gene_data->{accn}';window.opener.document.gene_search.ID_list.options[1].selected=true;window.opener.focus();window.close();\">$gene_data->{ID}</a></td>";
print "<td class='basictd' width='80' bgcolor=\"$colors{$bg_color}\">$gene_data->{desc}</td>";
print "<td class='basictd' width='80' bgcolor=\"$colors{$bg_color}\">$gene_data->{accn}</td>";
print "<td class='basictd' width='120' bgcolor=\"$colors{$bg_color}\">$gene_data->{ens_desc}</td>";
print "</tr>";

$bg_color =  1 - $bg_color;
}
print "</table><br></div></td></tr>";
}
print "</ul></table></body></html>";




sub select {

    my ($dbh, $sql,$cache) = @_;
    my $sth;
    if ($cache) {
	    unless ($sqlcache{$sql}) {
		$sth=$dbh->prepare($sql);
		$sqlcache{$sql}=$sth;
		}
	}
	else {
		$sth=$dbh->prepare($sql);
	}
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
