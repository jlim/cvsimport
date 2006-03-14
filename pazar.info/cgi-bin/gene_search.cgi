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

use constant DB_DRV  => 'mysql';
use constant DB_NAME => $ENV{PAZAR_name};
use constant DB_USER => $ENV{PAZAR_pubuser};
use constant DB_PASS => $ENV{PAZAR_pubpass};
use constant DB_HOST => $ENV{PAZAR_host};


# open the html header template
my $template = HTML::Template->new(filename => 'header.tmpl');

# fill in template parameters
$template->param(TITLE => 'PAZAR Gene Search');

# send the obligatory Content-Type and print the template output
print "Content-Type: text/html\n\n", $template->output;

#connect to the database
my $dbh = pazar->new( 
		      -host          =>    DB_HOST,
		      -user          =>    DB_USER,
		      -pass          =>    DB_PASS,
		      -pazar_user    =>    'elodie',
		      -pazar_pass    =>    'pazarpw',
		      -dbname        =>    DB_NAME,
		      -drv           =>    DB_DRV);


my $get = new CGI;
my %params = %{$get->Vars};
my $gene = $params{geneID};

if (!$gene) {
    print "<p class=\"warning\">Please provide a gene ID!</p>\n";
} else {
    my @regseqs = $dbh->get_reg_seqs_by_accn($gene); 
    if (!$regseqs[0]) {
	print "<p class=\"warning\">No regulatory sequence was found for this gene!</p>\n";
    } else {
	foreach my $reg_seq (@regseqs) {
	    print $reg_seq->seq."\n";
	    print $reg_seq->start."\n";
	    print $reg_seq->end."\n";
	    print $reg_seq->strand."\n";
	    print $reg_seq->id."\n";
	    print $reg_seq->accession_number."\n";
	    print $reg_seq->chromosome."\n";
	    print $reg_seq->band."\n";
	    print $reg_seq->quality."\n";
	    print $reg_seq->binomial_species."\n";
	    print $reg_seq->gene_dbname."\n";
	    print $reg_seq->gene_dbsubset."\n";
	    print $reg_seq->gene_accession."\n";
	    print $reg_seq->gene_description."\n";
	    print $reg_seq->transcript_dbname."\n";
	    print $reg_seq->transcript_dbsubset."\n";
	    print $reg_seq->transcript_accession."\n";
	    print $reg_seq->isoform."\n";
	    print $reg_seq->transcript_comment."\n";
	    print $reg_seq->seq_dbname."\n";
	    print $reg_seq->seq_dbsubset."\n";
	    print $reg_seq->seq_dbassembly."\n";
	    print $reg_seq->transcript_fuzzy_start."\n";
	    print $reg_seq->transcript_fuzzy_end."\n";
	    print $reg_seq->transcript_predominant_start."\n";
	}
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
