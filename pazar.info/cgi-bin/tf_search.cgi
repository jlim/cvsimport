#!/usr/local/bin/perl

use pazar;
use pazar::gene;
use pazar::talk;

use HTML::Template;

use CGI qw(:standard);
use CGI::Carp qw(fatalsToBrowser);
#use CGI::Debug( report => 'everything', on => 'anything' );

use TFBS::PatternGen::MEME;
use TFBS::Matrix::PFM;

#use Data::Dumper;

my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};
my $pazarhtdocspath = $ENV{PAZARHTDOCSPATH};

require "$pazarcgipath/getsession.pl";

# open the html header template
my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");

# fill in template parameters
$template->param(TITLE => 'PAZAR TF View');
$template->param(PAZAR_HTML => $pazar_html);
$template->param(PAZAR_CGI => $pazar_cgi);

 
$template->param(JAVASCRIPT_FUNCTION => qq{
document.getElementsByClassName = function(cl) {
var retnode = [];
var myclass = new RegExp('\\b'+cl+'\\b');
var elem = this.getElementsByTagName('*');
for (var i = 0; i < elem.length; i++) {
var classes = elem[i].className;
if (myclass.test(classes)) retnode.push(elem[i]);
}
return retnode;
};

function setCount(target){

if(target == 0) 
{
document.tf_search.action="$pazar_cgi/tf_list.cgi";
document.tf_search.target="Window1";
window.open('about:blank','Window1', 'resizable=1,scrollbars=yes, menubar=no, toolbar=no directories=no, height=800, width=800');
}
if(target == 1) 
{
document.tf_search.action="$pazar_cgi/tf_search.cgi";
document.tf_search.target="_self";
}
if(target == 2) 
{
document.tf_search.action="$pazar_cgi/tfbrowse_alpha.pl";
document.tf_search.target="Window2";
window.open('about:blank','Window2', 'resizable=1,scrollbars=yes, menubar=no, toolbar=no directories=no, height=600, width=650');
}
}}.q{
function verifyCheckedBoxes() {            
    var numChecked = 0;
    var counter;
    
    // iterate through sequenceform elements
    for(counter=0;counter<document.sequenceform.length;counter++)
    {
	if (document.sequenceform.elements[counter].checked)
	{
	    numChecked++;
	}
    }
    if (numChecked < 2)
    {
	alert('You must select at least 2 sequences\nNumber of sequences selected: ' + numChecked);
    }
    else
    {
	window.open('about:blank','logowin', 'resizable=1,scrollbars=yes, menubar=no, toolbar=no directories=no, height=600, width=600');
	document.sequenceform.submit();
    }
  }

function selectallseq (tableId) {
	tableObj=xGetElementById(tableId);
	var tbody=tableObj.getElementsByTagName('tbody');
	var trs = tbody[0].getElementsByTagName('tr');
	for (x=1; x<trs.length; x++) {
					tds=trs[x].getElementsByTagName('td');
					cb=tds[0].firstChild.firstChild;
					cb.checked=true;
			}
}

function resetallseq (tableId) {
	tableObj=xGetElementById(tableId);
	var tbody=tableObj.getElementsByTagName('tbody');
	var trs = tbody[0].getElementsByTagName('tr');
	for (x=1; x<trs.length; x++) {
					tds=trs[x].getElementsByTagName('td');
					cb=tds[0].firstChild.firstChild;
					cb.checked=false;
			}
}

function selectbytype (tableId,target) {
	tableObj=xGetElementById(tableId);
	var tbody=tableObj.getElementsByTagName('tbody');
	var trs = tbody[0].getElementsByTagName('tr');
	for (x=1; x<trs.length; x++) {
		if (trs[x].className==target) {
			tds=trs[x].getElementsByTagName('td');
			cb=tds[0].firstChild.firstChild;
			cb.checked=true;
		}
	}
}
}
	);

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

print<<page;
<h1>PAZAR TF View</h1>
          <table border="0" cellpadding="0" cellspacing="0" width="100%">
            <tbody><tr>
              <td colspan="2">
      <p class="title2">Search by TF</p>
      </td>
    </tr>
<form name="tf_search" method="post" action="" enctype="multipart/form-data" target="">
    <tr align="left">
      <td colspan="2">
