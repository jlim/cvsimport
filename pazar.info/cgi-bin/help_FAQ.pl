#!/usr/bin/perl

use HTML::Template;

my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};

# open the html header template
my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");

# fill in template parameters
$template->param(TITLE => 'PAZAR Help');
$template->param(PAZAR_HTML => $pazar_html);
$template->param(PAZAR_CGI => $pazar_cgi);

# send the obligatory Content-Type and print the template output
print "Content-Type: text/html\n\n", $template->output;

print<<page;

<p class="title1">PAZAR - Help</p>
<hr color='black'>
<p class="title2">Content</p>
<a href="#What is PAZAR?"><span class="title3">What is PAZAR?</span><br></a>
<a href="#Tutorials"><span class="title3">Tutorials</span><br></a>
<a href="#Definitions"><span class="title3">PAZAR Definitions</span><br></a>
<a href="#PAZAR Search Interface"><span class="title3">PAZAR Search Interface</span><br></a>
<a href="#1. PAZAR Mall Overview"><span class="title4 margin">1. PAZAR Mall Overview</span><br></a>
<a href="#2. Search by Gene"><span class="title4 margin">2. Search by Gene</span><br></a>
<a href="#2.1 Introduction"><span class="bold margin2">2.1. Introduction</span><br></a>
<a href="#2.2 Gene identifiers"><span class="bold margin2">2.2 Gene identifiers</span><br></a>
<a href="#2.3 Gene View"><span class="bold margin2">2.3 Gene View</span><br></a>
<a href="#2.4 Sequence View"><span class="bold margin2">2.4 Sequence View</span><br></a>
<a href="#2.5 Analysis View"><span class="bold margin2">2.5 Analysis View</span><br></a>
<a href="#3. Search by Transcription Factor"><span class="title4 margin">3. Search by Transcription Factor</span><br></a>
<a href="#3.1 Introduction"><span class="bold margin2">3.1. Introduction</span><br></a>
<a href="#3.2 TF identifiers"><span class="bold margin2">3.2 TF identifiers</span><br></a>
<a href="#3.3 TF View"><span class="bold margin2">3.3 TF View</span><br></a>
<a href="#3.4 Position Frequency Matrix and Binding Profile"><span class="bold margin2">3.4 Position Frequency Matrix and Binding Profile</span><br></a>
<a href="#4. Search by Transcription Factor Binding Profile"><span class="title4 margin">4. Search by Transcription Factor Binding Profile</span><br></a>
<a href="#5. Search within a specific Boutique Project"><span class="title4 margin">5. Search within a specific Boutique Project</span><br></a>
<a href="#PAZAR Submission Interface"><span class="title3">PAZAR Submission Interface</span><br></a>
<a href="#1. Introduction"><span class="title4 margin">1. Introduction</span></a><br>
<a href="#Screenshots"><span class="title4 margin">2. Submission Interface Screenshots</span><br></a>
<a href='#FAQ Topics'><span class="title4 margin">3. Frequently Asked Questions</span></a><br>
<span class="bold margin2"><a href="#Sequence Retrieval">Sequence Retrieval</a></span><br>
<span class="bold margin2"><a href="#Sequence Entry">Sequence Entry</a></span><br>
<span class="bold margin2"><a href="#Experimental Nomenclature">Experimental Nomenclature</a></span><br>
<span class="bold margin2"><a href="#Submission Interface">Submission Interface</a></span><br>
<hr color='black'>
<a name="What is PAZAR?"></a><p class="title3">What is PAZAR?</p>
 <ul type=disc><li>A software framework for the construction and maintenance of regulatory sequence data annotations which allows multiple boutique databases to function independently within a larger system (or information mall). For more information, see the <a href="$pazar_cgi/overview.pl">Overview</a> section.</li></ul>

