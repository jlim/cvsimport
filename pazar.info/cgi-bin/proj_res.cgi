#!/usr/bin/perl

use HTML::Template;
use strict;
use Data::Dumper;
use pazar;
use pazar::reg_seq;
use pazar::talk;
use pazar::tf::tfcomplex;
use pazar::tf::subunit;
use CGI qw(:standard);
use CGI::Carp qw(fatalsToBrowser);
use CGI::Debug( report => 'everything', on => 'anything' );

 
# open the html header template
my $template = HTML::Template->new(filename => 'header.tmpl');

# fill in template parameters
$template->param(TITLE => "PAZAR - Project Search Engine");

# send the obligatory Content-Type and print the template output
print "Content-Type: text/html\n\n", $template->output;

###getting the project_name
my $proj='gffparsertest';

###database connection
my $dbh= pazar->new( 
		       -host          =>    $ENV{PAZAR_host},
		       -user          =>    $ENV{PAZAR_pubuser},
		       -pass          =>    $ENV{PAZAR_pubpass},
		       -pazar_user    =>    'elodie@cmmt.ubc.ca',
		       -pazar_pass    =>    'pazarpw',
		       -dbname        =>    $ENV{PAZAR_name},
		       -drv           =>    'mysql',
		       -project       =>    $proj);

my $talkdb = pazar::talk->new(DB=>'ensembl',USER=>$ENV{ENS_USER},PASS=>$ENV{ENS_PASS},HOST=>$ENV{ENS_HOST},DRV=>'mysql');

my $ensdb = pazar::talk->new(DB=>'ensembl',USER=>$ENV{ENS_USER},PASS=>$ENV{ENS_PASS},HOST=>$ENV{ENS_HOST},DRV=>'mysql');

my $projid = $dbh->get_projectid();

my $get = new CGI;
my %param = %{$get->Vars};

print "<p class=\"title1\">PAZAR - Project $proj Results</p>";

