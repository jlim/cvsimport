#!/usr/bin/perl
use CGI;
use TFBS::PatternGen::MEME;
use Digest::MD5 qw(md5 md5_hex md5_base64);
use Data::Dumper;

my $cgi=new CGI;
my $pazarhtdocspath=$ENV{PAZARHTDOCSPATH};
my $pazar_html=$ENV{PAZAR_HTML};
print "Content-Type: text/html\n\n";
my $tfname = $cgi->param('tfname');

#a value containing both tfid and project id - used in this page to make form element names different for tfs with the same name (but from different projects)
my $tf_projid = $cgi->param('tfpid');

#need to make this file system and url friendly for passing to dumptfprofile.pl
$tfname =~s/\//_/g;
$tfname =~s/\(/_/g;
$tfname =~s/\)/_/g;

#need to replace - with _ for HTML form element names
my $tfname_form = $tfname;
$tfname_form =~s/-/_/g;


my @seq=$cgi->param('seq');
my $allseq=join("\n",@seq);
#print "Allseq $allseq";
my $fn=md5_hex($allseq) . '.fa';
open (SEQ,">/tmp/$fn")||print "Cannot open tmp file to write";
my $i=0;
foreach my $s (@seq) {
	$i++;
if (length($s)<8) {
my $def=8-length($s);
my $fl='N'x$def;
my $ns=$fl.$s.$fl;
$s=$ns;
}
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
		    my $urlstring=$prettystring;
#strip brackets from urlstring
$urlstring =~ s/(|\[|\])//g;
$urlstring =~ s/\ /%20/g;
$urlstring =~s/\n/br/g;

		    my @matrixlines = split /\n/, $prettystring;
		    $prettystring = join "<BR>\n", @matrixlines;
		    $prettystring =~ s/ /\&nbsp\;/g;

		    print "<table bordercolor='white' bgcolor='white' border=1 cellspacing=0 cellpadding=10><tr><td><span class=\"title4\">Position Frequency Matrix</span></td><td><SPAN class=\"monospace\">$prettystring</SPAN><br><!--<a href=\"dumptfprofile.pl?matrix=$urlstring\" target=\"tfprofiledownloadwin\">Click here to download text file</a>--><p><table bordercolor='white' bgcolor='white' cellspacing=0 border=1 cellpadding=5><tr><td align=left><form name=dlform$tfname><b>Profile Download</b><br>Enter a name for the profile (optional) <input type=\"text\" name=\"userfilename$tfname_form\_$tf_projid\"><br><br><table align=right><tr><td><input type=\"button\" value=\"Click here to download profile\" OnClick=javascript:window.open(\"http://$ENV{HTTP_HOST}/cgi-bin/dumptfprofile.pl?tfname=$tfname&matrix=$urlstring&userfilename=\"+this.form.userfilename$tfname_form\_$tf_projid.value);></td></tr></table></form></td></tr></table></p></td></tr>";

#draw the logo
		    my $logo = $pazarhtdocspath . '/tmp/' . $fn . '.png';
warn "LOGO $logo";
		    my $gd_image = $pfm->draw_logo(-file=>$logo, -xsize=>400);
		    print "<tr><td><span class=\"title4\">Logo</span></td><td><img src=\"$pazar_html/tmp/$fn\.png\">";
		    print "<p class=\"small\">These PFM and Logo were generated dynamically using the MEME pattern discovery algorithm.</p></td></tr>\n";
		    print "</table><br><br>\n";
}
		    
exit();
