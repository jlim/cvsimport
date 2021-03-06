#!/usr/bin/perl
use pazar;
use pazar::gene;
use pazar::talk;
use pazar::reg_seq;

my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};

require "$pazarcgipath/getsession.pl";
my $dbh = pazar->new(
	-host => $ENV{PAZAR_host},
	-user => $ENV{PAZAR_pubuser},
	-pass => $ENV{PAZAR_pubpass},
	-dbname => $ENV{PAZAR_name},
	-drv => $ENV{PAZAR_drv},
	-globalsearch => "yes");

my @pubprojects = $dbh->public_projects;

my %unsort_proj;
my $checkl_proj;

foreach my $project (@pubprojects) {
	my $proj_na = $dbh->get_project_name_by_ID($project);
	my $proj_lc = lc($proj_na);
	$unsort_proj{$proj_lc} = $proj_na;
}

foreach my $projname (sort(keys %unsort_proj)) {
	my $pn = $unsort_proj{$projname};
	my $pn_short = $pn;
	if (length($pn) > 14) {
		$pn_short = substr($pn, 0, 14) . qq{...};
	}
	$checkl_proj .= qq{<div class="float-l w20p ov-hide sml"><input type="checkbox" name="excl_proj" value="$pn"> $pn_short</div>};
}

my $shoe = 1;
my %stat = (
	"tfs" => "show",
	"genes" => "hide",
	"profiles" => "hide",
	"projects" => "hide"
);

if ($searchtab eq "tfs") {
	$shoe = 1;
	$stat{"tfs"} = "show";
	$stat{"genes"} = "hide";
	$stat{"sequences"} = "hide";
	$stat{"profiles"} = "hide";
	$stat{"projects"} = "hide";
} elsif ($searchtab eq "genes") {
	$shoe = 2;
	$stat{"tfs"} = "hide";
	$stat{"genes"} = "show";
	$stat{"sequences"} = "hide";
	$stat{"profiles"} = "hide";
	$stat{"projects"} = "hide";
} elsif ($searchtab eq "sequences") {
	$shoe = 3;
	$stat{"tfs"} = "hide";
	$stat{"genes"} = "hide";
	$stat{"sequences"} = "show";
	$stat{"profiles"} = "hide";
	$stat{"projects"} = "hide";
} elsif ($searchtab eq "profiles") {
	$shoe = 4;
	$stat{"tfs"} = "hide";
	$stat{"genes"} = "hide";
	$stat{"sequences"} = "hide";
	$stat{"profiles"} = "show";
	$stat{"projects"} = "hide";
} elsif ($searchtab eq "projects") {
	$shoe = 5;
	$stat{"tfs"} = "hide";
	$stat{"genes"} = "hide";
	$stat{"sequences"} = "hide";
	$stat{"profiles"} = "hide";
	$stat{"projects"} = "show";
} else {
	$shoe = 1;
	$stat{"tfs"} = "show";
	$stat{"genes"} = "hide";
	$stat{"sequences"} = "hide";
	$stat{"profiles"} = "hide";
	$stat{"projects"} = "hide";
}

$bowz = qq{
	<div class="p5to p10lo cc_smltxt">
		<img class="float-l" src="$pazar_html/images/search.png"/>
		<div class="p10to"><a href="$pazar_cgi/mallmap.pl" class="b">View interactive mall map</a></div>
		<div>(requires Adobe Flash player)</div>
		<div class="clear-l"></div>
	</div>};

