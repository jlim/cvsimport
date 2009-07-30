#!/usr/bin/perl

use HTML::Template;
my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};

my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");
my $temptail = HTML::Template->new(filename => "$pazarcgipath/tail.tmpl");
$template->param(TITLE => "Help | PAZAR");
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
<h1>Help</h1>
<h2>Content</h2>
<div class="p20lo">
	<div class="b"><a href="#What is PAZAR?">What is PAZAR?</a></div>
	<div class="b"><a href="#Tutorials">Tutorials</a></div>
	<div class="b"><a href="#Definitions">Definitions</a></div>
	<div class="b"><a href="#PAZAR Search Interface">Search interface</a></div>
	<div class="b p10lo"><a href="#1. PAZAR Mall Overview">1. PAZAR Mall Overview</a></div>
	<div class="b p10lo"><a href="#2. Search by Gene">2. Search by Gene</a></div>
	<div class="p20lo"><a href="#2.1 Introduction">2.1. Introduction</a></div>
	<div class="p20lo"><a href="#2.2 Gene identifiers">2.2 Gene identifiers</a></div>
	<div class="p20lo"><a href="#2.3 Gene View">2.3 Gene View</a></div>
	<div class="p20lo"><a href="#2.4 Sequence View">2.4 Sequence View</a></div>
	<div class="p20lo"><a href="#2.5 Analysis View">2.5 Analysis View</a></div>
	<div class="b p10lo"><a href="#3. Search by Transcription Factor">3. Search by Transcription Factor</a></div>
	<div class="p20lo"><a href="#3.1 Introduction">3.1. Introduction</a></div>
	<div class="p20lo"><a href="#3.2 TF identifiers">3.2 TF identifiers</a></div>
	<div class="p20lo"><a href="#3.3 TF View">3.3 TF View</a></div>
	<div class="p20lo"><a href="#3.4 Position Frequency Matrix and Binding Profile">3.4 Position Frequency Matrix and Binding Profile</a></div>
	<div class="b p10lo"><a href="#4. Search by Transcription Factor Binding Profile">4. Search by Transcription Factor Binding Profile</a></div>
	<div class="b p10lo"><a href="#5. Search within a specific Boutique Project">5. Search within a specific Boutique Project</a></div>
	<div class="b"><a href="#PAZAR Submission Interface">PAZAR Submission Interface</a></div>
	<div class="b p10lo"><a href="#1. Introduction">1. Introduction</a></div>
	<div class="b p10lo"><a href="#Screenshots">2. Submission Interface Screenshots</a></div>
	<div class="b p10lo"><a href='#FAQ Topics'>3. Frequently Asked Questions</a></div>
	<div class="p20lo"><a href="#Sequence Retrieval">Sequence Retrieval</a></div>
	<div class="p20lo"><a href="#Sequence Entry">Sequence Entry</a></div>
	<div class="p20lo"><a href="#Experimental Nomenclature">Experimental Nomenclature</a></div>
	<div class="p20lo"><a href="#Submission Interface">Submission Interface</a></div>
</div>

<h2><a name="What is PAZAR?"></a>What is PAZAR?</h2>
<p>PAZAR is a software framework for the construction and maintenance of regulatory sequence data annotations which allows multiple boutique databases to function independently within a larger system (or information mall). For more information, see the <a href="$pazar_cgi/overview.pl">Overview</a> section.</p>


<h2><a name="Tutorials"></a>Tutorials</h2>
<ul>
	<li><a href="$pazar_html/tutorials/Overview.htm" target="_blank">Mall overview and introduction</a> (2:00 minutes)</li>
	<li><a href="$pazar_html/tutorials/Gene.htm" target="_blank">Search for regulated genes</a> (2:27 minutes)</li>
	<li><a href="$pazar_html/tutorials/tf.htm" target="_blank">Search for transcription factors</a> (3:02 minutes)</li>
	<li><a href="$pazar_html/tutorials/TF_Binding_Profile_Search.htm" target="_blank">Search by transcription factor binding profiles</a> (0:54 minutes)</li>
	<li><a href="$pazar_html/tutorials/boutique.htm" target="_blank">Search within a specific boutique project</a> (1:02 minutes)</li>
