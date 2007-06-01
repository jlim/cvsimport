#!/usr/local/bin/perl

#use strict;ø

use pazar;
use pazar::gene;
use pazar::talk;

use HTML::Template;

use CGI qw(:standard);
use CGI::Carp qw(fatalsToBrowser);
###use CGI::Debug( report => 'everything', on => 'anything' );

#use Data::Dumper;

my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};

require "$pazarcgipath/getsession.pl";

# open the html header template
my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");

# fill in template parameters
$template->param(TITLE => 'PAZAR Analysis View');
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
<h1>PAZAR Analysis View</h1>
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
	      1 => "#B7DDA6"
	      );

my $get = new CGI;
my %params = %{$get->Vars};
my $aid = $params{aid};

#check if access is authorized
my $projstat=&select($dbh, "SELECT b.project_name,b.status FROM analysis a,project b WHERE a.analysis_id=$aid AND a.project_id=b.project_id");
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

my @an=$dbh->get_data_by_primary_key('analysis',$aid);
my $pazaranid=write_pazarid($aid,'AN');
my @met=$dbh->get_data_by_primary_key('method',$an[3]);
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
my @time=$dbh->get_data_by_primary_key('time',$an[5]);
my $timeinfo;
my @time_cols=('Name','Description','Scale','Range Start','Range End');
for (my $i=0;$i<5;$i++) {
    if ($time[$i] && $time[$i] ne '' && $time[$i] ne '0' && $time[$i] ne 'NA') {
	if ($timeinfo) {
	    $timeinfo.='<br>';
	}
	$timeinfo.=$time_cols[$i].": ".$time[$i];
    }
}
unless ($timeinfo) {$timeinfo='-';}
my @ref=$dbh->get_data_by_primary_key('ref',$an[6]);
my $comments=$an[7]||'-';
my @ev=$dbh->get_data_by_primary_key('evidence',$an[1]);
my $evinfo='Type: '.$ev[0].'<br>Status: '.$ev[1];
my @user=$dbh->get_data_by_primary_key('users',$an[0]);
my $userinfo;
unless ($user[0]||$user[1]) {
    $userinfo=$user[4];
} else {
    $userinfo=$user[0].' '.$user[1];
}

#print header

print<<HEADER_TABLE;
<p class="title2">Search Result Details</p>
<table class="summarytable">
<tr><td class="analysistabletitle"><span class="title4">Analysis ID</span></td><form name='intdetails' method='post' action="$pazar_cgi/exp_search.cgi" enctype='multipart/form-data'><input type='hidden' name='aid' value="$params{aid}"><td class="basictd"><input type="submit" class="submitLink" value="$pazaranid"></td></form></tr>
<tr><td class="analysistabletitle"><span class="title4">Analysis Method</span></td><td class="basictd">$met[0]</td></tr>
<tr><td class="analysistabletitle"><span class="title4">Cell Type</span></td><td class="basictd">$cellinfo</td></tr>
<tr><td class="analysistabletitle"><span class="title4">Time</span></td><td class="basictd">$timeinfo</td></tr>
<tr><td class="analysistabletitle"><span class="title4">Reference (PMID)</span></td><td class="basictd">$ref[0]</td></tr>
<tr><td class="analysistabletitle"><span class="title4">Comments</span></td><td class="basictd">$comments</td></tr>
<tr><td class="analysistabletitle"><span class="title4">Evidence</span></td><td class="basictd">$evinfo</td></tr>
<tr><td class="analysistabletitle"><span class="title4">Annotator</span></td><td class="basictd">$userinfo</td></tr>
<tr><td class="analysistabletitle"><span class="title4">Project</span></td><td class="basictd">$res[0]</td></tr></table>
HEADER_TABLE

my @analysis=$dbh->get_analysis_structure_by_id($aid);
my @idlist;
my %results;
my $mode;
my %sort;
foreach my $link (@analysis) {
    my @out_types=$link->get_output_types;
    $mode=$out_types[0];
    my ($type,$id,@ins)=$link->next_relationship;
    while ($type) {
	unless (grep(/^$id$/,@idlist)) {
	    push @idlist, $id;
	    my @seq;
	    my @tf;
	    my @condid;
	    foreach my $in (@ins) {
		my ($intable,$inid,@indata)=$dbh->links_to_data($in,'input');
		if ($intable eq 'reg_seq'||$intable eq 'construct'||$intable eq 'mutation_set') {
		    push @seq, [$intable,$inid];
		    push @{$sort{$intable}}, $id;
		} elsif ($intable eq 'funct_tf'||$intable eq 'sample') {
		    push @tf, [$intable,$inid];
		} elsif ($intable eq 'bio_condition') {
		    push @condid, $inid;
		}
	    }
	    $results{$id}{'seq'}=\@seq;
	    $results{$id}{'tf'}=\@tf;
	    $results{$id}{'condid'}=\@condid;
	}
	($type,$id,@ins)=$link->next_relationship;
    }
}
my @sorted_keys = @{$sort{'reg_seq'}};
push @sorted_keys, @{$sort{'mutation_set'}};
push @sorted_keys, @{$sort{'construct'}};

