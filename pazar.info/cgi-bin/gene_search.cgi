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

use Data::Dumper;

# open the html header template
my $template = HTML::Template->new(filename => 'header.tmpl');

# fill in template parameters
$template->param(TITLE => 'PAZAR Gene Search');

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
    my $projects=&select($dbh, "SELECT * FROM project WHERE status='open' OR status='published'");
    my @projects;
    while (my $project=$projects->fetchrow_hashref) {
	push @projects, $project->{project_name};
    }
    my $empty=0;
    foreach my $projname (@projects) {
#connect to the database
	$dbh = pazar->new( 
                              -globalsearch  =>    'no',		      
                              -host          =>    $ENV{PAZAR_host},
			      -user          =>    $ENV{PAZAR_pubuser},
			      -pass          =>    $ENV{PAZAR_pubpass},
			      -dbname        =>    $ENV{PAZAR_name},
			      -drv           =>    'mysql',
			      -project       =>    $projname);

	my @regseqs = $dbh->get_reg_seqs_by_accn($gene); 
	if (!$regseqs[0]) {
	    $empty++;
	    next;
	} else {
	    my @ens_coords = $ensdb->get_ens_chr($gene);
	    foreach my $regseq (@regseqs) {
		print "<ul style=\"margin: 0pt; padding: 0pt; list-style-type: none;\">";
		print "<li><b>Project: </b>".$projname."</li>";
		if ($params{gene} eq 'on') {
		    my $transcript=$regseq->transcript_accession || 'Transcript Not Specified';
		    print "<li><b>Gene/Transcript: </b>".$regseq->gene_accession."/".$transcript."</li>";
		    my @ens_coords = $ensdb->get_ens_chr($regseq->gene_accession);
		    my @desc = split('\[',$ens_coords[5]);
		    print "<li>".$desc[0]."</li>";
		}
		if ($params{tss} eq 'on') {
		    if ($regseq->transcript_fuzzy_start == $regseq->transcript_fuzzy_end) { print "<li><b>Transcription Start Site: </b>".$regseq->transcript_fuzzy_start."</li>";} else {
			print "<li>Transcription Start Site: </b>".$regseq->transcript_fuzzy_start."-".$regseq->transcript_fuzzy_end."</li>";
		    }
		}
		if ($params{species} eq 'on') {
		    print "<li><b>Species: </b>".$regseq->binomial_species."</li>";
		}
		if ($params{reg_seq_name} eq 'on' && $regseq->id) {
		    print "<li><b>Name: </b>".$regseq->id."</li>";
		}
		if ($params{sequence} eq 'on') {
		    print "<li><b>Sequence: </b>".$regseq->seq."</li>";
		}
		if ($params{coordinates} eq 'on') {
		    print "<li><b>Coordinates: </b>".$regseq->chromosome." (".$regseq->strand.") ".$regseq->start."-".$regseq->end."</li>";
		}
		if ($params{quality} eq 'on') {
		    print "<li><b>Quality: </b>".$regseq->quality."</li>";
		}
		my @interactors=$dbh->get_interacting_factor_by_regseq_id($regseq->accession_number);
		my $count=1;
		foreach my $inter (@interactors) {
		    if ($params{tf} eq 'on' || $params{tf_analysis} eq 'on' || $params{tf_reference} eq 'on' || $params{tf_interaction} eq 'on' || $params{tf_evidence} eq 'on') {
			print "<li><b>Line of evidence $count: </b></li>";
			if ($params{tf} eq 'on') {
			    my $tf = $dbh->create_tf;
			    my $complex = $tf->get_tfcomplex_by_id($inter->{tfcomplex}, 'notargets');
			    print "<li>Transcription Factor Complex Name: ".$complex->name."</li>";
			    while (my $subunit=$complex->next_subunit) {
				my $db = $subunit->get_tdb;
				my $tid = $subunit->get_transcript_accession($dbh);
				my $cl = $subunit->get_class ||'unknown'; 
				my $fam = $subunit->get_fam ||'unknown';
				print "<li>Transcription Factor Complex Subunit: ".$tid." - Class: ".$cl." - Family: ".$fam."</li>";
			    }
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
			    print "<li>Analysis: ";
			    print join(':',@anal)."</li>";
			}
			if ($params{tf_reference} eq 'on' && $an[6]) {
			    my @ref=$dbh->get_data_by_primary_key('ref',$an[6]);
			    print "<li>Reference: ".$ref[0]."</li>";
			}
			if ($params{tf_interaction} eq 'on') {
			    my ($table,$pazarid,@dat)=$dbh->links_to_data($inter->{olink},'output');
			    if ($table eq 'interaction') {
				print "<li>Interaction: ";
				my @data;
				for (my $i=0;$i<(@dat-3);$i++) {
				    if ($dat[$i] && $dat[$i] ne '0') {
					push @data,$dat[$i];
				    }
				}
				print join(":",@data)."</li>";
			    }
			}
			if ($params{tf_evidence} eq 'on' && $an[1]) {
			    my @ev=$dbh->get_data_by_primary_key('evidence',$an[1]);
			    print "<li>Evidence: ".$ev[0]."_".$ev[1]."</li>";
			}
			$count++;
		    }}
		my @expressors=$dbh->get_expression_by_regseq_id($regseq->accession_number);
		foreach my $exp (@expressors) {
		    if ($params{other_analysis} eq 'on' || $params{other_reference} eq 'on' || $params{other_effect} eq 'on' || $params{other_evidence} eq 'on') {
			print "<li><b>Line of evidence $count: </b></li>";
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
			    print "<li>Analysis: ";
			    print join(':',@anal)."</li>";
			}
			if ($params{other_reference} eq 'on' && $an[6]) {
			    my @ref=$dbh->get_data_by_primary_key('ref',$an[6]);
			    print "<li>Reference: ".$ref[0]."</li>";
			}
			if ($params{other_effect} eq 'on') {
			    my ($table,$tableid,@dat)=$dbh->links_to_data($exp->{olink},'output');
			    print "<li>Expression: ";
			    my @data;
			    for (my $i=0;$i<(@dat-3);$i++) {
				if ($dat[$i] && $dat[$i] ne '0') {
				    push @data,$dat[$i];
				}
			    }
			    print join(":",@data)."</li>";
			}
			if ($params{other_evidence} eq 'on' && $an[1]) {
			    my @ev=$dbh->get_data_by_primary_key('evidence',$an[1]);
			    print "<li>Evidence: ".$ev[0]."_".$ev[1]."</li>";
			}
			$count++;
		    }}
		print "</ul><br>";
	    }
	}
    }
    if (scalar(@projects)==$empty) {
	print "<p class=\"warning\">No regulatory sequence was found for gene $gene! Is it really an Ensembl Gene ID?</p>\n";
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