$bowz .= qq{
	<div id="1_bowz" class="$stat{'tfs'}">
		<div class="cc_searchtab_box">
			<div class="float-r"><div class="cc_searchtab"><a href="$pazar_cgi/projects.pl" class="b">Browse projects</a></div></div>
			<div class="cc_searchtab_active"><div class="tabbyred" onclick="toggleRows('bowz','1','5');">Transcription factors (TFs)</div> <a href="$pazar_cgi/help_FAQ.pl#2" target="helpwin" onClick="window.open('about:blank','helpwin');"><img src="$pazar_html/images/help.gif" alt="Help" align="bottom" width="10"></a></div>
			<div class="cc_searchtab"><div class="tabbyblu" onclick="toggleRows('bowz','2','5');">Target genes</div> <a href="$pazar_cgi/help_FAQ.pl#3" target="helpwin" onClick="window.open('about:blank','helpwin');"><img src="$pazar_html/images/help.gif" alt="Help" align="bottom" width="10"></a></div>
			<div class="cc_searchtab"><div class="tabbyora" onclick="toggleRows('bowz','3','5');">Regulatory sequences <a href="$pazar_cgi/help_FAQ.pl#4" target="_blank"><img src="$pazar_html/images/help.gif" alt="Help" align="bottom" width="10"></a></div></div>
			<div class="cc_searchtab"><div class="tabbygry" onclick="toggleRows('bowz','4','5');">Pre-computed TF profiles</div> <a href="$pazar_cgi/help_FAQ.pl#5" target="helpwin" onClick="window.open('about:blank','helpwin');"><img src="$pazar_html/images/help.gif" alt="Help" align="bottom" width="10"></a></div>
		</div><div class="cc_searchbox">
			<div class="wowza">
				<form name="tf_search" method="post" action="$pazar_cgi/tf_search.cgi" enctype="multipart/form-data" target="">
					<input type="hidden" name="searchtab" value="tfs"/>
					<div class="float-r">
						<select name="ID_list">
							<option selected="selected" value="tf_name">user-defined TF name</option>
							<option value="EnsEMBL_gene">Ensembl gene ID</option>
							<option value="EnsEMBL_transcript">Ensembl transcript ID</option>
							<option value="EntrezGene">Entrez Gene ID</option>
							<option value="nm">Refseq ID</option>
							<option value="swissprot">Swissprot ID</option>
							<option value="PAZAR_TF">PAZAR TF ID</option>
						</select>
						<input value="Find" name="Submit" type="submit"> 
						<a href="$pazar_html/TFID_help.htm" target="helpwin" onClick="window.open('about:blank','helpwin', 'scrollbars=yes, menubar=no, toolbar=no directories=no, height=650, width=350');"><img src="$pazar_html/images/help.gif" alt='Help' align='bottom' width=12></a>
					</div>
					<input class="invibu txt-grey" value="Enter a TF to search" onFocus="if(this.value=='Enter a TF to search'){this.value=''; this.className='invibu';}" onBlur="if(this.value==''){this.value='Enter a TF to search'; this.className='invibu txt-grey';}" name="geneID" type="text">
					<div class="clear-r"></div>
				</form>
			</div>
			<div class="show" id="1_aso1">
				<div class=""><a href="$pazar_cgi/tf_list.cgi">Select a TF from our list of reported TFs</a> &bull; <a href="#" onclick="toggleRows('aso1','2','2');">View advanced search options</a></div>
			</div>
			<div class="hide" id="2_aso1">
				<div class=""><a href="$pazar_cgi/tf_list.cgi">Select a TF from our list of reported TFs</a> &bull; <a href="#" onclick="toggleRows('aso1','1','2');">Hide advanced search options</a></div>
				<div class="p5bo p5to">You may select which projects you would like to <span class="b">exclude</span> from your search:</div>
				<div class="">
					$checkl_proj
					<div class="clear-l"></div>
				</div>
			</div>
		</div>
	</div>};

