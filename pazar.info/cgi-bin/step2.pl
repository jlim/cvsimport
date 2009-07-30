#!/usr/bin/perl

use HTML::Template;
my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};

my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");
my $temptail = HTML::Template->new(filename => "$pazarcgipath/tail.tmpl");
$template->param(TITLE => "Step 2 - Capturing information | PAZAR XML format | PAZAR");
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
		<a href="$pazar_cgi/dataformats.pl" class="b">Data formats</a> &raquo; <a href="$pazar_cgi/xml.pl" class="b">PAZAR XML format</a> &raquo; Step-by-step documentation
		<div class="clear-r"></div>
	</div>
	<h1>PAZAR XML format</h1>
	<h2>Step 2 &mdash; Capturing the regulatory sequence and (or) TF basic information</h2>
	<div class="">
		<p>Once the project element has been defined (<a href="$pazar_cgi/step1.pl">see Step 1</a>), you are ready to enter sequence and transcription factor information. These will be entered within the "data" element, which is a child element within the "pazar" element.</p>
		
		<h3>2.0. Initialization</h3>
		<div class="p20lo">
			<p>The "data" element stores all the annotations separately. They will be linked together later in the "analysis" element (<a href="$pazar_cgi/step3.pl">see Step 3</a>). First the "data" element has to initialized:</p>
			<div class="p5bo">
				<div class="p5 bg-lg monospace b">&nbsp;&nbsp;&lt;data&gt;</div>
			</div>
			<p>Then, different type of annotations can be inserted:</p>
			<ul>
				<li><a href="#Regulatory_Sequence_for_specific_gene">Regulatory sequence for a specific gene</a></li>
				<li><a href="#Regulatory_Sequence_without_gene_info">Regulatory sequence without any gene information</a></li>
				<li><a href="#Transcription_Factor">Transcription factor</a></li>
				<li><a href="#Artificial_sequence">Artificial sequence or a sequence that is not attached to genomic coordinates</a></li>
			</ul>
		</div>
		<h3>
			<div class="float-r"><a href="#Step2_TOP">Back to top</a></div>
			<a name="Regulatory_Sequence_for_specific_gene"></a>2.1. Annotating a regulatory sequence for a specific gene
		</h3>
		<div class="p20lo">
			<p>The "reg_seq" is embedded within "tsr" and "gene_source" elements. The "gene_source" element informs about the gene accession number. The "tsr" element describes the transcription start region based on the observation that transcription does not always start at exactly the same nucleotide (however, a unique start site can be described by inserting the same value in fuzzy_start and fuzzy_end).</p>
			<p>Thus, if a gene has two alternative promoters, each of which can be described with a different "tsr" element within the "gene_source" element, different regulatory sequences can be associated with each "tsr".</p>

			<div class="p5bo"><div class="p10 bg-lg monospace b">
				<div>&lt;gene_source db_accn="<span class="red">ENSG00000133256</span>" description="<span class="red">PDE6B</span>" pazar_id="<span class="red">gs_0001</span>"&gt;</span></div>
				<div class="p10lo">&lt;db_source db_name="<span class="red">EnsEMBL</span>" assembly="<span class="red">37_35j</span>"/&gt;</div>
				<div class="p10lo">&lt;tsr fuzzy_end="<span class="red">609373</span>" fuzzy_start="<span class="red">609373</span>" pazar_id="<span class="red">tsr_0001</span>"&gt;</div>
				<div class="p20lo">&lt;reg_seq&nbsp;pazar_id="<span class="red">rs_0001</span>" quality="<span class="red">tested</span>" sequence="<span class="red">ATTTGTAGGAGTGAGTCAGCTGACCCGC</span>"&gt;</div>
				<div class="p30lo">&lt;coordinate begin="<span class="red">609283</span>" end="<span class="red">609310</span>" length="<span class="red">28</span>" strand="<span class="red">+</span>"&gt;</div>
				<div class="p40lo">&lt;location band="<span class="red">p16.3</span>" chr="<span class="red">4</span>" species="<span class="red">Homo sapiens</span>"&gt;</div>
				<div class="p50lo">&lt;db_source db_name="<span class="red">EnsEMBL</span>" assembly="<span class="red">NCBI 35</span>"/&gt;</div>
				<div class="p40lo">&lt;/location&gt;</div>
				<div class="p30lo">&lt;/coordinate&gt;</div>
				<div class="p20lo">&lt;/reg_seq&gt;</div>
				<div class="p10lo">&lt;/tsr&gt;</div>
				<div>&lt;/gene_source&gt;</div>
			</div></div>
		<p><span class="b">Note: replace the red values with your own information.</span> The pazar IDs are internal IDs that will not be stored. They can be anything as long as they are unique throughout the file.</p>
	</div>
	<h3>
		<div class="float-r"><a href="$pazar_cgi/step2.pl#Step2_TOP">Back to top</a></div>
		<a name="Regulatory_Sequence_without_gene_info"></a>2.2. Annotating a regulatory sequence without any gene information
	</h3>
	<div class="p20lo">
		<p>The "reg_seq" element can also be embedded in a "marker" element if the gene regulated by the sequence is not defined yet. The marker can be a gene but then it is just used for location purpose and not to infer any role for the sequence on this gene.</p>
		<div class="p5bo"><div class="p10 bg-lg monospace b"><span>&nbsp;&nbsp;&nbsp;