<a name="Tutorials"></a><p class="title3">Tutorials</p>
 <ul type=disc><li>Mall Overview and Introduction:  <a href="$pazar_html/tutorials/Overview.htm" target='tutwin' onClick="window.open('about:blank','tutwin');">Overview Tutorial</a>  (2 min)</li></ul>
 <ul type=disc><li>Search by Gene:  <a href="$pazar_html/tutorials/Gene.htm" target='tutwin' onClick="window.open('about:blank','tutwin');">Gene Search Tutorial</a>  (2:27 min)</li></ul>
 <ul type=disc><li>Search by Transcription Factor:  <a href="$pazar_html/tutorials/tf.htm" target='tutwin' onClick="window.open('about:blank','tutwin');">TF Search Tutorial</a>  (3:02 min)</li></ul>
 <ul type=disc><li>Search by Transcription Factor Binding Profile:  <a href="$pazar_html/tutorials/TF_Binding_Profile_Search.htm" target='tutwin' onClick="window.open('about:blank','tutwin');">TF Profile Search Tutorial</a>  (0:54 min)</li></ul>
 <ul type=disc><li>Search within a specific Boutique Project:  <a href="$pazar_html/tutorials/boutique.htm" target='tutwin' onClick="window.open('about:blank','tutwin');">Boutique Search Tutorial</a>  (1:02 min)</li></ul>

<a name="Definitions"></a><p class="title3">PAZAR Definitions</p>
 <ul type=disc><li><a name="TFcomplexDef"></a><b>Transcription Factor Complex:</b></li></ul>
