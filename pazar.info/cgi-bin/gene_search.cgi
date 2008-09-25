#!/usr/bin/perl

#use strict;

use pazar;
use pazar::gene;
use pazar::talk;

use HTML::Template;

use CGI qw(:standard);
use CGI::Carp qw(fatalsToBrowser);
#use CGI::Debug( report => 'everything', on => 'anything' );

#use Data::Dumper;

my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};

require "$pazarcgipath/getsession.pl";

# open the html header template
my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");

# fill in template parameters
$template->param(TITLE => 'PAZAR Gene View');
$template->param(PAZAR_HTML => $pazar_html);
$template->param(PAZAR_CGI => $pazar_cgi);
$template->param(JAVASCRIPT_FUNCTION => qq{
function setCount(target){

if(target == 0) 
{
document.gene_search.action="$pazar_cgi/gene_list.cgi";
document.gene_search.target="Window1";
window.open('about:blank','Window1', 'scrollbars=yes, menubar=no, toolbar=no directories=no, height=800, width=800');
}
if(target == 1) 
{
var myTextField = document.getElementById('ID_list');

if(myTextField.value == "PAZAR_seq") {
document.gene_search.target="_self";
document.gene_search.action="$pazar_cgi/seq_search.cgi";
} else {
document.gene_search.target="_self";
document.gene_search.action="$pazar_cgi/gene_search.cgi";
}
}
if(target == 2) 
{
document.gene_search.action="$pazar_cgi/genebrowse_alpha.pl";
document.gene_search.target="Window2";
window.open('about:blank','Window2', 'resizable=1,scrollbars=yes, menubar=no, toolbar=no directories=no, height=600, width=650');
}
}

function confirm_entry(geneid)
{
input_box=confirm("Are you sure you want to delete this gene?");
if (input_box==true)

{ 
// submit geneid to delete page
    location.href="deletegene.pl?gid="+geneid;
}

}


});

if($loggedin eq 'true')
{
    #log out link
    $template->param(LOGOUT => "$info{first} $info{last} logged in. "."<a href=\'$pazar_cgi/logout.pl\'>Log Out</a>");
}
else
{
    #log in link
    $template->param(LOGOUT => "<a href=\'$pazar_cgi/login.pl\'>Log In</a>");
}

# send the obligatory Content-Type and print the template output
print "Content-Type: text/html\n\n", $template->output;

#connect to the database
my $dbh = pazar->new( 
		      -host          =>    $ENV{PAZAR_host},
		      -user          =>    $ENV{PAZAR_pubuser},
		      -pass          =>    $ENV{PAZAR_pubpass},
		      -dbname        =>    $ENV{PAZAR_name},
		      -drv           =>    $ENV{PAZAR_drv},
                      -globalsearch  =>    'yes');

my $ensdb = pazar::talk->new(DB=>'ensembl',USER=>$ENV{ENS_USER},PASS=>$ENV{ENS_PASS},HOST=>$ENV{ENS_HOST},DRV=>'mysql');

my $gkdb = pazar::talk->new(DB=>'genekeydb',USER=>$ENV{GKDB_USER},PASS=>$ENV{GKDB_PASS},HOST=>$ENV{GKDB_HOST},DRV=>'mysql');

my @pubprojects = $dbh->public_projects;

print<<page;
<h1>PAZAR Gene View <a href='$pazar_cgi/help_FAQ.pl#2.3%20Gene%20View' target='helpwin' onClick="window.open('about:blank','helpwin');"><img src="$pazar_html/images/help.gif" alt='Help' align='bottom' width=12></a></h1>
          <table border="0" cellpadding="0" cellspacing="0" width="100%">
            <tbody><tr>
              <td colspan="2">
      <p class="title2">Search by Gene or Sequence</p>
      </td>
    </tr>
<form name="gene_search" method="post" action="" enctype="multipart/form-data" target="">
    <tr align="left">
      <td colspan="2">
<p > Please enter a &nbsp;
      <select name="ID_list" id="ID_list">
      <option selected="selected" value="GeneName">User Defined Gene Name</option>
      <option value="EnsEMBL_gene">EnsEMBL gene ID</option>
      <option value="EnsEMBL_transcript">EnsEMBL transcript ID</option>
      <option value="EntrezGene">Entrezgene ID</option>
      <option value="nm">RefSeq ID</option>
      <option value="swissprot">Swissprot ID</option>
      <option value="PAZAR_gene">PAZAR Gene ID</option>
      <option value="PAZAR_seq">PAZAR Sequence ID</option>
      </select>
&nbsp; <input value="" name="geneID" type="text">&nbsp; <input value="Submit" name="submit" type="submit" onClick="setCount(1)">&nbsp; <a href='$pazar_html/ID_help.htm' target='helpwin'onClick="window.open('about:blank','helpwin', 'scrollbars=yes, menubar=no, toolbar=no directories=no, height=650, width=350');"><img src="$pazar_html/images/help.gif" alt='Help' align='bottom' width=12></a><br></p>
      </td>
    </tr>
    <tr align="left">
      <td colspan="2"><p > Or browse the current list of annotated genes
