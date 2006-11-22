#!/usr/local/bin/perl

#use strict;

use pazar;
use pazar::gene;
use pazar::talk;

use HTML::Template;

use CGI qw(:standard);
use CGI::Carp qw(fatalsToBrowser);
#use CGI::Debug( report => 'everything', on => 'anything' );

use Data::Dumper;

require 'getsession.pl';

# open the html header template
my $template = HTML::Template->new(filename => '/usr/local/apache/pazar.info/cgi-bin/header.tmpl');

# fill in template parameters
$template->param(TITLE => 'PAZAR Gene View');
$template->param(JAVASCRIPT_FUNCTION => q{
function setCount(target){

if(target == 0) 
{
document.gene_search.action="http://www.pazar.info/cgi-bin/gene_list.cgi";
document.gene_search.target="Window1";
window.open('about:blank','Window1', 'scrollbars=yes, menubar=no, toolbar=no directories=no, height=800, width=800');
}
if(target == 1) 
{
document.gene_search.target="_self";
document.gene_search.action="http://www.pazar.info/cgi-bin/gene_search.cgi";
}
if(target == 2) 
{
document.gene_search.action="http://www.pazar.info/cgi-bin/genebrowse_alpha.pl";
document.gene_search.target="Window2";
window.open('about:blank','Window2', 'resizable=1,scrollbars=yes, menubar=no, toolbar=no directories=no, height=600, width=650');
}
}
});

if($loggedin eq 'true')
{
    #log out link
    $template->param(LOGOUT => "$info{first} $info{last} logged in. ".'<a href=\'http://www.pazar.info/cgi-bin/logout.pl\'>Log Out</a>');
}
else
{
    #log in link
    $template->param(LOGOUT => '<a href=\'http://www.pazar.info/cgi-bin/login.pl\'>Log In</a>');
}

# send the obligatory Content-Type and print the template output
print "Content-Type: text/html\n\n", $template->output;

print<<page;
          <table border="0" cellpadding="0" cellspacing="0" width="100%">
            <tbody><tr>
              <td colspan="2">
      <p class="title1">PAZAR - Search by Gene</p>
      </td>
    </tr>
<form name="gene_search" method="post" action="" enctype="multipart/form-data" target="">
    <tr align="left">
      <td colspan="2">
<p > Please enter a &nbsp;
      <select name="ID_list">
      <option selected="selected" value="EnsEMBL_gene">EnsEMBL
gene ID</option>
      <option value="EnsEMBL_transcript"> EnsEMBL
transcript
ID</option>
      <option value="EntrezGene"> Entrezgene ID</option>
      <option value="nm"> RefSeq ID</option>
      <option value="swissprot"> Swissprot ID</option>
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
		      -drv           =>    'mysql',
                      -globalsearch  =>    'yes');

my $ensdb = pazar::talk->new(DB=>'ensembl',USER=>$ENV{ENS_USER},PASS=>$ENV{ENS_PASS},HOST=>$ENV{ENS_HOST},DRV=>'mysql');

my $gkdb = pazar::talk->new(DB=>'genekeydb',USER=>$ENV{GKDB_USER},PASS=>$ENV{GKDB_PASS},HOST=>$ENV{GKDB_HOST},DRV=>'mysql');

my $bg_color = 0;
my %colors = (0 => "#fffff0",
	      1 => "#BDE0DC"
	      );

my $get = new CGI;
my %params = %{$get->Vars};
my $accn = $params{geneID};
my $dbaccn = $params{ID_list}||'EnsEMBL_gene';
my $gene;

