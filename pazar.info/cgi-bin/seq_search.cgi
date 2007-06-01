#!/usr/local/bin/perl

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
$template->param(TITLE => 'PAZAR Sequence View');
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

print<<page;
<h1>PAZAR Sequence View</h1>
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
      <option selected="selected" value="EnsEMBL_gene">EnsEMBL gene ID</option>
      <option value="EnsEMBL_transcript">EnsEMBL transcript ID</option>
      <option value="GeneName">User Defined Gene Name</option>
      <option value="EntrezGene">Entrezgene ID</option>
      <option value="nm">RefSeq ID</option>
      <option value="swissprot">Swissprot ID</option>
      <option value="PAZAR_gene">PAZAR Gene ID</option>
      <option value="PAZAR_seq">PAZAR Sequence ID</option>
      </select>
&nbsp; <input value="" name="geneID" type="text">&nbsp; <input value="Submit" name="submit" type="submit" onClick="setCount(1)"><br></p>
      </td>
    </tr>
    <tr align="left">
      <td colspan="2"><p > Or browse the current list of annotated genes
&nbsp;
      <input value="View Gene List" name="submit" type="submit"  onClick="setCount(0)"><br></p>
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

my $bg_color = 0;
my %colors = (0 => "#fffff0",
	      1 => "#ffbd83"
	      );

my $get = new CGI;
my %params = %{$get->Vars};
my $regid = $params{regid};

unless ($regid) {
    $regid=$params{geneID};
    $regid=~s/^\D+0*//;
}

#check if access is authorized
my $projstat=&select($dbh, "SELECT b.project_name,b.status FROM reg_seq a,project b WHERE a.reg_seq_id=$regid AND a.project_id=b.project_id");
my @res = $projstat->fetchrow_array;
undef $dbh;
if($res[1]=~/restricted/i) {
    $dbh = pazar->new( 
		       -globalsearch  =>    'no',		      
		       -host          =>    $ENV{PAZAR_host},
		       -user          =>    $ENV{PAZAR_pubuser},
		       -pass          =>    $ENV{PAZAR_pubpass},
		       -dbname        =>    $ENV{PAZAR_name},
		       -pazar_user    =>    $info{user},
		       -pazar_pass    =>    $info{pass},
		       -drv           =>    $ENV{PAZAR_drv},
		       -project       =>    $res[0]);
} elsif ($res[1]=~/published/i || $res[1]=~/open/i ) {
    $dbh = pazar->new( 
		       -globalsearch  =>    'no',		      
		       -host          =>    $ENV{PAZAR_host},
		       -user          =>    $ENV{PAZAR_pubuser},
		       -pass          =>    $ENV{PAZAR_pubpass},
		       -dbname        =>    $ENV{PAZAR_name},
		       -drv           =>    $ENV{PAZAR_drv},
		       -project       =>    $res[0]);
}   

#get reg_seq and print out all information
my $reg_seq=$dbh->get_reg_seq_by_regseq_id($regid);

my $geneName = $reg_seq->gene_description||'-';
my $gid=$reg_seq->PAZAR_gene_ID;
my $pazargeneid = write_pazarid($gid,'GS');
    
my @ens_coords = $ensdb->get_ens_chr($reg_seq->gene_accession);
$ens_coords[5]=~s/\[.*\]//g;
$ens_coords[5]=~s/\(.*\)//g;
$ens_coords[5]=~s/\.//g;
my $geneDescription = $ens_coords[5]||'-';
my $gene_accession=$reg_seq->gene_accession||'-';
my $seqname=$reg_seq->id||'-';
my $coord="chr".$reg_seq->chromosome.":".$reg_seq->start."-".$reg_seq->end." (strand ".$reg_seq->strand.")";
my $quality=$reg_seq->quality||'-';

my $species = $ensdb->current_org();
$species = ucfirst($species)||'-';

my $transcript=$reg_seq->transcript_accession || '-';

my $tss;
if ($reg_seq->transcript_fuzzy_start == $reg_seq->transcript_fuzzy_end) {
    $tss=$reg_seq->transcript_fuzzy_start||'-';
} else {
    $tss=$reg_seq->transcript_fuzzy_start."-".$reg_seq->transcript_fuzzy_end||'-';
}
#my $regid=$reg_seq->accession_number;
my $id=write_pazarid($regid,'RS');

