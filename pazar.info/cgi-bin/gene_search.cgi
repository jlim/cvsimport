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

    my $projectsth=&select($dbh, "SELECT * FROM project WHERE upper(status)='OPEN' OR upper(status)='PUBLISHED'");
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

    my $species = $ensdb->current_org();

#print header

print<<HEADER_TABLE;

<table width='1150' border=1 cellspacing=0>
<tr><td align="center" valign="top" bgcolor="#39aecb"><span class="title4">Gene Name</span></td><td align='left'>&nbsp;&nbsp;&nbsp;&nbsp;$geneName</td></tr>
<tr><td align="center" valign="top" bgcolor="#39aecb"><span class="title4">Accession</span></td><td align='left'>&nbsp;&nbsp;&nbsp;&nbsp;$gene</td></tr>
<tr><td align="center" valign="top" bgcolor="#39aecb"><span class="title4">Description</span></td><td align='left'>&nbsp;&nbsp;&nbsp;&nbsp;$geneDescription</td></tr>
<tr><td align="center" valign="top" bgcolor="#39aecb"><span class="title4">Species</span></td><td align='left'>&nbsp;&nbsp;&nbsp;&nbsp;$species</td></tr>
</table>
HEADER_TABLE



########### start of HTML table
#get user's restricted projects if logged in


	if ($loggedin eq 'true') {
	    foreach my $proj (@projids) {
		my $restricted=&select($dbh, "SELECT project_name FROM project WHERE project_id='$proj' and upper(status)='RESTRICTED'");
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
	my $regseq_counter = 0; # counter for naming forms
	my @regseqs = $dbh->get_reg_seqs_by_accn($gene); 
	if (!$regseqs[0]) {
	    $empty++;
	    next;
	} else {
	    my @ens_coords = $ensdb->get_ens_chr($gene);
	    foreach my $regseq (@regseqs) {

		$regseq_counter = $regseq_counter + 1;

#reset row color
		$bg_color = 0;

#start table
print<<COLNAMES;	    
		<table width='1150' border=1 cellspacing=0><tr><td>
		    <table width='100%' border="1" cellspacing="0" cellpadding="3">
		    <tr>
		    <td width="100" align="center" valign="top" bgcolor="#61b9cf"><span class="title4">Project</span></td>
		    
COLNAMES

		print "<td width='150' align='center' valign='top' bgcolor='#61b9cf'><span class=\"title4\">Transcript ID</span></td>";

		if ($params{tss} eq 'on')
		{
		    print "<td width='100' align='center' valign='top' bgcolor='#61b9cf'><span class=\"title4\">Transcription Start Site</span></td>";
		}
		    print "<td width='150' align='center' valign='top' bgcolor='#61b9cf'><span class=\"title4\">Sequence Name</span></td>";
		    print "<td align='center' valign='top' bgcolor='#61b9cf'><span class=\"title4\">Sequence</span></td>";
		    print "<td width='100' align='center' valign='top' bgcolor='#61b9cf'><span class=\"title4\">RegSeq ID</span></td>";
		    print "<td width='150' align='center' valign='top' bgcolor='#61b9cf'><span class=\"title4\">Coordinates</span></td>";

		if ($params{quality} eq 'on') {
		    print "<td width='100' align='center' valign='top' bgcolor='#61b9cf'><span class=\"title4\">Quality</span></td>";
		}
		    print "<td width='80' align='center' valign='top' bgcolor='#61b9cf'><span class=\"title4\">Display</span></td>";

		print "</tr>";
		
#print out default information
		print "<form name='display$regseq_counter' method='post' action='http://www.pazar.info/cgi-bin/gff_custom_track.cgi' enctype='multipart/form-data' target='_blank'>";
		print "<tr>";
		print "<td width='100' align='center' bgcolor=\"$colors{$bg_color}\">$projname</td>";
		
		my $transcript=$regseq->transcript_accession || 'Not Specified';
		print "<td width='150' align='center' bgcolor=\"$colors{$bg_color}\">".$transcript."</td>";

		if ($params{tss} eq 'on') {
		    if ($regseq->transcript_fuzzy_start == $regseq->transcript_fuzzy_end) { print "<td width='100' align='center' bgcolor=\"$colors{$bg_color}\">".$regseq->transcript_fuzzy_start."</td>";} else {
			print "<td width='100' align='center' bgcolor=\"$colors{$bg_color}\">".$regseq->transcript_fuzzy_start."-".$regseq->transcript_fuzzy_end."</td>";
		    }
		}

		print "<td width='150' align='center' bgcolor=\"$colors{$bg_color}\">".$regseq->id."&nbsp;</td>";	       
		print "<td align='left' bgcolor=\"$colors{$bg_color}\">".chopstr($regseq->seq,40)."&nbsp;</td>";

		my $id=write_pazarid($regseq->accession_number,'RS');

		print "<td width='100' align='center' bgcolor=\"$colors{$bg_color}\">".$id."&nbsp;</td>";
		print "<td width='150' align='center' bgcolor=\"$colors{$bg_color}\">".$regseq->chromosome." (".$regseq->strand.") ".$regseq->start."-".$regseq->end."</td>";

		if ($params{quality} eq 'on') {
		    print "<td width='100' align='center' bgcolor=\"$colors{$bg_color}\">".$regseq->quality."&nbsp;</td>";
		}
		print "<td width='80' align='center' bgcolor=\"$colors{$bg_color}\"><input type='hidden' name='chr' value='".$regseq->chromosome."'><input type='hidden' name='start' value='".$regseq->start."'><input type='hidden' name='end' value='".$regseq->end."'><input type='hidden' name='species' value='".$regseq->binomial_species."'><input type='hidden' name='resource' value='ucsc'><a href='#' onClick=\"javascript:document.display$regseq_counter.resource.value='ucsc';document.display$regseq_counter.submit();\"><img src='http://www.pazar.info/images/ucsc_logo.png'></a><!--<input type='submit' name='ucsc' value='ucsc' onClick=\"javascript:document.display$regseq_counter.resource.value='ucsc';\">--><br><a href='#' onClick=\"javascript:document.display$regseq_counter.resource.value='ensembl';document.display$regseq_counter.submit();\"><img src='http://www.pazar.info/images/ensembl_logo.gif'></a><!--<input type='submit' name='ensembl' value='ensembl' onClick=\"javascript:document.display$regseq_counter.resource.value='ensembl';\">--></td>";
		print "</tr></form></table>";
		print "<p></td></tr>";

####################### get data objects for retrieving lines of evidence
		my @interactors=$dbh->get_interacting_factor_by_regseq_id($regseq->accession_number);
		my @expressors=$dbh->get_expression_by_regseq_id($regseq->accession_number);
########################
#make sure that if there is at least one interactor or expressor and that there is at least 1 field being displayed 	 if(scalar(@interactors)>0 || scalar(@expressors)>0)
		if((scalar(@interactors)>0 && ($params{tf} eq 'on' || $params{tf_analysis} eq 'on' || $params{tf_reference} eq 'on' || $params{tf_interaction} eq 'on' || $params{tf_mutants} eq 'on')) || (scalar(@expressors)>0 && ($params{other_analysis} eq 'on' || $params{other_reference} eq 'on' || $params{other_effect} eq 'on' || $params{other_mutants} eq 'on'))) 
{
		print "<tr><td align='center' bgcolor='#ff9a40'><center><span class=\"title4\">Lines of Evidence</span></center></td></tr><tr><td>";
}
################### BEGIN INTERACTING EVIDENCE SECTION #####################
#reset row color
		$bg_color = 0;
		my $count=1;
		
		if ($params{tf} eq 'on' || $params{tf_analysis} eq 'on' || $params{tf_reference} eq 'on' || $params{tf_interaction} eq 'on' || $params{tf_mutants} eq 'on') {
		    
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
			if ($params{tf_mutants} eq 'on' || $params{other_mutants} eq 'on')
			{
			    print "<td width='150' align='center' valign='top' bgcolor='#ff9a40'><span class=\"title4\">Mutants</span></td>";
			}
			print "</tr>";
		    }
		}
		

		foreach my $inter (@interactors) {
		    if ($params{tf} eq 'on' || $params{tf_analysis} eq 'on' || $params{tf_reference} eq 'on' || $params{tf_interaction} eq 'on' || $params{tf_mutants} eq 'on') {
			print "<tr><td width='150' align='center' bgcolor=\"$colors{$bg_color}\">Line of evidence $count</td>";
			if ($params{tf} eq 'on') {
			    if ($inter->{tftype} eq 'funct_tf') {
				my $tf = $dbh->create_tf;
				my $complex = $tf->get_tfcomplex_by_id($inter->{tfcomplex}, 'notargets');
				print "<td width='200' align='center' bgcolor=\"$colors{$bg_color}\"><b>".$complex->name."</b><br>";
				while (my $subunit=$complex->next_subunit) {
				    my $db = $subunit->get_tdb;
				    my $tid = $subunit->get_transcript_accession($dbh);
				    my $cl = $subunit->get_class; 
				    my $fam = $subunit->get_fam;
				    if (!$cl || $cl eq '0' || $cl eq 'unknown') {
					print $tid."<br>";
				    } elsif  (!$fam || $fam eq '0' || $fam eq 'unknown') {
					print $tid."&nbsp;(".$cl.")<br>";
				    } else {
					print $tid."&nbsp;(".$cl.", ".$fam.")<br>";
				    }
				}
				print "</td>";
			    }
			    if ($inter->{tftype} eq 'sample') {
				my @sample=$dbh->get_data_by_primary_key('sample',$inter->{tfcomplex});
				my @samplecell=$dbh->get_data_by_primary_key('cell',$sample[1]);
				print "<td width='200' align='center' bgcolor=\"$colors{$bg_color}\">".$sample[0]."&nbsp;".$samplecell[0]."</td>";
			    }
			}
			my @an=$dbh->get_data_by_primary_key('analysis',$inter->{aid});
			if ($params{tf_analysis} eq 'on') {
			    my $anal;
			    if ($an[3]) {
				my @met=$dbh->get_data_by_primary_key('method',$an[3]);
#				if ($met[0]) {
				    $anal.="<b>Method:</b> $met[0]<br>";
#				}
			    }
#			    if ($an[4]) {
				my @cell=$dbh->get_data_by_primary_key('cell',$an[4]);
#				if ($cell[0]) {
				    $anal.="<b>Cell Type:</b> $cell[0]<br>";
#				}
#			    }
#			    if ($an[5]) {
				my @time=$dbh->get_data_by_primary_key('time',$an[5]);
#				if ($time[0]) {
				    $anal.="<b>Time:</b> $time[0]<br>";
#				}
#			    }
#			    if ($an[7]) {
				$anal.="<b>Comments:</b> $an[7]<br>";
#			    }
			    print "<td align='center' bgcolor=\"$colors{$bg_color}\">";
			    print $anal."</td>";
			}
			if ($params{tf_reference} eq 'on') {
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
			if ($params{tf_mutants} eq 'on') {
			    print "<td width='150' align='center' bgcolor=\"$colors{$bg_color}\">";
			    my @mutants=$dbh->get_mutants_by_analysis_id($inter->{aid});
			    unless ($mutants[0]) {
				print "None";
			    }
			    foreach my $mutant (@mutants) {
				my @mut=$dbh->get_data_by_primary_key('mutation_set',$mutant->{mutid});
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
#			    my @ev=$dbh->get_data_by_primary_key('evidence',$an[1]);
			    print "</td>";
			}
			$count++;
			print "</tr>";
              $bg_color = 1 - $bg_color;
		    }}

		if ($params{tf} eq 'on' || $params{tf_analysis} eq 'on' || $params{tf_reference} eq 'on' || $params{tf_interaction} eq 'on' || $params{tf_mutants} eq 'on') {
		    
#end table that was created if there were results
		    if(scalar(@interactors)>0)
		    {
			print "</table>";
		    }		    
		}

################### BEGIN OTHER EVIDENCE SECTION #####################
#reset row color
		$bg_color = 0;

		
		
		if ($params{other_analysis} eq 'on' || $params{other_reference} eq 'on' || $params{other_effect} eq 'on' || $params{other_mutants} eq 'on') {
		    
		    		    
#print table only if results exist
		    if (scalar(@expressors) > 0)
		    {
			print "<table width='100%' border=1 cellspacing=0><tr><td width='150' align='center' valign='top' bgcolor='#ff9a40'><span class=\"title4\">&nbsp;</span></td>";

# 			if ($params{tf} eq 'on') {
# 			    print "<td width='200' align='center' valign='top' bgcolor='#ff9a40'><span class=\"title4\">Transcription Factor</span></td>";
# 			}
			if ($params{other_analysis} eq 'on' || $params{tf_analysis} eq 'on')
			{
			    print "<td align='center' valign='top' bgcolor='#ff9a40'><span class=\"title4\">Analysis Details</span></td>";
			}
			if ($params{other_reference} eq 'on' || $params{tf_reference} eq 'on')
			{
			    print "<td width='150' align='center' valign='top' bgcolor='#ff9a40'><span class=\"title4\">Reference (PMID)</span></td>";
			}
# 			if ($params{tf_interaction} eq 'on')
# 			{
# 			    print "<td width='100' align='center' valign='top' bgcolor='#ff9a40'><span class=\"title4\">Interaction Description</span></td>";
# 			}
			if ($params{other_effect} eq 'on')
			{
			    print "<td width='150' align='center' valign='top' bgcolor='#ff9a40'><span class=\"title4\">Effects</span></td>";
			    print "<td width='150' align='center' valign='top' bgcolor='#ff9a40'><span class=\"title4\">Conditions</span></td>";
			}
			if ($params{other_mutants} eq 'on' || $params{tf_mutants} eq 'on')
			{
			    print "<td width='150' align='center' valign='top' bgcolor='#ff9a40'><span class=\"title4\">Mutants</span></td>";
			}
			
			print "</tr>";
		    }
		}


		foreach my $exp (@expressors) {
		    if ($params{other_analysis} eq 'on' || $params{other_reference} eq 'on' || $params{other_effect} eq 'on' || $params{other_mutants} eq 'on') {
			print "<tr><td width='150' align='center' bgcolor=\"$colors{$bg_color}\">Line of evidence $count</td>";

# 			if ($params{tf} eq 'on') {
# 			    print "<td width='200' align='center' valign='top' bgcolor=\"$colors{$bg_color}\">&nbsp;</td>";
# 			}

			my @an=$dbh->get_data_by_primary_key('analysis',$exp->{aid});
			if ($params{other_analysis} eq 'on') {
			    my $anal;
			    if ($an[3]) {
				my @met=$dbh->get_data_by_primary_key('method',$an[3]);
#				if ($met[0]) {
				    $anal.="<b>Method:</b> $met[0]<br>";
#				}
			    }
#			    if ($an[4]) {
				my @cell=$dbh->get_data_by_primary_key('cell',$an[4]);
#				if ($cell[0]) {
				    $anal.="<b>Cell Type:</b> $cell[0]<br>";
#				}
#			    }
#			    if ($an[5]) {
				my @time=$dbh->get_data_by_primary_key('time',$an[5]);
#				if ($time[0]) {
				    $anal.="<b>Time:</b> $time[0]<br>";
#				}
#			    }
#			    if ($an[7]) {
				$anal.="<b>Comments:</b> $an[7]<br>";
#			    }
			    print "<td align='center' bgcolor=\"$colors{$bg_color}\">";
			    print $anal."</td>";
			}
			if ($params{other_reference} eq 'on') {
			    my @ref=$dbh->get_data_by_primary_key('ref',$an[6]);
			    print "<td width='150' align='center' bgcolor=\"$colors{$bg_color}\">".$ref[0]."</td>";
			}
# 			if ($params{tf_interaction} eq 'on')
# 			{
# 			    print "<td width='100' align='center' valign='top' bgcolor=\"$colors{$bg_color}\">&nbsp;</td>";
# 			}
			my @conds=@{$exp->{iotype}};
			my @condids=@{$exp->{ioid}};
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
			    print "<td width='150' align='center' bgcolor=\"$colors{$bg_color}\">";
			    my $nocond=0;
			    for (my $i=0;$i<@conds;$i++) {
				$nocond=1;
				my @dat=$dbh->get_data_by_primary_key($conds[$i],$condids[$i]);
				pop @dat;
				pop @dat;
				pop @dat;
				print join(":",@dat)."<br>";
				if ($dat[0] eq 'co-expression') {
				    my $tf = $dbh->create_tf;
				    my $complex = $tf->get_tfcomplex_by_id($dat[2], 'notargets');
				    print "<b>$complex->name</b><br>";
				    while (my $subunit=$complex->next_subunit) {
					my $db = $subunit->get_tdb;
					my $tid = $subunit->get_transcript_accession($dbh);
					my $cl = $subunit->get_class; 
					my $fam = $subunit->get_fam;
					if (!$cl || $cl eq '0' || $cl eq 'unknown') {
					    print $tid."<br>";
					} elsif  (!$fam || $fam eq '0' || $fam eq 'unknown') {
					    print $tid."&nbsp;(".$cl.")<br>";
					} else {
					    print $tid."&nbsp;(".$cl.", ".$fam.")<br>";
					}
				    }
				}
			    }
			    if ($nocond==0) {
				print "None";
			    }
			    print "</td>";
			}
			if ($params{other_mutants} eq 'on') {
			    print "<td width='150' align='center' bgcolor=\"$colors{$bg_color}\">";
			    my @mutants=$dbh->get_mutants_by_analysis_id($exp->{aid});
			    my $nomut=0;
			    foreach my $mutant (@mutants) {
				my @mut_condids=@{$exp->{ioid}};
				my $nomatch=0;
				if (@mut_condids==@condids) {
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
#			    my @ev=$dbh->get_data_by_primary_key('evidence',$an[1]);
			    if ($nomut==0) {
				print "None";
			    }
			    print "</td>";
			}
			$count++;
			print "</tr>";
			$bg_color = 1 - $bg_color;
		    }}

		if ($params{other_analysis} eq 'on' || $params{other_reference} eq 'on' || $params{other_effect} eq 'on' || $params{other_mutants} eq 'on') {

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

sub write_pazarid {
    my $id=shift;
    my $type=shift;
    my $id7d = sprintf "%07d",$id;
    my $pazarid=$type.$id7d;
    return $pazarid;
}