if ($accn) {
    if ($dbaccn eq 'EnsEMBL_gene') {
	unless ($accn=~/\w{4,}\d{6,}/) {print "<h3>An error occured! Check that the provided ID ($accn) is a $dbaccn ID!</h3>You will have the best results using an EnsEMBL gene ID!"; exit;} else {$gene=$accn;}
    } elsif ($dbaccn eq 'EnsEMBL_transcript') {
	my @gene = $ensdb->ens_transcr_to_gene($accn);
	$gene=$gene[0];
        unless ($gene=~/\w{4,}\d{6,}/) {print "<h3>An error occured! Check that the provided ID ($accn) is a $dbaccn ID!</h3>You will have the best results using an EnsEMBL gene ID!"; exit;}
    } elsif ($dbaccn eq 'EntrezGene') {
	my @gene=$gkdb->llid_to_ens($accn);
	$gene=$gene[0];
	unless ($gene=~/\w{4,}\d{6,}/) {print "<h3>An error occured! Check that the provided ID ($accn) is a $dbaccn ID!</h3>You will have the best results using an EnsEMBL gene ID!"; exit;}
    } else {
	my ($ens,$err) =convert_id($gkdb,$dbaccn,$accn);
	if (!$ens) {print "<h3>An error occured! Check that the provided ID ($accn) is a $dbaccn ID!</h3>You will have the best results using an EnsEMBL gene ID!"; exit;} else {$gene=$ens;}
    }

#get open or published projects
    my %projects;
    my @pubprojects = $dbh->public_projects;
    foreach my $project (@pubprojects) {
	my $projname = $dbh->get_project_name_by_ID($project);
	$projects{$project}=$projname;
    }

#get user's restricted projects if logged in
    if ($loggedin eq 'true') {
	foreach my $proj (@projids) {
	    my $projname = $dbh->get_project_name_by_ID($proj);
	    $projects{$proj}=$projname;
	}
    }

    my $empty=0;

#get the gene name
    my $pazarsth = $dbh->prepare("select * from gene_source where db_accn='$gene'");
    $pazarsth->execute();
		
#get the gene descriptions
    my @geneName;
    my @pazargeneid;
    my @geneproj;
    while (my $res = $pazarsth->fetchrow_hashref) {
	my $pid=$res->{project_id};
	if (grep(/^$pid$/,(keys %projects))) {
	    my $geneName = $res->{description}||'-';
	    push @geneName,$geneName;
	    my $pazargeneid = write_pazarid($res->{gene_source_id},'GS');
	    push @pazargeneid,$pazargeneid;
	    my $proj = $projects{$pid};
	    push @geneproj,$proj;
	}
    }
    my $geneName;
    my $pazargeneid;
    my $geneproj;
    if (!@geneName) {
	$geneName='<td class="basictd">-</td>';
	$pazargeneid='<td class="basictd">-</td>';
	$geneproj='<td class="basictd">-</td>';
    } elsif (@geneName==1) {
	$geneName="<td class=\"basictd\">$geneName[0]</td>";
	$pazargeneid="<td class=\"basictd\"><form name=\"genelink$pazargeneid[0]\" method='post' action='http://www.pazar.info/cgi-bin/gene_search.cgi' enctype='multipart/form-data'><input type='hidden' name='geneID' value=\"$gene\"><input type='hidden' name='ID_list' value='EnsEMBL_gene'><input type=\"submit\" class=\"submitLink\" value=\"$pazargeneid[0]\">&nbsp;</form></td>";
	$geneproj="<td class=\"basictd\">$geneproj[0]</td>";
    } else {
	$geneName='<td><table style="border-collapse:collapse;"><tr>';
	$pazargeneid='<td><table style="border-collapse:collapse;"><tr>';
	$geneproj='<td><table style="border-collapse:collapse;"><tr>';
	for (my $i=0;$i<@geneName;$i++) {
	    $geneName.="<td class='basictd' width=100>$geneName[$i]</td>";
	    $pazargeneid.="<td class='basictd' width=100><form name=\"genelink$pazargeneid[$i]\" method='post' action='http://www.pazar.info/cgi-bin/gene_search.cgi' enctype='multipart/form-data'><input type='hidden' name='geneID' value=\"$gene\"><input type='hidden' name='ID_list' value='EnsEMBL_gene'><input type=\"submit\" class=\"submitLink\" value=\"$pazargeneid[$i]\">&nbsp;</form></td>";
	    $geneproj.="<td class='basictd' width=100>$geneproj[$i]</td>";
	}
	$geneName.='</tr></table></td>';
	$pazargeneid.='</tr></table></td>';
	$geneproj.='</tr></table></td>';
    }

    my @ens_coords = $ensdb->get_ens_chr($gene);
    $ens_coords[5]=~s/\[.*\]//g;
    $ens_coords[5]=~s/\(.*\)//g;
    $ens_coords[5]=~s/\.//g;
    my $geneDescription = $ens_coords[5]||'-';

#get species

    my $species = $ensdb->current_org();
    $species = ucfirst($species)||'-';

#print header

print<<HEADER_TABLE;
<h1>PAZAR Gene View</h1>
<table class="summarytable">
<tr><td class="genetabletitle"><span class="title4">Species</span></td><td class="basictd">$species</td></tr>
<tr><td class="genetabletitle"><span class="title4">PAZAR Gene ID</span></td>$pazargeneid</tr>
<tr><td class="genetabletitle"><span class="title4">Gene Name (user defined)</span></td>$geneName</tr>
<tr><td class="genetabletitle"><span class="title4">EnsEMBL Gene ID</span></td><td class="basictd">$gene</td></tr>
<tr><td class="genetabletitle"><span class="title4">EnsEMBL Gene Description</span></td><td class="basictd">$geneDescription</td></tr>
<tr><td class="genetabletitle"><span class="title4">Project</span></td>$geneproj</tr>
</table><br><br>
HEADER_TABLE



########### start of HTML table
print<<COLNAMES;	    
		<table class="searchtable"><tr>
		    <td width="100" class="genedetailstabletitle"><span class="title4">Project</span></td>
		    
COLNAMES
    print "<td class=\"genedetailstabletitle\" width='100'><span class=\"title4\">RegSeq ID</span><br><span class=\"smallredbold\">click an ID to enter Sequence View</span></td>";
    print "<td width='150' class=\"genedetailstabletitle\"><span class=\"title4\">Sequence Name</span></td>";
    print "<td width='300' class=\"genedetailstabletitle\"><span class=\"title4\">Sequence</span></td>";
    print "<td width='300' class=\"genedetailstabletitle\"><span class=\"title4\">Coordinates</span></td>";
    print "<td width='100' class=\"genedetailstabletitle\"><span class=\"title4\">Display</span></td>";
    print "</tr>";

    foreach my $projid (keys %projects) {
	my $projname = $projects{$projid};
	
#use different connection if it's one of user's restricted projects
	my $restrictedproj = 0;
	foreach $pid (@projids)
	{	    
	    if("$pid" eq "$projid")
	    {
		$restrictedproj = 1;
	    }
	}


	if($restrictedproj == 1)
	{
	    $dbh = pazar->new( 
                              -globalsearch  =>    'no',		      
                              -host          =>    $ENV{PAZAR_host},
			      -user          =>    $ENV{PAZAR_pubuser},
			      -pass          =>    $ENV{PAZAR_pubpass},
			      -dbname        =>    $ENV{PAZAR_name},
			      -pazar_user    =>    $info{user},
			      -pazar_pass    =>    $info{pass},
			      -drv           =>    'mysql',
			      -project       =>    $projname);
    }
	else
	{
	    $dbh = pazar->new( 
                              -globalsearch  =>    'no',		      
                              -host          =>    $ENV{PAZAR_host},
			      -user          =>    $ENV{PAZAR_pubuser},
			      -pass          =>    $ENV{PAZAR_pubpass},
			      -dbname        =>    $ENV{PAZAR_name},
			      -drv           =>    'mysql',
			      -project       =>    $projname);
	}   

#get information for header

#loop through regseqs and print tables
	my $regseq_counter = 0; # counter for naming forms
	my @regseqs = $dbh->get_reg_seqs_by_accn($gene); 
	if (!$regseqs[0]) {
	    $empty++;
	    next;
	} else {
	    my @ens_coords = $ensdb->get_ens_chr($gene);
	    foreach my $regseq (@regseqs) {

		$regseq_counter = $regseq_counter + 1;

#print out default information
		print "<tr>";
		print "<form name='details$regseq_counter' method='post' action='http://www.pazar.info/cgi-bin/seq_search.cgi' enctype='multipart/form-data'><input type='hidden' name='regid' value='".$regseq->accession_number."'>";
		print "<td width='100' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'>$projname</div></td>";
		
		my $id=write_pazarid($regseq->accession_number,'RS');
		print "<td width='100' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'><input type=\"submit\" class=\"submitLink\" value=\"".$id."\"></div></td></form>";

		my $seqname=$regseq->id||'-';
		print "<td width='150' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'>".$seqname."&nbsp;</div></td>";	       

		my $seqstr=chopstr($regseq->seq,40);
		print "<td height=100 width=300 class=\"basictd\" bgcolor=\"$colors{$bg_color}\"><div style=\"font-family:monospace;height:100; width:300;overflow:auto;\">".$seqstr."</div></td>";

		print "<td width='300' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'>chr".$regseq->chromosome.":".$regseq->start."-".$regseq->end." (strand ".$regseq->strand.")</div></td>";

		print "<form name='display$regseq_counter' method='post' action='http://www.pazar.info/cgi-bin/gff_custom_track.cgi' enctype='multipart/form-data' target='_blank'>";

		print "<td width='100' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'><input type='hidden' name='chr' value='".$regseq->chromosome."'><input type='hidden' name='start' value='".$regseq->start."'><input type='hidden' name='end' value='".$regseq->end."'><input type='hidden' name='species' value='".$regseq->binomial_species."'><input type='hidden' name='resource' value='ucsc'><a href='#' onClick=\"javascript:document.display$regseq_counter.resource.value='ucsc';document.display$regseq_counter.submit();\"><img src='http://www.pazar.info/images/ucsc_logo.png'></a><!--<input type='submit' name='ucsc' value='ucsc' onClick=\"javascript:document.display$regseq_counter.resource.value='ucsc';\">--><br><br><a href='#' onClick=\"javascript:document.display$regseq_counter.resource.value='ensembl';document.display$regseq_counter.submit();\"><img src='http://www.pazar.info/images/ensembl_logo.gif'></a><!--<input type='submit' name='ensembl' value='ensembl' onClick=\"javascript:document.display$regseq_counter.resource.value='ensembl';\">--></div></td></form>";
		print "</tr>";
		$bg_color =  1 - $bg_color;
	    }
	}
    }
    print "</table>";
    if (scalar(keys %projects)==$empty) {
	print "<h3>There is currently no available annotation for gene $gene in PAZAR!<br>Do not hesitate to create your own project and enter information about this gene or any other gene!</h3>";
    }
}




# print out the html tail template
my $template_tail = HTML::Template->new(filename => '/usr/local/apache/pazar.info/cgi-bin/tail.tmpl');
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