my $count=0;
if ($mode eq 'expression') {
    print "<table class=\"evidencedetailstableborder\"><tr>";
    print "<td width='80' class=\"analysisdetailstabletitle\"><span class=\"title4\">Sequence Type</span></td>";
    print "<td class=\"analysisdetailstabletitle\" width='100'><span class=\"title4\">Sequence ID</span></td>";
    print "<td width='150' class=\"analysisdetailstabletitle\"><span class=\"title4\">Gene ID</span></td>";
    print "<td width='300' class=\"analysisdetailstabletitle\"><span class=\"title4\">Sequence</span></td>";
    print "<td width='250' class=\"analysisdetailstabletitle\"><span class=\"title4\">Sequence Info</span></td>";
    print "<td width='100' class=\"analysisdetailstabletitle\"><span class=\"title4\">Expression Level</span></td>";
    print "<td width='200' class=\"analysisdetailstabletitle\"><span class=\"title4\">Condition(s)</span></td>";
    print "</tr>";

    foreach my $key (@sorted_keys) {
	my $seqtable=$results{$key}{'seq'}->[0]->[0];
	my $seqid=$results{$key}{'seq'}->[0]->[1];
	$count++;
#get reg_seq and print out all information
	if ($seqtable eq 'reg_seq') {
	    my $reg_seq=$dbh->get_reg_seq_by_regseq_id($seqid);
	    print "<td width='80' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'>Genomic Sequence</div></td>";

	    my $regid=$reg_seq->accession_number;
	    my $pazarregid=write_pazarid($regid,'RS');
	    my $seqname=$reg_seq->id;
	    print "<td width='100' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'><form name='seqlink$count' method='post' action='$pazar_cgi/seq_search.cgi' enctype='multipart/form-data'><input type='hidden' name='regid' value=\"$regid\"><input type=\"submit\" class=\"submitLink\" value=\"$pazarregid\"><br>$seqname</form></div></td>";
	    my $gid=$reg_seq->PAZAR_gene_ID;
	    my $pazargeneid = write_pazarid($gid,'GS');
	    my $gene_accession=$reg_seq->gene_accession;
	    my @ens_coords = $ensdb->get_ens_chr($reg_seq->gene_accession);
	    $ens_coords[5]=~s/\[.*\]//g;
	    $ens_coords[5]=~s/\(.*\)//g;
	    $ens_coords[5]=~s/\.//g;
	    my $species = $ensdb->current_org();
	    $species = ucfirst($species)||'-';
	    print "<td width='150' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'><form name='genelink$count' method='post' action='$pazar_cgi/gene_search.cgi' enctype='multipart/form-data'><input type='hidden' name='geneID' value=\"$pazargeneid\"><input type='hidden' name='ID_list' value='PAZAR_gene'><input type=\"submit\" class=\"submitLink\" value=\"$pazargeneid\"><br><b>$ens_coords[5]</b><br>$species</form></div></td>";

	    my $seqstr=chopstr($reg_seq->seq,40)||'-';
		print "<td height=100 width=300 class=\"basictd\" bgcolor=\"$colors{$bg_color}\"><div style=\"font-family:monospace;height:100; width:300;overflow:auto;\">".$seqstr."</div></td>";

	    my $coord="chr".$reg_seq->chromosome.":".$reg_seq->start."-".$reg_seq->end." (strand ".$reg_seq->strand.")";
	    print "<td width='250' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'><b>Coordinates:</b><br>$coord</div></td>";
	}

#get mutant and print out all information
	if ($seqtable eq 'mutation_set') {
	    my @mut=$dbh->get_data_by_primary_key('mutation_set',$seqid);
	    my $regid=$mut[0];
	    my $pazarregid=write_pazarid($regid,'RS');
	    print "<td width='80' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'>Mutant of Sequence<form name='seqlink$count' method='post' action='$pazar_cgi/seq_search.cgi' enctype='multipart/form-data'><input type='hidden' name='regid' value=\"$regid\"><input type=\"submit\" class=\"submitLink\" value=\"$pazarregid\"></form></div></td>";

	    my $pazarmutid=write_pazarid($seqid,'MS');
	    my $seqname=$mut[1];
	    print "<td width='100' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'><b>$pazarmutid</b><br>$seqname</div></td>";

	    my $reg_seq=$dbh->get_reg_seq_by_regseq_id($regid);
	    my $gid=$reg_seq->PAZAR_gene_ID;
	    my $pazargeneid = write_pazarid($gid,'GS');
	    my $gene_accession=$reg_seq->gene_accession;
	    my @ens_coords = $ensdb->get_ens_chr($reg_seq->gene_accession);
	    $ens_coords[5]=~s/\[.*\]//g;
	    $ens_coords[5]=~s/\(.*\)//g;
	    $ens_coords[5]=~s/\.//g;
	    my $species = $ensdb->current_org();
	    $species = ucfirst($species)||'-';
	    print "<td width='150' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'><form name='genelink$count' method='post' action='$pazar_cgi/gene_search.cgi' enctype='multipart/form-data'><input type='hidden' name='geneID' value=\"$pazargeneid\"><input type='hidden' name='ID_list' value='PAZAR_gene'><input type=\"submit\" class=\"submitLink\" value=\"$pazargeneid\"><br><b>$ens_coords[5]</b><br>$species</form></div></td>";

	    my $seqstr=chopstr($mut[4],40)||'-';
	    print "<td height=100 width=300 class=\"basictd\" bgcolor=\"$colors{$bg_color}\"><div style=\"font-family:monospace;height:100; width:300;overflow:auto;\">".$seqstr."</div></td>";

	    print "<td width='250' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'>";
	    if ($mut[2]>0) {
		my @mutmet=$dbh->get_data_by_primary_key('method',$mut[2]);
		print "<b>Method:</b> $mutmet[0]<br>";
	    }
	    if ($mut[3]>0) {
		my @mutref=$dbh->get_data_by_primary_key('ref',$mut[3]);
		print "<b>PMID:</b> $mutref[0]<br>";
	    }
	    if ($mut[5] && $mut[5] ne '0') {
		print "<b>Comments:</b> $mut[5]<br>";
	    }
	    print "</div></td>";
	}

#get construct and print out all information
	if ($seqtable eq 'construct') {
	    my @construct=$dbh->get_data_by_primary_key('construct',$seqid);
	    my $pazarcoid=write_pazarid($seqid,'CO');
	    my $seqname=$construct[0];
	    print "<td width='80' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'>Artificial Sequence</div></td>";
	    print "<td width='100' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'>$pazarcoid<br>$seqname</div></td>";
	    print "<td width='150' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'>-</div></td>";

	    my $seqstr=chopstr($construct[2],40)||'-';
		print "<td height=100 width=300 class=\"basictd\" bgcolor=\"$colors{$bg_color}\"><div style=\"font-family:monospace;height:100; width:300;overflow:auto;\">".$seqstr."</div></td>";

	    my $desc=$construct[1]||'-';
	    print "<td width='250' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'><b>Description:</b><br>$desc</div></td>";
	}

	my ($outtable,$outid,@outdat)=$dbh->links_to_data($key,'output');
	print "<td width='100' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'>";
	my @outdata;
	for (my $i=0;$i<(@outdat-3);$i++) {
	    if ($outdat[$i] && $outdat[$i] ne '0') {
		push @outdata,$outdat[$i];
	    }
	}
	print join(" ",@outdata)."</div></td>";

	my @condids=@{$results{$key}{'condid'}};
	print "<td width='200' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'>";
	my $nocond=0;
	for (my $i=0;$i<@condids;$i++) {
	    if ($i>0) {print "<hr>";}
	    $nocond=1;
	    my @dat=$dbh->get_data_by_primary_key('bio_condition',$condids[$i]);
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
		my $tf = $dbh->create_tf;
		my $tfid=$dat[2];
		my $complex = $tf->get_tfcomplex_by_id($tfid, 'notargets');
		my $pazartfid=write_pazarid($tfid,'TF');
		print "<form name='tflink$pazartfid$count' method='post' action='$pazar_cgi/tf_search.cgi' enctype='multipart/form-data'><input type='hidden' name='ID_list' value='PAZAR_TF'><input type='hidden' name='geneID' value=\"".$pazartfid."\"><input type=\"submit\" class=\"submitLink\" value=\"$pazartfid\"><br><b>".$complex->name."</b><br></form>";
	    }
	}
	if ($nocond==0) {
	    print "None";
	}
	print "</div></td>";
	print "</tr>";
	$bg_color = 1 - $bg_color;
    }
} elsif ($mode eq 'interaction') {
    print "<table class=\"evidencedetailstableborder\"><tr>";
    print "<td width='80' class=\"analysisdetailstabletitle\"><span class=\"title4\">Sequence Type</span></td>";
    print "<td class=\"analysisdetailstabletitle\" width='100'><span class=\"title4\">Sequence ID</span></td>";
    print "<td width='150' class=\"analysisdetailstabletitle\"><span class=\"title4\">Gene ID</span></td>";
    print "<td width='300' class=\"analysisdetailstabletitle\"><span class=\"title4\">Sequence</span></td>";
    print "<td width='250' class=\"analysisdetailstabletitle\"><span class=\"title4\">Sequence Info</span></td>";
    print "<td width='100' class=\"analysisdetailstabletitle\"><span class=\"title4\">Interaction Level</span></td>";
    print "<td width='200' class=\"analysisdetailstabletitle\"><span class=\"title4\">Interacting Factor/Sample</span></td>";
    print "</tr>";

    foreach my $key (@sorted_keys) {
	my $seqtable=$results{$key}{'seq'}->[0]->[0];
	my $seqid=$results{$key}{'seq'}->[0]->[1];
	my $tftable=$results{$key}{'tf'}->[0]->[0];
	my $tfid=$results{$key}{'tf'}->[0]->[1];
	$count++;
#get reg_seq and print out all information
	if ($seqtable eq 'reg_seq') {
	    my $reg_seq=$dbh->get_reg_seq_by_regseq_id($seqid);
	    print "<td width='80' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'>Genomic Sequence</div></td>";

	    my $regid=$reg_seq->accession_number;
	    my $pazarregid=write_pazarid($regid,'RS');
	    my $seqname=$reg_seq->id;
	    print "<td width='100' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'><form name='seqlink$count' method='post' action='$pazar_cgi/seq_search.cgi' enctype='multipart/form-data'><input type='hidden' name='regid' value=\"$regid\"><input type=\"submit\" class=\"submitLink\" value=\"$pazarregid\"><br>$seqname</form></div></td>";
	    my $gid=$reg_seq->PAZAR_gene_ID;
	    my $pazargeneid = write_pazarid($gid,'GS');
	    my $gene_accession=$reg_seq->gene_accession;
	    my @ens_coords = $ensdb->get_ens_chr($reg_seq->gene_accession);
	    $ens_coords[5]=~s/\[.*\]//g;
	    $ens_coords[5]=~s/\(.*\)//g;
	    $ens_coords[5]=~s/\.//g;
	    my $species = $ensdb->current_org();
	    $species = ucfirst($species)||'-';
	    print "<td width='150' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'><form name='genelink$count' method='post' action='$pazar_cgi/gene_search.cgi' enctype='multipart/form-data'><input type='hidden' name='geneID' value=\"$pazargeneid\"><input type='hidden' name='ID_list' value='PAZAR_gene'><input type=\"submit\" class=\"submitLink\" value=\"$pazargeneid\"><br><b>$ens_coords[5]</b><br>$species</form></div></td>";

	    my $seqstr=chopstr($reg_seq->seq,40)||'-';
		print "<td height=100 width=300 class=\"basictd\" bgcolor=\"$colors{$bg_color}\"><div style=\"font-family:monospace;height:100; width:300;overflow:auto;\">".$seqstr."</div></td>";

	    my $coord="chr".$reg_seq->chromosome.":".$reg_seq->start."-".$reg_seq->end." (strand ".$reg_seq->strand.")";
	    print "<td width='250' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'>Coordinates:<br>$coord</div></td>";
	}
#get mutant and print out all information
	if ($seqtable eq 'mutation_set') {
	    my @mut=$dbh->get_data_by_primary_key('mutation_set',$seqid);
	    my $regid=$mut[0];
	    my $pazarregid=write_pazarid($regid,'RS');
	    print "<td width='80' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'>Mutant of Sequence<form name='seqlink$count' method='post' action='$pazar_cgi/seq_search.cgi' enctype='multipart/form-data'><input type='hidden' name='regid' value=\"$regid\"><input type=\"submit\" class=\"submitLink\" value=\"$pazarregid\"></form></div></td>";

	    my $pazarmutid=write_pazarid($seqid,'MS');
	    my $seqname=$mut[1];
	    print "<td width='100' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'><b>$pazarmutid</b><br>$seqname</div></td>";

	    my $reg_seq=$dbh->get_reg_seq_by_regseq_id($regid);
	    my $gid=$reg_seq->PAZAR_gene_ID;
	    my $pazargeneid = write_pazarid($gid,'GS');
	    my $gene_accession=$reg_seq->gene_accession;
	    my @ens_coords = $ensdb->get_ens_chr($reg_seq->gene_accession);
	    $ens_coords[5]=~s/\[.*\]//g;
	    $ens_coords[5]=~s/\(.*\)//g;
	    $ens_coords[5]=~s/\.//g;
	    my $species = $ensdb->current_org();
	    $species = ucfirst($species)||'-';
	    print "<td width='150' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'><form name='genelink$count' method='post' action='$pazar_cgi/gene_search.cgi' enctype='multipart/form-data'><input type='hidden' name='geneID' value=\"$pazargeneid\"><input type='hidden' name='ID_list' value='PAZAR_gene'><input type=\"submit\" class=\"submitLink\" value=\"$pazargeneid\"><br><b>$ens_coords[5]</b><br>$species</form></div></td>";

	    my $seqstr=chopstr($mut[4],40)||'-';
	    print "<td height=100 width=300 class=\"basictd\" bgcolor=\"$colors{$bg_color}\"><div style=\"font-family:monospace;height:100; width:300;overflow:auto;\">".$seqstr."</div></td>";

	    print "<td width='250' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'>";
	    if ($mut[2]>0) {
		my @mutmet=$dbh->get_data_by_primary_key('method',$mut[2]);
		print "<b>Method:</b> $mutmet[0]<br>";
	    }
	    if ($mut[3]>0) {
		my @mutref=$dbh->get_data_by_primary_key('ref',$mut[3]);
		print "<b>PMID:</b> $mutref[0]<br>";
	    }
	    if ($mut[5] && $mut[5] ne '0') {
		print "<b>Comments:</b> $mut[5]<br>";
	    }
	    print "</div></td>";
	}

#get construct and print out all information
	if ($seqtable eq 'construct') {
	    my @construct=$dbh->get_data_by_primary_key('construct',$seqid);
	    my $pazarcoid=write_pazarid($seqid,'CO');
	    my $seqname=$construct[0];
	    print "<td width='80' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'>Artificial Sequence</div></td>";
	    print "<td width='100' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'>$pazarcoid<br>$seqname</div></td>";
	    print "<td width='150' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'>-</div></td>";

	    my $seqstr=chopstr($construct[2],40)||'-';
		print "<td height=100 width=300 class=\"basictd\" bgcolor=\"$colors{$bg_color}\"><div style=\"font-family:monospace;height:100; width:300;overflow:auto;\">".$seqstr."</div></td>";

	    my $desc=$construct[1]||'-';
	    print "<td width='250' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'><b>Description:</b><br>$desc</div></td>";
	}

	my ($outtable,$outid,@outdat)=$dbh->links_to_data($key,'output');
	print "<td width='100' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'>";
	my @outdata;
	for (my $i=0;$i<(@outdat-3);$i++) {
	    if ($outdat[$i] && $outdat[$i] ne '0') {
		push @outdata,$outdat[$i];
	    }
	}
	print join(" ",@outdata)."</div></td>";

	if ($tftable eq 'funct_tf') {
	    my $tf = $dbh->create_tf;
	    my $complex = $tf->get_tfcomplex_by_id($tfid, 'notargets');
	    my $pazartfid=write_pazarid($tfid,'TF');
	    print "<td width='200' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'><form name='tflink$pazartfid$count' method='post' action='$pazar_cgi/tf_search.cgi' enctype='multipart/form-data'><input type='hidden' name='ID_list' value='PAZAR_TF'><input type='hidden' name='geneID' value=\"".$pazartfid."\"><input type=\"submit\" class=\"submitLink\" value=\"$pazartfid\"><br><b>".$complex->name."</b><br></form></div></td>";
	} elsif ($tftable eq 'sample') {
	    my @sample=$dbh->get_data_by_primary_key('sample',$tfid);
	    my @samplecell=$dbh->get_data_by_primary_key('cell',$sample[1]);
	    print "<td width='200' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'>".$sample[0]."&nbsp;".$samplecell[0]."</div></td>";
	}
	print "</tr>";
    	$bg_color = 1 - $bg_color;
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