$bowz .= qq{<div id="2_bowz" class="$stat{'genes'}">
		<div class="cc_searchtab_box">
			<div class="float-r"><div class="cc_searchtab"><a href="$pazar_cgi/projects.pl" class="b">Browse projects</a></div></div>
			<div class="cc_searchtab"><div class="tabbyred" onclick="toggleRows('bowz','1','5');">Transcription factors (TFs)</div> <a href="$pazar_cgi/help_FAQ.pl#2" target="helpwin" onClick="window.open('about:blank','helpwin');"><img src="$pazar_html/images/help.gif" alt="Help" align="bottom" width="10"></a></div>
			<div class="cc_searchtab_active"><div class="tabbyblu" onclick="toggleRows('bowz','2','5');">Target genes</div> <a href="$pazar_cgi/help_FAQ.pl#3" target="helpwin" onClick="window.open('about:blank','helpwin');"><img src="$pazar_html/images/help.gif" alt="Help" align="bottom" width="10"></a></div>
			<div class="cc_searchtab"><div class="tabbyora" onclick="toggleRows('bowz','3','5');">Regulatory sequences <a href="$pazar_cgi/help_FAQ.pl#4" target="_blank"><img src="$pazar_html/images/help.gif" alt="Help" align="bottom" width="10"></a></div></div>
			<div class="cc_searchtab"><div class="tabbygry" onclick="toggleRows('bowz','4','5');">Pre-computed TF profiles</div> <a href="$pazar_cgi/help_FAQ.pl#5" target="helpwin" onClick="window.open('about:blank','helpwin');"><img src="$pazar_html/images/help.gif" alt="Help" align="bottom" width="10"></a></div>
		</div><div class="cc_searchbox">
			<form name="gene_search" method="post" action="$pazar_cgi/gene_search.cgi" enctype="multipart/form-data" target="">
			<input type="hidden" name="searchtab" value="genes"/>
				<div class="wowza">
					<div class="float-r">
						<select name="ID_list">
							<option selected="selected" value="GeneName">user-defined gene name</option>
							<option value="EnsEMBL_gene">Ensembl gene ID</option>
							<option value="EnsEMBL_transcript">Ensembl transcript ID</option>
							<option value="EntrezGene">Entrez Gene ID</option>
							<option value="nm">Refseq ID</option>
							<option value="swissprot">Swissprot ID</option>
							<option value="PAZAR_gene">PAZAR gene ID</option>
						</select>
						<input value="Find" name="submit" type="submit"> 
						<a href="$pazar_html/ID_help.htm" target="helpwin" onClick="window.open('about:blank','helpwin', 'scrollbars=yes, menubar=no, toolbar=no directories=no, height=650, width=350');"><img src="$pazar_html/images/help.gif" alt='Help' align='bottom' width=12></a>
					</div>
					<input class="invibu txt-grey" value="Enter a gene to search" onFocus="if(this.value=='Enter a gene to search'){this.value=''; this.className='invibu';}" onBlur="if(this.value==''){this.value='Enter a gene to search'; this.className='invibu txt-grey';}" name="geneID" type="text"> 
					<div class="clear-r"></div>
				</div>
				<div class="show" id="1_aso2">
					<div class=""><a href="$pazar_cgi/gene_list.cgi">Select a gene from our list of annotated genes</a> &bull; <a href="#" onclick="toggleRows('aso2','2','2');">Show advanced search options</a></div>
				</div>
				<div class="hide" id="2_aso2">
					<div class=""><a href="$pazar_cgi/gene_list.cgi">Select a gene from our list of annotated genes</a> &bull; <a href="#" onclick="toggleRows('aso2','1','2');">Hide advanced search options</a></div>
					<div class="p5bo p5to">You may select which projects you would like to <span class="b">exclude</span> from your search:</div>
					<div>
						$checkl_proj
						<div class="clear-l"></div>
					</div>
				</div>
			</form>
		</div>
	</div>};

$bowz .= qq{<div id="3_bowz" class="$stat{'sequences'}">
		<div class="cc_searchtab_box">
			<div class="float-r"><div class="cc_searchtab"><a href="$pazar_cgi/projects.pl" class="b">Browse projects</a></div></div>
			<div class="cc_searchtab"><div class="tabbyred" onclick="toggleRows('bowz','1','5');">Transcription factors (TFs)</div> <a href="$pazar_cgi/help_FAQ.pl#2" target="helpwin" onClick="window.open('about:blank','helpwin');"><img src="$pazar_html/images/help.gif" alt="Help" align="bottom" width="10"></a></div>
			<div class="cc_searchtab"><div class="tabbyblu" onclick="toggleRows('bowz','2','5');">Target genes</div> <a href="$pazar_cgi/help_FAQ.pl#3" target="helpwin" onClick="window.open('about:blank','helpwin');"><img src="$pazar_html/images/help.gif" alt="Help" align="bottom" width="10"></a></div>
			<div class="cc_searchtab_active"><div class="tabbyora" onclick="toggleRows('bowz','3','5');">Regulatory sequences <a href="$pazar_cgi/help_FAQ.pl#4" target="_blank"><img src="$pazar_html/images/help.gif" alt="Help" align="bottom" width="10"></a></div></div>
			<div class="cc_searchtab"><div class="tabbygry" onclick="toggleRows('bowz','4','5');">Pre-computed TF profiles</div> <a href="$pazar_cgi/help_FAQ.pl#5" target="helpwin" onClick="window.open('about:blank','helpwin');"><img src="$pazar_html/images/help.gif" alt="Help" align="bottom" width="10"></a></div>
		</div><div class="cc_searchbox">
			<form name="gene_search" method="post" action="$pazar_cgi/seq_search.cgi" enctype="multipart/form-data" target="">
			<input type="hidden" name="searchtab" value="genes"/>
				<div class="wowza">
					<div class="float-r">
						<select name="qtype">
							<option selected="selected" value="actual_seq">Sequence fragment</option>
							<option value="PAZAR_seq">PAZAR sequence ID</option>
						</select>
						<input value="Find" name="submit" type="submit">
					</div>
					<input class="invibu txt-grey" value="Enter a sequence to search" onFocus="if(this.value=='Enter a sequence to search'){this.value=''; this.className='invibu';}" onBlur="if(this.value==''){this.value='Enter a sequence to search'; this.className='invibu txt-grey';}" name="query" type="text"> 
					<div class="clear-r"></div>
				</div>
			</form>
		</div>
	</div>};