### gene-centric view
if ($param{view} eq 'gene-centric') {
    my @reg_seqs;

### species filter
    if ($param{species_filter} eq 'on') {
	if (!$param{species}) {print "<p class=\"warning\">You need to select one or more species when using the species filter!</p>\n"; exit;}
	unless ($param{region_filter} eq 'on') {
	    @reg_seqs=$dbh->get_reg_seq_by_species($param{species});
            if (!$regseqs[0]) {print "<p class=\"warning\">No regulatory sequence was found for species $param{species}</p>\n"; exit;}
	} else {

### region filter
	    if ($param{chr_filter} eq 'on') {
		unless ($param{bp_filter} eq 'on') {
		    @reg_seqs=$dbh->get_reg_seq_by_chromosome($param{chromosome},$param{species});
                    if (!$regseqs[0]) {print "<p class=\"warning\">No regulatory sequence was found on chromosome $param{chromosome} in species $param{species}</p>\n"; exit;}
		} else {
if (!$param{bp_start} || !$param{bp_end}) {print "<p class=\"warning\">You need to specify the start and end of the region you're interested in when using the base pair filter!</p>\n"; exit;}
		    @reg_seqs=$dbh->get_reg_seq_by_region($param{bp_start},$param{bp_end},$param{chromosome},$param{species});
                    if (!$regseqs[0]) {print "<p class=\"warning\">No regulatory sequence was found between bp $param{bp_start} and $param{bp_end} on chromosome $param{chromosome} in species $param{species}</p>\n"; exit;}
		}
	    }
	}
    } else {
	if ($param{region_filter} eq 'on') {print "<p class=\"warning\">You have to select a species if you want to use the region filter!</p>\n"; exit;}
    }

### gene filter
    if ($param{gene_filter} eq 'on') {
	if ($regseqs[0]) {print "<p class=\"warning\">You cannot use species and region filters when using the gene filter!</p>\n"; exit;}
	if (!$param{gene}) {print "<p class=\"warning\">You need to select one or more gene when using the gene filter!</p>\n"; exit;}
	my @genes;
	while (@{$param{gene}}) {
	    push @genes, $_;
	}
        foreach my $accn (@genes) {
	    my @seqs=$dbh->get_reg_seq_by_accn($accn);
	    foreach my $regseq (@seqs) {
		push @reg_seqs, $regseq;
	    }
	}
	if (!$regseqs[0]) {print "<p class=\"warning\">No regulatory sequence was found for the genes ".join(',',@genes)."!</p>\n"; exit;}

    }
    if (!$regseqs[0]) {
	my @rsid = $dbh->get_all_regseq_ids();
	foreach my $id (@rsid) {
	    my @seqs=$dbh->get_reg_seq_by_regseq_id($id);
	    foreach my $regseq (@seqs) {
		push @reg_seqs, $regseq;
	    }
	}
    }
    if (!$regseqs[0]) {print "<p class=\"warning\">No regulatory sequence was found in this project!</p>\n"; exit;}

    foreach my $regseq (@regseqs) {

### length filter
	if ($param{length_filter} eq 'on' && $param{length} ne '0') {
	if (!$param{length} || $param{length}<=0) {print "<p class=\"warning\">You need to specify a length greater than 0 when using the length filter!</p>\n"; exit;}

	    my $length = $regseq->end - $regseq->start +1;
	    if ($param{shorter_larger} eq 'equal_to') {
		unless ($length == $param{length}) {
		    next;
		}
	    }
	    if ($param{shorter_larger} eq 'greater_than') {
		unless ($length >= $param{length}) {
		    next;
		}
	    }
	    if ($param{shorter_larger} eq 'less_than') {
		unless ($length <= $param{length}) {
		    next;
		}
	    }
	}
	my @inters;
	my @interactors=$dbh->get_interacting_factor_by_regseq_id($regseq->accession_number);
	$count=0;
       	foreach my $inter (@interactors) {
	    $count++;
### TF filter
	    if ($param{tf_filter} eq 'on') {
	        if (!$param{tf}) {print "<p class=\"warning\">You need to select one or more TF when using the TF filter!</p>\n"; exit;}
		my @tfs;
		while (@$param{tf}) {
		    push @tfs, $_;
		}
		my $tf_name = $dbh->get_complex_name_by_id($inter->{tfcomplex});
		unless (grep(/^$tf_name$/,@tfs)) {
		    next;
		}
	    }

### TF class filter
	    if ($param{class_filter} eq 'on') {
		my $tf = $dbh->create_tf;
		my $complex = $tf->get_tfcomplex_by_id($inter->{tfcomplex},'notargets');
		my $found = 0;
		my $cf;
		while (my $subunit=$tfcomplex->next_subunit) {
		    if ($subunit->get_class && $subunit->get_fam) {
			$cf = $subunit->get_class."/".$subunit->get_fam;
		    } elsif ($subunit->get_class && !$subunit->get_fam) {
			$cf = $subunit->get_class;
		    }
		    if ($param{class} == $cf)) {
			$found = 1;
		    }
		}
		if ($found == 0) {
		    next;
		}
	    }

### interaction filter
	    if ($param{interaction_filter} eq 'on') {
		my ($table,$pazarid,@dat)=$dbh->links_to_data($inter->{olink},'output');
		my $qual=lc($dat[0]);
		my $match=0;
		if ($qual eq $param{interaction}) {
		    $match = 1;
		} elsif ($param{interaction} eq 'not_null' && $qual && $qual ne 'none' && $qual ne 'na') {
		    $match = 1;
		} elsif ($param{interaction} ne 'none' && $dat[1]>0) {
		    $match = 1;
		} elsif ($param{interaction} eq 'none' && (!$qual || $qual eq 'na') && $dat[1]==0) {
		    $match = 1;
		}
		if ($match == 0) {
		    next;
		}
	    }

### evidence filter
	    if ($param{evidence_filter} eq 'on') {
	        if (!$param{evidence}) {print "<p class=\"warning\">You need to select one or more evidence type when using the evidence filter!</p>\n"; exit;}
		my @evids;
		while (@$param{evidence}) {
		    push @evids, $_;
		}
		my ($evid,@res)=$dbh->get_evidence_by_analysis_id($inter->{aid});
		unless (grep(/^$evid$/,@evids)) {
		    next;
		}
	    }

### method filter
	    if ($param{method_filter} eq 'on') {
	        if (!$param{method}) {print "<p class=\"warning\">You need to select one or more method type when using the method filter!</p>\n"; exit;}
		my @mets;
		while (@$param{method}) {
		    push @mets, $_;
		}
		my ($met,@res)=$dbh->get_method_by_analysis_id($inter->{aid});
		unless (grep(/^$met$/,@mets)) {
		    next;
		}
		push @inters, $inter;
	    }
	my @exprs;
	my @expressors=$dbh->get_expression_by_regseq_id($regseq->accession_number);
       	foreach my $expr (@expressors) {

### expression filter
	    if ($param{expression_filter} eq 'on') {
		my ($table,$pazarid,@dat)=$dbh->links_to_data($expr->{olink},'output');
		my $qual=lc($dat[0]);
		my $match=0;
		if ($qual eq $param{expression}) {
		    $match = 1;
		} elsif ($param{expression} eq 'change' && $qual && $qual ne ('no change'|| 'na')) {
		    $match = 1;
		} elsif ($param{expression} eq ('change' || 'highly induced' || 'induced') && $dat[1]>0) {
		    $match = 1;
		} elsif ($param{expression} eq ('change' || 'highly repressed' || 'repressed') && $dat[1]<0) {
		    $match = 1;
		}
		if ($match == 0) {
		    next;
		}
	    }

### evidence filter
	    if ($param{evidence_filter} eq 'on') {
	        if (!$param{evidence}) {print "<p class=\"warning\">You need to select one or more evidence type when using the evidence filter!</p>\n"; exit;}
		my @evids;
		while (@$param{evidence}) {
		    push @evids, $_;
		}
		my ($evid,@res)=$dbh->get_evidence_by_analysis_id($expr->{aid});
		unless (grep(/^$evid$/,@evids)) {
		    next;
		}
	    }

### method filter
	    if ($param{method_filter} eq 'on') {
	        if (!$param{method}) {print "<p class=\"warning\">You need to select one or more method type when using the method filter!</p>\n"; exit;}
		my @mets;
		while (@$param{method}) {
		    push @mets, $_;
		}
		my ($met,@res)=$dbh->get_method_by_analysis_id($expr->{aid});
		unless (grep(/^$met$/,@mets)) {
		    next;
		}
	    }
	    push @exprs, $expr;
	}
	if ($exprs[0] || $inters[0]) {
	    &print_gene_attributes($dbh, $ensdb, $regseq, /@inters, /@exprs, %param);
	}

### TF filter
} elsif ($param{view} eq 'tf-centric') 

}

