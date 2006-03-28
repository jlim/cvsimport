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
		      -drv           =>    'mysql');

my $ensdb = pazar::talk->new(DB=>'ensembl',USER=>$ENV{ENS_USER},PASS=>$ENV{ENS_PASS},HOST=>$ENV{ENS_HOST},DRV=>'mysql');

my $gkdb = pazar::talk->new(DB=>'genekeydb',USER=>$ENV{GKDB_USER},PASS=>$ENV{GKDB_PASS},HOST=>$ENV{GKDB_HOST},DRV=>'mysql');

my $get = new CGI;
my %params = %{$get->Vars};
my $accn = $params{geneID};
my $dbaccn = $params{ID_list};
my @trans;

if (!$accn) {
    print "<p class=\"warning\">Please provide a TF ID!</p>\n";
} else {
    if ($dbaccn eq 'EnsEMBL_gene') {
	@trans = $gkdb->ens_transcripts_by_gene($accn);
    } elsif ($dbaccn eq 'EnsEMBL_transcript') {
	push @trans,$accn;
        unless ($trans[0]=~/\w{2,}/) {die "Conversion failed for $accn";}
    } elsif ($dbaccn eq 'EntrezGene') {
	my @gene=$gkdb->llid_to_ens($accn);
	unless ($gene[0]=~/\w{2,}/) {die "Conversion failed for $accn";}
	@trans = $gkdb->ens_transcripts_by_gene($gene[0]);
    } elsif ($dbaccn eq 'nm') {
	@trans=$gkdb->nm_to_enst($accn);
	unless ($trans[0]=~/\w{2,}/) {die "Conversion failed for $accn";}
    } elsif ($dbaccn eq 'swissprot') {
	my $sp=$gkdb->prepare("select organism from ll_locus a, gk_ll2sprot b where a.ll_id=b.ll_id and sprot_id=?")||die;
	$sp->execute($accn)||die;
	my $species=$sp->fetchrow_array();
	$ensdb->change_mart_organism($species);
	my @trans =$ensdb->swissprot_to_enst($accn);
	unless ($trans[0]=~/\w{2,}/) {die "Conversion failed for $accn";}
    } elsif ($dbaccn eq 'tf_name') {
    }
    foreach my $trans (@trans) {
	print "you're looking for transcript: ".$trans."\n";
    }
#     my @tfcomplexes = $dbh->get_complex_by_name($tf_name); 
#     if (!$regseqs[0]) {
# 	print "<p class=\"warning\">No information was found for gene $gene!</p>\n";
#     } else {
# 	my @ens_coords = $ensdb->get_ens_chr($gene);
# 	foreach my $reg_seq (@regseqs) {
# 	    undef my %attr;
# 	    foreach my $item (keys %params) {
# 		if ($params{$item} eq 'on') {
# 		    eval {$reg_seq->$item };
# 		    unless ($@) {
# 			if ($item eq "binomial_species") {
# 			    $attr{'species'}=$reg_seq->$item;
# 			} else {
# 			    $attr{$item}=$reg_seq->$item;
# 			}
# 		    }
# 		    if ($item eq 'length') {
# 			$attr{$item}=($reg_seq->end)-($reg_seq->start)+1;
# 		    }
# 		    if ($item eq 'tss') {
# 			if ($reg_seq->transcript_fuzzy_start == $reg_seq->transcript_fuzzy_end) { 
# 			    $attr{$item}=$reg_seq->transcript_fuzzy_start;
# 			} else {
# 			    $attr{$item}=$reg_seq->transcript_fuzzy_start."-".$reg_seq->transcript_fuzzy_end; 
# 			}
# 		    }
# 		    if ($item eq 'EnsEMBL_description') {
# 			my @desc = split('\[',$ens_coords[5]);
# 			$attr{$item}=$desc[0];
# 		    }
# 		    if ($item =~ /TF/ || $item =~ /interaction/ || $item =~ /other/) {
# 			my $aid = $dbh->get_analysis_IO_by_regseq_id($reg_seq->accession_number);

# 			if ($item =~ /other/) {
# 			}

# 		    }

# 		}
# 	    }
# 	    my @attr=qw(gene_accession gene_description EnsEMBL_description transcript_accession isoform tss id seq chromosome band start end length strand quality species);
# 	    for (my $i=0;$i<@attr;$i++) {
# 		if ($attr{$attr[$i]}) {
# 		    print "<span class=\"bold\">".$attr[$i].": </span>".$attr{$attr[$i]}."<br>";
# 		}
# 	    }
#             print "<br><br>";
# 	}
#     }
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

