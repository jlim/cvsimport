#!/usr/local/bin/perl

use pazar;
use pazar::gene;
use pazar::talk;

use HTML::Template;

use CGI qw(:standard);
use CGI::Carp qw(fatalsToBrowser);
#use CGI::Debug( report => 'everything', on => 'anything' );

use TFBS::PatternGen::MEME;
use TFBS::Matrix::PFM;

use Data::Dumper;

#connect to the database
my $dbh = pazar->new( 
                      -globalsearch  =>    'yes',
		      -host          =>    $ENV{PAZAR_host},
		      -user          =>    $ENV{PAZAR_pubuser},
		      -pass          =>    $ENV{PAZAR_pubpass},
		      -dbname        =>    $ENV{PAZAR_name},
		      -drv           =>    'mysql');

my $ensdb = pazar::talk->new(DB=>'ensembl',USER=>$ENV{ENS_USER},PASS=>$ENV{ENS_PASS},HOST=>$ENV{ENS_HOST},DRV=>'mysql');

my $gkdb = pazar::talk->new(DB=>'genekeydb',USER=>$ENV{GKDB_USER},PASS=>$ENV{GKDB_PASS},HOST=>$ENV{GKDB_HOST},DRV=>'mysql');

my $get = new CGI;
my %param = %{$get->Vars};
foreach my $ac ($get->param('accn')) {
	push @accns, $ac;
    }
my $accn = join('_',@accns);

#initialize the html page
print $get->header("text/html");
print "<head>
       <title>PAZAR - TF Profile</title>
       </head>
       <body style=\"background-color: rgb(255, 255, 255);\" onload=\"coll_all();\" onblur=\"self.focus();\">";

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
		print TMP ">".$key."\n";
		print TMP $param{$key}."\n";
	    }
}
    close (TMP);

###################################
if ($count<2) {
    print "<p class=\"warning\">There are not enough targets to build a binding profile for this TF!</p>\n";
    exit;
} else {
	my $patterngen =
	    TFBS::PatternGen::MEME->new(-seq_file=> "$file",
					-binary => 'meme',
					-additional_params => '-revcomp -mod oops');
	my $pfm = $patterngen->pattern(); # $pfm is now a TFBS::Matrix::PFM object

	if (!$pfm) {
	    print "<p class=\"warning\">No motif could be found!</p>\n";
	} else {
#print a human readable format of the matrix
	my $prettystring = $pfm->prettyprint();
	my @matrixlines = split /\n/, $prettystring;
	$prettystring = join "<BR>\n", @matrixlines;
	$prettystring =~ s/ /\&nbsp\;/g;
	print $get->h3("Custom Profile for TF $accn");
	print "<span style=\"font-size: 14pt;\"><b>Position Frequency Matrix:</b></span><br><br><SPAN style=\"font-size: 11pt;font-family: monospace;\">$prettystring</SPAN><br>";
#draw the logo
	my $logo = $newaccn.".png";
	my $gd_image = $pfm->draw_logo(-file=>"/space/usr/local/apache/pazar.info/tmp/".$logo, -xsize=>400);
	print "<br><p style=\"font-size: 14pt;\"><b>Logo:</b><br><img src=\"http://www.pazar.info/tmp/$logo\"></p>";
	print "<p style=\"font-size: 10pt;\">These PFM and Logo were generated dynamically using the MEME pattern discovery algorithm.</p>";
    }
    }

# print out the html end
print "</body></html>";

