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

my $projid = $dbh->get_projectid();

my $get = new CGI;
my %param = %{$get->Vars};

print "<p class=\"title1\">PAZAR - Project $proj Results</p>";

### gene-centric view
if ($param{view} eq 'gene-centric') {
    my @reg_seqs;

### species filter
    if ($param{species_filter} eq 'on' && $param{species} ne 'all') {
	unless ($param{region_filter} eq 'on') {
	    @reg_seqs=$dbh->get_reg_seq_by_species($param{species});
            if (!$regseqs[0]) {print "<p class=\"warning\">No regulatory sequence was found for species $param{species}</p>\n"; exit;}
	} else {

### region filter
	    if ($param{chr_filter} eq 'on' && $param{chromosome} ne 'all') {
		unless ($param{bp_filter} eq 'on') {
		    @reg_seqs=$dbh->get_reg_seq_by_chromosome($param{chromosome},$param{species});
                    if (!$regseqs[0]) {print "<p class=\"warning\">No regulatory sequence was found on chromosome $param{chromosome} in species $param{species}</p>\n"; exit;}
		} else {
		    @reg_seqs=$dbh->get_reg_seq_by_chromosome($param{bp_start},$param{bp_end},$param{chromosome},$param{species});
                    if (!$regseqs[0]) {print "<p class=\"warning\">No regulatory sequence was found between bp $param{bp_start} and $param{bp_end} on chromosome $param{chromosome} in species $param{species}</p>\n"; exit;}
		}
	    }
	}
    } else {
	if ($param{region_filter} eq 'on') {print "<p class=\"warning\">You have to select a species if you want to use the region filter!</p>\n"; exit;}
    }

### gene filter
    if ($param{gene_filter} eq 'on' && !grep(/^all$/,@{$param{gene}})) {
	if ($regseqs[0]) {print "<p class=\"warning\">You cannot use species and region filters when using the gene filter!</p>\n"; exit;}
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
    my @filters;
    my @excluded;
    my @exclud_inter;
    my @exclud_expr;
    foreach my $regseq (@regseqs) {

### length filter
	if ($param{length_filter} eq 'on' && $param{length} && $param{length} ne '0') {
	    my $length = $regseq->end - $regseq->start +1;
	    if ($param{shorter_larger} eq 'equal_to') {
		unless ($length == $param{length}) {
		    push @excluded,$regseq->accession_number;
		    next;
		}
	    }
	    if ($param{shorter_larger} eq 'greater_than') {
		unless ($length >= $param{length}) {
		    push @excluded,$regseq->accession_number;
		    next;
		}
	    }
	    if ($param{shorter_larger} eq 'less_than') {
		unless ($length <= $param{length}) {
		    push @excluded,$regseq->accession_number;
		    next;
		}
	    }
	}
	my @interactors=$dbh->get_interacting_factor_by_regseq_id($regseq->accession_number);
       	foreach my $inter (@interactors) {

### TF filter
	    if ($param{tf_filter} eq 'on' && !grep(/^all$/,@{$param{tf}})) {
		my @tfs;
		while (@$param{tf}) {
		    push @tfs, $_;
		}
		my $tf_name = $dbh->get_complex_name_by_id($inter->{tfcomplex});
		unless (grep(/^$tf_name$/,@tfs)) {
		    my %an;
		    $an{aid}=$inter->{aid};
		    $an{olink}=$inter->{olink};
		    $an{tfcomplex}=$inter->{tfcomplex};
		    $an{rsid}=$regseq->accession_number;
		    push @exclud_inter,\%an;
		    next;
		}
	    }

### TF class filter


	my @expressors=$dbh->get_expression_by_regseq_id($regseq->accession_number);

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