$bowz .= qq{<div id="4_bowz" class="$stat{'profiles'}">
		<div class="cc_searchtab_box">
			<div class="float-r"><div class="cc_searchtab"><a href="$pazar_cgi/projects.pl" class="b">Browse projects</a></div></div>
			<div class="cc_searchtab"><div class="tabbyred" onclick="toggleRows('bowz','1','5');">Transcription factors (TFs)</div> <a href="$pazar_cgi/help_FAQ.pl#2" target="helpwin" onClick="window.open('about:blank','helpwin');"><img src="$pazar_html/images/help.gif" alt="Help" align="bottom" width="10"></a></div>
			<div class="cc_searchtab"><div class="tabbyblu" onclick="toggleRows('bowz','2','5');">Target genes</div> <a href="$pazar_cgi/help_FAQ.pl#3" target="helpwin" onClick="window.open('about:blank','helpwin');"><img src="$pazar_html/images/help.gif" alt="Help" align="bottom" width="10"></a></div>
			<div class="cc_searchtab"><div class="tabbyora" onclick="toggleRows('bowz','3','5');">Regulatory sequences <a href="$pazar_cgi/help_FAQ.pl#4" target="_blank"><img src="$pazar_html/images/help.gif" alt="Help" align="bottom" width="10"></a></div></div>
			<div class="cc_searchtab_active"><div class="tabbygry" onclick="toggleRows('bowz','4','5');">Pre-computed TF profiles</div> <a href="$pazar_cgi/help_FAQ.pl#5" target="helpwin" onClick="window.open('about:blank','helpwin');"><img src="$pazar_html/images/help.gif" alt="Help" align="bottom" width="10"></a></div>
		</div><div class="cc_searchbox">
			<div class="p5bo"><span class="b">This page allows you to access pre-computed profiles stored in the PAZAR boutiques.</span> They might not be linked to the sequences used to build them and they may not even be linked to an identifiable transcription factor. For instance, they might have been built from multiple species and (or) multiple factors presenting similar binding properties. If you want to build a profile from a specific transcription factor with all of its annotated binding sites, please go to the <a href="$pazar_cgi/tf_search.cgi">Transcription factors (TFs)</a> search page where the profiles are generated dynamically.</div>
			<div class="">
				<form method="post" action="$pazar_cgi/export_profile.cgi" enctype="multipart/form-data" target="_self">
				<input type="hidden" name="searchtab" value="profiles"/>
				Show pre-computed profiles sorted by: <input type="hidden" name="mode" value="list"> <input type="submit" name="BROWSE" value="Project"> <input type="submit" name="BROWSE" value="Name"> <input type="submit" name="BROWSE" value="Species"></form>
			</div>
		</div>
	</div>};

$bowz .= qq{<div id="5_bowz" class="$stat{'projects'}">
		<div class="cc_searchtab_box">
			<div class="float-r"><div class="cc_searchtab_active">Browse projects</div></div>
			<div class="cc_searchtab"><div class="tabbyred" onclick="toggleRows('bowz','1','5');">Transcription factors (TFs)</div> <a href="$pazar_cgi/help_FAQ.pl#2" target="helpwin" onClick="window.open('about:blank','helpwin');"><img src="$pazar_html/images/help.gif" alt="Help" align="bottom" width="10"></a></div>
			<div class="cc_searchtab"><div class="tabbyblu" onclick="toggleRows('bowz','2','5');">Target genes</div> <a href="$pazar_cgi/help_FAQ.pl#3" target="helpwin" onClick="window.open('about:blank','helpwin');"><img src="$pazar_html/images/help.gif" alt="Help" align="bottom" width="10"></a></div>
			<div class="cc_searchtab"><div class="tabbyora" onclick="toggleRows('bowz','3','5');">Regulatory sequences <a href="$pazar_cgi/help_FAQ.pl#4" target="_blank"><img src="$pazar_html/images/help.gif" alt="Help" align="bottom" width="10"></a></div></div>
			<div class="cc_searchtab"><div class="tabbygry" onclick="toggleRows('bowz','4','5');">Pre-computed TF profiles</div> <a href="$pazar_cgi/help_FAQ.pl#5" target="helpwin" onClick="window.open('about:blank','helpwin');"><img src="$pazar_html/images/help.gif" alt="Help" align="bottom" width="10"></a></div>
		</div><div class="cc_searchbox"><span class="b">Here you can review all public projects (&quot;boutiques&quot;) in the PAZAR database.</span> Clicking on one of the project will take you to a data access form that you can use to retrieve TFs, genes, profiles, and binding sequence information from that project. This page lists only non-private projects.</div>
	</div>};

$bowz = qq{<div class="p10to"><div class="">$bowz</div></div>};

1
