#!/usr/bin/perl

use HTML::Template;

# open the html header template
my $template = HTML::Template->new(filename => 'header.tmpl');

# fill in template parameters
$template->param(TITLE => 'PAZAR GFF format');

# send the obligatory Content-Type and print the template output
print "Content-Type: text/html\n\n", $template->output;

print<<page;
          <p class="title1">PAZAR - GFF format</p>
<p class="title2">Overview:</p>
<p>The PAZAR GFF format (<a href="http://www.sanger.ac.uk/Software/formats/GFF/" target="_blank">What is GFF?</a>) is intended to capture simple annotations. It is not meant to record a detailed annotation. Please use the XML format if you want more options.
One record is on a unique line and holds one annotation for one sequence, this annotation coming either from an interaction OR an expression experiment (NOT BOTH IN THE SAME RECORD). An interaction will be stored as 'good' and an expression as 'induced'. If a mutant sequence is reported it is assumed that this mutant has an impaired activity compared to the annotation of the original sequence(interaction = 'none' or expression = 'no change').</p>
<p class="title2">PAZAR GFF format (uppercase are mandatory fields):</p>
<p>SEQNAME	SOURCE	FEATURE	START	END	SCORE	STRAND	FRAME	SEQUENCE=""; DB_SEQINFO="DATABASE:ASSEMBLY"; SPECIES="BINOMIAL FORMAT"; DB_GENEINFO="DATABASE:ASSEMBLY:ACCESSION:name"; band=""; db_transcriptinfo="DATABASE:ASSEMBLY:ACCESSION:name"; transcript_start=""; analysis_name=""; db_tfinfo="DATABASE:ASSEMBLY:ACCESSION:NAME"; method=""; evidence=""; pmid=""; expression="CELL:SPECIES:time:time_scale"; impaired_mutant="";</p>
<p class="title2">Description:</p>
<p><span class="title4">Mandatory Fields</span><br>
<b>seqname</b> - The name of the sequence. Must be a chromosome.<br>
<b>source</b> - The project to store this feature in.<br>
<b>feature</b> - The name of this feature or '.'.<br>
<b>start</b> - The starting position of the feature in the sequence. The first base is numbered 1.<br>
<b>end</b> - The ending position of the feature (inclusive).<br>
<b>score</b> - No need here. If there is no score value, enter ".".<br>
<b>strand</b> - Valid entries include '+', '-', or '.' (for don't know/don't care).<br>
<b>frame</b> - No need here.The value should be '.'.<br></p>
<p><span class="title4">Mandatory Attributes</span><br>
<b>sequence=</b>"";<br>
<b>db_seqinfo=</b>"database:assembly";<br>
<b>species=</b>""; #binomial format (Homo sapiens, Mus musculus,Danio rerio,...)<br>
<b>db_geneinfo=</b>"database:assembly:accession:name"; #the database can be either of the following:EnsEMBL, Entrez Gene, RefSeq, SwissProt, Genbank. Last part (gene name) optional.<br>
</p>
<p><span class="title4">Optional Attributes</span><br>
<b>band=</b>"";<br>
<b>db_transcriptinfo=</b>"database:assembly:accession:name"; #the database can be either of the following:EnsEMBL, RefSeq, SwissProt, Genbank. Last part (isoform name) optional.<br>
<b>transcript_start=</b>"";<br>
<b>analysis_name=</b>"";<br>
<b>db_tfinfo=</b>"database:assembly:accession:name";<br>
<b>method=</b>"";<br>
<b>evidence=</b>""; #should be either curated or prediction<br>
<b>pmid=</b>"";<br>
<b>expression=</b>"cell:species:time:time_scale"; #time info is optional but if specified, the time_scale is required (secondes, hours, days,...)<br>
<b>impaired_mutant=</b>"sequence"; #the format of the sequence should be lowercase where the original sequence remains and uppercase for the mutated nucleotides. If the mutation is a deletion use 'N' where the original nucleotides were.<br></p>
<p class="title2">Examples:</p>
<p><span class="title4">Interaction example</span><br>
chr7	oreganno_example	OREG0000056	99037559	99037584	.	-	.	sequence="gcatcaagaacatgtggttctaatgg"; db_seqinfo="EnsEMBL:NCBI 35"; species="Homo sapiens"; db_geneinfo="EntrezGene:1576:CYP3A4"; band="q22.1"; analysis_name="gff_example1"; db_tfinfo="EnsEMBL:ENST00000289790:USF1"; method="EMSA_analysis"; evidence="curated"; pmid="14742674"; impaired_mutant="gcatcaagaacatTAggttctaatgg"
<br></p>
<p><span class="title4">Expression example</span><br>
chr7	oreganno_example	OREG0000056	99037559	99037584	.	-	.	sequence="gcatcaagaacatgtggttctaatgg"; db_seqinfo="EnsEMBL:NCBI 35"; species="Homo sapiens"; db_geneinfo="EntrezGene:1576:CYP3A4"; band="q22.1"; analysis_name="gff_example2"; expression="HepG2:Homo sapiens"; method="gene reporter assay"; evidence="curated"; pmid="14742674"; impaired_mutant="gcatcaagaacatTAggttctaatgg"
<br></p>
      <br>          
page

# print out the html tail template
my $template_tail = HTML::Template->new(filename => 'tail.tmpl');
print $template_tail->output;