&nbsp;
      <input value="View Gene List" name="submit" type="submit"  onClick="setCount(0)"><br><br></p>
      </td>
    </tr>
    <tr align="left">
      <td width='400' valign=top><span class='red'>!!!NEW!!!</span> Select projects you want to exclude from your search:<br><small>Make your selection before performing your query and hitting the Submit button above.<br>Hold the 'Ctrl' button ('Command' button on Mac) to select/unselect one or more projects.</small></td>
      <td valign=top><select name="excl_proj" size="3" multiple="multiple">
page

my %unsort_proj;
foreach my $project (@pubprojects) {
    my $proj = $dbh->get_project_name_by_ID($project);
    my $proj_lc=lc($proj);
    $unsort_proj{$proj_lc}=$proj;
}
foreach my $projname (sort(keys %unsort_proj)) {
    print "<option value=\"$unsort_proj{$projname}\"> $unsort_proj{$projname}</option>";
}
print "</td></tr></form></tbody></table><hr color='black'>";


my $bg_color = 0;
my %colors = (0 => "#fffff0",
	      1 => "#BDE0DC");

my $get = new CGI;
my %params = %{$get->Vars};
my $accn = $params{geneID};
$accn=~s/\s//g;
my $dbaccn = $params{ID_list}||'PAZAR_gene';
my $gene;

