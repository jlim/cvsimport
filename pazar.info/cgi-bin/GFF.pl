#!/usr/bin/perl

use HTML::Template;

my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};

# open the html header template
my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");

# fill in template parameters
$template->param(TITLE => 'PAZAR GFF format');
$template->param(PAZAR_HTML => $pazar_html);
$template->param(PAZAR_CGI => $pazar_cgi);

# send the obligatory Content-Type and print the template output
print "Content-Type: text/html\n\n", $template->output;

print<<page;
          <p class="title1">PAZAR - GFF format</p>
<p class="title2">Overview:</p>
<p>The PAZAR GFF format (<a href="http://www.sanger.ac.uk/Software/formats/GFF/" target="_blank">What is GFF?</a>) is intended to capture simple annotations. It is not meant to record a detailed annotation. Please use the XML format if you want more options.
One record is on a unique line and holds one annotation for one sequence, this annotation coming either from an interaction OR an expression experiment (NOT BOTH IN THE SAME RECORD). The record is stored as an interaction if db_tfinfo is provided. If you want to record an interaction but the factor is unknown, state db_tfinfo="unknown". If db_tfinfo is not provided, the record will be stored as an expression. An interaction will be stored as 'good' and an expression as 'induced'. If you want to record a specific expression level, use the expression field. If a mutant sequence is reported it is assumed that this mutant has an impaired activity compared to the annotation of the original sequence (interaction = 'none' or expression = 'no change').</p>
<p class="title2">PAZAR GFF format:</p>
<p class="bold">Fields are: &lt;seqname&gt;&nbsp; &lt;source&gt;&nbsp; &lt;feature&gt;&nbsp; &lt;start&gt&nbsp; &lt;end&gt;&nbsp; &lt;score&gt;&nbsp; &lt;strand&gt;&nbsp; &lt;frame&gt;&nbsp; [attributes]</p>
<p>Those 9 fields are tab-delimited.<br>
The attribute field must have a tag value structure with the following syntax, flattened onto one line by semicolon separators:<br>
tag1="value1";tag2="value2"</p>
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
<b>sequence=</b>""; # eg. "ATTTGTAGGAGTGAGTCAGCTGACCCGC"<br>
<b>db_seqinfo=</b>"database:assembly"; # eg. "EnsEMBL:NCBI 35"<br>
<b>species=</b>""; # binomial format (Homo sapiens, Mus musculus,Danio rerio,...)<br>
<b>db_geneinfo=</b>"database:accession:name"; # eg. "EnsEMBL_gene:ENSG00000133256:PDE6B"<br>The database can be either of the following:EnsEMBL Gene, Entrez Gene, RefSeq, SwissProt. Last part (gene name) optional.<br>
</p>
<p><span class="title4">Optional Attributes</span><br>
<b>band=</b>""; # eg. "p16.3"<br>
<b>db_transcriptinfo=</b>"database:accession:name"; # eg. "EnsEMBL_transcript:ENST00000255622"<br>The database can be either of the following:EnsEMBL Transcript, RefSeq, SwissProt. Last part (isoform name) optional.<br>
<b>transcript_start=</b>""; # eg. "609373"<br>
<b>analysis_name=</b>""; # eg. "gff_example1"<br><span class='red'>Note:</span> Please ensure that you provide the same analysis name to all records belonging to the same experiment.<br>
<b>analysis_comment=</b>""; # eg. "some comment on the experiment"<br><span class='red'>Note:</span> Please ensure that you provide the same analysis comment to all records belonging to the same experiment.<br>
<b>db_tfinfo=</b>"database:accession:name"; # eg. "EnsEMBL_transcript:ENST00000250471:NRL"<br>The database can be either of the following:EnsEMBL Transcript, RefSeq, SwissProt.<br><span class='red'>Note:</span> The record is stored as an interaction if db_tfinfo is provided. If you want to record an interaction but the factor is unknown, state db_tfinfo="unknown". If db_tfinfo is not provided, the record will be stored as an expression.<br>
<b>method=</b>""; # eg. "SELEX"<br>
<b>evidence=</b>""; # should be either "curated" or "prediction"<br>
<b>pmid=</b>""; # eg. "15264535"<br>
<b>cell_type</b>="cell:species"; # eg. "HepG2:Homo sapiens" Last part (species) optional.<br>
<b>expression=</b>"level:scale"; # eg. "56:percent"<br>Use this field if you want to record a specific expression level. If not used, an expression experiment is stored as 'induced'.<br>
<b>impaired_mutant=</b>"sequence"; # The format of the sequence should be lowercase where the original sequence remains and uppercase for the mutated nucleotides. If the mutation is a deletion use 'N' where the original nucleotides were.<br></p>
<p class="title2">Examples:</p>
<p><span class="title4">Interaction example</span><br>
chr7	oreganno_example	OREG0000056	99037559	99037584	.	-	.	sequence="gcatcaagaacatgtggttctaatgg"; db_seqinfo="EnsEMBL:NCBI 35"; species="Homo sapiens"; db_geneinfo="EntrezGene:1576:CYP3A4"; band="q22.1"; analysis_name="gff_example1"; db_tfinfo="EnsEMBL Transcript:ENST00000289790:USF1"; method="EMSA_analysis"; evidence="curated"; pmid="14742674"; impaired_mutant="gcatcaagaacatTAggttctaatgg"
<br></p>
<p><span class="title4">Expression example</span><br>
chr7	oreganno_example	OREG0000056	99037559	99037584	.	-	.	sequence="gcatcaagaacatgtggttctaatgg"; db_seqinfo="EnsEMBL:NCBI 35"; species="Homo sapiens"; db_geneinfo="EntrezGene:1576:CYP3A4"; band="q22.1"; analysis_name="gff_example2"; cell_type="HepG2:Homo sapiens"; method="gene reporter assay"; evidence="curated"; pmid="14742674"; impaired_mutant="gcatcaagaacatTAggttctaatgg"
<br></p>
      <br>          
page

# print out the html tail template
my $template_tail = HTML::Template->new(filename => "$pazarcgipath/tail.tmpl");
print $template_tail->output;