<p>In PAZAR, all Trancription Factors (TFs) are defined as complexes, a complex comprising from one to any number of individual proteins. This allows users to define different binding specificities for the same TF protein depending on if it acts as a monomer (one protein instance), a monodimer (two identical proteins bound together) or an heterodimer (two different proteins bound together). Thus, when submitting a new TF in PAZAR, the annotator is first asked to give a name to the complex (the name should reflect all proteins present in the complex). Then he will have to define each protein included in the complex (also called subunit) one after the other by providing at least their gene identifier, then clicking on 'Add more TFs to this complex'.</p>
<a name="PAZAR Search Interface"></a><p class="title3">PAZAR Search Interface</p>
<a name="1. PAZAR Mall Overview"></a><p class="title4 margin">1. PAZAR Mall Overview</p>
<p>The PAZAR Mall is the graphic user interface for the PAZAR database. Boutique datasets within PAZAR are represented by stores within the mall. In addition, the mall has six separate floors that are accessible via the escalator. Boutique datasets can be made public or private as is needed, and all boutique datasets are listed in the mall directory found at the bottom of the page.<br>
Three general query types can be conducted within PAZAR. 
Users can search PAZAR by gene, by TF, or by TF-binding profile simply by clicking on their corresponding department stores found at the ends of the mall. A more in-depth discussion of each of these search types may be found in the search type specific tutorials. While each of these queries will consider all of the public data within PAZAR, queries of specific boutique datasets can also be performed by clicking on their corresponding stores or their names listed in the mall directory found at the bottom of the page. PAZAR contact information is accessible via the information booth, found at the centre of the mall. In addition, links to other relevant internet sources, and PAZAR export formats are accessible via buttons found at the far left of the PAZAR main page.</p>
<p><a href="$pazar_html/tutorials/Overview.htm" target='tutwin' onClick="window.open('about:blank','tutwin');">Mall Overview and Introduction Tutorial</a>  (2 min)</p>
<a name="2. Search by Gene"></a><p class="title4 margin">2. Search by Gene</p>
<a name="2.1 Introduction"></a><p class="bold margin2">2.1. Introduction</p>
<p>In order to search PAZAR by gene, click on the 'Genes' department store at the upper right corner of the mall. This causes a query window to appear. Here, users have multiple options for their gene-specific query. Users can view the list of all genes in PAZAR for a given boutique database by clicking on the 'View Gene List' button. Alternatively, users can search for a specific gene within all of PAZAR based upon several gene-specific identifiers.</p>
<p><a href="$pazar_html/tutorials/Gene.htm" target='tutwin' onClick="window.open('about:blank','tutwin');">Gene Search Tutorial</a>  (2:27 min)</p>
<a name="2.2 Gene identifiers"></a><p class="bold margin2">2.2 Gene identifiers</p>
<p><b><u>User Defined Gene Name:</u> </b><font color='red'>(eg. GFAP)</font><br>
Gene symbol as defined by the user. We do not automatically use official symbols as they vary across species. The results will display all entries containing the provided subset of characters.<br>
<b><u>EnsEMBL gene ID:</u> </b><font color='red'>(eg. ENSG00000131095)</font><br>
EnsEMBL stable gene ID. This is the reference ID in PAZAR, thus the one to use preferentially.<br>
<b><u>EnsEMBL transcript ID:</u> </b><font color='red'>(eg. ENST00000253408)</font><br>
EnsEMBL stable transcript ID. This ID will be converted to an EnsEMBL gene ID first.<br>
<b><u>Entrezgene ID:</u> </b><font color='red'>(eg. 2670)</font><br>
NCBI Entrez Gene ID. This ID will be converted to an EnsEMBL gene ID first.<br>
<b><u>RefSeq ID:</u> </b><font color='red'>(eg. NM_002055)</font><br>
Refseq DNA ID. Do not use the ID that includes the version at the end (NM_002055.2). This ID will be converted to an EnsEMBL gene ID first.<br>
<b><u>Swissprot ID:</u> </b><font color='red'>(eg. Q9UFD0)</font><br>
UniProtKB/Swiss-Prot ID.  This ID will be converted to an EnsEMBL gene ID first.<br>
<b><u>PAZAR Gene ID:</u> </b><font color='red'>(eg. GS0000217</font>)<br>
PAZAR Gene IDs are unique to a project. Therefore, the same gene (same EnsEMBL Gene ID) will have different PAZAR Gene IDs if annotated in different projects. Use EnsEMBL Gene IDs to get all data about a gene across projects.<br>
<b><u>PAZAR Sequence ID:</u> </b><font color='red'>(eg. RS0000226)</font><br>
Providing a PAZAR Sequence ID will directly open the Sequence View for this particular sequence.</p>
<a name="2.3 Gene View"></a><p class="bold margin2">2.3 Gene View</p>
<p>At the top of the Gene View page is a summary table of all of the genes obtained from the search. By clicking on the magnifying glass next to the PAZAR gene ID, users will be taken directly to the specific data for their gene of interest. Within this section, users find a gene-specific summary table followed by a list of all of the PAZAR regulatory sequences that correspond to that gene. Users can visualize the genomic context of each regulatory sequence by clicking on the links to the UCSC Genome Browser and Ensembl found at the far right of the page. Also, by clicking on the regulatory sequence ID for a specific regulatory sequence, found in the far left column, users can access the PAZAR Sequence view for that sequence.</p>
<a name="2.4 Sequence View"></a><p class="bold margin2">2.4 Sequence View</p>
<p>In this view, data is color-coded, with gene-specific information presented in blue and sequence-specific data in orange. A gene-specific summary table is presented at the top of the page followed by a table of statistics pertaining to the specific regulatory sequence of interest. A third table summarizing the supporting experimental data for this regulatory sequence is also present at the bottom of the page. Clicking on the Analysis ID found in the leftmost column of this table takes users to the PAZAR Analysis View.</p>
<a name="2.5 Analysis View"></a><p class="bold margin2">2.5 Analysis View</p>
<p>The Analysis View is color-coded green. Within this view is a more in-depth description of the supporting experimental data.</p>
<a name="3. Search by Transcription Factor"></a><p class="title4 margin">3. Search by Transcription Factor</p>
<a name="3.1 Introduction"></a><p class="bold margin2">3.1. Introduction</p>
<p>To search PAZAR by TF, click on the 'TFMART' department store found at the left hand side of the mall. This causes a query window to appear. Users can view the list of all TFs in PAZAR for a given boutique database by clicking on the 'View TF List' button. Alternatively, users can search for a specific TF within all of PAZAR based upon several TF-specific identifiers.</p>
<p><a href="$pazar_html/tutorials/tf.htm" target='tutwin' onClick="window.open('about:blank','tutwin');">TF Search Tutorial</a>  (3:02 min)</p>
<a name="3.2 TF identifiers"></a><p class="bold margin2">3.2 TF identifiers</p>
<p><b><u>User Defined TF Name:</u> </b><font color='red'>(eg. NF1)</font><br>
TF name as defined by the user. We will be using soon a controlled vocabulary to replace this free text. The results will display all entries containing the provided subset of characters.<br>
<b><u>EnsEMBL gene ID:</u> </b><font color='red'>(eg. ENSG00000162599)</font><br>
EnsEMBL stable gene ID. This ID will be converted to the corresponding EnsEMBL transcript IDs first.<br>
<b><u>EnsEMBL transcript ID:</u> </b><font color='red'>(eg. ENST00000294608)</font><br>
EnsEMBL stable transcript ID. This is the reference ID for TFs in PAZAR, thus the one to use preferentially.<br>
<b><u>Entrezgene ID:</u> </b><font color='red'>(eg. 4774)</font><br>
NCBI Entrez Gene ID. This ID will be converted to an EnsEMBL gene ID first.<br>
<b><u>RefSeq ID:</u> </b><font color='red'>(eg. NM_005595)</font><br>
Refseq DNA ID. Do not use the ID that includes the version at the end (NM_005595.1). This ID will be converted to an EnsEMBL gene ID first.<br>
<b><u>Swissprot ID:</u> </b><font color='red'>(eg. Q12857)</font><br>
UniProtKB/Swiss-Prot ID.  This ID will be converted to an EnsEMBL gene ID first.<br>
<b><u>PAZAR TF ID:</u> </b><font color='red'>(eg. TF0000231</font>)<br>
PAZAR TF IDs are unique to a project. Therefore, the same TF (same EnsEMBL Gene ID) will have different PAZAR TF IDs if annotated in different projects. Use EnsEMBL Gene IDs to get all data about a TF across projects.</p>
<a name="3.3 TF View"></a><p class="bold margin2">3.3 TF View</p>
<p>At the top of the TF View is a summary table of all of the TFs obtained from the search. By clicking on the magnifying glass next to the PAZAR TF ID, users will be taken directly to the specific data for their TF of interest. Within this section, users find a TF-specific summary table followed by a list of all of the PAZAR regulatory sequences that are bound by that TF. Users can visualize the genomic context of each regulatory sequence by clicking on the links to the UCSC Genome Browser and Ensembl found at the far right of the page. Also, by clicking on a regulatory sequence ID or a gene ID, users can access the PAZAR Sequence or Gene view respectively. In addition, a position frequency scoring matrix and transcription factor binding profile are generated dynamically using the MEME software for each transcription factor. Users can construct a custom scoring matrix and binding profile based upon a subset of the sequences for that TF by clicking in the check boxes of those sequences meant to be included and clicking 'Generate PFM with selected sequences'. Alternatively, users can generate scoring matrices and binding profiles based upon just genomic or artificial sequences by clicking on 'Select genomic sequences' or 'Select artificial sequences' respectively. As well, users can generate a custom scoring matrix and binding profile based upon selected sequences from any of the transcription factors displayed on the page by clicking 'Generate PFM' at the very bottom of the page.</p>
<a name="3.4 Position Frequency Matrix and Binding Profile"></a><p class="bold margin2">3.4 Position Frequency Matrix and Sequence logo Generation</p>
<p>Based on an alignment of all known sites, the total number of observations of each nucleotide is recorded for each position, producing a Position Frequency Matrix (PFM). The sequence logo scales each nucleotide by the total bits of information multiplied by the relative occurence of the nucleotide at the position. Sequence logos enable fast and intuitive visual assessment of pattern characterics.<br>In PAZAR, PFMs and Logos are produced by using the probabilistic motif discovery algorithm MEME (see reference below).<br>
Timothy L. Bailey and Charles Elkan, "Fitting a mixture model by expectation maximization to discover motifs in biopolymers", Proceedings of the Second International Conference on Intelligent Systems for Molecular Biology, pp. 28-36, AAAI Press, Menlo Park, California, 1994.</p>
<a name="4. Search by Transcription Factor Binding Profile"></a><p class="title4 margin">4. Search by Transcription Factor Binding Profile</p>
<p>To search PAZAR by transcription factor binding profile, click on the 'TF PROFILES' department store found near to the bottom of the mall. This will cause a query window to appear. Users can retrieve TF binding profiles sorted by their associated project, name, species, or class by clicking on the corresponding buttons found near to the middle of the query page. On the PAZAR TF Binding Profile view, users are provided with a summary table with specific data for each transcription factor. Clicking 'More', found at the right hand side of the screen causes a secondary window to appear with even more detailed information regarding that specific transcription factor. The binding profiles in PAZAR are dynamically generated using the MEME software.</p>
<p><a href="$pazar_html/tutorials/TF_Binding_Profile_Search.htm" target='tutwin' onClick="window.open('about:blank','tutwin');">TF Profile Search Tutorial</a>  (0:54 min)</p>
<a name="5. Search within a specific Boutique Project"></a><p class="title4 margin">5. Search within a specific Boutique Project</p>
<p>One might desire to limit queries to a single collection. To do so, the user must find the corresponding boutique in the mall map or directory and click on it. The 'Project View' provides a brief description of the dataset as well as some statistics on the data it contains. Below, the user can choose amongst various filters to search through the data and display it in the 'Gene View', where regulatory sequences will be grouped by the genes they regulate, or in the 'TF View', where the sequences are grouped by the TFs that bind to them.</p>
<p><a href="$pazar_html/tutorials/boutique.htm" target='tutwin' onClick="window.open('about:blank','tutwin');">Boutique Search Tutorial</a>  (1:02 min)</p>
<a name="PAZAR Submission Interface"></a><p class="title3">PAZAR Submission Interface</p>
<a name="1. Introduction"></a><p class="title4 margin">1. Introduction</p>
<p> To enter data into PAZAR please follow those steps:<br>
<ul type=disc><li>Register under the <a href="$pazar_cgi/register.pl">Register</a> section.</li></ul>
<ul type=disc><li>Click on <a href="$pazar_cgi/editprojects.pl">My Projects</a> to see all the projects you belong to and to create new ones.</li></ul>
<ul type=disc><li>Click on <a href="$pazar_cgi/sWI/entry.pl">Submit</a> to enter new data. For more detailed questions on the submission interface, see the FAQ topics</a> section below.</li></ul>
<ul type=disc><li>If one has a pre-existing dataset, an automated data import can be realized upon contacting the PAZAR development team.</li></ul></p>
<a name='Screenshots'></a><p class="title4 margin">2. Submission Interface Screenshots</p>
<a href="$pazar_html/images/PAZAR_Screenshots_100406.pdf">Screenshots (10-04-06)</a>
<a name="FAQ Topics"></a><p class="title4 margin">3. Frequently Asked Questions</p>
<a name="Sequence Retrieval"></a><p class="bold margin2">Sequence Retrieval</p><table class='summarytable'>
 <tr>
  <td class='basictd'>
  <p><span style='font-family:Verdana'><b>Question</b></span></p>
  </td>
  <td class='basictd'>
  <p><span style='font-family:Verdana'><b>Response</b></span></p>
  </td>
 </tr>
 <tr>
  <td class='basictd'>
  <p><span style='font-family:Verdana'>If two transcripts varying by only 1 or
  2 bases could potentially be used for a given PAZAR record, does it matter
  which is chosen?  </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>Either can be used for the PAZAR record
  with the inclusion of a comment if necessary.</span></p>
  </td>
 </tr>
  <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>How can restriction fragment data be
  used to isolate a DNA sequence referenced in a paper?  <br>
   </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>Download a portion of the genomic
  sequence which encompasses the restriction sites described in the paper.
  Then, conduct a restriction fragment analysis of the sequence, and see if the
  restriction map matches the description given in the paper. <br>
   </span></p>
  </td>
 </tr>
