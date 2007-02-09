#!/usr/bin/perl

use HTML::Template;

# open the html header template
my $template = HTML::Template->new(filename => 'header.tmpl');

# fill in template parameters
$template->param(TITLE => 'PAZAR Project Outline');

# send the obligatory Content-Type and print the template output
print "Content-Type: text/html\n\n", $template->output;

print<<page;
          <p class="title1">PAZAR - FAQ</p>
<p class="title3">FAQ TOPICS</p>

<ul type=disc>
 <li><span style='font-family:
     Verdana'><a href="#SEQUENCERETRIEVAL">SEQUENCE RETRIEVAL</a></span></li>
</ul>

<ul type=disc>
 <li><span style='font-family:
     Verdana'><a href="#SEQUENCEENTRY">SEQUENCE ENTRY</a></span></li>
</ul>

<ul type=disc>
 <li><span style='font-family:
     Verdana'><a href="#EXPERIMENTALNOMENCLATURE">EXPERIMENTAL NOMENCLATURE</a></span></li>
</ul>

<ul type=disc>
 <li><span style='font-family:
     Verdana'><a href="#PAZARUSERINTERFACE">PAZAR USER INTERFACE</a></span></li>
</ul>

<p class="title3">CONSTRUCTING A SEQUENCE-SPECIFIC PAZAR RECORD</p>
<ul type=disc>
 <li><span style='font-family:
     Verdana'>Review all of the relevant papers that are available for a given
     sequence</span></li>
 <li><span style='font-family:
     Verdana'>Select the overall DNA sequence which includes all of the regions
     thought to be involved in gene expression regulation</span></li>
 <li><span style='font-family:
     Verdana'>Make note of all of the data that pertains to that specific
     sequence</span></li>
 <li><span style='font-family:
     Verdana'>Create additional records for subregions, if there is data to support
     it (ie. EMSA in which the probe is just the putative binding site of
     interest)</span></li>
</ul>
<p class="title3">PAZAR User Interface Screenshots </p>

<p>&nbsp;<a
href="http://www.pazar.info/images/PAZAR_Screenshots_100406.pdf">PAZAR
Screenshots (10-04-06)</a></p>

<hr>
<p class="title3">FAQ TOPICS</p>

<p class="bold"><a name='SEQUENCERETRIEVAL'></a>SEQUENCE
RETRIEVAL</p>

<table class='summarytable'>
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

<p class="bold"><a name=SEQUENCEENTRY></a><SEQUENCE ENTRY </p>

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
  src="http://pazar.info/images/FAQ-Figure.gif"> </span></p>
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

<p class="bold"><a name=EXPERIMENTALNOMENCLATURE></a>EXPERIMENTAL
NOMENCLATURE </p>

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
   <p><span style='font-family:Verdana'>For entering a DNA-binding experiment in
  which nuclear extract was used, what should be entered in the section
  "If the experiment is not in vitro, enter the cell/tissue information
  below" since there is already cell line information fields at the top of
  the page?  </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>Currently, within PAZAR there is a
  duplication of the cell type submission interface. All cell type information
  should be entered into only the first copy of the cell type submission
  interface found near the top of the window. </span></p>
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
  be recorded as a "TF/complex" or as an "Interaction with Unknown Factor (ie. nuclear extract)?   
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
</table>

<p class="bold"><a name=PAZARUSERINTERFACE></a>PAZAR USER INTERFACE </p>

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
my $template_tail = HTML::Template->new(filename => 'tail.tmpl');
print $template_tail->output;