my $seqstr=chopstr($reg_seq->seq,115)||'-';

#print header

print<<HEADER_TABLE;
<p class="title2">Search Result Details</p>
<table><tr><td>
<table class="summarytable">
<tr><td class="genetabletitle"><span class="title4">Species</span></td><td class="basictd">$species</td></tr>
<tr><td class="genetabletitle"><span class="title4">PAZAR Gene ID</span></td><form name='genelink' method='post' action="$pazar_cgi/gene_search.cgi" enctype='multipart/form-data'><input type='hidden' name='geneID' value="$pazargeneid"><input type='hidden' name='ID_list' value='PAZAR_gene'><td class="basictd"><input type="submit" class="submitLink" value="$pazargeneid">&nbsp;</td></form></tr>
<tr><td class="genetabletitle"><span class="title4">Gene Name (user defined)</span></td><td class="basictd">$geneName</td></tr>
<tr><td class="genetabletitle"><span class="title4">EnsEMBL Gene ID</span></td><td class="basictd">$gene_accession</td></tr>
<tr><td class="genetabletitle"><span class="title4">EnsEMBL Gene Description</span></td><td class="basictd">$geneDescription</td></tr>
<tr><td class="genetabletitle"><span class="title4">Project</span></td><td class="basictd">$res[0]</td></tr>
</table></td></tr><tr><td><table class="evidencetableborder">
<tr><td class="seqtabletitle"><span class="title4">PAZAR Sequence ID</span></td><form name='details' method='post' action="$pazar_cgi/seq_search.cgi" enctype='multipart/form-data'><input type='hidden' name='regid' value="$regid"><td class="basictd"><input type="submit" class="submitLink" value="$id">&nbsp;</td></form></tr>
<tr><td class="seqtabletitle"><span class="title4">Sequence Name</span></td><td class="basictd">$seqname</td></tr>
<tr><td class="seqtabletitle"><span class="title4">Sequence</span></td><td class="basictd"><div style="font-family:monospace;height:62; overflow:auto;">$seqstr</div></td></tr>
<tr><td class="seqtabletitle"><span class="title4">Coordinates</span></td><td class="basictd">$coord</td></tr>
<tr><td class="seqtabletitle"><span class="title4">EnsEMBL Transcript ID</span></td><td class="basictd">$transcript</td></tr>
<tr><td class="seqtabletitle"><span class="title4">Transcription Start Site</span></td><td class="basictd">$tss</td></tr>
<tr><td class="seqtabletitle"><span class="title4">Quality</span></td><td class="basictd">$quality</td></tr>
HEADER_TABLE

print "<tr><form name='display' method='post' action='$pazar_cgi/gff_custom_track.cgi' enctype='multipart/form-data' target='_blank'><td  class=\"seqtabletitle\"><span class=\"title4\">Display</span></td><td  class=\"basictd\"><input type='hidden' name='chr' value='".$reg_seq->chromosome."'><input type='hidden' name='start' value='".$reg_seq->start."'><input type='hidden' name='end' value='".$reg_seq->end."'><input type='hidden' name='species' value='".$reg_seq->binomial_species."'><input type='hidden' name='resource' value='ucsc'><a href='#' onClick=\"javascript:document.display.resource.value='ucsc';document.display.submit();\"><img src='$pazar_html/images/ucsc_logo.png'></a><!--<input type='submit' name='ucsc' value='ucsc' onClick=\"javascript:document.display.resource.value='ucsc';\">-->&nbsp;&nbsp;&nbsp;<a href='#' onClick=\"javascript:document.display.resource.value='ensembl';document.display.submit();\"><img src='$pazar_html/images/ensembl_logo.gif'></a><!--<input type='submit' name='ensembl' value='ensembl' onClick=\"javascript:document.display.resource.value='ensembl';\">--></td></form></tr></table><br><br></td></tr>";



####################### get data objects for retrieving lines of evidence
my @interactors=$dbh->get_interacting_factor_by_regseq_id($regid);
my @expressors=$dbh->get_expression_by_regseq_id($regid);


################### BEGIN INTERACTING EVIDENCE SECTION #####################
#reset row color
$bg_color = 0;
my $count=1;

#only print table if there is at least one result