</table>
<a name='Sequence Entry'></a><p class="bold margin2">Sequence Entry</p>
<table class='summarytable'>
  <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'><b>Question</b>  </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'><b>Response</b>  </span></p>
  </td>
 </tr>
  <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>If the same sequence is found in 2 or more
  species, should each be given a separate entry in PAZAR?  </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>Yes, Create a separate record for each
  species.  </span></p>
  </td>
 </tr>
  <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>If an identical genomic sequence is used
  in "identical" transient transfection expression assays in 2 or more papers, can mutants of that sequence from both
  papers be submitted to PAZAR as a part of a single experimental assay? <img border=0 width=350
  src="$pazar_html/images/FAQ-Figure.gif"> </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>Definitely not. One cannot compare and
  combine experimental data from separate papers in a single assay. Even if the
  design of the experiment is the same between papers, it was performed using
  different cells, reporters, conditions, etc. As a result, there is no way
  that the expression level of mutants from separate papers can be compared to
  that of the wild-type sequence in a single experimental assay. Instead, create
  a separate experimental assay for each of the papers, associated with the
  shared wild-type sequence.  </span></p>
  </td>
 </tr>
  <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>How can main page data be saved for a
  genomic sequence with no experimental evidence?  </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>By clicking the "Done" button
  at the bottom of the main page, all data entered will be saved to PAZAR. This
  would otherwise occur automatically upon opening an "Experimental
  Evidence" window. </span></p>
  </td>
 </tr>
  <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>What nomenclature should be used when
  entering TFs from different species?  </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>Enter the TF name as follows: Species_TFName (ie. Mouse_Phox2a, Human_Phox2a)  </span></p>
  </td>
 </tr>
 <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>Should elements within the 3' UTR of a
  gene be entered into PAZAR?  <br>
   </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>Definitely. We are interested in any
  regulatory elements whether they are upstream or downstream of a gene.
   <br>
   </span></p>
  </td>
 </tr>
  <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>What could be the problem if PAZAR does
  not permit a certain sequence name to be used? <br>
   </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>There are certain characters that are
  not recognized by PAZAR, such as the single quote ('). By selecting a name
  without such characters, problems will be averted. <br>
   </span></p>
  </td>
 </tr>
  <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>How are complexes named within PAZAR?  </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>Enter complex names as follows:
  Species_Protein1/Protein 2/etc.(ie. HUMAN_RXR/RAR). If a complex is given a specific name other than the simple combination
  of its components, use Species_specificcomplexname.<br>
   </span></p>
  </td>
 </tr>
  <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>Can insertion mutations be documented in
  PAZAR?  </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>Not yet. This is a feature that will be
  incorporated into the PAZAR submission interface in the near future.   <br>
   </span></p>
  </td>
 </tr>
</table>
<a name='Experimental Nomenclature'></a><p class="bold margin2">Experimental Nomenclature</p>
<table class='summarytable'>
  <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'><b>Question</b>  </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'><b>Response</b>  </span></p>
  </td>
 </tr>
  <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>What should be used as the point of
  reference when describing the expression level of sequence mutants?  </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>Changes in expression associated with
  sequence mutants should be expressed relative to the expression of the
  wild-type sequence.  </span></p>
  </td>
 </tr>
  <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>Can drug treatments be documented in
  PAZAR?  </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>For expression assays in which a
  wild-type sequence is tested for levels of expression in the presence or
  absence of a chemical compound, transcription factor, etc. the drug should be
  included in the record as a perturbation. In contrast, for all DNA-binding
  assays drug treatments or transcription factor co-expression should be
  described in the comment field.  </span></p>
  </td>
 </tr>
  <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>What is signified by the presence of "NA" in the 
effects column of the gene summary? </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>The presence of "NA" in the
  effects column of the gene summary suggests that the qualitative effect of
  the experimental evidence was not defined in the supporting publication. This
  option is often used when submitting transgenic mouse data to PAZAR. In such
  a case, the primary outcome examined is whether a given construct has been
  able to reconstitute wild-type patterns of expression. Nothing however can be
  said regarding the levels of expression present in the mice, making it
  necessary to use "NA".  </span></p>
  </td>
 </tr>
  <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>If there are multiple cell lines/cell types 
used for the same experiment, which should be submitted to PAZAR?  </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>If the results are the same for each
  cell line, only the most relevant cell line (ie. neuronal cell lines) should be 
  explicitly selected for the PAZAR submission.Any other cell lines that are deemed 
  relevant can be included in the comments section. If results differ between cell lines, 
  separate experimental assays should be submitted to PAZAR for each cell line associated 
  with informative data.  </span></p>
  </td>
 </tr>
  <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>What are potential choices for the
  "Sample Type" field on the nuclear extract page?  </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>Currently choices for sample type
  include nuclear extract, cellular extract, or even whole cell extract if
  applicable.  </span></p>
  </td>
 </tr>
  <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>Given the situation in which there is a supershift
  experiment performed using a nuclear extract should the factor to which the antibody binds 
  be recorded as a "TF/complex" or as an "Interaction with Unknown Factor (ie. nuclear extract)"?   
</span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>This type of an experiment does not
  prove that a TF is interacting directly with a cis-regulatory element (CRE). 
  It could be interacting with the CRE via any other protein
  from the nuclear extract. However, in the interest of linking the CRE to this
  TF within PAZAR, consider it to be a "TF/complex binding to this
  CRE". However, make sure to also mention that the protein was from a
  nuclear extract in the comments section of the record.  </span></p>
  </td>
 </tr>
  <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>What should be entered for a
  transcription factor name if in a Supershift assay,
  a paper states that an antibody recognized a protein family, and not just a
  single protein? <br>
   </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>Enter the most common member of the
  protein family as the transcription factor, but include in the comments that
  the antibody was not specific to that protein but instead recognized the
  protein family in general. <br>
   </span></p>
  </td>
 </tr>
  <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>How should an experiment with a
  perturbation (TF or chemical, etc) be submitted to PAZAR if there are no
  results provided for the experiment in the absence of the perturbation??
   </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>On the main experimental assay page,
  select "NA" for the wild-type expression level in the absence of
  perturbation. Then, enter the perturbation with its associated level of
  expression. Add mutants in a similar fashion.  </span></p>
  </td>
 </tr>
  <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>What should be the point of reference
  used for describing the level of expression associated with a mutant subject
  to a perturbation?  </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>Describe the expression level of the
  mutant with perturbation relative to the expression level of the wild-type
  with perturbation.  <br>
   </span></p>
  </td>
 </tr>
  <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>How do we qualitatively interpret the
  interaction level for gel shift competition experiments? <br>
   </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>A probe successfully able to eliminate a
  band shift involving wild-type probe is considered to be a good interactor. If the probe 
  (wild-type or mutant) is not able to compete away the initial interaction, it is considered 
  to be a poor interactor.  </span></p>
  </td>
 </tr>
 <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>When entering a mutation that leads to a
  complete elimination of binding, what should be indicated for the
  "Effect of this mutation on the interaction"? <br>
   </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>In this situation "None"
  should be chosen for the level of interaction. Do note that in this context,
  "None" means no binding, not "no effect on binding". <br>
   </span></p>
  </td>
 </tr>
 <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>In the annotation of a transcription
  factor that regulates a Pleiades Promoter Project gene, should experiments
  demonstrating a role in transcriptional regulation (ie. Coexpression of the TF 
  leads to transactivation) be submitted to PAZAR?  </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>This data should definitely be included
  as a perturbation in a PAZAR submission. Even though this information cannot
  be viewed currently from the TF summary page, it is important to have this
  supporting evidence. The summary view will be modified in the future in order
  to include this type of information. Even if coexpression of a TF leads to 
  repression of gene expression, the data should be submitted to PAZAR. </span></p>
  </td>
 </tr>
 <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>How should a "supershift"
  experiment in which incubation with antibody leads to the disappearance of a
  band be entered into PAZAR (ie. Interfering with binding instead of retarding mobility)?  <br>
   </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>Put the method in as a supershift,
  but in the comments also mention that the band did not shift to lower
  mobility but instead disappeared. </span></p>
  </td>
 </tr>
<tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>How should one verify whether a transcription factor (TF) is already present in PAZAR prior to submission?  <br>
   </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>Prior to submitting a new TF to PAZAR, conduct a search within PAZAR using the ENSEMBL ID for that TF. If the TF is present, it will be linked to that ENSEMBL ID and will be retrieved. Also, by convention use the HUGO gene name for all human TFs, or for other species, the Entrez Gene ID.</span></p>
  </td>
 </tr>
</table>
<a name='Submission Interface'></a><p class="bold margin2">Submission Interface</p>
<table class='summarytable'>
  <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'><b>Question</b>  </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'><b>Response</b>  </span></p>
  </td>
 </tr>
  <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>The same line of evidence appears twice
  for a given sequence submitted to PAZAR? What could have caused this problem?  </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>This is what results from clicking
  "submit" twice on the evidence submission page. </span></p>
  </td>
 </tr>
  <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>Where can mutation information submitted within the 
  "interaction evidence with unknown factor" page?  </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>Once the "interaction evidence with
  unknown factor" page is filled out and the submit button pressed, an
  option to add mutants is provided.  </span></p>
  </td>
 </tr>
 <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>How should a TF complex including a TF
  already present in PAZAR be submitted?  <br>
   </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>The information for this TF should be newly
  entered, even though it is already present in PAZAR. This is due to the fact
  that complex records exist independently of single TF records within PAZAR.  </span></p>
  </td>
 </tr>
</table>

page




# print out the html tail template
my $template_tail = HTML::Template->new(filename => "$pazarcgipath/tail.tmpl");
print $template_tail->output;