</ul>


<h2><a name="Definitions"></a>Definitions</h2>
<ul>
	<li><a name="TFcomplexDef"></a><span class="b">Transcription factor complex</span> &mdash; In PAZAR, all trancription factors (TFs) are defined as complexes, each complex being comprised of one or more individual proteins. This allows users to define different binding specificities for the same TF protein, depending on whether it acts as a monomer (one protein), a homodimer (two identical proteins bound together), a heterodimer (two different proteins bound together), <span class="i">etc</span>. Thus, when submitting a new TF in PAZAR, the annotator is first asked to give a name to the complex (the name should reflect all proteins present in the complex). Then each protein included in the complex (also called subunit) needs to be defined one after the other by providing at least its gene identifier, then clicking on "Add more TFs to this complex". If the complex is comprised of only one TF or subunit, then no more TFs need to be added to the complex.</li>
</ul>


<h2><a name="PAZAR Search Interface"></a>Search interface</h2>

<h3><a name="1. PAZAR Mall Overview"></a>1. PAZAR mall overview</h3>
<div class="p20lo">
	<p>The PAZAR Mall is the graphic user interface for the PAZAR database. Boutique datasets within PAZAR are represented by stores within the mall. In addition, the mall has six separate floors that are accessible via the escalator. Boutique datasets can be made public or private as is needed, and all boutique datasets are listed in the mall directory found at the bottom of the page.</p>
	<p>Three general query types can be conducted within PAZAR. Users can search PAZAR by gene, by TF, or by TF-binding profile simply by clicking on their corresponding department stores found at the ends of the mall. A more in-depth discussion of each of these search types may be found in the search type specific tutorials. While each of these queries will consider all of the public data within PAZAR, queries of specific boutique datasets can also be performed by clicking on their corresponding stores or their names listed in the mall directory found at the bottom of the page. PAZAR contact information is accessible via the information booth, found at the centre of the mall. In addition, links to other relevant internet sources, and PAZAR export formats are accessible via buttons found at the far left of the PAZAR main page.</p>
	<p><a href="$pazar_html/tutorials/Overview.htm" target="_blank" class="b">View the mall overview and introduction tutorial</a> (2 minutes)</p>