if(scalar(@interactors)>0)
{
    print "<tr><td><table class=\"evidencetable\"><tr><td class=\"evidencetitle\"><center><span class=\"title1\">Interaction Evidence</span></center></td></tr><tr><td>";
    print "<table class=\"evidencetableborder\"><tr><td width='100' class=\"evidencetabletitle\"><span class=\"title4\">Analysis ID</span><br><span class=\"smallredbold\">click an ID to enter Analysis View</span></td>";
    print "<td width='300' class=\"evidencetabletitle\"><span class=\"title4\">Analysis Method</span></td>";
    print "<td width='150' class=\"evidencetabletitle\"><span class=\"title4\">Cell Type</span></td>";
    print "<td width='200' class=\"evidencetabletitle\"><span class=\"title4\">Interacting<br>Factor/Sample</span></td>";
    print "<td width='100' class=\"evidencetabletitle\"><span class=\"title4\">Interaction<br>Level</span></td>";
    print "<td width='100' class=\"evidencetabletitle\"><span class=\"title4\">Reference<br>(PMID)</span></td>";
    print "<td width='100' class=\"evidencetabletitle\"><span class=\"title4\">Mutants</span></td>";
    print "</tr>";
}

foreach my $inter (@interactors) {
    my @an=$dbh->get_data_by_primary_key('analysis',$inter->{aid});
    my $pazaranid=write_pazarid($inter->{aid},'AN');

    print "<tr><form name='intdetails$count' method='post' action='$pazar_cgi/exp_search.cgi' enctype='multipart/form-data'><input type='hidden' name='aid' value=\"$inter->{aid}\"><td width='100' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'><input type=\"submit\" class=\"submitLink\" value=\"$pazaranid\"></div></td></form>";

    my @met=$dbh->get_data_by_primary_key('method',$an[3]);
    print "<td width='300' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'>$met[0]</div></td>";

    my @cell=$dbh->get_data_by_primary_key('cell',$an[4]);
    my $cellinfo;
    my @cell_cols=('Cell','Tissue','Status','Description','Species');
    for (my $i=0;$i<5;$i++) {
	if ($cell[$i] && $cell[$i] ne '' && $cell[$i] ne '0' && $cell[$i] ne 'NA') {
	    if ($cellinfo) {
		$cellinfo.='<br>';
	    }
	    if ($cell_cols[$i] eq 'Species') {$cell[$i]=lc($cell[$i]);$cell[$i]=ucfirst($cell[$i]);}
	    if ($cell_cols[$i] eq 'Status') {$cell[$i]=lc($cell[$i]);}
	    $cellinfo.=$cell_cols[$i].": ".$cell[$i];
	}
    }
    unless ($cellinfo) {$cellinfo='-';}
    print "<td width='150' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'>$cellinfo</div></td>";

    if ($inter->{tftype} eq 'funct_tf') {
	my $tf = $dbh->create_tf;
	my $complex = $tf->get_tfcomplex_by_id($inter->{tfcomplex}, 'notargets');
	my $tfid=$inter->{tfcomplex};
	my $pazartfid=write_pazarid($tfid,'TF');
	print "<td width='200' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'><form name='tflink$pazartfid$count' method='post' action='$pazar_cgi/tf_search.cgi' enctype='multipart/form-data'><input type='hidden' name='ID_list' value='PAZAR_TF'><input type='hidden' name='geneID' value=\"".$pazartfid."\"><input type=\"submit\" class=\"submitLink\" value=\"$pazartfid\"><br><b>".$complex->name."</b><br></form></div></td>";
    }
    if ($inter->{tftype} eq 'sample') {
	my @sample=$dbh->get_data_by_primary_key('sample',$inter->{tfcomplex});
	my @samplecell=$dbh->get_data_by_primary_key('cell',$sample[1]);
	print "<td width='200' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'>".$sample[0]."&nbsp;".$samplecell[0]."</div></td>";
    }
    
    my ($table,$pazarid,@dat)=$dbh->links_to_data($inter->{olink},'output');
    if ($table eq 'interaction') {
	print "<td width='100' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'>";
	my @data;
	for (my $i=0;$i<(@dat-3);$i++) {
	    if ($dat[$i] && $dat[$i] ne '0') {
		push @data,$dat[$i];
	    }
	}
	print join(" ",@data)."</div></td>";
    }

    my @ref=$dbh->get_data_by_primary_key('ref',$an[6]);
    print "<td width='100' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'>".$ref[0]."</div></td>";

    print "<td width='100' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'>";
    my @mutants=$dbh->get_mutants_by_analysis_id($inter->{aid});
    my $mutnb=0;
    foreach my $mutant (@mutants) {
	my @mut=$dbh->get_data_by_primary_key('mutation_set',$mutant->{mutid});
	unless ($mut[0]==$regid) {next;}
	$mutnb++;
	print "<b>Name:</b> $mut[1]<br>";
	my ($table,$pazarid,@dat)=$dbh->links_to_data($mutant->{olink},'output');
	if ($table eq 'interaction') {
	    my @data;
	    for (my $i=0;$i<(@dat-3);$i++) {
		if ($dat[$i] && $dat[$i] ne '0') {
		    push @data,$dat[$i];
		}
	    }
	    print "<b>Effect:</b> ";
	    print join(":",@data)."<br>";
	}
    }
    if ($mutnb==0) {
	print "None";
    }

#   my @ev=$dbh->get_data_by_primary_key('evidence',$an[1]);
    print "</div></td>";

    $count++;
    print "</tr>";
    $bg_color = 1 - $bg_color;
}