<p > Please enter a &nbsp;
      <select name="ID_list">
      <option selected="selected" value="EnsEMBL_gene">EnsEMBL gene ID</option>
      <option value="EnsEMBL_transcript">EnsEMBL transcript ID</option>
      <option value="tf_name">User Defined TF name</option>
      <option value="EntrezGene">Entrezgene ID</option>
      <option value="nm">RefSeq ID</option>
      <option value="swissprot">Swissprot ID</option>
      <option value="PAZAR_TF">PAZAR TF ID</option>
</select>
&nbsp; <input value="" name="geneID" type="text">&nbsp; <input value="Submit" name="submit" type="submit" onClick="setCount(1)"><br></p>
      </td>
    </tr>
    <tr align="left">
      <td colspan="2"><p > Or browse the current list of reported TFs
&nbsp;
      <input value="View TF List" name="submit" type="submit"  onClick="setCount(0)"><br></p>
      </td>
    </tr>
   </form>
  </tbody>
</table>
<hr color='black'> 
page

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


my $get = new CGI;
my %param = %{$get->Vars};
my $accn = $param{geneID};
$accn=~s/[\s]//g;
my $dbaccn = $param{ID_list}||'PAZAR_TF';
my @trans;
my $tfname;
if ($accn) {
    if ($dbaccn eq 'PAZAR_TF') {
	unless ($accn=~/TF\d{7}/i) {print "<h3>An error occured! Check that the provided ID ($accn) is a $dbaccn ID!</h3>"; exit;} else {@trans = ('PAZARid');}
    }if ($dbaccn eq 'EnsEMBL_gene') {
	@trans = $ensdb->ens_transcripts_by_gene($accn);
        unless ($trans[0]=~/\w{2,}\d{4,}/) {print "<h3>An error occured! Check that the provided ID ($accn) is a $dbaccn ID!</h3>You will have the best results using an EnsEMBL gene ID!"; exit;}
    } elsif ($dbaccn eq 'EnsEMBL_transcript') {
	push @trans,$accn;
        unless ($trans[0]=~/\w{2,}\d{4,}/) {print "<h3>An error occured! Check that the provided ID ($accn) is a $dbaccn ID!</h3>You will have the best results using an EnsEMBL gene ID!"; exit;}
    } elsif ($dbaccn eq 'EntrezGene') {
	my $species=$gkdb->llid_to_org($accn);
	if (!$species) {print "<h3>An error occured! Check that the provided ID ($accn) is a $dbaccn ID!</h3>You will have the best results using an EnsEMBL transcript ID!"; exit;}
	$ensdb->change_mart_organism($species);
	my @gene=$ensdb->llid_to_ens($accn);
	unless ($gene[0]=~/\w{2,}\d{4,}/) {print "<h3>An error occured! Check that the provided ID ($accn) is a $dbaccn ID!</h3>You will have the best results using an EnsEMBL gene ID!"; exit;}
	@trans = $ensdb->ens_transcripts_by_gene($gene[0]);
    } elsif ($dbaccn eq 'nm') {
	my $sp=$gkdb->{dbh}->prepare("select organism from ll_locus a, ll_refseq_nm b where a.ll_id=b.ll_id and b.nm_accn=?");
	$sp->execute($accn);
	my $species=$sp->fetchrow_array();
	if (!$species) {print "<h3>An error occured! Check that the provided ID ($accn) is a $dbaccn ID!</h3>You will have the best results using an EnsEMBL transcript ID!"; exit;}
	$ensdb->change_mart_organism($species);
	@trans=$ensdb->nm_to_enst($accn);
	unless ($trans[0]=~/\w{2,}\d{4,}/) {print "<h3>An error occured! Check that the provided ID ($accn) is a $dbaccn ID!</h3>You will have the best results using an EnsEMBL gene ID!"; exit;}
    } elsif ($dbaccn eq 'swissprot') {
	my $sp=$gkdb->{dbh}->prepare("select organism from ll_locus a, gk_ll2sprot b where a.ll_id=b.ll_id and sprot_id=?")||die;
	$sp->execute($accn)||die;
	my $species=$sp->fetchrow_array();
	if (!$species) {print "<h3>An error occured! Check that the provided ID ($accn) is a $dbaccn ID!</h3>You will have the best results using an EnsEMBL gene ID!"; exit;}
	$ensdb->change_mart_organism($species);
	@trans =$ensdb->swissprot_to_enst($accn);
	unless ($trans[0]=~/\w{2,}\d{4,}/) {print "<h3>An error occured! Check that the provided ID ($accn) is a $dbaccn ID!</h3>You will have the best results using an EnsEMBL gene ID!"; exit;}
    } elsif ($dbaccn eq 'tf_name') {
	@trans = ('none');
	$tfname = '%'.$accn.'%';
    }

    my $tfcount=0;
    my $seqcounter=0;
####start of form
    print "<form name='sequenceform' method='post' target='logowin' action='$pazar_cgi/tf_logo.pl'>";

    foreach my $trans (@trans) {
#	print "you're looking for transcript: ".$trans."\n";
	my $tf;
	my @tfcomplexes;
	if ($trans eq 'none') {
	    $tf = $dbh->create_tf;
	    @tfcomplexes = $tf->get_tfcomplex_by_name($tfname);
	} elsif ($trans eq 'PAZARid') {
	    my $PZid=$accn;
	    $PZid=~s/^\D+0*//;
	    $tf = $dbh->create_tf;
	    @tfcomplexes = $tf->get_tfcomplex_by_id($PZid);
        } else {
	    $tf = $dbh->create_tf;
	    @tfcomplexes = $tf->get_tfcomplex_by_transcript($trans);
	}
	if ($loggedin eq 'true') {
	    foreach my $proj (@projids) {
		my $restricted=&select($dbh, "SELECT project_name FROM project WHERE project_id='$proj' and upper(status)='RESTRICTED'");
		my $restr_proj=$restricted->fetchrow_array();
		if ($restr_proj) {
		    my $dbhandle = pazar->new( 
		      -host          =>    $ENV{PAZAR_host},
		      -user          =>    $ENV{PAZAR_pubuser},
		      -pass          =>    $ENV{PAZAR_pubpass},
		      -dbname        =>    $ENV{PAZAR_name},
  	              -pazar_user    =>    $info{user},
		      -pazar_pass    =>    $info{pass},
                      -drv           =>    $ENV{PAZAR_drv},
		      -project       =>    $restr_proj);

		    my @complexes;
		    if ($trans eq 'none') {
			$tf = $dbhandle->create_tf;
			@complexes = $tf->get_tfcomplex_by_name($tfname);
		    } elsif ($trans eq 'PAZARid') {
			my $PZid=$accn;
			$PZid=~s/^\D+0*//;
			$tf = $dbh->create_tf;
			@tfcomplexes = $tf->get_tfcomplex_by_id($PZid);
		    } else {
			$tf = $dbhandle->create_tf;
			@complexes = $tf->get_tfcomplex_by_transcript($trans);
		    }
		    foreach my $comp (@complexes) {
			push @tfcomplexes, $comp;
		    }
		}
	    }
	}

print<<SUMMARY_HEADER;
<a name='top'></a>
<p class="title2">Search Result Summary</p>
<table width='700' class='summarytable'><tr>
<td class='tftabletitle' width='100'>Species</td>
<td class='tftabletitle' width='100'>PAZAR TF ID</td>
<td class='tftabletitle' width='100'>TF Name<br><small>(user defined)</small></td>
<td class='tftabletitle' width='150'>Transcript Accession</td>
<td class='tftabletitle' width='150'>Class/Family</td>
<td class='tftabletitle' width='100'>Project</td></tr>
SUMMARY_HEADER

my $bg_color = 0;
my %colors = (0 => "#fffff0",
	      1 => "#FFB5AF");

	foreach my $complex (@tfcomplexes) {

	    my $tfproj=$dbh->get_project_name('funct_tf',$complex->dbid);
	    my $tf_name=$complex->name;
	    my $pazartfid=write_pazarid($complex->dbid,'TF');

	    my @classes = ();
	    my @families = ();
	    my @transcript_accessions = ();
	    my $species;
	    while (my $subunit=$complex->next_subunit) {
		my $fam=!$subunit->get_fam?'':'/'.$subunit->get_fam;
		my $class=!$subunit->get_class?'':$subunit->get_class.$fam;
		push(@classes,$class);
		my $tr_accn=$subunit->get_transcript_accession($dbh);
		push(@transcript_accessions, $tr_accn);
		unless ($species) {
		    my @ens_coords = $ensdb->get_ens_chr($tr_accn);
		    $ens_coords[5]=~s/\[.*\]//g;
		    $ens_coords[5]=~s/\(.*\)//g;
		    $ens_coords[5]=~s/\.//g;
		    $species = $ensdb->current_org();
		    $species = ucfirst($species);
		}
	    }
	    unless ($species) { $species='-';}
	    my $traccns=join('<br>',@transcript_accessions);
	    my $trclasses=join('<br>',@classes);

	print "<tr><td class='basictd' width='100' bgcolor=\"$colors{$bg_color}\">$species</td>";
	print "<td class='basictd' width='100' bgcolor=\"$colors{$bg_color}\"><a href='#$pazartfid'>$pazartfid</a></td>";
	print "<td class='basictd' width='100' bgcolor=\"$colors{$bg_color}\">$tf_name</td>";
	print "<td class='basictd' width='150' bgcolor=\"$colors{$bg_color}\">$traccns</td>";
	print "<td class='basictd' width='150' bgcolor=\"$colors{$bg_color}\">$trclasses</td>";
	print "<td class='basictd' width='100' bgcolor=\"$colors{$bg_color}\">$tfproj</td>";
	print "</tr>";

	$bg_color =  1 - $bg_color;
	}

print<<HEADER_TABLE;
</table><br><hr color='black'><p class="title2">Search Result Details TF by TF</p>
HEADER_TABLE

	foreach my $complex (@tfcomplexes) {
	    $bg_color = 0;

	    $tfcount++;
	    my $tfid=$complex->dbid;
	    my $tfproj=$dbh->get_project_name('funct_tf',$tfid);
	    my $tf_name=$complex->name;
	    my $pazartfid=write_pazarid($tfid,'TF');
# 	    my $tfname_s=$tf_name;
# 	    $tfname_s=~s/\//-/g;
# 	    print "<input type='hidden' name='accn' value='$tfname_s'";
	    my $file="$pazarhtdocspath/tmp/".$pazartfid.".fa";
	    open (TMP, ">$file");

	    my @classes = ();
	    my @families = ();
	    my @transcript_accessions = ();
	    my $species;
	    while (my $subunit=$complex->next_subunit) {
		my $class=!$subunit->get_class?'-':$subunit->get_class;
		my $fam=!$subunit->get_fam?'-':$subunit->get_fam;
		push(@classes,$class);
		push(@families,$fam);
		my $tr_accn=$subunit->get_transcript_accession($dbh);
		push(@transcript_accessions, $tr_accn);
		unless ($species) {
		    my @ens_coords = $ensdb->get_ens_chr($tr_accn);
		    $ens_coords[5]=~s/\[.*\]//g;
		    $ens_coords[5]=~s/\(.*\)//g;
		    $ens_coords[5]=~s/\.//g;
		    $species = $ensdb->current_org();
		    $species = ucfirst($species);
		}
	    }
	    unless ($species) { $species='-';}
	    my $traccns=join('<br>',@transcript_accessions);
	    my $trclasses=join('<br>',@classes);
	    my $trfams=join('<br>',@families);

print<<COLNAMES;
<a href='#top'>Back to top</a>
<table class="summarytable"><a name='$pazartfid'></a>
<tr><td class="tftabletitle"><span class="title4">Species</span></td><td class="basictd">$species</td></tr>
<tr><td class="tftabletitle"><span class="title4">TF Name</span></td><td class="basictd">$tf_name</td></tr>
<tr><td class="tftabletitle"><span class="title4">PAZAR TF ID</span></td><td class="basictd"><a href="$pazar_cgi/tf_search.cgi?geneID=$pazartfid">$pazartfid</a></td></tr>
<tr><td class="tftabletitle"><span class="title4">Transcript Accession</span></td><td class="basictd">$traccns</td></tr>
<tr><td class="tftabletitle"><span class="title4">Class</span></td><td class="basictd">$trclasses</td></tr>
<tr><td class="tftabletitle"><span class="title4">Family</span></td><td class="basictd">$trfams</td></tr>
<tr><td class="tftabletitle"><span class="title4">Project</span></td><td class="basictd">$tfproj</td></tr>
</table><br>
COLNAMES

########### start of HTML table
print<<COLNAMES2;	    
<input type="button" name="selectall" id="selectall" value="Select all" onclick="selectallseq('SummaryTable$tf_name');">
<input type="button" name="selecttype1" id="selecttype1" value="Select genomic sequences" onclick="selectbytype('SummaryTable$tf_name','genomic');">
<input type="button" name="selecttype2" id="selecttype2" value="Select constructs" onclick="selectbytype('SummaryTable$tf_name','construct');">
<input type="button" name="resetall" id="resetall" value="Reset" onclick="resetallseq('SummaryTable$tf_name');">
		<table id="SummaryTable$tf_name" class="evidencetableborder"><tr>
		    <td width="100" class="tfdetailstabletitle"><span class="title4">Sequence Type</span></td>
		    
COLNAMES2
    print "<td class=\"tfdetailstabletitle\" width='100'><span class=\"title4\">Sequence ID</span><br><span class=\"smallbold\">click an ID to enter Sequence View</span></td>";
    print "<td width='150' class=\"tfdetailstabletitle\"><span class=\"title4\">Gene ID</span></td>";
    print "<td width='300' class=\"tfdetailstabletitle\"><span class=\"title4\">Sequence</span></td>";
    print "<td width='300' class=\"tfdetailstabletitle\"><span class=\"title4\">Sequence Info</span></td>";
    print "<td width='100' class=\"tfdetailstabletitle\"><span class=\"title4\">Display Genomic Context</span></td>";
    print "</tr>";

	    if (!$complex->{targets}) {
		print "<span class='red'>No target could be found for this TF!</span><br><br><br><br>\n";
		next;
	    }
	    my $count = 0;
	    my @rsids;
	    my @coids;
	    while (my $site=$complex->next_target) {
		my $type=$site->get_type;
		if ($type eq 'matrix') {next;}
		if ($type eq 'reg_seq') {
		    my $rsid=$site->get_dbid;
		    if (grep/^$rsid$/,@rsids) {next;}
		    push @rsids, $rsid;
		    my $id=write_pazarid($rsid,'RS');
		    my $seqname=!$site->get_name?'':$site->get_name;
		    my $reg_seq = $dbh->get_reg_seq_by_regseq_id($site->get_dbid);
		    my $gid=$reg_seq->PAZAR_gene_ID;
		    my $pazargeneid = write_pazarid($gid,'GS');
		    my $gene_accession=$reg_seq->gene_accession;
		    my @ens_coords = $ensdb->get_ens_chr($reg_seq->gene_accession);
		    $ens_coords[5]=~s/\[.*\]//g;
		    $ens_coords[5]=~s/\(.*\)//g;
		    $ens_coords[5]=~s/\.//g;
		    my $species = $ensdb->current_org();
		    $species = ucfirst($species)||'-';
		    $seqcounter++;
		    $count++;
		    my $coord="chr".$reg_seq->chromosome.":".$reg_seq->start."-".$reg_seq->end." (strand ".$reg_seq->strand.")";

		    print "<tr class=\"genomic\"><td width='100' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'><input type='checkbox' name='seq$seqcounter' value='".$site->get_seq."'><br>Genomic<br>Sequence</div></td>";
		    print "<td width='100' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'><a href=\"$pazar_cgi/seq_search.cgi?regid=$rsid\">".$id."</a><br>$seqname</div></td>";
		    print "<td width='150' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'><a href=\"$pazar_cgi/gene_search.cgi?geneID=$pazargeneid\">".$pazargeneid."</a><br><b>$ens_coords[5]</b><br>$species</div></td>";
		    print "<td width='300' class=\"basictd\" bgcolor=\"$colors{$bg_color}\"><div style=\"font-family:monospace;height:100; width:300;overflow:auto;\">".chopstr($site->get_seq,40)."</div></td>";
		    print "<td width='300' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'><b>Coordinates:</b><br>".$coord."</div></td>";
			print "<td width='100' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'><a href=\"$pazar_cgi/gff_custom_track.cgi?resource=ucsc&chr=".$reg_seq->chromosome."&start=".$reg_seq->start."&end=".$reg_seq->end."&species=".$reg_seq->binomial_species."\" target='_blank'><img src='$pazar_html/images/ucsc_logo.png'></a><br><br>";
			print "<a href=\"$pazar_cgi/gff_custom_track.cgi?resource=ensembl&chr=".$reg_seq->chromosome."&start=".$reg_seq->start."&end=".$reg_seq->end."&species=".$reg_seq->binomial_species."\" target='_blank'><img src='$pazar_html/images/ensembl_logo.gif'></a>";
			print "</div></td>";
		}
		if ($type eq 'construct') {
		    my $coid=$site->get_dbid;
		    if (grep/^$coid$/,@coids) {next;}
		    push @coids, $coid;
		    my $id=write_pazarid($coid,'CO');
		    my $seqname=$site->get_name==0?'':$site->get_name;
		    my $desc=$site->get_desc||'-';
		    $seqcounter++;
		    $count++;
		    print "<tr class=\"construct\"><td width='100' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'><input type='checkbox' name='seq$seqcounter' value='".$site->get_seq."'><br>Artificial<br>Sequence</div></td>";
		    print "<td width='100' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'><b>".$id."</b><br>$seqname</div></td>";
		    print "<td width='150' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'>-</div></td>";
		    print "<td width='300' class=\"basictd\" bgcolor=\"$colors{$bg_color}\"><div style=\"font-family:monospace;height:100; width:300;overflow:auto;\">".chopstr($site->get_seq,40)."</div></td>";
			print "<td width='300' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'><b>Description:</b><br>".$desc."</div></td>";
		    print "<td width='100' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\">&nbsp</td>";
		}
                print "</tr>";

		my $construct_name=$cor_accn."_site".$count;
		print TMP ">".$construct_name."\n";
		my $construct_seq=$site->get_seq;
		$construct_seq=~s/N//ig;
		print TMP $construct_seq."\n";
                $bg_color = 1 - $bg_color;
            }
	    print "</table><br>";
	    close (TMP);

	    if ($count<2) {
		print "<span class='red'>There are not enough targets to build a binding profile for this TF!</span><br><br><br><br>\n";
		next;
	    } else {
	    	#Ajax call, no callback func defined for now
	    	print "<input type='button' name='Generate PFM' value='Generate PFM' onclick=\"cuteGet('','Summary'".$tf_name."','memediv".$tf_name."')\">
	    		<div id='memediv' name='memediv".$tf_name."'>";
		my $patterngen =
		    TFBS::PatternGen::MEME->new(-seq_file=> "$file",
						-binary => 'meme',
						-additional_params => '-revcomp -mod oops');
		my $pfm = $patterngen->pattern(); # $pfm is now a TFBS::Matrix::PFM object
		if (!$pfm) {
		    print "<span class='red'>No motif could be found!<br>Try running the motif discovery again with a sub-selection of sequences.</span><br><br><br><br>\n";
		    next;
		} else {
#print a human readable format of the matrix
		    my $prettystring = $pfm->prettyprint();
		    my @matrixlines = split /\n/, $prettystring;
		    $prettystring = join "<BR>\n", @matrixlines;
		    $prettystring =~ s/ /\&nbsp\;/g;
		    print "<table bordercolor='white' bgcolor='white' border=1 cellspacing=0 cellpadding=10><tr><td><span class=\"title4\">Position Frequency Matrix</span></td><td><SPAN class=\"monospace\">$prettystring</SPAN></td></tr>";
#draw the logo
		    my $logo = $pazartfid.".png";
		    my $gd_image = $pfm->draw_logo(-file=>"$pazarhtdocspath/tmp/".$logo, -xsize=>400);
		    print "<tr><td><span class=\"title4\">Logo</span></td><td><img src=\"$pazar_html/tmp/$logo\">";
		    print "<p class=\"small\">These PFM and Logo were generated dynamically using the MEME pattern discovery algorithm.</p></td></tr>\n";
		    print "</table><br><br><br><br>\n";
########### end of HTML table
		}
	    }
	}
    }

    if ($tfcount==0) {
	print "<h3>There is currently no available annotation for the Transcription Factor $accn in PAZAR!<br>Do not hesitate to create your own project and enter information about this TF or any other TF!</h3>";
	exit;
    }

####hidden form inputs
    print "<table bordercolor='white' bgcolor='white'><tr><td class=\"title2\">Click Go to recalculate matrix and logo based on selected sequences</td>";
    print "<td><input type='button' value='Go' onClick=\"verifyCheckedBoxes();\"></td></tr>
<tr><td>(you can combine sequences from multiple TFs)</td></tr></table>";
    print "</form>";
####end of form
}

# print out the html tail template
my $template_tail = HTML::Template->new(filename => 'tail.tmpl');
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

sub write_pazarid {
    my $id=shift;
    my $type=shift;
    my $id7d = sprintf "%07d",$id;
    my $pazarid=$type.$id7d;
    return $pazarid;
}