if ($accn) {
    if ($dbaccn eq 'GeneName') {
	$gene='GeneName';
    } elsif ($dbaccn eq 'PAZAR_gene') {
	unless ($accn=~/GS\d{7}/i) {print "<h3>An error occured! Check that the provided ID ($accn) is a $dbaccn ID!</h3>"; exit;} else {$gene='PAZARid';}
    } elsif ($dbaccn eq 'EnsEMBL_gene') {
	my @gene = $ensdb->ens_transcripts_by_gene($accn);
	$gene=$gene[0];
 	unless ($gene) {print "<h3>An error occured! Check that the provided ID ($accn) is a $dbaccn ID!</h3>You will have the best results using an EnsEMBL gene ID!"; exit;} else {$gene=$accn;}
    } elsif ($dbaccn eq 'EnsEMBL_transcript') {
	my @gene = $ensdb->ens_transcr_to_gene($accn);
	$gene=$gene[0];
        unless ($gene) {print "<h3>An error occured! Check that the provided ID ($accn) is a $dbaccn ID!</h3>You will have the best results using an EnsEMBL gene ID!"; exit;}
    } elsif ($dbaccn eq 'EntrezGene') {
        my $species=$gkdb->llid_to_org($accn);
        if (!$species) {print "<h3>An error occured! Check that the provided ID ($accn) is a $dbaccn ID!</h3>You will have the best results using an EnsEMBL gene ID!"; exit;}
        $ensdb->change_mart_organism($species);
        my @gene=$ensdb->llid_to_ens($accn);
	$gene=$gene[0];
	unless ($gene) {print "<h3>An error occured! Check that the provided ID ($accn) is a $dbaccn ID!</h3>You will have the best results using an EnsEMBL gene ID!"; exit;}
    } else {
	my $ens = convert_id($ensdb,$gkdb,$dbaccn,$accn);
	if (!$ens) {print "<h3>An error occured! Check that the provided ID ($accn) is a $dbaccn ID!</h3>You will have the best results using an EnsEMBL gene ID!"; exit;} else {$gene=$ens;}
    }

#get open or published projects
    my %projects;
    my @excluded_proj;
    my $excluded='none';
    if ($params{excl_proj}) {
	foreach my $val ($get->param('excl_proj')) {
	    push @excluded_proj, $val;
	}
	$excluded=join('__',@excluded_proj);
    } elsif ($params{excluded}) {
	$excluded=$params{excluded};
	@excluded_proj=split(/__/,$excluded);
    }

    foreach my $project (@pubprojects) {
	my $projname = $dbh->get_project_name_by_ID($project);
	unless (grep(/^$projname$/,@excluded_proj)) {
	    $projects{$project}=$projname;
	}
    }

#get user's restricted projects if logged in
    if ($loggedin eq 'true') {
	foreach my $proj (@projids) {
	    my $projname = $dbh->get_project_name_by_ID($proj);
	    unless (grep(/^$projname$/,@excluded_proj)) {
		$projects{$proj}=$projname;
	    }
	}
    }

    my $pazarsth;
#get the gene info
    if ($gene eq 'PAZARid') {
	my $PZid=$accn;
	$PZid=~s/^\D+0*//;
	$pazarsth = $dbh->prepare("select * from gene_source where gene_source_id='$PZid'");
    } elsif ($gene eq 'GeneName') {
	$pazarsth = $dbh->prepare("select * from gene_source where description like '%$accn%'");
    } else {
	$pazarsth = $dbh->prepare("select * from gene_source where db_accn='$gene'");
    }
    $pazarsth->execute();

#get the marker info
    my $markersth;
    if ($gene eq 'PAZARid') {
	my $PZid=$accn;
	$PZid=~s/^\D+0*//;
	$markersth = $dbh->prepare("select * from marker where marker_id='$PZid'");
    } elsif ($gene eq 'GeneName') {
	$markersth = $dbh->prepare("select * from marker where description like '%$accn%'");
    } else {
	$markersth = $dbh->prepare("select * from marker where db_accn='$gene'");
    }
    $markersth->execute();
		
#get the gene descriptions
    my @gene_info;
    while (my $res = $pazarsth->fetchrow_hashref) {
	my $pid=$res->{project_id};
	if (grep(/^$pid$/,(keys %projects))) {
	    my $geneaccn = $res->{db_accn};
	    my $geneName = $res->{description}||'-';
	    my $geneid = $res->{gene_source_id};
	    my $pazargeneid = write_pazarid($res->{gene_source_id},'GS');
	    my $proj = $projects{$pid};
	    my @ens_coords = $ensdb->get_ens_chr($geneaccn);
	    $ens_coords[5]=~s/\[.*\]//g;
	    $ens_coords[5]=~s/\(.*\)//g;
	    $ens_coords[5]=~s/\.//g;
	    my $geneDescription = $ens_coords[5]||'-';
	    my $species = $ensdb->current_org();
	    $species = ucfirst($species)||'-';

	    push @gene_info, { desc => $geneName,
                               GID => $geneid,
                               ID => $pazargeneid,
                               proj => $proj,
                               ens_desc => $geneDescription,
                               species => $species,
                               accn => $geneaccn};
	}
    }

#get the marker descriptions
    my @marker_info;
    while (my $res = $markersth->fetchrow_hashref) {
	my $pid=$res->{project_id};
	if (grep(/^$pid$/,(keys %projects))) {
	    my $geneaccn = $res->{db_accn};
	    my $geneName = $res->{description}||'-';
	    my $geneid = $res->{marker_id};
	    my $pazargeneid = write_pazarid($res->{marker_id},'MK');
	    my $proj = $projects{$pid};
	    my @ens_coords = $ensdb->get_ens_chr($geneaccn);
	    $ens_coords[5]=~s/\[.*\]//g;
	    $ens_coords[5]=~s/\(.*\)//g;
	    $ens_coords[5]=~s/\.//g;
	    my $geneDescription = $ens_coords[5]||'-';
	    my $species = $ensdb->current_org();
	    $species = ucfirst($species)||'-';

	    push @marker_info, { desc => $geneName,
                               GID => $geneid,
                               ID => $pazargeneid,
                               proj => $proj,
                               ens_desc => $geneDescription,
                               species => $species,
                               accn => $geneaccn};
	}
    }

###if no data finish the script###
    if (!@gene_info && !@marker_info) {
	print "<p><b>Projects excluded from the search:</b> $excluded</p><h3>No annotation could be found for gene $accn!<br>Do not hesitate to create your own project and enter information about this gene or any other gene!</h3>";

# print out the html tail template and exit
	my $template_tail = HTML::Template->new(filename => "$pazarcgipath/tail.tmpl");
	print $template_tail->output;
	exit;
    }

###if data, print summary table###
print<<SUMMARY_HEADER;
<a name='top'></a>
      <p class="title2">Summary</p>
<p><b>Projects excluded from the search:</b> $excluded</p>
<table width='700' class='summarytable'><tr>
<td class='genedetailstabletitle' width='100'>Species</td>
<td class='genedetailstabletitle' width='100'>PAZAR Gene ID</td>
<td class='genedetailstabletitle' width='100'>Gene Name<br><small>(user defined)</small></td>
<td class='genedetailstabletitle' width='150'>EnsEMBL Gene ID</td>
<td class='genedetailstabletitle' width='150'>EnsEMBL Gene Description</td>
<td class='genedetailstabletitle' width='100'>Project</td></tr>
SUMMARY_HEADER

#start with summary of genes
    foreach my $gene_data (@gene_info) {
	print "<tr><td class='basictd' width='100' bgcolor=\"$colors{$bg_color}\">$gene_data->{species}</td>";
	print "<td class='basictd' width='100' bgcolor=\"$colors{$bg_color}\">$gene_data->{ID}&nbsp&nbsp<a href='#$gene_data->{ID}'><img src='$pazar_html/images/magni.gif' alt='View Details' align='bottom' width=12></a></td>";
	print "<td class='basictd' width='100' bgcolor=\"$colors{$bg_color}\">$gene_data->{desc}</td>";
	print "<td class='basictd' width='150' bgcolor=\"$colors{$bg_color}\">$gene_data->{accn}</td>";
	print "<td class='basictd' width='150' bgcolor=\"$colors{$bg_color}\">$gene_data->{ens_desc}</td>";
	print "<td class='basictd' width='100' bgcolor=\"$colors{$bg_color}\">$gene_data->{proj}</td>";
	print "</tr>";

	$bg_color =  1 - $bg_color;
    }

#then, summary of markers, all in the same table but different colors
    my $marks=0;
    foreach my $marker_data (@marker_info) {
	$marks++;
	print "<tr><td class='basictd' width='100' bgcolor=\"$colors{$bg_color}\"><span class='warning'>*</span>$marker_data->{species}</td>";
	print "<td class='basictd' width='100' bgcolor=\"$colors{$bg_color}\"><span class='warning'>*</span>$marker_data->{ID}&nbsp&nbsp<a href='#$marker_data->{ID}'><img src='$pazar_html/images/magni.gif' alt='View Details' align='bottom' width=12></a></td>";
	print "<td class='basictd' width='100' bgcolor=\"$colors{$bg_color}\"><span class='warning'>*</span>$marker_data->{desc}</td>";
	print "<td class='basictd' width='150' bgcolor=\"$colors{$bg_color}\"><span class='warning'>*</span>$marker_data->{accn}</td>";
	print "<td class='basictd' width='150' bgcolor=\"$colors{$bg_color}\"><span class='warning'>*</span>$marker_data->{ens_desc}</td>";
	print "<td class='basictd' width='100' bgcolor=\"$colors{$bg_color}\"><span class='warning'>*</span>$marker_data->{proj}</td>";
	print "</tr>";

	$bg_color =  1 - $bg_color;
    }
    if ($marks == 0) {
	print "</table><p></p><hr color='black'><p class=\"title2\">Details Gene-by-Gene</p>";
    } else {
	print "</table><p><i><span class='warning'>*</span>The genes marked with a red asterisk are used as markers located in the vicinity of the regulatory region. They have not been shown to be regulated by the described sequence.</i></p><hr color='black'><p class=\"title2\">Details Gene-by-Gene</p>";
    }
    
    my $regseq_counter = 0; # counter for naming forms

###gene details for gene_sources###
    foreach my $gene_data (@gene_info) {
	$species=$gene_data->{species};
	my $ensspecies=$species;
	$ensspecies=~s/ /_/g;
	$pazargeneid=$gene_data->{ID};
	$geneName=$gene_data->{desc};
	$gene=$gene_data->{accn};
	$geneDescription=$gene_data->{ens_desc};
	$proj=$gene_data->{proj};

my $genename_editable = "false";
#make gene name editable if page viewed by project member
if ($loggedin eq 'true') {

#determine the project that this reg seq belongs to

my $genenamesth = &select($dbh,"select project_id from gene_source where gene_source_id=".$gene_data->{GID});
#$geneName = $geneName . "gene id: ".$pazargeneid;

my $genenameresultshref = $genenamesth->fetchrow_hashref;

    my $gene_projid = $genenameresultshref->{"project_id"};

	foreach my $proj (@projids) {
	#see if $proj is the same as the sequence or if my userid is same as sequence user_id
	if($proj == $gene_projid)
	{
		#gene name is editable
		$genename_editable = "true";
	}
    }


if($genename_editable eq "true")
{
	$geneName = "<div id =\"ajaxgenename\">".$geneName."</div><input type=\"button\" name=\"genenameupdatebutton\" value=\"Update Gene Name\" onClick=\"javascript:window.open('updategenename.pl?mode=form&pid=$gene_projid&gid=".$gene_data->{GID}."');\">";
}

}



#print details
	$bg_color = 0;

#generate a unique id for ORCA
my $sid = $$ . time;
my $species_urlfriendly = $species;

$species_urlfriendly =~ s/ /%20/g;

=speciestranslation
if(lc($species_monomial) eq "mus musculus")
{
        $species_monomial = "mouse";
}
if(lc($species_monomial) eq "homo sapiens")
{
        $species_monomial = "human";
}
if(lc($species_monomial) eq "rattus norvegicus")
{
        $species_monomial = "rat";
}
if(lc($species_monomial) eq "gallus gallus")
{
        $species_monomial = "chicken";
}
if(lc($species_monomial) eq "canis familiaris")
{
        $species_monomial = "dog";
}
if(lc($species_monomial) eq "oryctolagus cuniculus")
{
        $species_monomial = "rabbit";
}
if(lc($species_monomial) eq "equus caballus")
{
        $species_monomial = "horse";
}
if(lc($species_monomial) eq "dasypus novemcinctus")
{
        $species_monomial = "armadillo";
}
=cut


print<<HEADER_TABLE;
<a href='#top'>Back to top</a><a name='$pazargeneid'></a>
<table class="summarytable">
<tr><td class="genetabletitle"><span class="title4">Species</span></td><td class="basictd">$species</td></tr>
<tr><td class="genetabletitle"><span class="title4">PAZAR Gene ID</span></td><td class=\"basictd\"><form name=\"genelink$pazargeneid\" method='post' action="$pazar_cgi/gene_search.cgi" enctype='multipart/form-data'><input type='hidden' name='geneID' value=\"$pazargeneid\"><input type='hidden' name='excluded' value="$excluded"><input type='hidden' name='ID_list' value='PAZAR_gene'><input type=\"submit\" class=\"submitLink\" value=\"$pazargeneid\">&nbsp;</form></td></tr>
<tr><td class="genetabletitle"><span class="title4">Gene Name (user defined)</span></td><td class=\"basictd\">$geneName</td></tr>
<tr><td class="genetabletitle"><span class="title4">EnsEMBL Gene ID</span></td><td class="basictd"><a href="http://www.ensembl.org/$ensspecies/geneview?gene=$gene" target='enswin' onClick="window.open('about:blank','enswin');">$gene</a></td></tr>
<tr><td class="genetabletitle"><span class="title4">EnsEMBL Gene Description</span></td><td class="basictd">$geneDescription</td></tr>
<tr><td class="genetabletitle"><span class="title4">Project</span></td><td class=\"basictd\"><a href="$pazar_cgi/project.pl?project_name=$proj">$proj</a></td></tr>
HEADER_TABLE

#show delete button if user is logged in and member of the project ie. same requirements as editing gene name
=pod
if($genename_editable eq "true")
{
    print "<tr><td class=\"basictd\" colspan=2 align=\"left\"><input type=\"button\" value=\"Delete This Gene\" onClick=\"confirm_entry(".$gene_data->{GID}.")\"></td></tr>";
}
=cut
print "</table><br>";

#print "<table class=\"summarytable\">";
#print "<tr><td class=\"genetabletitle\"><span class=\"title4\">Run a regulatory region analysis for this gene</span></td><td class=\"basictd\"><!--<a target=\"orcawin\" href=\"http://burgundy.cmmt.ubc.ca/cgi-bin/OrcaTK/orcatk?sid=$sid&from=select_seqs_name&rm=select_gene&species1=$species_monomial&gene_name=$geneName\">Run OrcaTK</a>--><input type=\"button\" value=\"Run OrcaTK\" OnClick=javascript:window.open(\"http://burgundy.cmmt.ubc.ca/cgi-bin/OrcaTK/orcatk?sid=$sid&from=select_seqs_name&rm=select_gene&species1=$species_monomial&gene_name=$geneName\");></td></tr>";
#print "</table><br>";
#print "<table><tr><td><span class=\"title4\">Run a regulatory region analysis for this gene: </span><input type=\"button\" value=\"Run ORCAtk\" OnClick=javascript:window.open(\"http://www.cisreg.ca/cgi-bin/OrcaTK/orca?sid=$sid&from=select_seqs_name&rm=select_gene&species1=$species_monomial&gene_name=$geneName\");></td></tr></table><br>";

print "<table><tr><td><span class=\"title4\">Run a regulatory region analysis for this gene: </span><input type=\"button\" value=\"Run ORCAtk\" OnClick=javascript:window.open(\"http://www.cisreg.ca/cgi-bin/ORCAtk/orca?rm=select_gene1&species=$species_urlfriendly&ensembl_id=$gene\");></td></tr></table><br>";
#http://www.cisreg.ca/cgi-bin/ORCAtk/orca?rm=select_transcript1&species=<species>&ensembl_id=<ensembl_id> 

########### start of reg_seq table
    print "<table class=\"searchtable\"><tr><td class=\"genedetailstabletitle\" width='100'><span class=\"title4\">RegSeq ID</span><br><span class=\"smallredbold\">click an ID to enter Sequence View</span></td>";
    print "<td width='150' class=\"genedetailstabletitle\"><span class=\"title4\">Sequence Name</span></td>";
    print "<td width='300' class=\"genedetailstabletitle\"><span class=\"title4\">Sequence</span></td>";
    print "<td width='300' class=\"genedetailstabletitle\"><span class=\"title4\">Coordinates<br><small>[assembly]</small></span></td>";
    print "<td width='100' class=\"genedetailstabletitle\"><span class=\"title4\">Display Genomic Context</span></td>";
    print "</tr>";


#loop through regseqs and print tables
	my @regseqs = $dbh->get_reg_seqs_by_gene_id($gene_data->{GID}); 
	if (!$regseqs[0]) {
	    print "</table><span class='red'>There is currently no available annotation for this gene!<br>Do not hesitate to create your own project and enter information about this gene or any other gene!</span>";
	    next;
	} else {
	    my @ens_coords = $ensdb->get_ens_chr($gene);
	    foreach my $regseq (@regseqs) {

		$regseq_counter = $regseq_counter + 1;

#print out default information
		print "<tr>";
		print "<form name='details$regseq_counter' method='post' action='$pazar_cgi/seq_search.cgi' enctype='multipart/form-data'><input type='hidden' name='regid' value='".$regseq->accession_number."'><input type='hidden' name='excluded' value='$excluded'>";
		
		my $id=write_pazarid($regseq->accession_number,'RS');
		print "<td width='100' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'><input type=\"submit\" class=\"submitLink\" value=\"".$id."\"></div></td></form>";

		my $seqname=$regseq->id||'-';
		print "<td width='150' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'>".$seqname."&nbsp;</div></td>";	       

		my $seqstr=chopstr($regseq->seq,40);
		print "<td height=100 width=300 class=\"basictd\" bgcolor=\"$colors{$bg_color}\"><div style=\"font-family:monospace;height:100; width:300;overflow:auto;\">".$seqstr."</div></td>";

		print "<td width='300' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'>chr".$regseq->chromosome.":".$regseq->start."-".$regseq->end." (".$regseq->strand.")<br><small>[".$regseq->seq_dbname." ".$regseq->seq_dbassembly."]</small></div></td>";

#		print "<form name='display$regseq_counter' method='post' action='$pazar_cgi/gff_custom_track.cgi' enctype='multipart/form-data' target='_blank'>";

		print "<td width='100' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><form name='display$regseq_counter' method='post' action='$pazar_cgi/gff_custom_track.cgi' enctype='multipart/form-data' target='_blank'><div class='overflow'><input type='hidden' name='excluded' value='$excluded'><input type='hidden' name='chr' value='".$regseq->chromosome."'><input type='hidden' name='start' value='".$regseq->start."'><input type='hidden' name='end' value='".$regseq->end."'><input type='hidden' name='species' value='".$regseq->binomial_species."'><input type='hidden' name='resource' value='ucsc'><a href='#' onClick=\"javascript:document.display$regseq_counter.resource.value='ucsc';document.display$regseq_counter.submit();\"><img src='$pazar_html/images/ucsc_logo.png' alt='Go to UCSC Genome Browser'></a><!--<input type='submit' name='ucsc' value='ucsc' onClick=\"javascript:document.display$regseq_counter.resource.value='ucsc';\">--><br><br><a href='#' onClick=\"javascript:document.display$regseq_counter.resource.value='ensembl';document.display$regseq_counter.submit();\"><img src='$pazar_html/images/ensembl_logo.gif' alt='Go to EnsEMBL Genome Browser'></a><!--<input type='submit' name='ensembl' value='ensembl' onClick=\"javascript:document.display$regseq_counter.resource.value='ensembl';\">--></div></form><!--<form method=\"post\"><input type=\"hidden\" name=\"seq\" value =\"$seqstr\"><input type=\"submit\" value=\"ORCA\"</form>--></td>";
		print "</tr>";
		$bg_color =  1 - $bg_color;
	    }
	}
	print "</table>";
    }

###gene details for markers###
    foreach my $gene_data (@marker_info) {
	$species=$gene_data->{species};
	my $ensspecies=$species;
	$ensspecies=~s/ /_/g;
	$pazargeneid=$gene_data->{ID};
	$geneName=$gene_data->{desc};
	$gene=$gene_data->{accn};
	$geneDescription=$gene_data->{ens_desc};
	$proj=$gene_data->{proj};

my $genename_editable = "false";
#make gene name editable if page viewed by project member
if ($loggedin eq 'true') {

#determine the project that this reg seq belongs to

my $genenamesth = &select($dbh,"select project_id from marker where marker_id=".$gene_data->{GID});
#$geneName = $geneName . "gene id: ".$pazargeneid;

my $genenameresultshref = $genenamesth->fetchrow_hashref;

    my $gene_projid = $genenameresultshref->{"project_id"};

	foreach my $proj (@projids) {
	#see if $proj is the same as the sequence or if my userid is same as sequence user_id
	if($proj == $gene_projid)
	{
		#gene name is editable
		$genename_editable = "true";
	}
    }

=pod
if($genename_editable eq "true")
{
	$geneName = "<div id =\"ajaxgenename\">".$geneName."</div><input type=\"button\" name=\"genenameupdatebutton\" value=\"Update Gene Name\" onClick=\"javascript:window.open('updategenename.pl?mode=form&pid=$gene_projid&gid=".$gene_data->{GID}."');\">";
}
=cut
}



#print details
	$bg_color = 0;

my $sid = $$ . time;
my $species_urlfriendly = $species;
$species_urlfriendly =~ s/ /%20/g;


print<<HEADER_TABLE;
<a href='#top'>Back to top</a><a name='$pazargeneid'></a>
<table class="summarytable">
<tr><td class="genetabletitle"><span class="title4">Species</span></td><td class="basictd"><span class='warning'>*</span>$species</td></tr>
<tr><td class="genetabletitle"><span class="title4">PAZAR Gene ID</span></td><td class=\"basictd\"><form name=\"genelink$pazargeneid\" method='post' action="$pazar_cgi/gene_search.cgi" enctype='multipart/form-data'><span class='warning'>*</span><input type='hidden' name='geneID' value=\"$pazargeneid\"><input type='hidden' name='excluded' value="$excluded"><input type='hidden' name='ID_list' value='PAZAR_gene'><input type=\"submit\" class=\"submitLink\" value=\"$pazargeneid\">&nbsp;</form></td></tr>
<tr><td class="genetabletitle"><span class="title4">Gene Name (user defined)</span></td><td class=\"basictd\"><span class='warning'>*</span>$geneName</td></tr>
<tr><td class="genetabletitle"><span class="title4">EnsEMBL Gene ID</span></td><td class="basictd"><span class='warning'>*</span><a href="http://www.ensembl.org/$ensspecies/geneview?gene=$gene" target='enswin' onClick="window.open('about:blank','enswin');">$gene</a></td></tr>
<tr><td class="genetabletitle"><span class="title4">EnsEMBL Gene Description</span></td><td class="basictd"><span class='warning'>*</span>$geneDescription</td></tr>
<tr><td class="genetabletitle"><span class="title4">Project</span></td><td class=\"basictd\"><span class='warning'>*</span><a href="$pazar_cgi/project.pl?project_name=$proj">$proj</a></td></tr>
HEADER_TABLE

#show delete button if user is logged in and member of the project ie. same requirements as editing gene name
=pod
if($genename_editable eq "true")
{
    print "<tr><td class=\"basictd\" colspan=2 align=\"left\"><input type=\"button\" value=\"Delete This Gene\" onClick=\"confirm_entry(".$gene_data->{GID}.")\"></td></tr>";
}
=cut
print "</table><p><i><span class='warning'>*</span>The genes marked with a red asterisk are used as markers located in the vicinity of the regulatory region. They have not been shown to be regulated by the described sequence.</i></p><br>";

#print "<table class=\"summarytable\">";
#print "<tr><td class=\"genetabletitle\"><span class=\"title4\">Run a regulatory region analysis for this gene</span></td><td class=\"basictd\"><a target=\"orcawin\" href=\"http://burgundy.cmmt.ubc.ca/cgi-bin/OrcaTK/orcatk?sid=$sid&from=select_seqs_name&rm=select_gene&species1=$species_monomial&gene_name=$geneName\">Run OrcaTK</a></td></tr>";
#print "</table><br>";

#print "<table><tr><td><span class=\"title4\">Run a regulatory region analysis for this gene: </span><input type=\"button\" value=\"Run ORCAtk\" OnClick=javascript:window.open(\"http://burgundy.cmmt.ubc.ca/cgi-bin/OrcaTK/orcatk?sid=$sid&from=select_seqs_name&rm=select_gene&species1=$species_monomial&gene_name=$geneName\");></td></tr></table><br>"; 

print "<table><tr><td><span class=\"title4\">Run a regulatory region analysis for this gene: </span><input type=\"button\" value=\"Run ORCAtk\" OnClick=javascript:window.open(\"http://www.cisreg.ca/cgi-bin/ORCAtk/orca?rm=select_gene1&species=$species_urlfriendly&ensembl_id=$gene\");></td></tr></table><br>";

#http://www.cisreg.ca/cgi-bin/ORCAtk/orca?rm=select_transcript1&species=<species>&ensembl_id=<ensembl_id> 

########### start of reg_seq table
    print "<table class=\"searchtable\"><tr><td class=\"genedetailstabletitle\" width='100'><span class=\"title4\">RegSeq ID</span><br><span class=\"smallredbold\">click an ID to enter Sequence View</span></td>";
    print "<td width='150' class=\"genedetailstabletitle\"><span class=\"title4\">Sequence Name</span></td>";
    print "<td width='300' class=\"genedetailstabletitle\"><span class=\"title4\">Sequence</span></td>";
    print "<td width='300' class=\"genedetailstabletitle\"><span class=\"title4\">Coordinates<br><small>[assembly]</small></span></td>";
    print "<td width='100' class=\"genedetailstabletitle\"><span class=\"title4\">Display Genomic Context</span></td>";
    print "</tr>";


#loop through regseqs and print tables
	my @regseqs = $dbh->get_reg_seqs_by_marker_id($gene_data->{GID}); 
	if (!$regseqs[0]) {
	    print "</table><span class='red'>There is currently no available annotation for this gene!<br>Do not hesitate to create your own project and enter information about this gene or any other gene!</span>";
	    next;
	} else {
	    my @ens_coords = $ensdb->get_ens_chr($gene);
	    foreach my $regseq (@regseqs) {

		$regseq_counter = $regseq_counter + 1;

#print out default information
		print "<tr>";
		print "<form name='details$regseq_counter' method='post' action='$pazar_cgi/seq_search.cgi' enctype='multipart/form-data'><input type='hidden' name='regid' value='".$regseq->accession_number."'><input type='hidden' name='excluded' value='$excluded'>";
		
		my $id=write_pazarid($regseq->accession_number,'RS');
		print "<td width='100' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'><input type=\"submit\" class=\"submitLink\" value=\"".$id."\"></div></td></form>";

		my $seqname=$regseq->id||'-';
		print "<td width='150' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'>".$seqname."&nbsp;</div></td>";	       

		my $seqstr=chopstr($regseq->seq,40);
		print "<td height=100 width=300 class=\"basictd\" bgcolor=\"$colors{$bg_color}\"><div style=\"font-family:monospace;height:100; width:300;overflow:auto;\">".$seqstr."</div></td>";

		print "<td width='300' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'>chr".$regseq->chromosome.":".$regseq->start."-".$regseq->end." (".$regseq->strand.")<br><small>[".$regseq->seq_dbname." ".$regseq->seq_dbassembly."]</small></div></td>";

#		print "<form name='display$regseq_counter' method='post' action='$pazar_cgi/gff_custom_track.cgi' enctype='multipart/form-data' target='_blank'>";

		print "<td width='100' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><form name='display$regseq_counter' method='post' action='$pazar_cgi/gff_custom_track.cgi' enctype='multipart/form-data' target='_blank'><div class='overflow'><input type='hidden' name='excluded' value='$excluded'><input type='hidden' name='chr' value='".$regseq->chromosome."'><input type='hidden' name='start' value='".$regseq->start."'><input type='hidden' name='end' value='".$regseq->end."'><input type='hidden' name='species' value='".$regseq->binomial_species."'><input type='hidden' name='resource' value='ucsc'><a href='#' onClick=\"javascript:document.display$regseq_counter.resource.value='ucsc';document.display$regseq_counter.submit();\"><img src='$pazar_html/images/ucsc_logo.png' alt='Go to UCSC Genome Browser'></a><!--<input type='submit' name='ucsc' value='ucsc' onClick=\"javascript:document.display$regseq_counter.resource.value='ucsc';\">--><br><br><a href='#' onClick=\"javascript:document.display$regseq_counter.resource.value='ensembl';document.display$regseq_counter.submit();\"><img src='$pazar_html/images/ensembl_logo.gif' alt='Go to EnsEMBL Genome Browser'></a><!--<input type='submit' name='ensembl' value='ensembl' onClick=\"javascript:document.display$regseq_counter.resource.value='ensembl';\">--></div></form><!--<form method=\"post\"><input type=\"hidden\" name=\"seq\" value =\"$seqstr\"><input type=\"submit\" value=\"ORCA\"</form>--></td>";
		print "</tr>";
		$bg_color =  1 - $bg_color;
	    }
	}
	print "</table>";
    }
}




