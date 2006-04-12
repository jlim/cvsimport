#!/usr/local/bin/perl

use lib '/space/usr/local/src/ensembl-36/ensembl/modules/';
use lib '/space/usr/local/src/bioperl-live/';

use strict;

use pazar;
use pazar::gene;
use pazar::talk;

use HTML::Template;

use CGI qw(:standard);
use CGI::Carp qw(fatalsToBrowser);
use CGI::Debug( report => 'everything', on => 'anything' );

use TFBS::PatternGen::MEME;
use TFBS::Matrix::PFM;

use Data::Dumper;

# open the html header template
my $template = HTML::Template->new(filename => 'header.tmpl');

# fill in template parameters
$template->param(TITLE => 'PAZAR TF Results');

$template->param(JAVASCRIPT_FUNCTION => q{function verifyCheckedBoxes() {            
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
	document.sequenceform.submit();
    }

        }});


# send the obligatory Content-Type and print the template output
print "Content-Type: text/html\n\n", $template->output;

#connect to the database
my $dbh = pazar->new( 
                      -globalsearch  =>    'yes',
		      -host          =>    $ENV{PAZAR_host},
		      -user          =>    $ENV{PAZAR_pubuser},
		      -pass          =>    $ENV{PAZAR_pubpass},
		      -pazar_user    =>    'elodie@cmmt.ubc.ca',
		      -pazar_pass    =>    'pazarpw',
		      -dbname        =>    $ENV{PAZAR_name},
		      -drv           =>    'mysql');

my $ensdb = pazar::talk->new(DB=>'ensembl',USER=>$ENV{ENS_USER},PASS=>$ENV{ENS_PASS},HOST=>$ENV{ENS_HOST},DRV=>'mysql');

my $gkdb = pazar::talk->new(DB=>'genekeydb',USER=>$ENV{GKDB_USER},PASS=>$ENV{GKDB_PASS},HOST=>$ENV{GKDB_HOST},DRV=>'mysql');

my $bg_color = 0;
my %colors = (0 => "#fffff0",
	      1 => "#9ad3e2"
	      );