</div>
<h3><a name="2. Search by Gene"></a>2. Search by gene</h3>
<div class="p20lo">
	<h4><a name="2.1 Introduction"></a>2.1. Introduction</h4>
	<p>In order to search PAZAR by gene, click on the 'Genes' department store at the upper right corner of the mall. This causes a query window to appear. Here, users have multiple options for their gene-specific query. Users can view the list of all genes in PAZAR for a given boutique database by clicking on the 'View Gene List' button. Alternatively, users can search for a specific gene within all of PAZAR based upon several gene-specific identifiers.</p>
	<p><a href="$pazar_html/tutorials/Gene.htm" target="_blank" class="b">view the gene search tutorial</a>  (2:27 minutes)</p>
	<h4><a name="2.2 Gene identifiers"></a>2.2. Gene identifiers</h4>
	<ul>
		<li><p class="b">User-defined gene name</p>
			<ul><li><span class="i">i.e.</span> <span class="b">GFAP</span></li>
			<li>Gene symbol as defined by the user. We do not automatically use official symbols as they vary across species. The results will display all entries containing the provided subset of characters.</li></ul></li>
		<li><p class="b">Ensembl gene ID</p>
			<ul><li><span class="i">i.e.</span> <span class="b">ENSG00000131095</span></li>
			<li>the Ensembl stable gene ID. This is the reference ID in PAZAR, thus the one to use preferentially.</li></ul></li>
		<li><p class="b">Ensembl transcript ID</p>
			<ul><li><span class="i">i.e.</span> <span class="b">ENST00000253408</span></li>
			<li>Ensembl stable transcript ID. This ID will be converted to an Ensembl gene ID first.</li></ul></li>
		<li><p class="b">Entrez Gene ID</p>
			<ul><li><span class="i">i.e.</span> <span class="b">2670</span></li>
			<li>NCBI Entrez Gene ID. This ID will be converted to an Ensembl gene ID first.</li></ul></li>
		<li><p class="b">Refseq ID</p>
			<ul><li><span class="i">i.e.</span> <span class="b">NM_002055</span></li>
			<li>Refseq DNA ID. Do not include the version at the end (NM_002055.2). This ID will be converted to an Ensembl gene ID.</li></ul></li>
		<li><p class="b">Swissprot ID</p>
			<ul><li><span class="i">i.e.</span> <span class="b">Q9UFD0</span></li>
			<li>UniProtKB/Swiss-Prot ID.  This ID will be converted to an Ensembl gene ID first.</li></ul></li>
		<li><p class="b">PAZAR gene ID</p>
			<ul><li><span class="i">i.e.</span> <span class="b">GS0000217</span></li>
			<li>PAZAR Gene IDs are unique to a project. Therefore, the same gene (same Ensembl Gene ID) will have different PAZAR Gene IDs if annotated in different projects. Use Ensembl Gene IDs to get all data about a gene across projects.</li></ul></li>
		<li><p class="b">PAZAR sequence ID</p>
			<ul><li><span class="i">i.e.</span> <span class="b">RS0000226</span></li>
			<li>Providing a PAZAR Sequence ID will directly open the Sequence View for this particular sequence.</li></ul></li>
	</ul>

	<h4><a name="2.3 Gene View"></a>2.3. Gene View</h4>
	<p>At the top of the Gene View page is a summary table of all of the genes obtained from the search. By clicking on the magnifying glass next to the PAZAR gene ID, users will be taken directly to the specific data for their gene of interest. Within this section, users find a gene-specific summary table followed by a list of all of the PAZAR regulatory sequences that correspond to that gene. Users can visualize the genomic context of each regulatory sequence by clicking on the links to the UCSC Genome Browser and Ensembl found at the far right of the page. Also, by clicking on the regulatory sequence ID for a specific regulatory sequence, found in the far left column, users can access the PAZAR Sequence view for that sequence.</p>

	<h4><a name="2.4 Sequence View"></a>2.4. Sequence View</h4>
	<p>In this view, data is color-coded, with gene-specific information presented in blue and sequence-specific data in orange. A gene-specific summary table is presented at the top of the page followed by a table of statistics pertaining to the specific regulatory sequence of interest. A third table summarizing the supporting experimental data for this regulatory sequence is also present at the bottom of the page. Clicking on the Analysis ID found in the leftmost column of this table takes users to the PAZAR Analysis View.</p>

	<h4><a name="2.5 Analysis View"></a>2.5. Analysis View</h4>
	<p>The Analysis View is color-coded green. Within this view is a more in-depth description of the supporting experimental data.</p>
</div>

