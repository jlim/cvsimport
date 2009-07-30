#!/usr/bin/perl

use HTML::Template;
my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};

my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");
my $temptail = HTML::Template->new(filename => "$pazarcgipath/tail.tmpl");
$template->param(TITLE => "Links | PAZAR");
$template->param(PAZAR_HTML => $pazar_html);
$template->param(PAZAR_CGI => $pazar_cgi);

require "$pazarcgipath/getsession.pl";
if ($loggedin eq "true") {
	$template->param(LOGOUT => qq{<span class="b">You are signed in as $info{first} $info{last}.</span> <a href="$pazar_cgi/logout.pl" class="b">Sign out</a>});
} else {
	$template->param(LOGOUT => qq{<a href="$pazar_cgi/login.pl"><span class="b">Sign in</span></a>});
}

print "Content-Type: text/html\n\n", $template->output;
print qq{
	<div class="docp">
		<div class="float-r b txt-grey">PAZAR Documentation</div>
		<div class="clear-r"></div>
	</div>
<h1>Links</h1>
<h2>Content</h2>
<div class="p20lo">
	<div class="b">
		<a href="#1. Useful Software">Useful software
		</a>
	</div>
	<div class="b p10lo">
		<a href="#1.1 Introduction">Introduction
		</a>
	</div>
	<div class="b p10lo">
		<a href="#1.2 Software Classes">Software classes
		</a>
	</div>
	<div class="b p10lo">
		<a href="#1.3 Software List">Software list
		</a>
	</div>
	<div class="b p10bo">
		<a href="#2. Regulatory Datasets">Regulatory datasets
		</a>
	</div>
</div>
<h2>
	<a name="1. Useful Software">
	</a>Useful software
</h2>
<div class="p20lo p20bo">
	<h3>
		<a name="1.1 Introduction">
		</a>Introduction
	</h3>
	<p>The data found within PAZAR can be used in association with a large array of online resources. We do not directly provide such tools within PAZAR. We believe the data should be accessed by sequence analysis tools through the PAZAR software interface. For now, one must still copy data from PAZAR and paste it into the web services you choose to use. The following list of resources is not comprehensive. If you have encountered a program that you think is noteworthy, please let us know.
	</p>
	<h3>
		<a name="1.2 Software Classes">
		</a>Software Classes
	</h3>
	<table class="sibo w100p">
		<tbody>
			<tr>
				<td class="tl psp b bg-bl w20p">Class</td>
				<td class="tl psp b bg-bl w80p">Description</td>
			</tr>
			<tr class="bg-vlg">
				<td class="tl psp b">"TFBS Discrimination"</td>
				<td class="tl psp">Given a count matrix summarizing the binding sites for a TF, predict TFBS in a sequence of your choice.</td>
			</tr>
			<tr>
				<td class="tl psp b">"Pattern Discovery"</td>
				<td class="tl psp">Given a set of regulatory sequences, you wish to find new patterns that might be a novel type of TFBS.</td>
			</tr>
			<tr class="bg-vlg">
				<td class="tl psp b">"TFBS Over-representation"</td>
				<td class="tl psp">Given a set of genes and a count matrix, you wish to determine if the pattern defined by the count matrix is significantly enriched compared to background. Unfortunately there is no TFBS over-representation tool that allows for user-submitted binding profiles. Tools like oPOSSUM must analyze enormous numbers of genes to perform the analysis and therefore do not offer submission (yet).</td>
			</tr>
			<tr>
				<td class="tl psp b">"TFBS Model Comparison"</td>
				<td class="tl psp">You have recovered a new TFBS pattern (count matrix) and wish to see if the pattern resembles other known TFBS profiles. Once you find a pattern, it is natural to want to compare it against a database of patterns to see if it matches a characterized type of TFBS.</td>
			</tr>
			<tr class="bg-vlg">
				<td class="tl psp b">"TFBS Combination Detection"</td>
				<td class="tl psp">You have a set of TFBS count matrices (1 or more), and wish to find segments in a DNA sequence significantly enriched for combinations of matches to the pattern(s).</td>
			</tr>
			<tr>
				<td class="tl psp b">"TF Information"</td>
				<td class="tl psp">Sometimes you need to look up information about a gene or protein. Everyone knows about Enrez Gene and UniProt. You might also try <a href="http://www.transcriptionfactors.org/" target="_blank">http://www.transcriptionfactors.org/</a>.</td>
			</tr>
		</tbody>
	</table>

	<h3>
		<a name="1.3 Software List">
		</a>Software list
	</h3>
	<table class="sibo w100p">
		<tbody>
			<tr>
				<td class="tl psp b w20p bg-bl">Name</td>
				<td class="tl psp b w30p bg-bl">Classes</td>
				<td class="tl psp b w50p bg-bl">URL</td>
			</tr>
			<tr class="bg-vlg">
				<td class="tl psp b">AHAB</td>
				<td class="tl psp">TFBS Combination Detection</td>
				<td class="tl psp"><a href="http://gaspard.bio.nyu.edu/Ahab.html">http://gaspard.bio.nyu.edu/Ahab.html</a></td>
			</tr>
			<tr>
				<td class="tl psp b">Cluster Buster</td>
				<td class="tl psp">TFBS Combination Detection</td>
				<td class="tl psp"><a href="http://zlab.bu.edu/cluster-buster/cbust.html">http://zlab.bu.edu/cluster-buster/cbust.html</a></td>
			</tr>
			<tr class="bg-vlg">
				<td class="tl psp b">ConSite</td>
				<td class="tl psp">TFBS Discrimination</td>
				<td class="tl psp"><a href="http://asp.ii.uib.no:8090/cgi-bin/CONSITE/consite/">http://asp.ii.uib.no:8090/cgi-bin/CONSITE/consite/</a></td>
			</tr>
			<tr>
				<td class="tl psp b">CRE works</td>
				<td class="tl psp">TFBS Discrimination
					<br>TFBS Combination Detection</td>
				<td class="tl psp"><a href="http://genereg.ornl.gov/scancre/">http://genereg.ornl.gov/scancre/</a></td>
			</tr>
			<tr class="bg-vlg">
				<td class="tl psp b">FOOTER</td>
				<td class="tl psp">TFBS Discrimination</td>
				<td class="tl psp"><a href="http://biodev.hgen.pitt.edu/footer_php/Footerv2_0.php">http://biodev.hgen.pitt.edu/footer_php/Footerv2_0.php</a></td>
			</tr>
			<tr>
				<td class="tl psp b">JASPAR</td>
				<td class="tl psp">TFBS Model Comparison</td>
				<td class="tl psp"><a href="http://jaspar.genereg.net/">http://jaspar.genereg.net/</a></td>
			</tr>
			<tr class="bg-vlg">
				<td class="tl psp b">MAST</td>
				<td class="tl psp">TFBS Discrimination
					<br>TFBS Combination Detection</td>
				<td class="tl psp"><a href="http://meme.sdsc.edu/meme/mast.html">http://meme.sdsc.edu/meme/mast.html</a></td>
			</tr>
			<tr>
				<td class="tl psp b">MSCAN</td>
				<td class="tl psp">TFBS Combination Detection</td>
				<td class="tl psp"></td>
			</tr>
			<tr class="bg-vlg">
				<td class="tl psp b">RSA TOOLS</td>
				<td class="tl psp">TFBS Discrimination
					<br>Pattern Discovery</td>
				<td class="tl psp"><a href="http://rsat.ulb.ac.be/rsat/">http://rsat.ulb.ac.be/rsat/</a></td>
			</tr>
			<tr>
				<td class="tl psp b">STAMP</td>
				<td class="tl psp">TFBS Model Comparison</td>
				<td class="tl psp"><a href="http://www.benoslab.pitt.edu/stamp/">http://www.benoslab.pitt.edu/stamp/</a></td>
			</tr>
			<tr class="bg-vlg">
				<td class="tl psp b">TOUCAN</td>
				<td class="tl psp">TFBS Discrimination
					<br>Pattern Discovery
					<br>TFBS Combination Detection</td>
				<td class="tl psp"><a href="http://homes.esat.kuleuven.be/~saerts/software/toucan.php">http://homes.esat.kuleuven.be/~saerts/software/toucan.php</a></td>
			</tr>
			<tr>
				<td class="tl psp b">WebMotifs</td>
				<td class="tl psp">Pattern Discovery</td>
				<td class="tl psp"><a href="http://fraenkel.mit.edu/webmotifs/">http://fraenkel.mit.edu/webmotifs/</a></td>
			</tr>
		</tbody>
	</table>
</div>
<h2><a name="2. Regulatory Datasets"></a>Regulatory Datasets</h2>
<div class="p20lo">
<table class="sibo w100p">
	<tbody>
		<tr>
			<td class="tl psp b w20p bg-bl">Name</td>
			<td class="tl psp b w80p bg-bl">Description and URL</td>
		</tr>
		<tr class="bg-vlg">
			<td class="tl psp b">ABS</td>
			<td class="tl psp">A database of annotated regulatory binding sites from orthologous promoters. <a href="http://genome.imim.es/datasets/abs2005/downloads.html">http://genome.imim.es/datasets/abs2005/downloads.html</a></td>
		</tr>
		<tr>
			<td class="tl psp b">AGRIS AtcisDB and AtTFDB</td>
			<td class="tl psp">An <span class="i">Arabidopsis thaliana</span> cis-regulatory and transcription factor database. <a href="http://arabidopsis.med.ohio-state.edu/">http://arabidopsis.med.ohio-state.edu/</a></td>
		</tr>
		<tr class="bg-vlg">
			<td class="tl psp b">AtProbe</td>
			<td class="tl psp">An <span class="i">Arabidopsis thaliana</span> promoter binding element database. <a href="http://rulai.cshl.edu/cgi-bin/atprobe/atprobe.pl">http://rulai.cshl.edu/cgi-bin/atprobe/atprobe.pl</a></td>
		</tr>
		<tr>
			<td class="tl psp b">AthaMap</td>
			<td class="tl psp">A genome-wide map of potential transcription factor binding sites in <i>Arabidopsis thaliana</i>. <a href="http://www.athamap.de/">http://www.athamap.de/</a></td>
		</tr>
		<tr class="bg-vlg">
			<td class="tl psp b">BOND</td>
			<td class="tl psp">The biomolecular object network databank (BOND) is a resource to perform cross-database searches of available sequence, interaction, complex and pathway information. <a href="http://bond.unleashedinformatics.com/Action?">http://bond.unleashedinformatics.com/Action?</a></td>
		</tr>
		<tr>
			<td class="tl psp b">CEPDB</td>
			<td class="tl psp">A <span class="i">Caenorhabditis elegans</span> promoter database. <a href="http://rulai.cshl.edu/cgi-bin/CEPDB/home.cgi">http://rulai.cshl.edu/cgi-bin/CEPDB/home.cgi</a></td>
		</tr>
		<tr class="bg-vlg">
			<td class="tl psp b">Cisreg.ca</td>
			<td class="tl psp">Our laboratory website that features a muscle and liver data set. <a href="http://www.cisreg.ca/tjkwon/">http://www.cisreg.ca/tjkwon/</a></td>
		</tr>
		<tr>
			<td class="tl psp b">Compel</td>
			<td class="tl psp">Composite regulatory elements&mdash;structure, function and classification. <a href="http://compel.bionet.nsc.ru/new/compel/compel.html">http://compel.bionet.nsc.ru/new/compel/compel.html</a></td>
		</tr>
		<tr class="bg-vlg">
			<td class="tl psp">DATF</td>
			<td class="tl psp">The Database of <span class="i">Arabidopsis thaliana</span> transcription factors (DATF). <a href="http://datf.cbi.pku.edu.cn/">http://datf.cbi.pku.edu.cn/</a></td>
		</tr>
		<tr>
			<td class="tl psp b">DBTSS</td>
			<td class="tl psp">A database of transcriptional start sites (TSS). <a href="http://dbtss.hgc.jp/">http://dbtss.hgc.jp/</a></td>
		</tr>
		<tr class="bg-vlg">
			<td class="tl psp b">DoOP</td>
			<td class="tl psp">An orthologous-clusters-of-promoters database. <a href="http://doop.abc.hu/">http://doop.abc.hu/</a></td>
		</tr>
		<tr>
			<td class="tl psp b">DBSD</td>
			<td class="tl psp">A drosophila binding site database. Please note that this website is not yet functional but will be soon. <a href="http://rulai.cshl.org/dbsd/index.html">http://rulai.cshl.org/dbsd/index.html</a></td>
		</tr>
		<tr class="bg-vlg">
			<td class="tl psp b">Drosophila DNase I Footprint Database</td>
			<td class="tl psp">A webpage providing access to results of the systematic curation and genome annotation of 1,365 DNase I footprints for the fruitfly <em>Drosophila melanogaster</em>. <a href="http://www.flyreg.org/">http://www.flyreg.org/</a></td>
		</tr>
		<tr>
			<td class="tl psp b">DRTF</td>
			<td class="tl psp">A database of rice transcription factors. <a href="http://drtf.cbi.pku.edu.cn/">http://drtf.cbi.pku.edu.cn/</a></td>
		</tr>
		<tr class="bg-vlg">
			<td class="tl psp b">ECRBase</td>
			<td class="tl psp">A database of evolutionary conserved regions (ECRs), promoters, and
				transcription factor binding sites in vertebrate genomes created using ECR browser alignments. <a href="http://ecrbase.dcode.org/">http://ecrbase.dcode.org/</a></td>
		</tr>
		<tr>
			<td class="tl psp b">EDGEdb</td>
			<td class="tl psp">PDI, PPI and gene expression data generated by the Walhout laboratory and others are made available to the community through EDGEdb (elegans differential gene expression data). <a href="http://edgedb.umassmed.edu/IndexAction.do">http://edgedb.umassmed.edu/IndexAction.do</a></td>
		</tr>
		<tr class="bg-vlg">
			<td class="tl psp b">EPD</td>
			<td class="tl psp">A eukaryotic promoter database. <a href="http://www.epd.isb-sib.ch/">http://www.epd.isb-sib.ch/</a></td>
		</tr>
		<tr>
			<td class="tl psp b">ERTargetDB</td>
			<td class="tl psp">ERTargetDB integrates information from ongoing chip-on-chip experiments and promoter sequence conservation from the OMGProm database. <a href="http://bioinformatics.med.ohio-state.edu/ERTargetDB/">http://bioinformatics.med.ohio-state.edu/ERTargetDB/</a></td>
		</tr>
		<tr class="bg-vlg">
			<td class="tl psp b">Globin Gene Server</td>
			<td class="tl psp">A database for experimental data on the regulation of the globin gene cluster. <a href="http://globin.cse.psu.edu/">http://globin.cse.psu.edu/</a></td>
		</tr>
		<tr>
			<td class="tl psp b">Harbison Lab</td>
			<td class="tl psp">Datasets useful in comparative genomics and in erythroid gene regulation. <a href="http://www.bx.psu.edu/%7Eross/dataset/DatasetHome.html">http://www.bx.psu.edu/~ross/dataset/DatasetHome.html</a></td>
		</tr>
		<tr class="bg-vlg">
			<td class="tl psp b">HemoPDB</td>
			<td class="tl psp">A hematopoiesis promoter database. <a href="http://bioinformatics.med.ohio-state.edu/HemoPDB/">http://bioinformatics.med.ohio-state.edu/HemoPDB/</a></td>
		</tr>
		<tr>
			<td class="tl psp b">JASPAR</td>
			<td class="tl psp">A high-quality transcription factor binding profile database. <a href="http://jaspar.cgb.ki.se/cgi-bin/jaspar_db.pl">http://jaspar.cgb.ki.se/cgi-bin/jaspar_db.pl</a></td>
		</tr>
		<tr class="bg-vlg">
			<td class="tl psp b">LSPD</td>
			<td class="tl psp">The liver specific gene promoter database. <a href="http://rulai.cshl.edu/LSPD/">http://rulai.cshl.edu/LSPD/</a></td>
		</tr>
		<tr>
			<td class="tl psp b">MPD</td>
			<td class="tl psp">A mammalian promoter database for human, mouse and rat. <a href="http://rulai.cshl.edu/CSHLmpd2">http://rulai.cshl.edu/CSHLmpd2</a></td>
		</tr>
		<tr class="bg-vlg">
			<td class="tl psp b">MPromDb</td>
			<td class="tl psp">A mammalian promoter database with experimentally supported annotations. 
			<br><a href="http://bioinformatics.med.ohio-state.edu/MPromDb/">http://bioinformatics.med.ohio-state.edu/MPromDb/</a></td>
		</tr>
		<tr>
			<td class="tl psp b">MTIR</td>
			<td class="tl psp">A database for muscle-specific regulation of transcription. <a href="http://www.cbil.upenn.edu/MTIR/HomePage.html">http://www.cbil.upenn.edu/MTIR/HomePage.html</a></td>
		</tr>
		<tr class="bg-vlg">
			<td class="tl psp b">OMGProm</td>
			<td class="tl psp">A database for orthologous mammalian gene promoters. <a href="http://bioinformatics.med.ohio-state.edu/OMGProm/">http://bioinformatics.med.ohio-state.edu/OMGProm/</a></td>
		</tr>
		<tr>
			<td class="tl psp b">ooTFD</td>
			<td class="tl psp">An object-oriented transcription factors database. <a href="http://www.ifti.org/ootfd/">ttp://www.ifti.org/ootfd/</a></td>
		</tr>
		<tr class="bg-vlg">
			<td class="tl psp b">OPD</td>
			<td class="tl psp">An osteo-promoter database&mdash;promoters of genes in the osteogenic pathway. <a href="http://www.opd.tau.ac.il/">http://www.opd.tau.ac.il/</a></td>
		</tr>
		<tr>
			<td class="tl psp b">Oreganno</td>
			<td class="tl psp">Open regulatory annotation database. <a href="http://oreganno.org/" mce_href="http://oreganno.org" rel="nofollow" linktype="raw" linktext="http://oreganno.org">http://oreganno.org</a></td>
		</tr>
		<tr class="bg-vlg">
			<td class="tl psp b">PLACE</td>
			<td class="tl psp">A database of plant cis-acting regulatory DNA elements. <a href="http://www.dna.affrc.go.jp/PLACE/">http://www.dna.affrc.go.jp/PLACE/</a></td>
		</tr>
		<tr>
			<td class="tl psp b">Plant CARE</td>
			<td class="tl psp">A cis-acting regulatory element database for plants. <a href="http://intra.psb.ugent.be:8080/PlantCARE/">http://intra.psb.ugent.be:8080/PlantCARE/</a>
			</td>
		</tr>
		<tr class="bg-vlg">
			<td class="tl psp b">Plant Prom DB</td>
			<td class="tl psp">A database of plant promoter sequences. <a href="http://mendel.cs.rhul.ac.uk/mendel.php?topic=plantprom">http://mendel.cs.rhul.ac.uk/mendel.php?topic=plantprom</a></td>
		</tr>
		<tr>
			<td class="tl psp b">RARTF</td>
			<td class="tl psp">The RIKEN arabidopsis transcription factor database. <a href="http://rarge.gsc.riken.jp/rartf/">http://rarge.gsc.riken.jp/rartf/</a></td>
		</tr>
		<tr class="bg-vlg">
			<td class="tl psp b">REDfly</td>
			<td class="tl psp">Regulatory element database for drosophila. <a href="http://redfly.ccr.buffalo.edu/?content=/search.php">http://redfly.ccr.buffalo.edu/?content=/search.php</a></td>
		</tr>
		<tr>
			<td class="tl psp b">RiceTFDB</td>
			<td class="tl psp">Rice genes involved in transcriptional control. <a href="http://ricetfdb.bio.uni-potsdam.de/v2.1/">http://ricetfdb.bio.uni-potsdam.de/v2.1/</a></td>
		</tr>
		<tr class="bg-vlg">
			<td class="tl psp b"> RIKEN TFdb</td>
			<td class="tl psp">A mouse transcription factor database. <a href="http://genome.gsc.riken.jp/TFdb/">http://genome.gsc.riken.jp/TFdb/</a></td>
		</tr>
		<tr>
			<td class="tl psp b">rSNP</td>
			<td class="tl psp">Influence of single nucleotide mutations in regulatory gene regions. <a href="http://wwwmgs.bionet.nsc.ru/mgs/systems/rsnp/">http://wwwmgs.bionet.nsc.ru/mgs/systems/rsnp/</a></td>
		</tr>
		<tr class="bg-vlg">
			<td class="tl psp b">SCPD</td>
			<td class="tl psp">A Saccharomyces cerevisiae promoter database. <a href="http://rulai.cshl.edu/SCPD/">http://rulai.cshl.edu/SCPD/</a></td>
		</tr>
		<tr>
			<td class="tl psp b">Stanford Encode Project</td>
			<td class="tl psp">An encyclopedia of DNA elements. <a href="http://www-shgc.stanford.edu/genetics/encode.html">http://www-shgc.stanford.edu/genetics/encode.html</a></td>
		</tr>
		<tr class="bg-vlg">
			<td class="tl psp b">Transcription Factors DD</td>
			<td class="tl psp">A database for transcription factors of humans and other organisms. <a href="http://www.proteinlounge.com/trans_home.asp">http://www.proteinlounge.com/trans_home.asp</a></td>
		</tr>
		<tr>
			<td class="tl psp b">TRANSFAC</td>
			<td class="tl psp">A database for eukaryotic transcription factors and their binding profiles. <a href="http://www.gene-regulation.de/">http://www.gene-regulation.de/</a></td>
		</tr>
		<tr class="bg-vlg">
			<td class="tl psp b">TRED</td>
			<td class="tl psp">The transcriptional regulatory element database. <a href="http://rulai.cshl.edu/cgi-bin/TRED/tred.cgi?process=home">http://rulai.cshl.edu/cgi-bin/TRED/tred.cgi?process=home</a></td>
		</tr>
		<tr>
			<td class="tl psp b">TRRD</td>
			<td class="tl psp">A database for transcription regulatory regions. <a href="http://wwwmgs.bionet.nsc.ru/mgs/gnw/trrd/">http://wwwmgs.bionet.nsc.ru/mgs/gnw/trrd/</a></td>
		</tr>
		<tr class="bg-vlg">
			<td class="tl psp b">VISTA Enhancer Browser</td>
			<td class="tl psp">A database of tissue-specific human enhancers. <a href="http://enhancer.lbl.gov/">http://enhancer.lbl.gov</a></td>
		</tr>
	</tbody>
</table>
</div>};

