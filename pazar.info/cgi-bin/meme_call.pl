#!/usr/bin/perl
use CGI;
use TFBS::PatternGen::MEME;

my $cgi=new CGI;
print "Content-Type: text/html\n\n";
my $mpram=join(' ',@{$cgi->param('mparam')});
my $file=$cgi->param('seqfile');
		my $patterngen =
		    TFBS::PatternGen::MEME->new(-seq_file=> $file,
						-binary => 'meme',
						-additional_params => $mparam);
		my $pfm = $patterngen->pattern(); # $pfm is now a TFBS::Matrix::PFM object
		if (!$pfm) {
		    print "<span class='red'>No motif could be found!<br>Try running the motif discovery again with a sub-selection of sequences.</span><br><br><br><br>\n";
		    next;
		} else {
#print a human readable format of the matrix
		    my $prettystring = $pfm->prettyprint();
		    my @matrixlines = split /\n/, $prettystring;
		    $prettystring = join "<BR>\n", @matrixlines;
		    $prettystring =~ s/ /\&nbsp\;/g;
		    print "<table bordercolor='white' bgcolor='white' border=1 cellspacing=0 cellpadding=10><tr><td><span class=\"title4\">Position Frequency Matrix</span></td><td><SPAN class=\"monospace\">$prettystring</SPAN></td></tr>";
#draw the logo
		    my $logo = $pazartfid.".png";
		    my $gd_image = $pfm->draw_logo(-file=>"$pazarhtdocspath/tmp/".$logo, -xsize=>400);
		    print "<tr><td><span class=\"title4\">Logo</span></td><td><img src=\"$pazar_html/tmp/$logo\">";
		    print "<p class=\"small\">These PFM and Logo were generated dynamically using the MEME pattern discovery algorithm.</p></td></tr>\n";
		    print "</table><br><br><br><br>\n";
		    
exit();