# print out the html tail template
my $template_tail = HTML::Template->new(filename => "$pazarcgipath/tail.tmpl");
print $template_tail->output;

#split long lines into several smaller ones by inserting a line break at a specified character interval
#parameters: string to break up, interval
sub chopstr {

    my $longstr = $_[0];
    my $interval = $_[1];
    my $newstr = "";

    while(length($longstr) > $interval)
    {
#put line break at character+1 position
	$newstr = $newstr.substr($longstr,0,$interval)."<br>";
	$longstr = substr($longstr,$interval); #return everything starting at interval'th character	
    }
    $newstr = $newstr . $longstr;

    return $newstr;
}

sub select {

    my ($dbh, $sql) = @_;
    my $sth=$dbh->prepare($sql);
    $sth->execute or die "$dbh->errstr\n";
    return $sth;
}

sub convert_id {
 my ($ensdb,$gkdb,$genedb,$geneid)=@_;
undef my @id;
 my $add=$genedb . "_to_llid";
# print "Working on $geneid in $genedb; $add";
 @id=$gkdb->$add($geneid);
 my $ll=$id[0];
 my @gene;
 if ($ll) {
   my $species=$gkdb->llid_to_org($ll);
   if (!$species) {print "<h3>An error occured! Check that the provided ID ($geneid) is a $genedb ID!</h3>You will have the best results using an EnsEMBL gene ID!"; exit;}
   $ensdb->change_mart_organism($species);
   @gene=$ensdb->llid_to_ens($ll);
 }
 return $gene[0];
}

sub write_pazarid {
    my $id=shift;
    my $type=shift;
    my $id7d = sprintf "%07d",$id;
    my $pazarid=$type.$id7d;
    return $pazarid;
}