<h3><a name="3. Search by Transcription Factor"></a>3. Search by Transcription Factor</h3>
<div class="p20lo">
	<h4><a name="3.1 Introduction"></a>3.1. Introduction</h4>
	<p>To search PAZAR by TF, click on the 'TFMART' department store found at the left hand side of the mall. This causes a query window to appear. Users can view the list of all TFs in PAZAR for a given boutique database by clicking on the 'View TF List' button. Alternatively, users can search for a specific TF within all of PAZAR based upon several TF-specific identifiers.</p>
	<p><a href="$pazar_html/tutorials/tf.htm" target="_blank" class="b">View the TF search tutorial</a> (3:02 minutes)</p>

	<h4><a name="3.2 TF identifiers"></a>3.2. TF identifiers</h4>
	<ul>
		<li><p class="b">User-defined TF name</p>
			<ul><li><span class="i">i.e.</span> <span class="b">NF1</span></li>
			<li>TF name as defined by the user. We will be using soon a controlled vocabulary to replace this free text. The results will display all entries containing the provided subset of characters.</li></ul></li>
		<li><p class="b">Ensembl gene ID</p>
			<ul><li><span class="i">i.e.</span> <span class="b">ENSG00000162599</span></li>
			<li>Ensembl stable gene ID. This ID will be converted to the corresponding Ensembl transcript IDs first.</li></ul></li>
		<li><p class="b">Ensembl transcript ID</p>
			<ul><li><span class="i">i.e.</span> <span class="b">ENST00000294608</span></li>
			<li>Ensembl stable transcript ID. This is the reference ID for TFs in PAZAR, thus the one to use preferentially.</li></ul></li>
		<li><p class="b">Entrez Gene ID</p>
			<ul><li><span class="i">i.e.</span> <span class="b">4774</span></li>
			<li>NCBI Entrez Gene ID. This ID will be converted to an Ensembl gene ID first.</li></ul></li>
		<li><p class="b">Refseq ID</p>
			<ul><li><span class="i">i.e.</span> <span class="b">NM_005595</span></li>
			<li>Refseq DNA ID. Do not include the version at the end (NM_005595.1). This ID will be converted to an Ensembl gene ID first.</li></ul></li>
		<li><p class="b">Swissprot ID</p>
			<ul><li><span class="i">i.e.</span> <span class="b">Q12857</span></li>
			<li>UniProtKB/Swiss-Prot ID.  This ID will be converted to an Ensembl gene ID first.</li></ul></li>
		<li><p class="b">PAZAR TF ID</p>
			<ul><li><span class="i">i.e.</span> <span class="b">TF0000231</span></li>
			<li>PAZAR TF IDs are unique to a project. Therefore, the same TF (same Ensembl Gene ID) will have different PAZAR TF IDs if annotated in different projects. Use Ensembl Gene IDs to get all data about a TF across projects.</li></ul></li>
	</ul>

	<h4><a name="3.3 TF View"></a>3.3. TF view</h4>
	<p>At the top of the TF View is a summary table of all of the TFs obtained from the search. By clicking on the magnifying glass next to the PAZAR TF ID, users will be taken directly to the specific data for their TF of interest. Within this section, users find a TF-specific summary table followed by a list of all of the PAZAR regulatory sequences that are bound by that TF. Users can visualize the genomic context of each regulatory sequence by clicking on the links to the UCSC Genome Browser and Ensembl found at the far right of the page. Also, by clicking on a regulatory sequence ID or a gene ID, users can access the PAZAR Sequence or Gene view respectively. In addition, a position frequency scoring matrix and transcription factor binding profile are generated dynamically using the MEME software for each transcription factor. Users can construct a custom scoring matrix and binding profile based upon a subset of the sequences for that TF by clicking in the check boxes of those sequences meant to be included and clicking 'Generate PFM with selected sequences'. Alternatively, users can generate scoring matrices and binding profiles based upon just genomic or artificial sequences by clicking on 'Select genomic sequences' or 'Select artificial sequences' respectively. As well, users can generate a custom scoring matrix and binding profile based upon selected sequences from any of the transcription factors displayed on the page by clicking 'Generate PFM' at the very bottom of the page.</p>

	<h4><a name="3.4 Position Frequency Matrix and Binding Profile"></a>3.4. Position frequency matrix and sequence logo generation</h4>
	<p>Based on an alignment of all known sites, the total number of observations of each nucleotide is recorded for each position, producing a Position Frequency Matrix (PFM). The sequence logo scales each nucleotide by the total bits of information multiplied by the relative occurence of the nucleotide at the position. Sequence logos enable fast and intuitive visual assessment of pattern characterics.<br>In PAZAR, PFMs and Logos are produced by using the probabilistic motif discovery algorithm MEME (see reference below).</p>
	<div class="p5bo"><div class="p10 bg-lg">Timothy L. Bailey and Charles Elkan. <span class="b">Fitting a mixture model by expectation maximization to discover motifs in biopolymers.</span> Proceedings of the Second International Conference on Intelligent Systems for Molecular Biology, pp. 28-36, AAAI Press, Menlo Park, California, 1994.</div></div>
