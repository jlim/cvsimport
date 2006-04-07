#!/usr/local/bin/perl

use lib '/space/usr/local/src/ensembl-36/ensembl/modules/';
use lib '/space/usr/local/src/bioperl-live/';


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

my $get = new CGI;
my %param = %{$get->Vars};
my $accn = $param{accn};


my $count=0;
#alter file name by adding random number with current time as seed
srand(time() ^ ($$ + ($$ << 15) ) );
my $randnum = substr(rand() * 100,3);

my $newaccn = $accn.$randnum;
#print "using randum number for filename: $randnum";
    my $file="/space/usr/local/apache/pazar.info/tmp/".$newaccn.".fa";
    open (TMP, ">$file");

##########
#display param keys
#get each sequence

my @keys = keys %param;
while (@keys)
{
    my $key = pop(@keys);
    if($key =~ /seq/)
    {	
		$count++;
		my $construct_name=$accn."_site".$count;
		print TMP ">".$construct_name."\n";
		print TMP $param{$key}."\n";
	    }
}
    close (TMP);

###################################
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
	print "<span class=\"title4\">Position Frequency Matrix</span><br><SPAN class=\"monospace\">$prettystring</SPAN><br>";
#draw the logo
	my $logo = $newaccn.".png";
	my $gd_image = $pfm->draw_logo(-file=>"/space/usr/local/apache/pazar.info/tmp/".$logo, -xsize=>400);
	print "<br><p class=\"title4\">Logo: <br><img src=\"http://www.pazar.info/tmp/$logo\"></p>";
	print "<p class=\"small\">These PFM and Logo were generated dynamically using the MEME pattern discovery algorithm.</p>";
    }

# print out the html tail template
my $template_tail = HTML::Template->new(filename => 'tail.tmpl');
print $template_tail->output;


