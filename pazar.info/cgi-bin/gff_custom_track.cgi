#!/usr/bin/perl -w

use lib '/space/usr/local/src/ensembl-36/ensembl/modules/';
use lib '/space/usr/local/src/bioperl-live/';

use strict;

use pazar;
use pazar::reg_seq;

use CGI qw(:standard);
use CGI::Carp qw(fatalsToBrowser);
use CGI::Debug( report => 'everything', on => 'anything' );

require 'getsession.pl';

###database connection
my $dbh= pazar->new( 
		     -host          =>    $ENV{PAZAR_host},
		     -user          =>    $ENV{PAZAR_user},
		     -pass          =>    $ENV{PAZAR_pass},
		     -dbname        =>    $ENV{PAZAR_dbname},
		     -drv           =>    'mysql');

my @projects;

my $projects=&select($dbh, "SELECT project_id, project_name FROM project WHERE upper(status)='OPEN' OR upper(status)='PUBLISHED'");
while (my ($pid,$proj)=$projects->fetchrow_array) {
    push @projects, {name => $proj,
                     id   => $pid};
}
if ($loggedin eq 'true') {
    foreach my $proj (@projids) {
	my $restricted=&select($dbh, "SELECT project_name FROM project WHERE project_id='$proj' and upper(status)='RESTRICTED'");
	my @restr_proj=$restricted->fetchrow_array();
	if (@restr_proj) {
	    push @projects,  {name => $restr_proj[0],
			      id   => $proj}};
    }
}

my $file = 'pazar.gff';
open (GFF,">$file")||die;

foreach my $project (@projects) {
    my $proj=$project->{name};
    my $pid=$project->{id};
    my $rsh = &select($dbh, "SELECT reg_seq_id FROM reg_seq WHERE project_id='$pid'");
    while (my $rsid=$rsh->fetchrow_array) {
	my $regseq=$dbh->get_reg_seq_by_regseq_id($rsid);

	my @rest;
	push @rest,'sequence'.'="'.$regseq->seq.'"';
	push @rest,'db_seqinfo'.'="'.$regseq->seq_dbname.":".$regseq->seq_dbassembly.'"';
	if ($regseq->gene_description) {
	    push @rest,'db_geneinfo'.'="'.$regseq->gene_dbname.":".$regseq->gene_accession.":".$regseq->gene_description.'"';
	} else {
	    push @rest,'db_geneinfo'.'="'.$regseq->gene_dbname.":".$regseq->gene_accession.'"';
	}
	push @rest,'species'.'="'.$regseq->binomial_species.'"';

	my $rest=join(';',@rest);
	my $rsid7d = sprintf "%07d",$rsid;
	my $id="RS".$rsid7d;
	my $gff='chr'. $regseq->chromosome."\t". join("\t",$proj,$id,$regseq->start,$regseq->end,'.',$regseq->strand,'.',$rest);
	print GFF $gff."\n";
    }
}
close(GFF);

sub select {

    my ($dbh, $sql) = @_;
    my $sth=$dbh->prepare($sql);
    $sth->execute or die "$dbh->errstr\n";
    return $sth;
}
