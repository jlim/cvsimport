#!/usr/bin/perl
use CGI;

my $cgi = new CGI;
my $pazarhtdocspath = $ENV{PAZARHTDOCSPATH};
my $pazar_html = $ENV{PAZAR_HTML};
my $fasta = $cgi->param("fasta");
my $tf = $cgi->param("TFID");

print "Content-Type:application/x-download\n";  
print "Content-Disposition:attachment;filename=PAZAR_$tf"."_seqs.txt\n\n"; 
print $fasta; 