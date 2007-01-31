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
  <p><span style='font-family:Verdana'>If there are two
  transcripts with the same sequence, but one is missing one base at the very
  end, does it matter which one we choose?  </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>NO  </span></p>
  </td>
 </tr>
  <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>Can restriction fragment
  data be used to obtain a DNA sequence referenced in a paper, in the presence
  of only minimal identifying sequence information (ie. the identity of one
  basepair)?  <br>
   </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>Yes. Download a portion
  of the genomic sequence which encompasses the restriction sites described in
  the paper. Then, conduct a restriction fragment analysis of the sequence, and
  see if the restriction map matches the description given in the paper. <br>
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
   <p><span style='font-family:Verdana'>If the same sequence is
  found in 2 or more species, do we make a separate entry for each?  </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>Yes, create a separate
  entry for each.  </span></p>
  </td>
 </tr>
  <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>Given this example
  (using the same promoter sequence): <img border=0 width=250
  src="http://pazar.info/images/FAQ-example1.PNG"> </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>Create a separate
  sequence entry for each long sequence from the 2 papers, because cannot
  compare experiment from paper 2 to paper 1 due to use of different cells and
  reporters (there is no way to compare activity of mutants 2 &amp; 3 to wt
  sequence)  </span></p>
  </td>
 </tr>
  <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>How should main page
  data be saved for a sequence for which there is no experimental evidence?  </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>In the case in which
  there is no experimental evidence for a sequence, clicking the
  &quot;Done&quot; button at the bottom of the main page will save all data
  entered to the database. This would otherwise occur automatically upon the
  opening of the &quot;experimental evidence&quot;.  </span></p>
  </td>
 </tr>
  <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>How do I enter TFs from
  different species?  </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>Add the species in the
  front of the TF name eg) Mouse_Phox2a, Human_Phox2a  </span></p>
  </td>
 </tr>
  <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>Does case matter when
  entering a sequence in PAZAR?  </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>Yes. If a sequence is
  entered in both upper and lower case, it will not be found. It should be
  entered either in all upper or lower case.  </span></p>
  </td>
 </tr>
  <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>Should a regulatory
  sequence be entered into PAZAR if it is transfected into cells upstream of
  the complete gene sequence?  <br>
   </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>Yes. This can be entered
  under the category &quot;transient transfection gene expression assay&quot;. <br>
   </span></p>
  </td>
 </tr>
  <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>Should 3' regulatory
  element data (ie. elements within the 3' UTR of the gene) be entered into
  PAZAR?  <br>
   </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>Yes. We are interested
  in any regulatory elements whether they are upstream or downstream of a gene.
   <br>
   </span></p>
  </td>
 </tr>
  <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>PAZAR is having
  difficulties with the name of a sequence. <br>
   </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>There are certain
  characters that are not recognized by PAZAR, such as the single quote ('). Choose
  another name without this character for now. <br>
   </span></p>
  </td>
 </tr>
  <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>How do we name
  complexes?  </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>ie. HUMAN_RXR/RAR unless
  the complex has a specific name, separate components by slash <br>
   </span></p>
  </td>
 </tr>
  <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>Refer to PMID 9099914:
  This construct contains a single 8 bp Xho linker in the place of the deleted
  internal 4 bp in the CRE 5'-TG<em><span style='font-family:Verdana'>ACGT</span></em>CA-3'.
  How to enter this as a mutation in Pazar?  </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>In this case, since the
  length of the inserted sequence is greater than the length of the deleted
  sequence, you can't enter this as a mutation. So, the best thing to do is to
  delete the 4 bases as a mutation, and enter the insertion of the RE site in
  the comments.  <br>
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
   <p><span style='font-family:Verdana'>How should the
  expression level of sequence mutants be expressed?  </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>Changes in expression
  associated with sequence mutants should be expressed relative to the
  expression of the wild-type sequence.  </span></p>
  </td>
 </tr>
  <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>Should drug treatments
  be documented in PAZAR and if so, where?  </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>Drug treatments can be
  inserted into the conditions field as a part of a PAZAR record.  </span></p>
  </td>
 </tr>
  <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>What does the comment
  &quot;NA&quot; mean in the effects column of the gene summary?  </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>It means that the
  qualitative effect of the experimental evidence in not attributed and that
  only the quantitative effect was added.  </span></p>
  </td>
 </tr>
  <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>What if there are
  multiple cell lines for the same experiment?  </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>If the results are the
  same for each cell line, you can include only a neuronal one. You can enter
  some of the others in the comments section. If results are different, you
  should include all the cell lines that contain important information.  </span></p>
  </td>
 </tr>
  <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>For entering a nuclear
  extract experiment, what do we put under the section &quot;If the experiment
  is not in vitro, enter the cell/tissue information below&quot; since there is
  already cell line information fields at the top of the page?  </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>just ignore the &quot;If
  the experiment is not in vitro, enter the cell/tissue information below&quot;
  field for now, and enter your cell line info at the top. We need to ask
  Elodie about this.  </span></p>
  </td>
 </tr>
  <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>What do we put under
  &quot;Sample Type&quot;, first field of nuclear extract page?  </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>nuclear extract, or
  whatever the sample is. Another example would be cellular extract.  </span></p>
  </td>
 </tr>
  <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>If wild-type and mutant
  transcripts are tested in various cell lines, should separate experiments be
  made for each?  </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>NO. Create an
  experimental record for one cell line, and then include a message for all
  other cell lines in the comment box on either the experimental record page,
  or each of the mutant pages if there are significant differences between
  mutants.  </span></p>
  </td>
 </tr>
  <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>There is a supershift
  experiment with a nuclear extract. Should the factor to which to antibody is
  attached be recorded as a &quot;TF/complex binding to this CRE&quot; or as a
  &quot;Interaction with Unknown Factor (ie. nuclear extract)&quot;? (because
  the experiment doesn't show that the TF is binding the DNA directly).  </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>Put it as a
  &quot;TF/complex binding to this CRE&quot; because we want the sequence to be
  linked to this TF in the database. Then in the comments of the experiment,
  make sure to mention that its from a nuclear extract.  </span></p>
  </td>
 </tr>
  <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>What should be entered
  for the transcription factor name if in a Supershift assay, a paper states
  that antibody recognized a protein family, and not just a single protein? <br>
   </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>Enter the most common
  member of the protein family as the transcription factor, but include in the
  comments that the antibody was not specific to that protein but instead
  recognized the protein family in general. <br>
   </span></p>
  </td>
 </tr>
  <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>Say there is an
  experiment (ie. deletion assay) with a perturbation condition (TF or
  chemical, etc), but it is not comparative (ie. no results are given for the
  experiment without presence of the perturbation). How to imput this in Pazar?
   </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>Add the experiment, and
  in the initial page where you specify the experiment type (ie. Luc reporter
  assay) and the cell type, pubmed id, expression level etc. leave the
  expression level at NA. Then, you get to the page where you can enter the
  perturbation - do so, add your mutated sequences and report the expression
  levels from there.  </span></p>
  </td>
 </tr>
  <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>If, when a mutant of a
  given sequence is subjected to a perturbation, there is a change of expression
  relative to the mutant without the perturbation, what should be the point of
  reference for describing the change that the perturbation has had on
  expression for that mutant?  </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>The change in expression
  associated with the mutant in the presence of the perturbation should be
  expressed relative to the expression level of the wild-type in the presence
  of the perturbation.  <br>
   </span></p>
  </td>
 </tr>
  <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>How do we interpret
  interaction levels for gel shift competition experiments? <br>
   </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>Level of interaction is
  good if the probe competed. If add a mutant probe, level of interaction is
  poor if the probe does not compete.  </span></p>
  </td>
 </tr>
 <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>When entering a mutation
  that causes no binding, what do you indicate for &quot;Effect of this
  mutation on the interaction&quot;? <br>
   </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>You can chooses
  &quot;None&quot;. In this case, &quot;None&quot; means no binding, not no
  effect on the interaction level. <br>
   </span></p>
  </td>
 </tr>
 <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>If I am annotating a TF
  that regulates a Pleiades gene, do I add experiments showing its role in
  transcription transactivation to PAZAR (ie. as a permutation in a
  transactivation entry)?  </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>Yes. Even though this
  information cannot be viewed currently from the TF summary page, it is
  important to have this supporting evidence. Elodie will change the summary
  view in the future to be able to display this data.  </span></p>
  </td>
 </tr>
 <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>Do I also include this
  information if the role of the TF is repression of transcription from a given
  sequence?  </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>Yes.  </span></p>
  </td>
 </tr>
 <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>How do we annotate a
  supershift experiment that causes a disappearance of the band, rather than a
  supershift? (because the Ab interferes with the DNA-binding ability of the
  protein).  <br>
   </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>Just put the method as
  supershift, and in the comments mention the band disappearance as opposed to
  shift  </span></p>
  </td>
 </tr>
 <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>If a transactivation
  experiment is repeated exactly in another paper, with the exception that a
  different permutation was added, how do I enter this into PAZAR?  </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>Enter it as a new
  experiment, since the PMIDs will be different. <br>
   </span></p>
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
   <p><span style='font-family:Verdana'>Why do I get the same
  line of evidence entered twice?  </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>You hit submit twice in
  the evidence page.&nbsp; If you hit the back button on your browser, make
  sure you use the forward button to carry on and do not hit submit again.  </span></p>
  </td>
 </tr>
  <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>Why are my comments from
  the evidence page not showing up on the gene summary page?  </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>The gene summary display
  needs to be updated, and will display that information in the future.  </span></p>
  </td>
 </tr>
  <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>When I enter an
  experiment with multiple mutations, how come only the base sequence and its
  induction level show up in the gene summary page?  </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>The gene summary display
  needs to be updated, and will display that information in the future.  </span></p>
  </td>
 </tr>
  <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>How come when I search
  for a gene in a project from the mall, the experimental evidence doesn't show
  up?  </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>You have to go to the
  search page and search by Gene (<a
  href="http://www.pazar.info/cgi-bin/gsearch.pl"
  title="Visit page outside Confluence">http://www.pazar.info/cgi-bin/gsearch.pl</a>)
  because the display features are under construction.  </span></p>
  </td>
 </tr>
  <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>Is there a spot to enter
  mutation information in the &quot;interaction evidence with unknown
  factor&quot; page?  </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>Yes, once you've
  submitted the evidence and hit the submit button, you will be asked if you
  have any mutants to add.  </span></p>
  </td>
 </tr>
  <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>is the nuclear extract
  info supposed to be displaying when you look at the gene's evidence page?  </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>no. Elodie will fix
  that. you may want her to check that it is in the database  </span></p>
  </td>
 </tr>
  <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>Why aren't experimental
  conditions (ie. presence of chemical) showing up in the display page?  </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>That hasn't been
  implemented yet.  </span></p>
  </td>
 </tr>
  <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>&quot;The vanishing
  window syndrome&quot;: trying to view the gene list when an evidence window
  is open will result in the gene list opening up in the evidence window. <br>
   </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>Open the gene list in
  another browser until issue is solved. <br>
   </span></p>
  </td>
 </tr>
 <tr>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>When entering a complex
  with a TF that is already in PAZAR, how do we add this TF to the
  complex?&nbsp;  <br>
   </span></p>
  </td>
   <td class='basictd'>
   <p><span style='font-family:Verdana'>You must re-enter in the
  information for this TF, as the complex entry will be completely seperate
  from the individual TF entries.  </span></p>
  </td>
 </tr>
</table>


page


# print out the html tail template
my $template_tail = HTML::Template->new(filename => 'tail.tmpl');
print $template_tail->output;