###  print out the html tail template
  my $template_tail = HTML::Template->new(filename => 'tail.tmpl');
  print $template_tail->output;

sub select {

    my ($dbh, $sql) = @_;
    my $sth=$dbh->prepare($sql);
    $sth->execute or die "$dbh->errstr\n";
    return $sth;
}

sub print_gene_attr {
    my ($dbh, $ensdb, $reg_seq, $inters, $exprs, %params) = @_;
	    print "<ul style=\"margin: 0pt; padding: 0pt; list-style-type: none;\">";
	    if ($params{at_gene} eq 'on') {
		my $transcript=$regseq->transcript_accession || 'Transcript Not Specified';
		print "<li><b>Gene/Transcript: </b>".$regseq->gene_accession."/".$transcript."</li>";
		my @ens_coords = $ensdb->get_ens_chr($regseq->gene_accession);
		my @desc = split('\[',$ens_coords[5]);
		print "<li>".$desc[0]."</li>";
	    }
	    if ($params{at_tss} eq 'on') {
		if ($regseq->transcript_fuzzy_start == $regseq->transcript_fuzzy_end) { print "<li><b>Transcription Start Site: </b>".$regseq->transcript_fuzzy_start."</li>";} else {
		    print "<li>Transcription Start Site: </b>".$regseq->transcript_fuzzy_start."-".$regseq->transcript_fuzzy_end."</li>";
		}
	    }
	    if ($params{at_species} eq 'on') {
		print "<li><b>Species: </b>".$regseq->binomial_species."</li>";
	    }
	    if ($params{at_reg_seq_name} eq 'on' && $regseq->id) {
		print "<li><b>Name: </b>".$regseq->id."</li>";
	    }
	    if ($params{at_sequence} eq 'on') {
		print "<li><b>Sequence: </b>".$regseq->seq."</li>";
	    }
	    if ($params{at_coordinates} eq 'on') {
		print "<li><b>Coordinates: </b>".$regseq->chromosome." (".$regseq->strand.") ".$regseq->start."-".$regseq->end."</li>";
	    }
	    if ($params{at_quality} eq 'on') {
		print "<li><b>Quality: </b>".$regseq->quality."</li>";
	    }
	    my $count=1;
	    foreach my $inter (@$inters) {
		print "<li><b>Line of evidence $count: </b></li>";
		if ($params{at_tf} eq 'on') {
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
		if ($params{at_tf_analysis} eq 'on') {
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
		if ($params{at_tf_reference} eq 'on' && $an[6]) {
		    my @ref=$dbh->get_data_by_primary_key('ref',$an[6]);
		    print "<li>Reference: ".$ref[0]."</li>";
		}
		if ($params{at_tf_interaction} eq 'on') {
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
		if ($params{at_tf_evidence} eq 'on' && $an[1]) {
		    my @ev=$dbh->get_data_by_primary_key('evidence',$an[1]);
		    print "<li>Evidence: ".$ev[0]."_".$ev[1]."</li>";
		}
		$count++;
	    }
	    foreach my $exp (@$exprs) {
		print "<li><b>Line of evidence $count: </b></li>";
	    	my @an=$dbh->get_data_by_primary_key('analysis',$exp->{aid});
		if ($params{at_other_analysis} eq 'on') {
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
		if ($params{at_other_reference} eq 'on' && $an[6]) {
		    my @ref=$dbh->get_data_by_primary_key('ref',$an[6]);
		    print "<li>Reference: ".$ref[0]."</li>";
		}
		if ($params{at_other_effect} eq 'on') {
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
		if ($params{at_other_evidence} eq 'on' && $an[1]) {
		    my @ev=$dbh->get_data_by_primary_key('evidence',$an[1]);
		    print "<li>Evidence: ".$ev[0]."_".$ev[1]."</li>";
		}
		$count++;
	    }
	    print "</ul>";
}