</div>

<h3><a name="4. Search by Transcription Factor Binding Profile"></a>4. Search by transcription factor binding profile</h3>
<div class="p20lo">
	<p>To search PAZAR by transcription factor binding profile, click on the 'TF PROFILES' department store found near to the bottom of the mall. This will cause a query window to appear. Users can retrieve TF binding profiles sorted by their associated project, name, species, or class by clicking on the corresponding buttons found near to the middle of the query page. On the PAZAR TF Binding Profile view, users are provided with a summary table with specific data for each transcription factor. Clicking 'More', found at the right hand side of the screen causes a secondary window to appear with even more detailed information regarding that specific transcription factor. The binding profiles in PAZAR are dynamically generated using the MEME software.</p>
	<p><a href="$pazar_html/tutorials/TF_Binding_Profile_Search.htm" target="_blank" class="b">View the TF profile search tutorial</a> (0:54 minutes)</p>
</div>

<h3><a name="5. Search within a specific Boutique Project"></a>5. Search within a specific boutique project</h3>
<div class="p20lo">
	<p>One might desire to limit queries to a single collection. To do so, the user must find the corresponding boutique in the mall map or directory and click on it. The 'Project View' provides a brief description of the dataset as well as some statistics on the data it contains. Below, the user can choose amongst various filters to search through the data and display it in the 'Gene View', where regulatory sequences will be grouped by the genes they regulate, or in the 'TF View', where the sequences are grouped by the TFs that bind to them.</p>
	<p><a href="$pazar_html/tutorials/boutique.htm" target="_blank" class="b">View the boutique search tutorial</a> (1:02 minutes)</p>
</div>

<h2><a name="PAZAR Submission Interface"></a>PAZAR submission interface</h2>

<h3><a name="1. Introduction"></a>1. Introduction</h3>
<div class="p20lo">
	<p>To enter data into PAZAR please follow those steps:</p>
	<ul>
		<li>Register at the <a href="$pazar_cgi/register.pl">register</a> page.</li>
		<li>Click on <a href="$pazar_cgi/editprojects.pl">my projects</a> to see all the projects you belong to and to create new ones.</li>
		<li>Click on <a href="$pazar_cgi/sWI/entry.pl">submit</a> to enter new data. For more detailed questions on the submission interface, see the FAQ topics</a> section below.</li>
		<li>If one has a pre-existing dataset, an automated data import can be realized upon contacting the PAZAR development team.</li>
	</ul>
</div>
<h3><a name='Screenshots'></a>2. Submission interface screenshots</h3>
<div class="p20lo">
	<a href="$pazar_html/images/PAZAR_Screenshots_100406.pdf">View the screenshots (10-04-06)</a>
