#!/usr/local/bin/perl

use lib '/space/usr/local/src/ensembl-36/ensembl/modules/';
use lib '/space/usr/local/src/bioperl-live/';

#use strict;

use pazar;
use pazar::gene;
use pazar::talk;

use HTML::Template;

use CGI qw(:standard);
use CGI::Carp qw(fatalsToBrowser);
use CGI::Debug( report => 'everything', on => 'anything' );

use Data::Dumper;

require 'getsession.pl';

# open the html header template
my $template = HTML::Template->new(filename => 'header.tmpl');

# fill in template parameters
$template->param(TITLE => 'PAZAR Gene Search');

if($loggedin eq 'true')
{
    #log out link
    $template->param(LOGOUT => "$info{first} $info{last} logged in. ".'<a href=\'logout.pl\'>Log Out</a>');
}
else
{
    #log in link
    $template->param(LOGOUT => '<a href=\'login.pl\'>Log In</a>');
}

# send the obligatory Content-Type and print the template output
print "Content-Type: text/html\n\n", $template->output;

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
#	      1 => "#9ad3e2"
	      1 => "#ffbd83"
	      );

my $get = new CGI;
my %params = %{$get->Vars};
my $accn = $params{geneID};
my $dbaccn = $params{ID_list};
my $gene;

