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
	    undef my %attr;
	    foreach my $item (keys %params) {
		if ($params{$item} eq 'on') {
		    eval {$reg_seq->$item };
		    if ($@) { next;}
		    else {
			if ($item eq "binomial_species") {
			    $attr{'species'}=$reg_seq->$item;
			} else {
			    $attr{$item}=$reg_seq->$item;
			}
		    }
		    if ($item eq 'length') {
			$attr{$item}=($reg_seq->end)-($reg_seq->start)+1;
		    }
		    if ($item eq 'tss') {
			if ($reg_seq->transcript_fuzzy_start == $reg_seq->transcript_fuzzy_end) { 
			    $attr{$item}=$reg_seq->transcript_fuzzy_start;
			} else {
			    $attr{$item}=$reg_seq->transcript_fuzzy_start."-".$reg_seq->transcript_fuzzy_end; 
			}
		    }

		}
	    }
	    my @attr=qw(gene_accession gene_description transcript_accession isoform tss id seq chromosome band start end length strand quality species);
	    for (my $i=0;$i<@attr;$i++) {
		if ($attr{$attr[$i]}) {
		    print "<span class=\"bold\">".$attr[$i].": </span>".$attr{$attr[$i]}."<br>";
		}
	    }
            print "<br><br>";
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
