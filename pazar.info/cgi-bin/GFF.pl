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
					<p class="b">sequence</p>
					<ul>
						<li>example &mdash; <div class="inline p5 bg-lg monospace"> sequence="ATTTGTAGGAGTGAGTCAGCTGACCCGC"; </div></li>
					</ul>
				</li>
				<li>
					<p class="b">db_seqinfo</p> 
					<ul>
						<li>format &mdash; <span class="b">database:assembly</span></li>
						<li>example &mdash; <div class="inline p5 bg-lg monospace"> db_seqinfo="EnsEMBL:NCBI 35"; </li>
					</ul>
				</li>
				<li><p class="b">species</p>
					<ul>
						<li>example &mdash; <div class="inline p5 bg-lg monospace"> species="Homo sapiens"; </div></li>
					</ul>
				</li>
				<li><p class="b">db_geneinfo</p>
					<ul>
						<li>format &mdash; <span class="b">database:accession:name</span></li>
						<li>example &mdash; <div class="inline p5 bg-lg monospace"> db_geneinfo="EnsEMBL_gene:ENSG00000133256:PDE6B"; </div></li>
						<li>note &mdash; the database can be either "EnsEMBL_gene", "Entrez_gene", "RefSeq", or "SwissProt". Last part (gene name) optional.</li>
					</ul>
				</li>
			</ul></div>
			
			<h3>Optional attributes</h3>
			<div class="p5to p5bo"><ul>
				<li>
					<p class="b">band</p>
					<ul>
						<li>example &mdash; <div class="inline p5 bg-lg monospace">band="16.3";</div>
					</ul>
				</li>
				<li>
					<p class="b">db_transcriptinfo</p>
					<ul>
						<li>format &mdash; <span class="b">database:accession:name</span></li>
						<li>example &mdash; <div class="inline p5 bg-lg monospace">db_transcriptinfo="EnsEMBL_transcript:ENST00000255622";</div></li>
						<li>note &mdash; the database can be either "EnsEMBL_transcript", "RefSeq", or "SwissProt". Last part (isoform name) is optional.</li>
					</ul>
				</li>
				<li>
					<p class="b">transcript_start</p>
					<ul>
						<li>example &mdash; <div class="inline p5 bg-lg monospace">transcript_start="609373";</div></li>
					</ul>
				</li>
				<li>
					<p class="b">analysis_name</p>
					<ul>
						<li>example &mdash; <div class="inline p5 bg-lg monospace">analysis_name="gff_example1";</div></li>
						<li>note &mdash; please ensure that you provide the same analysis name to all records belonging to the same experiment.</li>
					</ul>
				</li>
				<li>
					<p class="b">analysis_comment</p>
					<ul>
						<li>example &mdash; <div class="inline p5 bg-lg monospace">analysis_comment="some comment on the experiment";</div></li>
						<li>note &mdash; please ensure that you provide the same analysis comment to all records belonging to the same experiment.</li>
					</ul>
				</li>
				<li>
					<p class="b">db_tfinfo</p>
					<ul>
						<li>format &mdash; <span class="b">database:accession:name</span></li>
						<li>example &mdash; <div class="inline p5 bg-lg monospace">db_tfinfo="EnsEMBL_transcript:ENST00000250471:NRL";</div></li>
						<li>note &mdash; the database can be either "EnsEMBL_transcript", "RefSeq", or "SwissProt". The record is stored as an interaction if db_tfinfo is provided. If you want to record an interaction but the factor is unknown, state db_tfinfo="unknown". If db_tfinfo is not provided, the record will be stored as an expression.</li>
					</ul>
				</li>
				<li>
					<p class="b">method</p>
					<ul>
						<li>example &mdash; <div class="inline p5 bg-lg monospace">method="SELEX";</div></li>
					</ul>
				</li>
				<li>
					<p class="b">evidence</p>
					<ul>
						<li>example &mdash; <div class="inline p5 bg-lg monospace">evidence="curated";</div></li>
						<li>note &mdash; the evidence should be either "curated" or "prediction".</li>
					</ul>
				</li>
				<li>
					<p class="b">pmid</p>
					<ul>
						<li>example &mdash; <div class="inline p5 bg-lg monospace">pmid="15264535";</div></li>
					</ul>
				</li>
				<li>
					<p class="b">cell_type</p>
					<ul>
						<li>format &mdash; <span class="b">cell:species</span></li>
						<li>example &mdash; <div class="inline p5 bg-lg monospace">cell_type="HepG2:Homo sapiens";</div></li>
					</ul>
				</li>
				<li>
					<p class="b">expression</p>
					<ul>
						<li>format &mdash; <span class="b">level:scale</span></li>
						<li>example &mdash; <div class="inline p5 bg-lg monospace">expression="56:percent";</div></li>
						<li>note &mdash; use this field if you want to record a specific expression level. If not used, an expression experiment is stored as "induced".</li>
					</ul>
				</li>
				<li>
					<p class="b">impaired_mutant</p>
					<ul>
						<li>format &mdash; <span class="b">sequence</span></li>
						<li>example &mdash; <div class="inline p5 bg-lg monospace">impaired_mutant="gactactgatgGtaacNagtcga";</div></li>
						<li>note &mdash; the format of the sequence should be lowercase where the original sequence remains and uppercase for the mutated nucleotides. If the mutation is a deletion use "N" where the original nucleotides were.</li>
					</ul>
				</li>
			</ul>
			</div>
		</div>
	<h2>Examples</h2>
		<div class="p20lo">
			<h3>Interaction example</h3>
			<div class="p10 bg-lg monospace">chr7	oreganno_example	OREG0000056	99037559	99037584	.	-	.	sequence="gcatcaagaacatgtggttctaatgg"; db_seqinfo="EnsEMBL:NCBI 35"; species="Homo sapiens"; db_geneinfo="EntrezGene:1576:CYP3A4"; band="q22.1"; analysis_name="gff_example1"; db_tfinfo="EnsEMBL Transcript:ENST00000289790:USF1"; method="EMSA_analysis"; evidence="curated"; pmid="14742674"; impaired_mutant="gcatcaagaacatTAggttctaatgg"</div>

			<h3>Expression example</h3>
			<div class="p10 bg-lg monospace">chr7	oreganno_example	OREG0000056	99037559	99037584	.	-	.	sequence="gcatcaagaacatgtggttctaatgg"; db_seqinfo="EnsEMBL:NCBI 35"; species="Homo sapiens"; db_geneinfo="EntrezGene:1576:CYP3A4"; band="q22.1"; analysis_name="gff_example2"; cell_type="HepG2:Homo sapiens"; method="gene reporter assay"; evidence="curated"; pmid="14742674"; impaired_mutant="gcatcaagaacatTAggttctaatgg"</div>
		</div>};

print $temptail->output;