</div>
<h3><a name="FAQ Topics"></a>3. Frequently asked questions</h3>
<div class="p20lo">
	<h4><a name="Sequence Retrieval"></a>Sequence Retrieval</h4>
	<ul>
		<li><span class="b">Q: if two transcripts varying by only 1 or 2 bases could potentially be used for a given PAZAR record, does it matter which is chosen?</span> A: Either can be used for the PAZAR record with the inclusion of a comment if necessary.</li>
		<li><span class="b">Q: how can restriction fragment data be used to isolate a DNA sequence referenced in a paper?</span> A: download a portion of the genomic sequence which encompasses the restriction sites described in the paper. Then, conduct a restriction fragment analysis of the sequence, and see if the restriction map matches the description given in the paper.</li>
	</ul>
	<h4><a name='Sequence Entry'></a>Sequence entry</h4>
	<ul>
		<li><span class="b">Q: if the same sequence is found in 2 or more species, should each be given a separate entry in PAZAR?</span> A: yes, Create a separate record for each species.</li>
		<li><div class="float-r p10lo p10bo"><img border="0" width="350" src="$pazar_html/images/FAQ-Figure.gif" alt=""></div><span class="b">Q: if an identical genomic sequence is used in "identical" transient transfection expression assays in 2 or more papers, can mutants of that sequence from both papers be submitted to PAZAR as a part of a single experimental assay?</span> A: definitely not. One cannot compare and combine experimental data from separate papers in a single assay. Even if the design of the experiment is the same between papers, it was performed using different cells, reporters, conditions, etc. As a result, there is no way that the expression level of mutants from separate papers can be compared to that of the wild-type sequence in a single experimental assay. Instead, create a separate experimental assay for each of the papers, associated with the shared wild-type sequence.</li>
		<li><span class="b">Q: how can main page data be saved for a genomic sequence with no experimental evidence?</span> A: by clicking the "Done" button at the bottom of the main page, all data entered will be saved to PAZAR. This would otherwise occur automatically upon opening an "Experimental Evidence" window.</li>
		<li><span class="b">Q: what nomenclature should be used when entering TFs from different species?</span> A: enter the TF name as follows: Species_TFName (ie. Mouse_Phox2a, Human_Phox2a)</li>
		<li><span class="b">Q: should elements within the 3' UTR of a gene be entered into PAZAR?</span> A: definitely. We are interested in any regulatory elements whether they are upstream or downstream of a gene.</li>
		<li><span class="b">Q: what could be the problem if PAZAR does not permit a certain sequence name to be used?</span> A: there are certain characters that are not recognized by PAZAR, such as the single quote ('). By selecting a name without such characters, problems will be averted.</li>
		<li><span class="b">Q: how are complexes named within PAZAR?</span> A: enter complex names as follows: Species_Protein1/Protein 2/etc.(ie. HUMAN_RXR/RAR). If a complex is given a specific name other than the simple combination of its components, use Species_specificcomplexname.</li>
		<li><span class="b">Q: can insertion mutations be documented in PAZAR?</span> A: not yet. This is a feature that will be incorporated into the PAZAR submission interface in the near future.</li>
	</ul>
	<h4><a name='Experimental Nomenclature'></a>Experimental nomenclature</h4>
	<ul>
		<li><span class="b">Q: what should be used as the point of reference when describing the expression level of sequence mutants?</span> A: changes in expression associated with sequence mutants should be expressed relative to the expression of the wild-type sequence.</li>
		<li><span class="b">Q: can drug treatments be documented in PAZAR?</span> A: for expression assays in which a wild-type sequence is tested for levels of expression in the presence or  absence of a chemical compound, transcription factor, etc. the drug should be included in the record as a perturbation. In contrast, for all DNA-binding assays drug treatments or transcription factor co-expression should be described in the comment field.</li>
		<li><span class="b">Q: what is signified by the presence of "NA" in the effects column of the gene summary?</span> A: the presence of "NA" in the effects column of the gene summary suggests that the qualitative effect of the experimental evidence was not defined in the supporting publication. This option is often used when submitting transgenic mouse data to PAZAR. In such a case, the primary outcome examined is whether a given construct has been able to reconstitute wild-type patterns of expression. Nothing however can be said regarding the levels of expression present in the mice, making it necessary to use "NA".</li>
		<li><span class="b">Q: if there are multiple cell lines/cell types used for the same experiment, which should be submitted to PAZAR?</span> A: if the results are the same for each cell line, only the most relevant cell line (i.e. neuronal cell lines) should be   explicitly selected for the PAZAR submission. Any other cell lines that are deemed relevant can be included in the comments section. If results differ between cell lines, separate experimental assays should be submitted to PAZAR for each cell line associated with informative data.</li>
		<li><span class="b">Q: what are potential choices for the "Sample Type" field on the nuclear extract page?</span> A: currently choices for sample type include nuclear extract, cellular extract, or even whole cell extract if applicable.
		<li><span class="b">Q: Given the situation in which there is a supershift experiment performed using a nuclear extract should the factor to which the antibody binds be recorded as a "TF/complex" or as an "Interaction with Unknown Factor (ie. nuclear extract)"?</span> A: this type of an experiment does not prove that a TF is interacting directly with a cis-regulatory element (CRE). It could be interacting with the CRE via any other protein from the nuclear extract. However, in the interest of linking the CRE to this TF within PAZAR, consider it to be a "TF/complex binding to this CRE". However, make sure to also mention that the protein was from a nuclear extract in the comments section of the record.</li>
		<li><span class="b">Q: what should be entered for a transcription factor name if in a Supershift assay, a paper states that an antibody recognized a protein family, and not just a single protein?</span> A: enter the most common member of the protein family as the transcription factor, but include in the comments that the antibody was not specific to that protein but instead recognized the protein family in general.</li>
		<li><span class="b">Q: how should an experiment with a perturbation (TF or chemical, etc) be submitted to PAZAR if there are no results provided for the experiment in the absence of the perturbation?</span> A: on the main experimental assay page, select "NA" for the wild-type expression level in the absence of perturbation. Then, enter the perturbation with its associated level of expression. Add mutants in a similar fashion.</li>
		<li><span class="b">Q: what should be the point of reference used for describing the level of expression associated with a mutant subject to a perturbation?</span> A: describe the expression level of the mutant with perturbation relative to the expression level of the wild-type with perturbation.</li>
		<li><span class="b">Q: how do we qualitatively interpret the interaction level for gel shift competition experiments?</span> A: a probe successfully able to eliminate a band shift involving wild-type probe is considered to be a good interactor. If the probe (wild-type or mutant) is not able to compete away the initial interaction, it is considered to be a poor interactor.</li>
		<li><span class="b">Q: when entering a mutation that leads to a complete elimination of binding, what should be indicated for the "Effect of this mutation on the interaction"?</span> A: in this situation "None" should be chosen for the level of interaction. Do note that in this context, "None" means no binding, not "no effect on binding".</li>
		<li><span class="b">Q: in the annotation of a transcription factor that regulates a Pleiades Promoter Project gene, should experiments demonstrating a role in transcriptional regulation (ie. Coexpression of the TF leads to transactivation) be submitted to PAZAR?</span> A: this data should definitely be included as a perturbation in a PAZAR submission. Even though this information cannot be viewed currently from the TF summary page, it is important to have this supporting evidence. The summary view will be modified in the future in order to include this type of information. Even if coexpression of a TF leads to repression of gene expression, the data should be submitted to PAZAR.</li>
		<li><span class="b">Q: wow should a "supershift" experiment in which incubation with antibody leads to the disappearance of a band be entered into PAZAR (i.e. interfering with binding instead of retarding mobility)?</span> A: put the method in as a supershift, but in the comments also mention that the band did not shift to lower mobility but instead disappeared.</li>
		<li><span class="b">Q: how should one verify whether a transcription factor (TF) is already present in PAZAR prior to submission?</span> A: prior to submitting a new TF to PAZAR, conduct a search within PAZAR using the ENSEMBL ID for that TF. If the TF is present, it will be linked to that ENSEMBL ID and will be retrieved. Also, by convention use the HUGO gene name for all human TFs, or for other species, the Entrez Gene ID.</li>
	</ul>
	<h4><a name='Submission Interface'></a>Submission interface</h4>
	<ul>
		<li><span class="b">Q: the same line of evidence appears twice for a given sequence submitted to PAZAR? What could have caused this problem?</span> A: this is what results from clicking "submit" twice on the evidence submission page.</li>
		<li><span class="b">Q: where can mutation information submitted within the "interaction evidence with unknown factor" page?</span> A: once the "interaction evidence with unknown factor" page is filled out and the submit button pressed, an option to add mutants is provided.</li>
		<li><span class="b">Q: how should a TF complex including a TF already present in PAZAR be submitted?</span> A: The information for this TF should be newly entered, even though it is already present in PAZAR. This is due to the fact that complex records exist independently of single TF records within PAZAR.</li>
	</ul>
</div>};

print $temptail->output;