#end table that was created if there were results
if(scalar(@interactors)>0)
{
    print "</table></td></tr></table><br></td></tr>";
}		    


################### BEGIN OTHER EVIDENCE SECTION #####################
#reset row color
$bg_color = 0;

#print table only if results exist
if (scalar(@expressors) > 0)
{
    print "<tr><td><table class=\"evidencetable\"><tr><td class=\"evidencetitle\"><center><span class=\"title1\">Cis-Regulation Evidence</span></center></td></tr><tr><td>";
    print "<table class=\"evidencetableborder\"><tr><td width='100' class=\"evidencetabletitle\"><span class=\"title4\">Analysis ID</span><br><span class=\"smallredbold\">click an ID to enter Analysis View</span></td>";
    print "<td width='300' class=\"evidencetabletitle\"><span class=\"title4\">Analysis Method</span></td>";
    print "<td width='150' class=\"evidencetabletitle\"><span class=\"title4\">Cell Type</span></td>";
    print "<td width='200' class=\"evidencetabletitle\"><span class=\"title4\">Conditions</span></td>";
    print "<td width='100' class=\"evidencetabletitle\"><span class=\"title4\">Expression<br>Level</span></td>";
    print "<td width='100' class=\"evidencetabletitle\"><span class=\"title4\">Reference<br>(PMID)</span></td>";
    print "<td width='100' class=\"evidencetabletitle\"><span class=\"title4\">Mutants</span></td>";
    print "</tr>";
}