&lt;marker db_accn="<span class="red">ENSG00000133256</span>"
description="<span class="red">PDE6B</span>"
pazar_id="<span class="red">ma_0001</span>"&gt;</span><br>

      <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&lt;db_source db_name="<span class="red">EnsEMBL</span>" assembly="<span class="red">37_35j</span>"/&gt;</span><br>

      <span>&nbsp;</span><span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&lt;reg_seq&nbsp;pazar_id="<span class="red">rs_0001</span>"
quality="<span class="red">tested</span>"
sequence="<span class="red">ATTTGTAGGAGTGAGTCAGCTGACCCGC</span>"&gt;</span><br>

      <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&lt;coordinate begin="<span class="red">609283</span>"
end="<span class="red">609310</span>"
length="<span class="red">28</span>"
strand="<span class="red">+</span>"&gt;</span><br>

      <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&lt;location band="<span class="red">p16.3</span>"
chr="<span class="red">4</span>"
species="<span class="red">Homo sapiens</span>"&gt;</span><br>

      <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&lt;db_source db_name="<span class="red">EnsEMBL</span>" assembly="<span class="red">37_35j</span>"/&gt;</span><br>

      <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&lt;/location&gt;</span><br>

      <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&lt;/coordinate&gt;</span><br>

      <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&lt;/reg_seq&gt;</span><br>

      <span></span><span>&nbsp;&nbsp;&nbsp;
&lt;/marker&gt;</span></div></div>
		<p><span class="b">Note: replace the red values with your own information.</span> The pazar IDs are internal IDs that will not be stored. They can be anything as long as they are unique throughout the file.</p>
	</div>

	<h3>
		<div class="float-r"><a href="$pazar_cgi/step2.pl#Step2_TOP">Back to top</a></div>
		<a name="Transcription_Factor"></a>2.3. Annotating a transcription factor
	</h3>
		<div class="p20lo">
			<p>A transcription factor is described in multiple steps. First, at the gene level: the "tf" element is embedded in both "transcript" and "gene_source" elements. Multiple "transcript" elements can be used to describe multiple isoforms of a gene. Then, at the protein level: The "funct_tf" element captures the functional protein information with as many "tf_unit" elements as there are proteins in the complex (1 for monomers, 2 for dimers, <span class="i">etc.</span>) The tf_id calls a pazar_id from a "tf" element.</p>
			<div class="p5bo"><div class="p10 bg-lg monospace b">
&nbsp;&nbsp;&nbsp;
&lt;gene_source db_accn="<span class="red">ENSG00000129535</span>"
description="<span class="red">NRL</span>"
pazar_id="<span class="red">gs_0002</span>"&gt;</span><br>

      <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&lt;db_source db_name="<span class="red">EnsEMBL</span>" assembly="<span class="red">37_35j</span>"/&gt;</span><br>

      <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&lt;transcript db_accn="<span class="red">ENST00000250471</span>"
pazar_id="<span class="red">tr_0002</span>"&gt;</span><br>

      <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&lt;db_source db_name="<span class="red">EnsEMBL</span>" assembly="<span class="red">37_35j</span>"/&gt;</span><br>

      <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&lt;tf class="<span class="red">bZIP</span>"
family="<span class="red">MAF</span>"
pazar_id="<span class="red">tf_0001</span>"/&gt;</span><br>

      <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&lt;/transcript&gt;</span><br>

      <span>&nbsp;&nbsp;&nbsp;
&lt;/gene_source&gt;</span><br>

      <span>&nbsp;&nbsp;&nbsp;
&lt;funct_tf funct_tf_name="<span class="red">NRL</span>"
pazar_id="<span class="red">fu_0001</span>"&gt;</span><br>

      <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&lt;tf_unit pazar_id="<span class="red">tu_0001</span>"
tf_id="<span class="red">tf_0001</span>"/&gt;</span><br>

      <span>&nbsp;&nbsp;&nbsp;
&lt;/funct_tf&gt;</div></div>
		<p><span class="b">Note: replace the red values with your own information.</span> The pazar IDs are internal IDs that will not be stored. They can be anything as long as they are unique throughout the file.</p>
	</div>

	<h3>
		<div class="float-r"><a href="$pazar_cgi/step2.pl#Step2_TOP">Back to top</a></div>
		<a name="Artificial_sequence"></a>2.4. Annotating an artificial sequence
	</h3>
	<div class="p20lo">
		<p>The "construct" element can be used to describe any sequence without specific genomic coordinates (<span class="i">e.g.</span> a synthesized oligonucleotide representing a consensus binding site).</p>
		<div class="p5bo"><div class="p10 bg-lg monospace b">&lt;construct construct_name="<span class="red">FN-13A</span>" description="<span class="red">random oligo</span>" sequence="<span class="red">gggtgagtcagcg</span>" pazar_id="<span class="red">co_0001</span>"/&gt;</span></div></div>
		<p><span class="b">Note: replace the red values with your own information.</span> The pazar IDs are internal IDs that will not be stored. They can be anything as long as they are unique throughout the file.</p>
	</div>
	<div><a href="$pazar_cgi/step1.pl" class="b">&laquo; Go to Step 1</a> &nbsp; <a href="$pazar_cgi/step3.pl" class="b">Go to Step 3 &raquo;</a></div>
</div>};

print $temptail->output;