my $get = new CGI;
my %param = %{$get->Vars};
my $accn = $param{geneID};
my $dbaccn = $param{ID_list};
my @trans;
my $tfname;
if (!$accn) {
    print "<p class=\"warning\">Please provide a TF ID!</p>\n";
    exit;
} else {
    if ($dbaccn eq 'EnsEMBL_gene') {
	@trans = $gkdb->ens_transcripts_by_gene($accn);
        unless ($trans[0]=~/\w{4,}\d{6,}/) {print "<p class=\"warning\">Conversion failed for $accn! Maybe it is not a $dbaccn ID!</p>"; exit;}
    } elsif ($dbaccn eq 'EnsEMBL_transcript') {
	push @trans,$accn;
        unless ($trans[0]=~/\w{4,}\d{6,}/) {print "<p class=\"warning\">Conversion failed for $accn! Maybe it is not a $dbaccn ID!</p>"; exit;}
    } elsif ($dbaccn eq 'EntrezGene') {
	my @gene=$gkdb->llid_to_ens($accn);
	unless ($gene[0]=~/\w{4,}\d{6,}/) {print "<p class=\"warning\">Conversion failed for $accn! Maybe it is not a $dbaccn ID!</p>"; exit;}
	@trans = $gkdb->ens_transcripts_by_gene($gene[0]);
    } elsif ($dbaccn eq 'nm') {
	@trans=$gkdb->nm_to_enst($accn);
	unless ($trans[0]=~/\w{4,}\d{6,}/) {print "<p class=\"warning\">Conversion failed for $accn! Maybe it is not a $dbaccn ID!</p>"; exit;}
    } elsif ($dbaccn eq 'swissprot') {
	my $sp=$gkdb->{dbh}->prepare("select organism from ll_locus a, gk_ll2sprot b where a.ll_id=b.ll_id and sprot_id=?")||die;
	$sp->execute($accn)||die;
	my $species=$sp->fetchrow_array();
	if (!$species) {print "<p class=\"warning\">Conversion failed for $accn! Maybe it is not a $dbaccn ID!</p>"; exit;}
	$ensdb->change_mart_organism($species);
	@trans =$ensdb->swissprot_to_enst($accn);
	unless ($trans[0]=~/\w{4,}\d{6,}/) {print "<p class=\"warning\">Conversion failed for $accn! Maybe it is not a $dbaccn ID!</p>"; exit;}
    } elsif ($dbaccn eq 'tf_name') {
	@trans = ('none');
	$tfname = $accn;
    }
    my $count=0;
    my $file="/space/usr/local/apache/pazar.info/tmp/".$accn.".fa";
    open (TMP, ">$file");
####start of form
    print "<form name='sequenceform' method='post' target='logowin' action='tf_logo.pl' onsubmit='window.open('','foo','resizable=1,scrollbars=1,width=400,height=300')'>";
    print "<input type='hidden' name='accn' value='$accn'";
    foreach my $trans (@trans) {
#	print "you're looking for transcript: ".$trans."\n";
	my $tf;
	my @tfcomplexes;
	if ($trans eq 'none') {
	    $tf = $dbh->create_tf;
	    @tfcomplexes = $tf->get_tfcomplex_by_name($tfname);
	    if (!$tfcomplexes[0]){
		print "<p class=\"warning\">No $tfname TF could be found in the database!</p>\n";
		exit;
	    }
	} else {
	    $tf = $dbh->create_tf;
	    @tfcomplexes = $tf->get_tfcomplex_by_transcript($trans);
	    if (!$tfcomplexes[0]){
		print "<p class=\"warning\">No $trans transcript could be found in the database!</p>\n";
		exit;
	    }
	}


	foreach my $complex (@tfcomplexes) {

	    
########### start of HTML table

	    print "<table width='600' bordercolor='white' bgcolor='white' border=1 cellspacing=0>\n";
	print<<COLNAMES;
<tr>
      <td width="100" align="center" valign="top" bgcolor="#e65656"><span class="title4">Project</span></td>
 <td align="center" width="187" valign="top" bgcolor="#e65656"><span class="title4">Name</span></td>
      <td align="center" bgcolor="#e65656"><span class="title4">Classes</span>
      </td> 

<td align="center" bgcolor="#e65656"><span class="title4">Transcript Accessions</span>
      </td> 

<td align="center" bgcolor="#e65656"><span class="title4">Families</span>
      </td> 
  </tr>
COLNAMES

	    print "<tr><td bgcolor=\"$colors{$bg_color}\">".$dbh->get_project_name('funct_tf',$complex->dbid)."</td><td bgcolor=\"$colors{$bg_color}\">".$complex->name."</td>";

    my @classes = ();
    my @families = ();
    my @transcript_accessions = ();

	    while (my $subunit=$complex->next_subunit) {
		my $tid = $subunit->get_transcript_accession($dbh);
		my $cl = $subunit->get_class ||'unknown'; 
		my $fam = $subunit->get_fam ||'unknown';

		push(@classes,$subunit->get_class);
		push(@families,$subunit->get_fam);
		push(@transcript_accessions, $subunit->get_transcript_accession($dbh));
	    }
    #print subunit information
    print "<td bgcolor=\"$colors{$bg_color}\">";
    #class
    foreach my $c (@classes)
    {
	print $c."<br>";
    }
    print "&nbsp;</td>";
    print "<td bgcolor=\"$colors{$bg_color}\">";
    #transcript accession
    foreach my $ta (@transcript_accessions)
    {
	print $ta."<br>";
    }
    print  "&nbsp;</td>";
    print "<td bgcolor=\"$colors{$bg_color}\">";
    #family
    foreach my $f (@families)
    {
	print $f."<br>";
    }
    print "&nbsp;</td>";
    print  "</tr></table>";

#separate tables for artificial and genomic targets
	    print "<p><table bordercolor='white' bgcolor='white' border=1 cellspacing=0><tr><td align='center' bgcolor='#61b9cf'><span class=\"title4\">Target type</span></td><td align='center' bgcolor='#61b9cf'><span class=\"title4\">Sequence</span></td>";

if ($param{reg_seq_name} eq 'on' || $param{construct_name} eq 'on')
{
    print "<td align='center' bgcolor='#61b9cf'><span class=\"title4\">Name</span></td>"
}

 if ($param{gene} eq 'on') 
{
    print "<td align='center' bgcolor='#61b9cf'><span class=\"title4\">Gene</span></td>";
}
 if ($param{species} eq 'on')
{
    print "<td align='center' bgcolor='#61b9cf'><span class=\"title4\">Species</span></td>";
}

if ($param{coordinates} eq 'on')
{
    print "<td align='center' bgcolor='#61b9cf'><span class=\"title4\">Coordinates</span></td>";
}

if ($param{quality} eq 'on')
{
    print "<td align='center' bgcolor='#61b9cf'><span class=\"title4\">Quality</span></td>";
}

if ($param{description} eq 'on')
{
    print "<td align='center' bgcolor='#61b9cf'><span class=\"title4\">Description</span></td>";
}

if ($param{analysis} eq 'on')
{
    print "<td align='center' bgcolor='#61b9cf'><span class=\"title4\">Analysis</span></td>";
}

if ($param{reference} eq 'on')
{
    print "<td align='center' bgcolor='#61b9cf'><span class=\"title4\">Reference</span></td>";
}

if ($param{interaction} eq 'on')
{
    print "<td align='center' bgcolor='#61b9cf'><span class=\"title4\">Interaction</span></td>";
}
if ($param{evidence} eq 'on') 
{
    print "<td align='center' bgcolor='#61b9cf'><span class=\"title4\">Evidence</span></td>";
}

    print "</tr>\n";


	    if (!$complex->{targets}) {
		print "<p class=\"warning\">No target could be found for this TF!</p>\n";
		next;
	    }
	    my $seqcounter = 0;
	    while (my $site=$complex->next_target) {
		$seqcounter++;
		my $type=$site->get_type;
		if ($type eq 'matrix') {next;}
		if ($type eq 'reg_seq' && $param{reg_seq} eq 'on') {
		    print "<tr><td bgcolor=\"$colors{$bg_color}\"><input type='checkbox' name='seq$seqcounter' value='".$site->get_seq."'>Genomic Target (reg_seq): </td><td bgcolor=\"$colors{$bg_color}\">".$site->get_seq."</td>";
                    my @regseq = $dbh->get_reg_seq_by_regseq_id($site->get_dbid);
#		    print Dumper(@regseq);
		    print "<ul style=\"margin: 0pt; padding: 0pt; list-style-type: none;\">";
		    if ($param{reg_seq_name} eq 'on') {
			if($site->get_name)
			{
			    print "<td bgcolor=\"$colors{$bg_color}\">".$site->get_name."</td>";
			}
			else
			{
			    print "<td bgcolor=\"$colors{$bg_color}\">&nbsp;</td>";
			}
		    }
		    if ($param{gene} eq 'on') {
			my $transcript=$regseq[0]->transcript_accession || 'Transcript Not Specified';
			print "<td>".$regseq[0]->gene_accession."</td><td>".$transcript."</td>";
			my @ens_coords = $ensdb->get_ens_chr($regseq[0]->gene_accession);
			my @desc = split('\[',$ens_coords[5]);
			print "<td bgcolor=\"$colors{$bg_color}\">".$desc[0]."</td>";
		    }
		    if ($param{species} eq 'on') {
			print "<td bgcolor=\"$colors{$bg_color}\">".$regseq[0]->binomial_species."</td>";
		    }
		    if ($param{coordinates} eq 'on') {
			print "<td bgcolor=\"$colors{$bg_color}\">".$regseq[0]->chromosome." (".$regseq[0]->strand.") ".$regseq[0]->start."-".$regseq[0]->end."</td>";
		    }
		    if ($param{quality} eq 'on') {
			print "<td bgcolor=\"$colors{$bg_color}\">".$regseq[0]->quality."</td>";
		    }

#fill in blank cells in table
if ($param{description} eq 'on')
{
    print "<td bgcolor=\"$colors{$bg_color}\">&nbsp;</td>";
}

if ($param{analysis} eq 'on')
{
    print "<td bgcolor=\"$colors{$bg_color}\">&nbsp;</td>";
}

if ($param{reference} eq 'on')
{
    print "<td bgcolor=\"$colors{$bg_color}\">&nbsp;</td>";
}

if ($param{interaction} eq 'on')
{
    print "<td bgcolor=\"$colors{$bg_color}\">&nbsp;</td>";
}
if ($param{evidence} eq 'on') 
{
    print "<td bgcolor=\"$colors{$bg_color}\">&nbsp;</td>";
}
		    print"</tr>";
		}
		if ($type eq 'construct' && $param{construct} eq 'on') {
		    print "<tr><td bgcolor=\"$colors{$bg_color}\"><input type='checkbox' name='seq$seqcounter' value='".$site->get_seq."'>Artificial Target (construct): </td><td bgcolor=\"$colors{$bg_color}\">".$site->get_seq."</td>";
		    print "<ul style=\"margin: 0pt; padding: 0pt; list-style-type: none;\">";
		    if ($param{construct_name} eq 'on') {
			print "<td bgcolor=\"$colors{$bg_color}\">".$site->get_name."</td>";
		    }

#fill in blank cells
 if ($param{gene} eq 'on') 
{
    print "<td bgcolor=\"$colors{$bg_color}\">&nbsp;</td>";
}
 if ($param{species} eq 'on')
{
    print "<td bgcolor=\"$colors{$bg_color}\">&nbsp;</td>";
}

if ($param{coordinates} eq 'on')
{
    print "<td bgcolor=\"$colors{$bg_color}\">&nbsp;</td>";
}

if ($param{quality} eq 'on')
{
    print "<td bgcolor=\"$colors{$bg_color}\">&nbsp;</td>";
}


###
		    if ($param{description} eq 'on') {
			if($site->get_desc)
			{
			    print "<td bgcolor=\"$colors{$bg_color}\">".$site->get_desc."</td>";			   
		        }
			else
			{
			    print "<td bgcolor=\"$colors{$bg_color}\">&nbsp;</td>";
			}
		    }
		}
		my @an=$dbh->get_data_by_primary_key('analysis',$site->get_analysis);
		if ($param{analysis} eq 'on') {
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
		    print "<td bgcolor=\"$colors{$bg_color}\">";
		    print join(':',@anal)."&nbsp;</td>";
		}
		if ($param{reference} eq 'on') {
                   if ($an[6])
                   {
		       my @ref=$dbh->get_data_by_primary_key('ref',$an[6]);
		       print "<td bgcolor=\"$colors{$bg_color}\">".$ref[0]."&nbsp;</td>";
                   }
                   else
                   {
		       print "<td bgcolor=\"$colors{$bg_color}\">&nbsp;</td>"
                   }
		}
		if ($param{interaction} eq 'on') {
                    print "<td bgcolor=\"$colors{$bg_color}\">";
		    my ($table,$pazarid,@dat)=$dbh->links_to_data($site->get_olink,'output');
		    if ($table eq 'interaction') {

			my @data;
			for (my $i=0;$i<(@dat-3);$i++) {
			    if ($dat[$i] && $dat[$i] ne '0') {
				push @data,$dat[$i];
			    }
			}
			print join(":",@data);



		    }
                    print "&nbsp;</td>";
		}
		if ($param{evidence} eq 'on') {
                    if ($an[1])
                    {
			my @ev=$dbh->get_data_by_primary_key('evidence',$an[1]);
			print "<td bgcolor=\"$colors{$bg_color}\">".$ev[0]."_".$ev[1]."</td>";
                    }
                    else
                    {
			print "<td bgcolor=\"$colors{$bg_color}\">&nbsp;</td>";
                    }
		}
                print "</tr>";
		$count++;
		my $construct_name=$accn."_site".$count;
		print TMP ">".$construct_name."\n";
		print TMP $site->get_seq."\n";
                $bg_color = 1 - $bg_color;
            }
	    print "</table>";
         }
     }
    close (TMP);
####hidden form inputs


    print "<table bordercolor='white' bgcolor='white'><tr><td>Click Go to recalculate matrix and logo based on selected sequences</td>";
    print "<td><input type='button' value='Go' onClick=\"verifyCheckedBoxes();\"></td></tr></table>";
    print "</form>";
####end of form
    unless ($count==0) {
	my $patterngen =
	    TFBS::PatternGen::MEME->new(-seq_file=> "$file",
					-binary => 'meme',
					-additional_params => '-mod oops');
	my $pfm = $patterngen->pattern(); # $pfm is now a TFBS::Matrix::PFM object
#print a human readable format of the matrix
	my $prettystring = $pfm->prettyprint();
	my @matrixlines = split /\n/, $prettystring;
	$prettystring = join "<BR>\n", @matrixlines;
	$prettystring =~ s/ /\&nbsp\;/g;
	print "<p><table bordercolor='white' bgcolor='white' border=1 cellspacing=0><tr><td><span class=\"title4\">Position Frequency Matrix</span></td><td><SPAN class=\"monospace\">$prettystring</SPAN></td></tr>";
#draw the logo
	my $logo = $accn.".png";
	my $gd_image = $pfm->draw_logo(-file=>"/space/usr/local/apache/pazar.info/tmp/".$logo, -xsize=>400);
	print "<tr><td><span class=\"title4\">Logo</span></td><td><img src=\"http://www.pazar.info/tmp/$logo\">";
	print "<p class=\"small\">These PFM and Logo were generated dynamically using the MEME pattern discovery algorithm.</p></td></tr>\n";
	print "</table>\n";
########### end of HTML table

    }
}
# print out the html tail template
my $template_tail = HTML::Template->new(filename => 'tail.tmpl');
print $template_tail->output;



sub select {

    my ($dbh, $sql) = @_;
    my $sth=$dbh->prepare($sql);
    $sth->execute or die "$dbh->errstr\n";
    return $sth;
}