foreach my $exp (@expressors) {
    my @an=$dbh->get_data_by_primary_key('analysis',$exp->{aid});
    my $pazaranid=write_pazarid($exp->{aid},'AN');

    print "<tr><form name='expdetails$count' method='post' action='$pazar_cgi/exp_search.cgi' enctype='multipart/form-data'><input type='hidden' name='aid' value=\"$exp->{aid}\"><td width='100' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'><input type=\"submit\" class=\"submitLink\" value=\"$pazaranid\"></div></td></form>";

    my @met=$dbh->get_data_by_primary_key('method',$an[3]);
    print "<td width='300' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'>$met[0]</div></td>";

    my @cell=$dbh->get_data_by_primary_key('cell',$an[4]);
    my $cellinfo;
    my @cell_cols=('Cell','Tissue','Status','Description','Species');
    for (my $i=0;$i<5;$i++) {
	if ($cell[$i] && $cell[$i] ne '' && $cell[$i] ne '0' && $cell[$i] ne 'NA') {
	    if ($cellinfo) {
		$cellinfo.='<br>';
	    }
	    if ($cell_cols[$i] eq 'Species') {$cell[$i]=lc($cell[$i]);$cell[$i]=ucfirst($cell[$i]);}
	    if ($cell_cols[$i] eq 'Status') {$cell[$i]=lc($cell[$i]);}
	    $cellinfo.=$cell_cols[$i].": ".$cell[$i];
	}
    }
    unless ($cellinfo) {$cellinfo='-';}
    print "<td width='150' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'>$cellinfo</div></td>";

    my @conds=@{$exp->{iotype}};
    my @condids=@{$exp->{ioid}};
    print "<td width='200' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'>";
    my $nocond=0;
    for (my $i=0;$i<@conds;$i++) {
	if ($i>0) {print "<hr>";}
	$nocond=1;
	my @dat=$dbh->get_data_by_primary_key($conds[$i],$condids[$i]);
	my $condinfo;
	my @cond_cols=('Type','Molecule','Description','Concentration','Scale');
	for (my $j=0;$j<5;$j++) {
	    if (lc($dat[0]) eq 'co-expression' && $j==2) {
		next;
	    }
	    if ($dat[$j] && $dat[$j] ne '' && $dat[$j] ne 'NA') {
		if ($condinfo) {
		    $condinfo.='<br>';
		}
		$condinfo.=$cond_cols[$j].": ".$dat[$j];
	    }
	}
	print $condinfo;
	if (lc($dat[0]) eq 'co-expression') {
	    my $tfid=$dat[2];
	    my $tf = $dbh->create_tf;
	    my $complex = $tf->get_tfcomplex_by_id($tfid, 'notargets');
	    my $pazartfid=write_pazarid($tfid,'TF');
	    print "<form name='tflink$pazartfid$count' method='post' action='$pazar_cgi/tf_search.cgi' enctype='multipart/form-data'><input type='hidden' name='ID_list' value='PAZAR_TF'><input type='hidden' name='geneID' value=\"".$pazartfid."\"><input type=\"submit\" class=\"submitLink\" value=\"$pazartfid\"><br><b>".$complex->name."</b><br></form>";
	}
    }
    if ($nocond==0) {
	print "None";
    }
    print "</div></td>";

    my ($table,$tableid,@dat)=$dbh->links_to_data($exp->{olink},'output');
    print "<td width='100' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'>";
    my @data;
    for (my $i=0;$i<(@dat-3);$i++) {
	if ($dat[$i] && $dat[$i] ne '0') {
	    push @data,$dat[$i];
	}
    }
    print join(" ",@data)."</div></td>";

    my @ref=$dbh->get_data_by_primary_key('ref',$an[6]);
    print "<td width='100' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'>".$ref[0]."</div></td>";

    print "<td width='100' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'>";
    my @mutants=$dbh->get_mutants_by_analysis_id($exp->{aid});
    my $nomut=0;
    foreach my $mutant (@mutants) {
	my @mut_condids=@{$mutant->{ioid}};
	my $nomatch=0;
	if (@mut_condids!=@condids) {
	    $nomatch=1;
	}
	if (@mut_condids==@condids && @mut_condids!=0) {
	    for (my $j=0;$j<@mut_condids;$j++) {
		unless (grep(/^$mut_condids[$j]$/,@condids)) {
		    $nomatch=1;
		}
	    }
	}
	next if ($nomatch==1);
	my @mut=$dbh->get_data_by_primary_key('mutation_set',$mutant->{mutid});
	$nomut=1;
	print "<b>Name:</b> $mut[1]<br>";
	my ($table,$pazarid,@dat)=$dbh->links_to_data($mutant->{olink},'output');
	if ($table eq 'expression') {
	    my @data;
	    for (my $i=0;$i<(@dat-3);$i++) {
		if ($dat[$i] && $dat[$i] ne '0') {
		    push @data,$dat[$i];
		}
	    }
	    print "<b>Effect:</b> ";
	    print join(":",@data)."<br>";
	}
    }
#   my @ev=$dbh->get_data_by_primary_key('evidence',$an[1]);
    if ($nomut==0) {
	print "None";
    }
    print "</div></td>";
    
    $count++;
    print "</tr>";
    $bg_color = 1 - $bg_color;
}

#end table only if results exist
if(scalar(@expressors)>0)
{
    print "</table>";
}


#end table around evidence
print "</td></tr></table></td></tr></table>";

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

sub convert_id {
    my ($auxdb,$genedb,$geneid,$ens)=@_;
    undef my @id;
    my $add=$genedb . "_to_llid";
# print "Working on $geneid in $genedb; $add";
    @id=$auxdb->$add($geneid);
    my $ll = $id[0];
    my @ensembl;
    if ($ll) { 
	@ensembl=$ens?$ens:$auxdb->llid_to_ens($ll) ;
    }
    return $ensembl[0];
}

sub write_pazarid {
    my $id=shift;
    my $type=shift;
    my $id7d = sprintf "%07d",$id;
    my $pazarid=$type.$id7d;
    return $pazarid;
}
