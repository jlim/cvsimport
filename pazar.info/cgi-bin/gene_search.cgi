#!/usr/local/bin/perl

use lib '/space/usr/local/src/ensembl-36/ensembl/modules/';
use lib '/space/usr/local/src/bioperl-live/';

use strict;

use pazar;

use CGI qw(:standard);
use CGI::Carp qw(fatalsToBrowser);
use CGI::Debug( report => 'everything', on => 'anything' );

use constant DB_DRV  => 'mysql';
use constant DB_NAME => $ENV{PAZAR_name};
use constant DB_USER => $ENV{PAZAR_pubuser};
use constant DB_PASS => $ENV{PAZAR_pubpass};
use constant DB_HOST => $ENV{PAZAR_host};

my $get = new CGI;
my $action = $get->param('submit');

#initialize the html page
print $get->header("text/html");

#connect to the database
my $dbh = pazar->new( 
	  	   -host    =>    DB_HOST,
                   -user    =>    DB_USER,
                   -pass    =>    DB_PASS,
                   -dbname  =>    DB_NAME,
		   -drv     =>    DB_DRV);

print "<head>
    <title>PAZAR - search by gene</title>
    </head>


    <body style=\"background-color: rgb(255, 255, 255);\">

    <center>
    <table width=\"600\">

    <tbody>

    <tr>

    <td width=\"600\">
    <center>
    <p><b><i><span style=\"font-size: 20pt;\">PAZAR</span></i></b><b><span style=\"font-size: 14pt;\"> </span></b><b><span style=\"font-size: 20pt;\"><i>-</i> Search by Gene
    </span></b></p>
    </center>

    <hr><br>";

my $gene = $get->param('geneID');

if (!$gene) {
    print "<big>Please provide a gene ID!</big>\n";
} else {
 
my $reg_seqs = $dbh->get_psms_by_accn($gene);
print "$reg_seqs\n";

if (!$reg_seqs) {
    print "<big>No regulatory sequence was found for this gene!</big>\n";
} else {
foreach my $psm (@{$reg_seqs}) {
		print $psm->id,"\t",$psm->start,"\t",$psm->end,"\t",$psm->seq,"\n";
}
}}
print "</td></tr></tbody></table></center></body></html>";




sub select {

    my ($dbh, $sql) = @_;
    my $sth=$dbh->prepare($sql);
    $sth->execute or die "$dbh->errstr\n";
    return $sth;
}