if (!$accn) {
    print "<p class=\"warning\">Please provide a gene ID!</p>\n";
} else {
    if ($dbaccn eq 'EnsEMBL_gene') {
	unless ($accn=~/\w{4,}\d{6,}/) {print "<p class=\"warning\">Conversion failed for $accn! Maybe it is not a $dbaccn ID!</p>"; exit;} else {$gene=$accn;}
    } elsif ($dbaccn eq 'EnsEMBL_transcript') {
	my @gene = $ensdb->ens_transcr_to_gene($accn);
	$gene=$gene[0];
        unless ($gene=~/\w{4,}\d{6,}/) {print "<p class=\"warning\">Conversion failed for $accn! Maybe it is not a $dbaccn ID!</p>"; exit;}
    } elsif ($dbaccn eq 'EntrezGene') {
	my @gene=$gkdb->llid_to_ens($accn);
	$gene=$gene[0];
	unless ($gene=~/\w{4,}\d{6,}/) {print "<p class=\"warning\">Conversion failed for $accn! Maybe it is not a $dbaccn ID!</p>"; exit;}
    } else {
	my ($ens,$err) =convert_id($gkdb,$dbaccn,$accn);
	if (!$ens) {print "<p class=\"warning\">Conversion failed for $accn! Maybe it is not a $dbaccn ID!</p>"; exit;} else {$gene=$ens;}
    }

#get open or published projects

    my $projectsth=&select($dbh, "SELECT * FROM project WHERE status='open' OR status='published'");
    my @projects;
    while (my $project=$projectsth->fetchrow_hashref) {
	push @projects, [$project->{project_name},$project->{project_id}];
	
    }

    my $empty=0;


#get the gene name
    my $pazarsth = $dbh->prepare("select * from gene_source where db_accn='$gene'");
    $pazarsth->execute();
		
#pazar load tfs from results for each result
    my $res = $pazarsth->fetchrow_hashref;

    my $geneName = $res->{description};
    
    my @ens_coords = $ensdb->get_ens_chr($gene);
    my @des = split('\(',$ens_coords[5]);
    my @desc = split('\[',$des[0]);    
    my $geneDescription = $desc[0];

#get species

    my $sources_projects_handle = &select($dbh,"select db_source_id,project_id from gene_source where db_accn='$gene'");
#just get the first one
    my $href = $sources_projects_handle->fetchrow_hashref;
 
    my $tmp_src = $href->{db_source_id};
    my $tmp_proj =  $href->{project_id};
    my $specieshandle = &select($dbh,"select species from location where db_source_id='$tmp_src' and project_id='$tmp_proj'");
#just get the first one
    my $specieshref = $specieshandle->fetchrow_hashref;
    my $tempspecies = $specieshref->{species};
#print header

print<<HEADER_TABLE;

<table width='1200' border=1 cellspacing=0>
<tr><td align="center" valign="top" bgcolor="#39aecb"><span class="title4">Gene Name</span></td><td align='left'>&nbsp;&nbsp;&nbsp;&nbsp;$geneName</td></tr>
<tr><td align="center" valign="top" bgcolor="#39aecb"><span class="title4">Accession</span></td><td align='left'>&nbsp;&nbsp;&nbsp;&nbsp;$gene</td></tr>
<tr><td align="center" valign="top" bgcolor="#39aecb"><span class="title4">Description</span></td><td align='left'>&nbsp;&nbsp;&nbsp;&nbsp;$geneDescription</td></tr>
<tr><td align="center" valign="top" bgcolor="#39aecb"><span class="title4">Species</span></td><td align='left'>&nbsp;&nbsp;&nbsp;&nbsp;$tempspecies</td></tr>
</table>
HEADER_TABLE



########### start of HTML table
#get user's restricted projects if logged in


	if ($loggedin eq 'true') {
	    foreach my $proj (@projids) {
		my $restricted=&select($dbh, "SELECT project_name FROM project WHERE project_id='$proj' and status='restricted'");
		my @restr_proj=$restricted->fetchrow_array();
		if (@restr_proj) {
		    push @projects, [$restr_proj[0],$proj];
#		    push @projects, ["some project",$proj];
=pod
		    my $pname = "";
		    foreach my $p (@projids)
		    {
			$pname = $pname.",".$p;
		    }

		    push @projects, [$pname,$proj];
=cut
		}
	    }
	}


    foreach my $arrayref (@projects) {
	my $projname = $arrayref->[0];
	
#use different connection if it's one of user's restricted projects
	my $restrictedproj = 0;
	foreach $pid (@projids)
	{	    
	    if("$pid" eq "$arrayref->[1]")
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
	my @regseqs = $dbh->get_reg_seqs_by_accn($gene); 
	if (!$regseqs[0]) {
	    $empty++;
	    next;
	} else {
	    my @ens_coords = $ensdb->get_ens_chr($gene);
	    foreach my $regseq (@regseqs) {

#reset row color
		$bg_color = 0;

#start table
print<<COLNAMES;	    
		<table width='1200' border=1 cellspacing=0><tr><td>
		    <table width='100%' border="1" cellspacing="0" cellpadding="3">
		    <tr>
		    <td width="150" align="center" valign="top" bgcolor="#61b9cf"><span class="title4">Project</span></td>
		    
COLNAMES

		print "<td width='150' align='center' valign='top' bgcolor='#61b9cf'><span class=\"title4\">Gene/Transcript ID</span></td>";

		if ($params{tss} eq 'on')
		{
		    print "<td width='180' align='center' valign='top' bgcolor='#61b9cf'><span class=\"title4\">Transcription Start Site</span></td>";
		}
		    print "<td width='150' align='center' valign='top' bgcolor='#61b9cf'><span class=\"title4\">Sequence Name</span></td>";
		    print "<td align='center' valign='top' bgcolor='#61b9cf'><span class=\"title4\">Sequence</span></td>";
		    print "<td width='150' align='center' valign='top' bgcolor='#61b9cf'><span class=\"title4\">Coordinates</span></td>";

		if ($params{quality} eq 'on') {
		    print "<td width='100' align='center' valign='top' bgcolor='#61b9cf'><span class=\"title4\">Quality</span></td>";
		}
		print "</tr>";
		
#print out default information
		print "<tr>";
		print "<td width='100' align='center' bgcolor=\"$colors{$bg_color}\">$projname</td>";
		
		my $transcript=$regseq->transcript_accession || 'Transcript Not Specified';
		print "<td width='150' align='center' bgcolor=\"$colors{$bg_color}\">".$transcript."</td>";

		if ($params{tss} eq 'on') {
		    if ($regseq->transcript_fuzzy_start == $regseq->transcript_fuzzy_end) { print "<td width='150' align='center' bgcolor=\"$colors{$bg_color}\">".$regseq->transcript_fuzzy_start."</td>";} else {
			print "<td width='180' align='center' bgcolor=\"$colors{$bg_color}\">".$regseq->transcript_fuzzy_start."-".$regseq->transcript_fuzzy_end."</td>";
		    }
		}

		print "<td width='150' align='center' bgcolor=\"$colors{$bg_color}\">".$regseq->id."&nbsp;</td>";	       
		print "<td align='left' bgcolor=\"$colors{$bg_color}\">".chopstr($regseq->seq,40)."&nbsp;</td>";
		print "<td width='150' align='center' bgcolor=\"$colors{$bg_color}\">".$regseq->chromosome." (".$regseq->strand.") ".$regseq->start."-".$regseq->end."</td>";

		if ($params{quality} eq 'on') {
		    print "<td width='100' align='center' bgcolor=\"$colors{$bg_color}\">".$regseq->quality."&nbsp;</td>";
		}

		print "</tr></table>";
		print "<p></td></tr>";

####################### get data objects for retrieving lines of evidence
		my @interactors=$dbh->get_interacting_factor_by_regseq_id($regseq->accession_number);
		my @expressors=$dbh->get_expression_by_regseq_id($regseq->accession_number);
########################
if(scalar(@interactors)>0 || scalar(@expressors)>0)
{
		print "<tr><td align='center' bgcolor='#ff9a40'><center><span class=\"title4\">Lines of Evidence</span></center></td></tr><tr><td>";
}
################### BEGIN INTERACTING EVIDENCE SECTION #####################
#reset row color
		$bg_color = 0;
		my $count=1;
		
		if ($params{tf} eq 'on' || $params{tf_analysis} eq 'on' || $params{tf_reference} eq 'on' || $params{tf_interaction} eq 'on' || $params{tf_evidence} eq 'on') {
		    
#    print "<td align='center' bgcolor=\"$colors{$bg_color}\">";

#only print table if there is at least one result

		    if(scalar(@interactors)>0)
		    {
			print "<table width='100%' cellspacing=0 border=1><tr><td width='150' align='center' valign='top' bgcolor='#ff9a40'><span class=\"title4\">&nbsp;</span></td>";
			
			if ($params{tf} eq 'on') {
			    print "<td width='200' align='center' valign='top' bgcolor='#ff9a40'><span class=\"title4\">Transcription Factor</span></td>";
			}
			if ($params{tf_analysis} eq 'on' || $params{other_analysis} eq 'on')
			{
			    print "<td align='center' valign='top' bgcolor='#ff9a40'><span class=\"title4\">Analysis Details</span></td>";
			}
			if ($params{tf_reference} eq 'on' || $params{other_reference} eq 'on')
			{
			    print "<td width='150' align='center' valign='top' bgcolor='#ff9a40'><span class=\"title4\">Reference (PMID)</span></td>";
			}
			if ($params{tf_interaction} eq 'on')
			{
			    print "<td width='100' align='center' valign='top' bgcolor='#ff9a40'><span class=\"title4\">Interaction Description</span></td>";
			}
			if ($params{other_effect} eq 'on')
			{
			    print "<td width='150' align='center' valign='top' bgcolor='#ff9a40'><span class=\"title4\">Effects</span></td>";
			}
			if ($params{tf_evidence} eq 'on' || $params{other_evidence} eq 'on')
			{
			    print "<td width='150' align='center' valign='top' bgcolor='#ff9a40'><span class=\"title4\">Evidence</span></td>";
			}
			print "</tr>";
		    }
		}
		

		foreach my $inter (@interactors) {
		    if ($params{tf} eq 'on' || $params{tf_analysis} eq 'on' || $params{tf_reference} eq 'on' || $params{tf_interaction} eq 'on' || $params{tf_evidence} eq 'on') {
			print "<tr><td width='150' align='center' bgcolor=\"$colors{$bg_color}\">Line of evidence $count</td>";
			if ($params{tf} eq 'on') {
			    my $tf = $dbh->create_tf;
			    my $complex = $tf->get_tfcomplex_by_id($inter->{tfcomplex}, 'notargets');
			    print "<td width='200' align='center' bgcolor=\"$colors{$bg_color}\">".$complex->name;
			    while (my $subunit=$complex->next_subunit) {
				my $db = $subunit->get_tdb;
				my $tid = $subunit->get_transcript_accession($dbh);
				my $cl = $subunit->get_class ||'unknown'; 
				my $fam = $subunit->get_fam ||'unknown';
				print $tid."&nbsp;(".$cl.")&nbsp; - Family: ".$fam."<br>";
			    }
			    print "</td>";
			}
			my @an=$dbh->get_data_by_primary_key('analysis',$inter->{aid});
			if ($params{tf_analysis} eq 'on') {
			    my $aname=$an[2];
			    my @anal;
			    push @anal,$aname;
			    if ($an[3]) {
				my @met=$dbh->get_data_by_primary_key('method',$an[3]);
				push @anal,$met[0];
			    }
			    if ($an[4]) {
				my @cell=$dbh->get_data_by_primary_key('cell',$an[4]);
				push @anal,$cell[0];
			    }
			    if ($an[5]) {
				my @time=$dbh->get_data_by_primary_key('time',$an[5]);
				push @anal,$time[0];
			    }
			    print "<td align='center' bgcolor=\"$colors{$bg_color}\">";
			    print join(':',@anal)."</td>";
			}
			if ($params{tf_reference} eq 'on' && $an[6]) {
			    my @ref=$dbh->get_data_by_primary_key('ref',$an[6]);
			    print "<td width='150' align='center' bgcolor=\"$colors{$bg_color}\">".$ref[0]."</td>";
			}
			if ($params{tf_interaction} eq 'on') {
			    my ($table,$pazarid,@dat)=$dbh->links_to_data($inter->{olink},'output');
			    if ($table eq 'interaction') {
				print "<td width='100' align='center' bgcolor=\"$colors{$bg_color}\">";
				my @data;
				for (my $i=0;$i<(@dat-3);$i++) {
				    if ($dat[$i] && $dat[$i] ne '0') {
					push @data,$dat[$i];
				    }
				}
				print join(":",@data)."</td>";
			    }
			}
			if ($params{other_effect} eq 'on')
			{
			    print "<td width='150' align='center' valign='top' bgcolor=\"$colors{$bg_color}\">&nbsp;</td>";
			}

			if ($params{tf_evidence} eq 'on' && $an[1]) {
			    my @ev=$dbh->get_data_by_primary_key('evidence',$an[1]);
			    print "<td width='150' align='center' bgcolor=\"$colors{$bg_color}\">".$ev[0]."_".$ev[1]."</td>";
			}
			$count++;
			print "</tr>";
              $bg_color = 1 - $bg_color;
		    }}

		if ($params{tf} eq 'on' || $params{tf_analysis} eq 'on' || $params{tf_reference} eq 'on' || $params{tf_interaction} eq 'on' || $params{tf_evidence} eq 'on') {
		    
#end table that was created if there were results
		    if(scalar(@interactors)>0)
		    {
			print "</table>";
		    }		    
		}

################### BEGIN OTHER EVIDENCE SECTION #####################
#reset row color
		$bg_color = 0;

		
		
		if ($params{other_analysis} eq 'on' || $params{other_reference} eq 'on' || $params{other_effect} eq 'on' || $params{other_evidence} eq 'on') {
		    
		    		    
#print table only if results exist
		    if (scalar(@expressors) > 0)
		    {
			print "<table width='100%' border=1 cellspacing=0><tr><td width='150' align='center' valign='top' bgcolor='#ff9a40'><span class=\"title4\">&nbsp;</span></td>";

			if ($params{tf} eq 'on') {
			    print "<td width='200' align='center' valign='top' bgcolor='#ff9a40'><span class=\"title4\">Transcription Factor</span></td>";
			}
			if ($params{other_analysis} eq 'on' || $params{tf_analysis} eq 'on')
			{
			    print "<td align='center' valign='top' bgcolor='#ff9a40'><span class=\"title4\">Analysis Details</span></td>";
			}
			if ($params{other_reference} eq 'on' || $params{tf_reference} eq 'on')
			{
			    print "<td width='150' align='center' valign='top' bgcolor='#ff9a40'><span class=\"title4\">Reference (PMID)</span></td>";
			}
			if ($params{tf_interaction} eq 'on')
			{
			    print "<td width='100' align='center' valign='top' bgcolor='#ff9a40'><span class=\"title4\">Interaction Description</span></td>";
			}
			if ($params{other_effect} eq 'on')
			{
			    print "<td width='150' align='center' valign='top' bgcolor='#ff9a40'><span class=\"title4\">Effects</span></td>";
			}
			if ($params{other_evidence} eq 'on' || $params{tf_evidence} eq 'on')
			{
			    print "<td width='150' align='center' valign='top' bgcolor='#ff9a40'><span class=\"title4\">Evidence</span></td>";
			}
			
			print "</tr>";
		    }
		}


		foreach my $exp (@expressors) {
		    if ($params{other_analysis} eq 'on' || $params{other_reference} eq 'on' || $params{other_effect} eq 'on' || $params{other_evidence} eq 'on') {
			print "<tr><td width='150' align='center' bgcolor=\"$colors{$bg_color}\">Line of evidence $count</td>";

			if ($params{tf} eq 'on') {
			    print "<td width='200' align='center' valign='top' bgcolor=\"$colors{$bg_color}\">&nbsp;</td>";
			}

			my @an=$dbh->get_data_by_primary_key('analysis',$exp->{aid});
			if ($params{other_analysis} eq 'on') {
			    my $aname=$an[2];
			    my @anal;
			    push @anal,$aname;
			    if ($an[3]) {
				my @met=$dbh->get_data_by_primary_key('method',$an[3]);
				push @anal,$met[0];
			    }
			    if ($an[4]) {
				my @cell=$dbh->get_data_by_primary_key('cell',$an[4]);
				push @anal,$cell[0];
			    }
			    if ($an[5]) {
				my @time=$dbh->get_data_by_primary_key('time',$an[5]);
				push @anal,$time[0];
			    }
			    print "<td align='center' bgcolor=\"$colors{$bg_color}\">";
			    print join(':',@anal)."</td>";
			}
			if ($params{other_reference} eq 'on' && $an[6]) {
			    my @ref=$dbh->get_data_by_primary_key('ref',$an[6]);
			    print "<td width='150' align='center' bgcolor=\"$colors{$bg_color}\">".$ref[0]."</td>";
			}
			if ($params{tf_interaction} eq 'on')
			{
			    print "<td width='100' align='center' valign='top' bgcolor=\"$colors{$bg_color}\">&nbsp;</td>";
			}
			if ($params{other_effect} eq 'on') {
			    my ($table,$tableid,@dat)=$dbh->links_to_data($exp->{olink},'output');
			    print "<td width='150' align='center' bgcolor=\"$colors{$bg_color}\">";
			    my @data;
			    for (my $i=0;$i<(@dat-3);$i++) {
				if ($dat[$i] && $dat[$i] ne '0') {
				    push @data,$dat[$i];
				}
			    }
			    print join(":",@data)."</td>";
			}
			if ($params{other_evidence} eq 'on' && $an[1]) {
			    my @ev=$dbh->get_data_by_primary_key('evidence',$an[1]);
			    print "<td width='150' align='center' bgcolor=\"$colors{$bg_color}\">".$ev[0]."_".$ev[1]."</td>";
			}
			$count++;
			print "</tr>";
			$bg_color = 1 - $bg_color;
		    }}

		if ($params{other_analysis} eq 'on' || $params{other_reference} eq 'on' || $params{other_effect} eq 'on' || $params{other_evidence} eq 'on') {

#end table only if results exist
		    if(scalar(@expressors)>0)
		    {
			print "</table>";
		    }
		}

#end table around evidence
		print "</td></tr></table><br>";

	    } #end of regseq loop
	}    
}


    if (scalar(@projects)==$empty) {
	print "<p class=\"warning\">No regulatory sequence was found for gene $gene! Is it really an Ensembl Gene ID?</p>\n";
    }
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