my $oldtext = qq{<div class="docp"><div class="float-r b txt-grey">PAZAR Documentation</div><div class="clear-r"></div></div><h1>Links</h1><h2>Content</h2><div class="p20lo"><div class="b"><a href="#1. Useful Software">Useful software</a></div><div class="b p10lo"><a href="#1.1 Introduction">Introduction</a></div><div class="b p10lo"><a href="#1.2 Software Classes">Software classes</a></div><div class="b p10lo"><a href="#1.3 Software List">Software list</a></div><div class="b p10bo"><a href="#2. Regulatory Datasets">Regulatory datasets</a></div></div><h2><a name="1. Useful Software"></a>Useful software</h2><div class="p20lo p20bo"><h3><a name="1.1 Introduction"></a>Introduction</h3><p>The data found within PAZAR can be used in association with a large array of online resources. We do not directly provide such tools within PAZAR. We believe the data should be accessed by sequence analysis tools through the PAZAR software interface. For now, one must still copy data from PAZAR and paste it into the web services you choose to use. The following list of resources is not comprehensive. If you have encountered a program that you think is noteworthy, please let us know.</p><h3><a name="1.2 Software Classes"></a>Software Classes</h3><table class="sibo w100p"><tbody><tr><td class="tl psp b bg-ye w20p">Class</td><td class="tl psp b bg-ye w80p">Description</td></tr><tr class="bg-vlg"><td class="tl psp b">"TFBS Discrimination"</td><td class="tl psp">Given a count matrix summarizing the binding sites for a TF, predict TFBS in a sequence of your choice.</td></tr><tr><td class="tl psp b">"Pattern Discovery"</td><td class="tl psp">Given a set of regulatory sequences, you wish to find new patterns that might be a novel type of TFBS.</td></tr><tr class="bg-vlg"><td class="tl psp b">"TFBS Over-representation"</td><td class="tl psp">Given a set of genes and a count matrix, you wish to determine if the pattern defined by the count matrix is significantly enriched compared to background. Unfortunately there is no TFBS over-representation tool that allows for user-submitted binding profiles. Tools like oPOSSUM must analyze enormous numbers of genes to perform the analysis and therefore do not offer submission (yet).</td></tr><tr><td class="tl psp b">"TFBS Model Comparison"</td><td class="tl psp">You have recovered a new TFBS pattern (count matrix) and wish to see if the pattern resembles other known TFBS profiles. Once you find a pattern, it is natural to want to compare it against a database of patterns to see if it matches a characterized type of TFBS.</td></tr><tr class="bg-vlg"><td class="tl psp b">"TFBS Combination Detection"</td><td class="tl psp">You have a set of TFBS count matrices (1 or more), and wish to find segments in a DNA sequence significantly enriched for combinations of matches to the pattern(s).</td></tr><tr><td class="tl psp b">"TF Information"</td><td class="tl psp">Sometimes you need to look up information about a gene or protein. Everyone knows about Enrez Gene and UniProt. You might also try <a href="http://www.transcriptionfactors.org/" target="_blank">http://www.transcriptionfactors.org/</a></td></tr></tbody></table><h3><a name="1.3 Software List"></a>Software list</h3><table class="sibo w100p"><tbody><tr><td class="tl psp b w20p bg-ye">Name</td><td class="tl psp b w30p bg-ye">Classes</td><td class="tl psp b w50p bg-ye">URL</td></tr><tr class="bg-vlg"><td class="tl psp b">AHAB</td><td class="tl psp">TFBS Combination Detection</td><td class="tl psp"><a href="http://gaspard.bio.nyu.edu/Ahab.html">http://gaspard.bio.nyu.edu/Ahab.html</a></td></tr><tr><td class="tl psp b">Cluster Buster</td><td class="tl psp">TFBS Combination Detection</td><td class="tl psp"><a href="http://zlab.bu.edu/cluster-buster/cbust.html">http://zlab.bu.edu/cluster-buster/cbust.html</a></td></tr><tr class="bg-vlg"><td class="tl psp b">ConSite</td><td class="tl psp">TFBS Discrimination</td><td class="tl psp"><a href="http://asp.ii.uib.no:8090/cgi-bin/CONSITE/consite/">http://asp.ii.uib.no:8090/cgi-bin/CONSITE/consite/</a></td></tr><tr><td class="tl psp b">CRE works</td><td class="tl psp">TFBS Discrimination<br>TFBS Combination Detection</td><td class="tl psp"><a href="http://genereg.ornl.gov/scancre/">http://genereg.ornl.gov/scancre/</a></td></tr><tr class="bg-vlg"><td class="tl psp b">FOOTER</td><td class="tl psp">TFBS Discrimination</td><td class="tl psp"><a href="http://biodev.hgen.pitt.edu/footer_php/Footerv2_0.php">http://biodev.hgen.pitt.edu/footer_php/Footerv2_0.php</a></td></tr><tr><td class="tl psp b">JASPAR</td><td class="tl psp">TFBS Model Comparison</td><td class="tl psp"><a href="http://jaspar.genereg.net/">http://jaspar.genereg.net/</a></td></tr><tr class="bg-vlg"><td class="tl psp b">MAST</td><td class="tl psp">TFBS Discrimination<br>TFBS Combination Detection</td><td class="tl psp"><a href="http://meme.sdsc.edu/meme/mast.html">http://meme.sdsc.edu/meme/mast.html</a></td></tr><tr><td class="tl psp b">MSCAN</td><td class="tl psp">TFBS Combination Detection</td><td class="tl psp"></td></tr><tr class="bg-vlg"><td class="tl psp b">RSA TOOLS</td><td class="tl psp">TFBS Discrimination<br>Pattern Discovery</td><td class="tl psp"><a href="http://rsat.ulb.ac.be/rsat/">http://rsat.ulb.ac.be/rsat/</a></td></tr><tr><td class="tl psp b">STAMP</td><td class="tl psp">TFBS Model Comparison</td><td class="tl psp"><a href="http://www.benoslab.pitt.edu/stamp/">http://www.benoslab.pitt.edu/stamp/</a></td></tr><tr class="bg-vlg"><td class="tl psp b">TOUCAN</td><td class="tl psp">TFBS Discrimination<br>Pattern Discovery<br>TFBS Combination Detection</td><td class="tl psp"><a href="http://homes.esat.kuleuven.be/~saerts/software/toucan.php">http://homes.esat.kuleuven.be/~saerts/software/toucan.php</a></td></tr><tr><td class="tl psp b">WebMotifs</td><td class="tl psp">Pattern Discovery</td><td class="tl psp"><a href="http://fraenkel.mit.edu/webmotifs/">http://fraenkel.mit.edu/webmotifs/</a></td></tr></tbody></table></div><h2><a name="2. Regulatory Datasets"></a>Regulatory Datasets</h2><div class="p20lo"><table class="sibo w100p"><tbody><tr><td class="tl psp b w20p bg-ye">Name</td><td class="tl psp b w40p bg-ye">Description</td><td class="tl psp b w40p bg-ye">URL</td></tr><tr><td class="tl psp">ABS</td><td class="tl psp">Database of Annotated regulatory Binding Sites from orthologous promoters</td><td class="tl psp"><a href="http://genome.imim.es/datasets/abs2005/downloads.html" mce_href="http://genome.imim.es/datasets/abs2005/downloads.html" rel="nofollow" linktype="raw" linktext="http://genome.imim.es/datasets/abs2005/downloads.html">http://genome.imim.es/datasets/abs2005/downloads.html</a></td></tr><tr><td class="tl psp">AGRIS AtcisDB and AtTFDB</td><td class="tl psp">Arabidopsis thaliana cis-regulatory db and&nbsp; transcription factor db</td><td class="tl psp"><a href="http://arabidopsis.med.ohio-state.edu/" mce_href="http://arabidopsis.med.ohio-state.edu/" rel="nofollow" linktype="raw" linktext="http://arabidopsis.med.ohio-state.edu/">http://arabidopsis.med.ohio-state.edu/</a></td></tr><tr><td class="tl psp">AtProbe</td><td class="tl psp">Arabidopsis thaliana promoter binding element database</td><td class="tl psp"><a href="http://rulai.cshl.edu/cgi-bin/atprobe/atprobe.pl" mce_href="http://rulai.cshl.edu/cgi-bin/atprobe/atprobe.pl" rel="nofollow" linktype="raw" linktext="http://rulai.cshl.edu/cgi-bin/atprobe/atprobe.pl">http://rulai.cshl.edu/cgi-bin/atprobe/atprobe.pl</a></td></tr><tr><td class="tl psp">AthaMap</td><td class="tl psp">Genome-wide map of potential transcription factor binding sites in <i>Arabidopsis thaliana</i></td><td class="tl psp"><a href="http://www.athamap.de/" mce_href="http://www.athamap.de/" rel="nofollow" linktype="raw" linktext="http://www.athamap.de/">http://www.athamap.de/</a></td></tr><tr><td class="tl psp">BOND</td><td class="tl psp">The Biomolecular Object Network Databank (BOND) is a&nbsp;resource to perform cross-database searches of available sequence, interaction, complex and pathway information.</td><td class="tl psp"><a href="http://bond.unleashedinformatics.com/Action?" mce_href="http://bond.unleashedinformatics.com/Action?" rel="nofollow" linktype="raw" linktext="http://bond.unleashedinformatics.com/Action?">http://bond.unleashedinformatics.com/Action?</a></td></tr><tr><td class="tl psp">CEPDB</td><td class="tl psp">C. elegans Promoter Db</td><td class="tl psp"><a href="http://rulai.cshl.edu/cgi-bin/CEPDB/home.cgi" mce_href="http://rulai.cshl.edu/cgi-bin/CEPDB/home.cgi" rel="nofollow" linktype="raw" linktext="http://rulai.cshl.edu/cgi-bin/CEPDB/home.cgi">http://rulai.cshl.edu/cgi-bin/CEPDB/home.cgi</a></td></tr><tr><td class="tl psp">cisreg.ca</td><td class="tl psp">Contains musle and liver data sets </td><td class="tl psp"><a href="http://www.cisreg.ca/tjkwon/" mce_href="http://www.cisreg.ca/tjkwon/" rel="nofollow" linktype="raw" linktext="http://www.cisreg.ca/tjkwon/">http://www.cisreg.ca/tjkwon/</a></td></tr><tr><td class="tl psp">Compel</td><td class="tl psp" style="width: 406px; font-family: Times New Roman; color: rgb(0, 0, 0);"><font size="+2"><strong></strong>Composite regulatory elements: structure, function and classification</td><td class="tl psp"><a href="http://compel.bionet.nsc.ru/new/compel/compel.html" mce_href="http://compel.bionet.nsc.ru/new/compel/compel.html" rel="nofollow" linktype="raw" linktext="http://compel.bionet.nsc.ru/new/compel/compel.html">http://compel.bionet.nsc.ru/new/compel/compel.html</a></td></tr><tr><td class="tl psp">DATF</td><td class="tl psp">The Database of Arabidopsis Transcription Factors (DATF)</td><td class="tl psp"><a href="http://datf.cbi.pku.edu.cn/" mce_href="http://datf.cbi.pku.edu.cn/" rel="nofollow" linktype="raw" linktext="http://datf.cbi.pku.edu.cn/">http://datf.cbi.pku.edu.cn/</a></td></tr><tr><td class="tl psp">DBTSS</td><td class="tl psp">Database of Transcriptional Start Sites</td><td class="tl psp"><a href="http://dbtss.hgc.jp/" mce_href="http://dbtss.hgc.jp/" rel="nofollow" linktype="raw" linktext="http://dbtss.hgc.jp/">http://dbtss.hgc.jp/</a></td></tr><tr><td class="tl psp">DoOP</td><td class="tl psp">Orthologous clusters of promoters</td><td class="tl psp"><a href="http://doop.abc.hu/" mce_href="http://doop.abc.hu/" rel="nofollow" linktype="raw" linktext="http://doop.abc.hu/">http://doop.abc.hu/</a></td></tr><tr><td class="tl psp">DBSD</td><td class="tl psp">Drosophila Binding Site Database</td><td class="tl psp"><a href="http://rulai.cshl.org/dbsd/index.html" mce_href="http://rulai.cshl.org/dbsd/index.html" rel="nofollow" linktype="raw" linktext="http://rulai.cshl.org/dbsd/index.html">http://rulai.cshl.org/dbsd/index.html</a> <br>*Note that this website is not yet functional but will be soon.</td></tr><tr><td class="tl psp">Drosophila DNase I Footprint Database</td><td class="tl psp">Webpage providing access to results of the systematic curation and genome annotation of 1,365 DNase I footprints for the fruitfly <em>D. melanogaster</em></td><td class="tl psp"><a href="http://www.flyreg.org/" mce_href="http://www.flyreg.org/" rel="nofollow" linktype="raw" linktext="http://www.flyreg.org/">http://www.flyreg.org/</a></td></tr><tr><td class="tl psp">DRTF</td><td class="tl psp">Database of Rice Transcription Factors</td><td class="tl psp"><a href="http://drtf.cbi.pku.edu.cn/" mce_href="http://drtf.cbi.pku.edu.cn/" rel="nofollow" linktype="raw" linktext="http://drtf.cbi.pku.edu.cn/">http://drtf.cbi.pku.edu.cn/</a></td></tr><tr><td class="tl psp">ECRBase</td><td class="tl psp">Database of Evolutionary Conserved Regions (ECRs), Promoters, andTranscription Factor Binding Sites in Vertebrate Genomes created usingECR Browser alignments</td><td class="tl psp"><a href="http://ecrbase.dcode.org/" mce_href="http://ecrbase.dcode.org/" rel="nofollow" linktype="raw" linktext="http://ecrbase.dcode.org/">http://ecrbase.dcode.org/</a></td></tr><tr><td class="tl psp">EDGEdb</td><td class="tl psp">PDI, PPI and gene expression datagenerated by the Walhout laboratory and others are made available tothe community through EDGEdb (elegans differential gene expression data)</td><td class="tl psp"><a href="http://edgedb.umassmed.edu/IndexAction.do" mce_href="http://edgedb.umassmed.edu/IndexAction.do" rel="nofollow" linktype="raw" linktext="http://edgedb.umassmed.edu/IndexAction.do">http://edgedb.umassmed.edu/IndexAction.do</a></td></tr><tr><td class="tl psp">EPD</td><td class="tl psp">Eukaryotic Promoter Database</td><td class="tl psp"><a href="http://www.epd.isb-sib.ch/" mce_href="http://www.epd.isb-sib.ch/" rel="nofollow" linktype="raw" linktext="http://www.epd.isb-sib.ch/">http://www.epd.isb-sib.ch/</a></td></tr><tr><td class="tl psp">ERTargetDB&nbsp;</td><td class="tl psp">ERTargetDB integrates information from ongoing Chip-on-chip experiments and promoter sequence conservation from the OMGProm database.</td><td class="tl psp"><a href="http://bioinformatics.med.ohio-state.edu/ERTargetDB/" mce_href="http://bioinformatics.med.ohio-state.edu/ERTargetDB/" rel="nofollow" linktype="raw" linktext="http://bioinformatics.med.ohio-state.edu/ERTargetDB/">http://bioinformatics.med.ohio-state.edu/ERTargetDB/</a></td></tr><tr><td class="tl psp">Globin Gene Server</td><td class="tl psp">Experimental data on the regulation of the globin gene cluster</td><td class="tl psp"><a href="http://globin.cse.psu.edu/" mce_href="http://globin.cse.psu.edu/" rel="nofollow" linktype="raw" linktext="http://globin.cse.psu.edu/">http://globin.cse.psu.edu/</a></td></tr><tr><td class="tl psp">Harbison Lab</td><td class="tl psp">Datasets useful in comparative genomics and in erythroid gene regulation</td><td class="tl psp"><a href="http://www.bx.psu.edu/%7Eross/dataset/DatasetHome.html" mce_href="http://www.bx.psu.edu/~ross/dataset/DatasetHome.html" rel="nofollow" linktype="raw" linktext="http://www.bx.psu.edu/~ross/dataset/DatasetHome.html">http://www.bx.psu.edu/~ross/dataset/DatasetHome.html</a></td></tr><tr><td class="tl psp">HemoPDB</td><td class="tl psp">Hematopoiesis Promoter Db</td><td class="tl psp"><a href="http://bioinformatics.med.ohio-state.edu/HemoPDB/" mce_href="http://bioinformatics.med.ohio-state.edu/HemoPDB/" rel="nofollow" linktype="raw" linktext="http://bioinformatics.med.ohio-state.edu/HemoPDB/">http://bioinformatics.med.ohio-state.edu/HemoPDB/</a></td></tr><tr><td class="tl psp">JASPAR</td><td class="tl psp">high-quality transcription factor binding profile database.</td><td class="tl psp"><a href="http://jaspar.cgb.ki.se/cgi-bin/jaspar_db.pl" mce_href="http://jaspar.cgb.ki.se/cgi-bin/jaspar_db.pl" rel="nofollow" linktype="raw" linktext="http://jaspar.cgb.ki.se/cgi-bin/jaspar_db.pl">http://jaspar.cgb.ki.se/cgi-bin/jaspar_db.pl</a></td></tr><tr><td class="tl psp"><font color="#000000">LSPD</td><td class="tl psp"><font color="#000000">The Liver Specific Gene Promoter Database</td><td class="tl psp"><font color="#000000"><font color="#000000"><a href="http://rulai.cshl.edu/LSPD/" mce_href="http://rulai.cshl.edu/LSPD/" rel="nofollow" linktype="raw" linktext="http://rulai.cshl.edu/LSPD/">http://rulai.cshl.edu/LSPD/</a></td></tr><tr><td class="tl psp">MPD</td><td class="tl psp">Mammalian Promoter Db (human, mouse and rat)</td><td class="tl psp"><a href="http://rulai.cshl.edu/CSHLmpd2" mce_href="http://rulai.cshl.edu/CSHLmpd2" rel="nofollow" linktype="raw" linktext="http://rulai.cshl.edu/CSHLmpd2">http://rulai.cshl.edu/CSHLmpd2</a></td></tr><tr><td class="tl psp">MPromDb</td><td class="tl psp">Mammalian Promoter Db with experimentally supported annotations</td><td class="tl psp"><a href="http://bioinformatics.med.ohio-state.edu/MPromDb/" mce_href="http://bioinformatics.med.ohio-state.edu/MPromDb/" rel="nofollow" linktype="raw" linktext="http://bioinformatics.med.ohio-state.edu/MPromDb/">http://bioinformatics.med.ohio-state.edu/MPromDb/</a></td></tr><tr><td class="tl psp">MTIR</td><td class="tl psp">Muscle-specific regulation of transcription</td><td class="tl psp"><a href="http://www.cbil.upenn.edu/MTIR/HomePage.html" mce_href="http://www.cbil.upenn.edu/MTIR/HomePage.html" rel="nofollow" linktype="raw" linktext="http://www.cbil.upenn.edu/MTIR/HomePage.html">http://www.cbil.upenn.edu/MTIR/HomePage.html</a></td></tr><tr><td class="tl psp">OMGProm</td><td class="tl psp">Orthologous Mammalian Gene Promoters</td><td class="tl psp"><a href="http://bioinformatics.med.ohio-state.edu/OMGProm/" mce_href="http://bioinformatics.med.ohio-state.edu/OMGProm/" rel="nofollow" linktype="raw" linktext="http://bioinformatics.med.ohio-state.edu/OMGProm/">http://bioinformatics.med.ohio-state.edu/OMGProm/</a></td></tr><tr><td class="tl psp">ooTFD</td><td class="tl psp">object-oriented Transcription Factors Db</td><td class="tl psp"><a href="http://www.ifti.org/ootfd/" mce_href="http://www.ifti.org/ootfd/" rel="nofollow" linktype="raw" linktext="http://www.ifti.org/ootfd/">ttp://www.ifti.org/ootfd/</a></td></tr><tr><td class="tl psp">OPD</td><td class="tl psp">Osteo-Promoter Db (promoters of genes in the osteogenic pathway)</td><td class="tl psp"><a href="http://www.opd.tau.ac.il/" mce_href="http://www.opd.tau.ac.il/" rel="nofollow" linktype="raw" linktext="http://www.opd.tau.ac.il/">http://www.opd.tau.ac.il/</a></td></tr><tr><td class="tl psp">Oreganno</td><td class="tl psp">Open regulatory annotation database</td><td class="tl psp"><a href="http://oreganno.org/" mce_href="http://oreganno.org" rel="nofollow" linktype="raw" linktext="http://oreganno.org">http://oreganno.org</a></td></tr><tr><td class="tl psp">PLACE</td><td class="tl psp">Plant Cis-acting Regulatory DNA Elements</td><td class="tl psp"><a href="http://www.dna.affrc.go.jp/PLACE/" mce_href="http://www.dna.affrc.go.jp/PLACE/" rel="nofollow" linktype="raw" linktext="http://www.dna.affrc.go.jp/PLACE/">http://www.dna.affrc.go.jp/PLACE/</a></td></tr><tr><td class="tl psp">Plant CARE</td><td class="tl psp">Cis-Acting regulatory element.database</td><td class="tl psp"><a href="http://intra.psb.ugent.be:8080/PlantCARE/" mce_href="http://intra.psb.ugent.be:8080/PlantCARE/" rel="nofollow" linktype="raw" linktext="http://intra.psb.ugent.be:8080/PlantCARE/">http://intra.psb.ugent.be:8080/PlantCARE/</a><br><span style="color: rgb(0, 0, 0);">*Note: This database does not appear to currently be online.</span></td></tr><tr><td class="tl psp">Plant Prom DB</td><td class="tl psp">Plant Promoter Sequences</td><td class="tl psp"><a href="http://mendel.cs.rhul.ac.uk/mendel.php?topic=plantprom" mce_href="http://mendel.cs.rhul.ac.uk/mendel.php?topic=plantprom" rel="nofollow" linktype="raw" linktext="http://mendel.cs.rhul.ac.uk/mendel.php?topic=plantprom">http://mendel.cs.rhul.ac.uk/mendel.php?topic=plantprom</a></td></tr><tr><td class="tl psp">RARTF</td><td class="tl psp">RIKEN Arabidopsis Transcription Factor db</td><td class="tl psp"><a href="http://rarge.gsc.riken.jp/rartf/" mce_href="http://rarge.gsc.riken.jp/rartf/" rel="nofollow" linktype="raw" linktext="http://rarge.gsc.riken.jp/rartf/">http://rarge.gsc.riken.jp/rartf/</a></td></tr><tr><td class="tl psp">REDfly</td><td class="tl psp">Regulatory Element Database for Drosophila</td><td class="tl psp"><a href="http://redfly.ccr.buffalo.edu/?content=/search.php" mce_href="http://redfly.ccr.buffalo.edu/?content=/search.php" rel="nofollow" linktype="raw" linktext="http://redfly.ccr.buffalo.edu/?content=/search.php">http://redfly.ccr.buffalo.edu/?content=/search.php</a></td></tr><tr><td class="tl psp">RiceTFDB</td><td class="tl psp">Rice genes involved in transcriptional control</td><td class="tl psp"><a href="http://ricetfdb.bio.uni-potsdam.de/v2.1/" mce_href="http://ricetfdb.bio.uni-potsdam.de/v2.1/" rel="nofollow" linktype="raw" linktext="http://ricetfdb.bio.uni-potsdam.de/v2.1/">http://ricetfdb.bio.uni-potsdam.de/v2.1/</a></td></tr><tr><td class="tl psp"> RIKEN TFdb</td><td class="tl psp">Mouse Transcription Factor Db</td><td class="tl psp"><a href="http://genome.gsc.riken.jp/TFdb/" mce_href="http://genome.gsc.riken.jp/TFdb/" rel="nofollow" linktype="raw" linktext="http://genome.gsc.riken.jp/TFdb/">http://genome.gsc.riken.jp/TFdb/</a></td></tr><tr><td class="tl psp">rSNP</td><td class="tl psp">Influence of single nucleotide mutations in     regulatory gene regions</td><td class="tl psp"><a href="http://wwwmgs.bionet.nsc.ru/mgs/systems/rsnp/" mce_href="http://wwwmgs.bionet.nsc.ru/mgs/systems/rsnp/" rel="nofollow" linktype="raw" linktext="http://wwwmgs.bionet.nsc.ru/mgs/systems/rsnp/">http://wwwmgs.bionet.nsc.ru/mgs/systems/rsnp/</a></td></tr><tr><td class="tl psp">SCPD</td><td class="tl psp">S. cerevisiae Promoter Db</td><td class="tl psp"><a href="http://rulai.cshl.edu/SCPD/" mce_href="http://rulai.cshl.edu/SCPD/" rel="nofollow" linktype="raw" linktext="http://rulai.cshl.edu/SCPD/">http://rulai.cshl.edu/SCPD/</a></td></tr><tr><td class="tl psp">Stanford Encode Project</td><td class="tl psp">ENCyclopedia Of DNA Elements</td><td class="tl psp"><a href="http://www-shgc.stanford.edu/genetics/encode.html" mce_href="http://www-shgc.stanford.edu/genetics/encode.html" rel="nofollow" linktype="raw" linktext="http://www-shgc.stanford.edu/genetics/encode.html">http://www-shgc.stanford.edu/genetics/encode.html</a></td></tr><tr><td class="tl psp">transcription factors dd</td><td class="tl psp"> transcription factors of humans and other organisms</td><td class="tl psp"><a href="http://www.proteinlounge.com/trans_home.asp" mce_href="http://www.proteinlounge.com/trans_home.asp" rel="nofollow" linktype="raw" linktext="http://www.proteinlounge.com/trans_home.asp">http://www.proteinlounge.com/trans_home.asp</a><br>*Note: a subscription is required to view search results</td></tr><tr><td class="tl psp">TRANSFAC</td><td class="tl psp">eukaryotic transcription factors and their binding profiles</td><td class="tl psp"><a href="http://www.gene-regulation.de/" mce_href="http://www.gene-regulation.de/" rel="nofollow" linktype="raw" linktext="http://www.gene-regulation.de/">http://www.gene-regulation.de/</a><br>*Note: Downloads from the public version are not available</td></tr><tr><td class="tl psp">TRED</td><td class="tl psp">Transcriptional Regulatory Element Database</td><td class="tl psp"><a href="http://rulai.cshl.edu/cgi-bin/TRED/tred.cgi?process=home" mce_href="http://rulai.cshl.edu/cgi-bin/TRED/tred.cgi?process=home" rel="nofollow" linktype="raw" linktext="http://rulai.cshl.edu/cgi-bin/TRED/tred.cgi?process=home">http://rulai.cshl.edu/cgi-bin/TRED/tred.cgi?process=home</a></td></tr><tr><td class="tl psp">TRRD</td><td class="tl psp">Transcription Regulatory Regions Db</td><td class="tl psp"><a href="http://wwwmgs.bionet.nsc.ru/mgs/gnw/trrd/" mce_href="http://wwwmgs.bionet.nsc.ru/mgs/gnw/trrd/" rel="nofollow" linktype="raw" linktext="http://wwwmgs.bionet.nsc.ru/mgs/gnw/trrd/">http://wwwmgs.bionet.nsc.ru/mgs/gnw/trrd/</a></td></tr><tr><td class="tl psp">VISTA Enhancer Browser</td><td class="tl psp">A database of tissue-specific human enhancers.</td><td class="tl psp"><a href="http://enhancer.lbl.gov/" mce_href="http://enhancer.lbl.gov" rel="nofollow" linktype="raw" linktext="http://enhancer.lbl.gov">http://enhancer.lbl.gov</a></td></tr></tbody></table></div>};
print $temptail->output;
