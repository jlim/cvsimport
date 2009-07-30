#!/usr/bin/perl
use CGI;
use TFBS::PatternGen::MEME;
use Digest::MD5 qw(md5 md5_hex md5_base64);
use Data::Dumper;

my $cgi = new CGI;
my $pazarhtdocspath = $ENV{PAZARHTDOCSPATH};
my $pazar_html = $ENV{PAZAR_HTML};
print $cgi->header("text/html; charset=utf-8");
my $tfname = $cgi->param("tfname");

# A value containing both tfid and project id used in this page 
# to make form element names different for tfs with the same name 
# (but from different projects).
my $tf_projid = $cgi->param("tfpid");

# Need to make this file system and url friendly for passing to 
# dumptfprofile.pl
$tfname =~ s/\//_/g;
$tfname =~ s/\(/_/g;
$tfname =~ s/\)/_/g;

# Need to replace "-" with "_" for HTML form element names
my $tfname_form = $tfname;
$tfname_form =~ s/-/_/g;

my @seq = $cgi->param("seq");
my $allseq = join("\n",@seq);
my $fn = md5_hex($allseq) . ".fa";
open (SEQ,">/tmp/$fn");
my $i = 0;
foreach my $s (@seq) {
	$i++;
	if (length($s) < 8) {
		my $def = 8 - length($s);
		my $fl = "N" x $def;
		my $ns = $fl . $s . $fl;
		$s = $ns;
	}
	print SEQ qq{>pazarseqs\_$i\n$s\n};
}
close SEQ;
my $patterngen = TFBS::PatternGen::MEME->new(
                 -seq_file => "/tmp/$fn",
                 -binary => "meme",
                 -additional_params => "-revcomp -mod oops");
my $pfm = $patterngen->pattern();

if (!$pfm) {

	print qq{<div class="emp">MEME could not find a motif in the set of sequences you provided. It might be that the sequences are too short, or that there are too few of them. Please try to run the motif discovery again with a different selection of sequences.</div>};

} else {

	my $prettystring = $pfm->prettyprint();
	my $urlstring = $prettystring;
	$urlstring =~ s/(|\[|\])//g;
	$urlstring =~ s/\ /%20/g;
	$urlstring =~s/\n/br/g;

	my @matrixlines = split /\n/, $prettystring;
	$prettystring = join "\n", @matrixlines;
	$prettystring =~ s/ /\&nbsp\;/g;

	my $logo = $pazarhtdocspath . "/tmp/" . $fn . ".png";
	#warn "LOGO $logo";
	my $gd_image = $pfm->draw_logo(-file => $logo, -xsize => 360);

	print qq{
	<div class="">
		<form name="dlform$tfname">
			<table class="tblw" cellspacing="0" cellpadding="0">
				<tbody><tr>
					<td class="btc bg-wh">
						<div><img src="$pazar_html/tmp/$fn\.png"></div>
					</td><td class="btd tl bg-wh">
						<div class="p10to p10bo p5lo p5ro">
							<div class="b p5bo">Frequency matrix</div>
							<div class="p10lo p10bo"><div><textarea class="w100p he100 monospace">$prettystring</textarea></div></div>
							<div class="b p5to">Profile download</div>
							<div class="p10lo p10bo">
								Custom name (optional): <input type="text" name="userfilename$tfname_form\_$tf_projid"> <input type="button" value="Get" onclick="window.open('http://$ENV{HTTP_HOST}/cgi-bin/dumptfprofile.pl?tfname=$tfname&matrix=$urlstring&userfilename='+this.form.userfilename$tfname_form\_$tf_projid.value);">
							</div>
							<div class="small b">Note: these PFMs and logos are generated dynamically using the <a href="http://www.ncbi.nlm.nih.gov/pubmed/16845028" class="b">MEME&nbsp;pattern&nbsp;discovery&nbsp;algorithm</a>.</div>
						</div>
					</td>
				</tr>
			</tbody></table>
		</form>
	</div>};
}