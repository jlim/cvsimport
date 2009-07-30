#!/usr/bin/perl

use HTML::Template;
my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};

my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");
my $temptail = HTML::Template->new(filename => "$pazarcgipath/tail.tmpl");
$template->param(TITLE => "The PAZAR GFF format | PAZAR");
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
		<a href="$pazar_cgi/dataformats.pl" class="b">Data formats</a> &raquo; PAZAR GFF format
		<div class="clear-r"></div>
	</div>
	<h1>PAZAR GFF Format</h1>
	<h2>Overview</h2>
		<div class="p20lo">
			<p><span class="b">The PAZAR GFF format (<a href="http://www.sanger.ac.uk/Software/formats/GFF/" target="_blank">What is GFF?</a>) is intended to capture simple annotations.</span> It is not meant to record a detailed annotation. Please use the XML format if you want more options. One record is on a unique line and holds one annotation for one sequence, this annotation coming either from an interaction <span class="b">or</span> an expression experiment (<span class="b">not both in the same record</span>).</p>
			<p>The record is stored as an interaction if db_tfinfo is provided. If you want to record an interaction but the factor is unknown, state:</p>
			<div class="p5bo"><div class="p10 bg-lg monospace">db_tfinfo="unknown"</div></div>
			<p>If db_tfinfo is not provided, the record will be stored as an expression. An interaction will be stored as "good" and an expression as "induced". If you want to record a specific expression level, use the expression field. If a mutant sequence is reported it is assumed that this mutant has an impaired activity compared to the annotation of the original sequence (interaction = "none" or expression = "no change").</p>
		</div>
	<h2>Structure of format</h2>
		<div class="p20lo">
			<p class="bold">Fields are: &lt;seqname&gt;&nbsp; &lt;source&gt;&nbsp; &lt;feature&gt;&nbsp; &lt;start&gt&nbsp; &lt;end&gt;&nbsp; &lt;score&gt;&nbsp; &lt;strand&gt;&nbsp; &lt;frame&gt;&nbsp; [attributes]</p>
			<p>Those 9 fields are tab-delimited. The attribute field must have a tag value structure with the following syntax, flattened onto one line by semicolon separators:</p>
			<div class="p10 bg-lg monospace">tag1="value1";tag2="value2"</div>

			<h3>Mandatory fields</h3>
			<ul>
				<li><span class="b">seqname</span> - the name of the sequence&mdash;must be a chromosome</li>
				<li><span class="b">source</span> - the project to store this feature in</li>
				<li><span class="b">feature</span> - the name of this feature or enter a single period (".")</li>
				<li><span class="b">start</span> - the starting position of the feature in the sequence (the first base is numbered 1)</li>
				<li><span class="b">end</span> - the ending position of the feature (inclusive)</li>
				<li><span class="b">score</span> - no need here&mdash;if there is no score value, enter a single period (".")</li>
				<li><span class="b">strand</span> - valid entries include a plus sign ("+"), a minus sign ("-"), or&mdash;for those who don't know or don't care&mdash;a period (".")</li>
				<li><span class="b">frame</span> - no need here&mdash;the value should be a single period (".")</li>
			</ul>
			
			<h3>Mandatory attributes</h3>
			<div class="p5to p5bo"><ul>
				<li>
					<div class="b p5bo">sequence</div>
					<ul>
						<li>example &mdash; <div class="inline p5 bg-lg monospace"> sequence="ATTTGTAGGAGTGAGTCAGCTGACCCGC"; </div></li>
					</ul>
				</li>
				<li>
					<div class="b p5bo">db_seqinfo</div> 
					<ul>
						<li>format &mdash; <span class="b">database:assembly</span></li>
						<li>example &mdash; <div class="inline p5 bg-lg monospace"> db_seqinfo="EnsEMBL:NCBI 35"; </li>
					</ul>
				</li>
				<li><div class="b p5bo">species</div>
					<ul>
						<li>example &mdash; <div class="inline p5 bg-lg monospace"> species="Homo sapiens"; </div></li>
					</ul>
				</li>
				<li><div class="b p5bo">db_geneinfo</div>
					<ul>
						<li>format &mdash; <span class="b">database:accession:name</span></li>
						<li>example &mdash; <div class="inline p5 bg-lg monospace"> db_geneinfo="EnsEMBL_gene:ENSG00000133256:PDE6B"; </div></li>
						<li>note &mdash; the database can be either "EnsEMBL_gene", "Entrez_gene", "RefSeq", or "SwissProt". Last part (gene name) optional.</li>
					</ul>
				</li>
			</ul></div>
			
			<h3>Optional attributes</h3>
			<p><span class="b">band=</span>""; # eg. "p16.3"<br>
			<span class="b">db_transcriptinfo=</span>"database:accession:name"; # eg. "EnsEMBL_transcript:ENST00000255622"<br>The database can be either of the following:EnsEMBL Transcript, RefSeq, SwissProt. Last part (isoform name) optional.<br>
			<span class="b">transcript_start=</span>""; # eg. "609373"<br>
			<span class="b">analysis_name=</span>""; # eg. "gff_example1"<br><span class='red'>Note:</span> Please ensure that you provide the same analysis name to all records belonging to the same experiment.<br>
			<span class="b">analysis_comment=</span>""; # eg. "some comment on the experiment"<br><span class='red'>Note:</span> Please ensure that you provide the same analysis comment to all records belonging to the same experiment.<br>
			<span class="b">db_tfinfo=</span>"database:accession:name"; # eg. "EnsEMBL_transcript:ENST00000250471:NRL"<br>The database can be either of the following:EnsEMBL Transcript, RefSeq, SwissProt.<br><span class='red'>Note:</span> The record is stored as an interaction if db_tfinfo is provided. If you want to record an interaction but the factor is unknown, state db_tfinfo="unknown". If db_tfinfo is not provided, the record will be stored as an expression.<br>
			<span class="b">method=</span>""; # eg. "SELEX"<br>
			<span class="b">evidence=</span>""; # should be either "curated" or "prediction"<br>
			<span class="b">pmid=</span>""; # eg. "15264535"<br>
			<span class="b">cell_type</span>="cell:species"; # eg. "HepG2:Homo sapiens" Last part (species) optional.<br>
			<span class="b">expression=</span>"level:scale"; # eg. "56:percent"<br>Use this field if you want to record a specific expression level. If not used, an expression experiment is stored as 'induced'.<br>
			<span class="b">impaired_mutant=</span>"sequence"; # The format of the sequence should be lowercase where the original sequence remains and uppercase for the mutated nucleotides. If the mutation is a deletion use 'N' where the original nucleotides were.<br></p>
		</div>
	<h2>Examples</h2>
		<div class="p20lo">
			<h3>Interaction example</h3>
			<div class="p10 bg-lg monospace">chr7	oreganno_example	OREG0000056	99037559	99037584	.	-	.	sequence="gcatcaagaacatgtggttctaatgg"; db_seqinfo="EnsEMBL:NCBI 35"; species="Homo sapiens"; db_geneinfo="EntrezGene:1576:CYP3A4"; band="q22.1"; analysis_name="gff_example1"; db_tfinfo="EnsEMBL Transcript:ENST00000289790:USF1"; method="EMSA_analysis"; evidence="curated"; pmid="14742674"; impaired_mutant="gcatcaagaacatTAggttctaatgg"</div>

			<h3>Expression example</h3>
			<div class="p10 bg-lg monospace">chr7	oreganno_example	OREG0000056	99037559	99037584	.	-	.	sequence="gcatcaagaacatgtggttctaatgg"; db_seqinfo="EnsEMBL:NCBI 35"; species="Homo sapiens"; db_geneinfo="EntrezGene:1576:CYP3A4"; band="q22.1"; analysis_name="gff_example2"; cell_type="HepG2:Homo sapiens"; method="gene reporter assay"; evidence="curated"; pmid="14742674"; impaired_mutant="gcatcaagaacatTAggttctaatgg"</div>
		</div>};

print $temptail->output;
