#!/usr/bin/perl
use CGI;
use TFBS::PatternGen::MEME;
use Digest::MD5 qw(md5 md5_hex md5_base64);
use Data::Dumper;

my $cgi=new CGI;
print "Content-Type: text/html\n\n";
my @seq=$cgi->param('seq');
my $allseq=join("\n",@seq);
#print "Allseq $allseq";
my $fn=md5_hex($allseq) . '.fa';
open (SEQ,">/tmp/$fn")||print "Cannot open tmp file to write";
my $i=0;
foreach my $s (@seq) {
	$i++;
	print SEQ ">pazarseqs\_$i\n$s\n";
}
close SEQ;
		my $patterngen =
		    TFBS::PatternGen::MEME->new(-seq_file=> "/tmp/$fn",
						-binary => 'meme',
						-additional_params => '-revcomp -mod oops');
#print Dumper $patterngen;
		my $pfm = $patterngen->pattern(); # $pfm is now a TFBS::Matrix::PFM object
		#print Dumper $pfm;
		if (!$pfm) {
		    print "<span class='red'>No motif could be found!<br>Try running the motif discovery again with a sub-selection of sequences.</span><br><br><br><br>\n";
		   exit(1);
		} else {
#print a human readable format of the matrix
		    my $prettystring = $pfm->prettyprint();
		    my @matrixlines = split /\n/, $prettystring;
		    $prettystring = join "<BR>\n", @matrixlines;
		    $prettystring =~ s/ /\&nbsp\;/g;
		    print "<table bordercolor='white' bgcolor='white' border=1 cellspacing=0 cellpadding=10><tr><td><span class=\"title4\">Position Frequency Matrix</span></td><td><SPAN class=\"monospace\">$prettystring</SPAN></td></tr>";
#draw the logo
		    my $logo = $fn . ".png";
		    my $gd_image = $pfm->draw_logo(-file=>"$pazarhtdocspath/tmp/".$logo, -xsize=>400);
		    print "<tr><td><span class=\"title4\">Logo</span></td><td><img src=\"$pazar_html/tmp/$logo\">";
		    print "<p class=\"small\">These PFM and Logo were generated dynamically using the MEME pattern discovery algorithm.</p></td></tr>\n";
		    print "</table><br><br><br><br>\n";
}
		    
exit();
