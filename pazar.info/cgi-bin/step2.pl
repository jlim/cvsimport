#!/usr/bin/perl

use HTML::Template;

my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};

# open the html header template
my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");

# fill in template parameters
$template->param(TITLE => 'PAZAR XML writing Step 2');
$template->param(PAZAR_HTML => $pazar_html);
$template->param(PAZAR_CGI => $pazar_cgi);

# send the obligatory Content-Type and print the template output
print "Content-Type: text/html\n\n", $template->output;

print<<page;
          <span class="title1">PAZAR - XML format</span><br>
          <span class="title2">Step-by-Step Documentation</span><br><br>
          <p class="title3"><a name="Step2_TOP"></a>Step2: Capturing the regulatory sequence and/or TF basic information</p>
      <div style="text-align: justify;">Once the project
element has been defined (<a href="$pazar_cgi/step1.pl">see Step 1</a>), you are ready to enter sequence
and transcription factor information. These will be entered within the
'data' element, which is a child element within the 'pazar' element.
      <br>
      <br>

      </div>

      <span style="margin-left: 0.5in; text-decoration: underline;">2.0-
Initialization<br>

      </span>
      <div style="text-align: justify;">The 'data' element
stores all the annotations separately. They will be linked together
later in the 'analysis' element (<a href="$pazar_cgi/step3.pl">see
Step 3</a>). <br>

First the 'data' element has to initialized:<br>

      <span style="font-weight: bold;"></span><br>

      <span style="font-weight: bold;"></span></div>

      <span style="font-weight: bold;">&nbsp;&nbsp;&lt;data&gt;</span><br>

      <span style="margin-left: 0.5in;"><br>

Then, different type of annotations can be inserted:<br>

      </span>
      <ul>

      </ul>

      <ol>

        <li><a href="#Regulatory_Sequence_for_specific_gene"><span>Regulatory
Sequence for a Specific Gene</span></a><span></span></li>

        <li><a href="#Regulatory_Sequence_without_gene_info"><span>Regulatory
Sequence without any gene information</span></a></li>

        <li><a href="#Transcription_Factor"><span>Transcription
Factor</span></a></li>

        <li><span><a href="#Artificial_sequence">Artificial
sequence/Sequence not attached
to genomic coordinates</a><br>

          </span></li>

      </ol>

      <ul>

      </ul>

      <span style="margin-left: 0.5in; text-decoration: underline;"><br style="text-decoration: underline;">

      </span><span style="margin-left: 0.5in; text-decoration: underline;"><a name="Regulatory_Sequence_for_specific_gene">2.1 -
Annotating a Regulatory Sequence for a Specific Gene</a></span><small><span style="margin-left: 0.1in;"> <a href="#Step2_TOP">TOP</a></span></small><span style="margin-left: 0.5in;"><br>

      </span>
      <div style="text-align: justify;"><span>The
'reg_seq' is embedded within '</span><span>tsr'</span><span>
and&nbsp;</span><span>'gene_source' elements.</span><span>
The 'gene_source' element informs about the gene accession number.</span>
The 'tsr' element describes the transcription start region based on the
observation that transcription does not always start at exactly the same
nucleotide (however, a unique start site can be described by inserting
the same value in fuzzy_start and fuzzy_end).<br>
Thus, if a gene has 2 alternative promoters, each of which can be
described with a different 'tsr' element within the 'gene_source'
element,&nbsp;different regulatory sequences can be associated with
each 'tsr'.<br>
      <br>
      </div>


      <span style="font-weight: bold;">&nbsp;&nbsp;&nbsp;
&lt;gene_source db_accn="<span style="color: rgb(255, 0, 0);">ENSG00000133256</span>"
description="<span style="color: rgb(255, 0, 0);">PDE6B</span>"
pazar_id="<span style="color: rgb(255, 0, 0);">gs_0001</span>"&gt;</span><br style="font-weight: bold;">

      <span style="font-weight: bold;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&lt;db_source db_name="<span style="color: rgb(255, 0, 0);">EnsEMBL</span>" assembly="<span style="color: rgb(255, 0, 0);">37_35j</span>"/&gt;</span><br style="font-weight: bold;">
      <span style="font-weight: bold;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&lt;tsr fuzzy_end="<span style="color: rgb(255, 0, 0);">609373</span>"
fuzzy_start="<span style="color: rgb(255, 0, 0);">609373</span>"
pazar_id="<span style="color: rgb(255, 0, 0);">tsr_0001</span>"&gt;</span><br style="font-weight: bold;">

      <span style="font-weight: bold;"></span><span style="font-weight: bold;"></span><span style="font-weight: bold;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&lt;reg_seq&nbsp;pazar_id="<span style="color: rgb(255, 0, 0);">rs_0001</span>"
quality="<span style="color: rgb(255, 0, 0);">tested</span>"
sequence="<span style="color: rgb(255, 0, 0);">ATTTGTAGGAGTGAGTCAGCTGACCCGC</span>"&gt;</span><br style="font-weight: bold;">

      <span style="font-weight: bold;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&lt;coordinate begin="<span style="color: rgb(255, 0, 0);">609283</span>"
end="<span style="color: rgb(255, 0, 0);">609310</span>"
length="<span style="color: rgb(255, 0, 0);">28</span>"
strand="<span style="color: rgb(255, 0, 0);">+</span>"&gt;</span><br style="font-weight: bold;">

      <span style="font-weight: bold;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&lt;location band="<span style="color: rgb(255, 0, 0);">p16.3</span>"
chr="<span style="color: rgb(255, 0, 0);">4</span>"
species="<span style="color: rgb(255, 0, 0);">Homo sapiens</span>"&gt;</span><br style="font-weight: bold;">

      <span style="font-weight: bold;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&lt;db_source db_name="<span style="color: rgb(255, 0, 0);">EnsEMBL</span>" assembly="<span style="color: rgb(255, 0, 0);">NCBI 35</span>"/&gt;</span><br style="font-weight: bold;">

      <span style="font-weight: bold;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&lt;/location&gt;</span><br style="font-weight: bold;">

      <span style="font-weight: bold;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&lt;/coordinate&gt;</span><br style="font-weight: bold;">

      <span style="font-weight: bold;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&lt;/reg_seq&gt;</span><br style="font-weight: bold;">

      <span style="font-weight: bold;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&lt;/tsr&gt;</span><br style="font-weight: bold;">

      <span style="font-weight: bold;">&nbsp;&nbsp;&nbsp;
&lt;/gene_source&gt;</span><br>

      <br>

      <small>Replace the red values with your own information.<br>

The pazar IDs are internal IDs that will not be stored. They can be
anything as long as they are unique throughout the file.</small><br>

      <br>

      <span style="margin-left: 0.5in; text-decoration: underline;"><a name="Regulatory_Sequence_without_gene_info">2.2 -
Annotating a Regulatory Sequence without any gene information</a></span><small><span style="margin-left: 0.1in;"> <a href="$pazar_cgi/step2.pl#Step2_TOP">TOP</a></span></small>
      <div style="text-align: justify;"><span>The
'reg_seq' element can also be embedded in a 'marker' element if the
gene regulated by the sequence is not defined yet. The marker can be a
gene but then it is just used for location purpose and not to infer any
role for the sequence on this gene.</span><br>

      <span></span></div>

      <span><br>

      </span><span style="text-decoration: underline;"></span><span style="font-weight: bold;">&nbsp;&nbsp;&nbsp;
&lt;marker db_accn="<span style="color: rgb(255, 0, 0);">ENSG00000133256</span>"
description="<span style="color: rgb(255, 0, 0);">PDE6B</span>"
pazar_id="<span style="color: rgb(255, 0, 0);">ma_0001</span>"&gt;</span><br style="font-weight: bold;">

      <span style="font-weight: bold;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&lt;db_source db_name="<span style="color: rgb(255, 0, 0);">EnsEMBL</span>" assembly="<span style="color: rgb(255, 0, 0);">37_35j</span>"/&gt;</span><br style="font-weight: bold;">

      <span style="font-weight: bold;">&nbsp;</span><span style="font-weight: bold;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&lt;reg_seq&nbsp;pazar_id="<span style="color: rgb(255, 0, 0);">rs_0001</span>"
quality="<span style="color: rgb(255, 0, 0);">tested</span>"
sequence="<span style="color: rgb(255, 0, 0);">ATTTGTAGGAGTGAGTCAGCTGACCCGC</span>"&gt;</span><br style="font-weight: bold;">

      <span style="font-weight: bold;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&lt;coordinate begin="<span style="color: rgb(255, 0, 0);">609283</span>"
end="<span style="color: rgb(255, 0, 0);">609310</span>"
length="<span style="color: rgb(255, 0, 0);">28</span>"
strand="<span style="color: rgb(255, 0, 0);">+</span>"&gt;</span><br style="font-weight: bold;">

      <span style="font-weight: bold;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&lt;location band="<span style="color: rgb(255, 0, 0);">p16.3</span>"
chr="<span style="color: rgb(255, 0, 0);">4</span>"
species="<span style="color: rgb(255, 0, 0);">Homo sapiens</span>"&gt;</span><br style="font-weight: bold;">

      <span style="font-weight: bold;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&lt;db_source db_name="<span style="color: rgb(255, 0, 0);">EnsEMBL</span>" assembly="<span style="color: rgb(255, 0, 0);">37_35j</span>"/&gt;</span><br style="font-weight: bold;">

      <span style="font-weight: bold;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&lt;/location&gt;</span><br style="font-weight: bold;">

      <span style="font-weight: bold;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&lt;/coordinate&gt;</span><br style="font-weight: bold;">

      <span style="font-weight: bold;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&lt;/reg_seq&gt;</span><br style="font-weight: bold;">

      <span style="font-weight: bold;"></span><span style="font-weight: bold;">&nbsp;&nbsp;&nbsp;
&lt;/marker&gt;<br>

      <br>

      </span><small>Replace the red values with your own
information.<br>

The pazar IDs are internal IDs that will not be stored. They can be
anything as long as they are unique throughout the file.<br>

      <br>

      </small><span style="margin-left: 0.5in; text-decoration: underline;"><a name="Transcription_Factor">2.3 -
Annotating a Transcription Factor</a></span><small><span style="margin-left: 0.1in;"> <a href="$pazar_cgi/step2.pl#Step2_TOP">TOP</a></span></small><br>

      <div style="text-align: justify;"><span>A
transcription factor is described in
multiple steps.</span><br>

      <span>First, at the gene level: The
'tf' element is embedded in both 'transcript' and 'gene_source'
elements. Multiple 'transcript' elements can be used to describe
multiple isoforms of a gene.</span><br>

      <span>Then, at the protein level: The 'funct_tf' element
captures the
functional protein information</span><span> with as many
'tf_unit' elements as there are proteins in the complex (1
for monomers, 2 for dimers,...). The tf_id calls a pazar_id from a 'tf'
element.</span><br>

      <span></span></div>

      <span><br>

      <span style="font-weight: bold;">&nbsp;&nbsp;&nbsp;
&lt;gene_source db_accn="<span style="color: rgb(255, 0, 0);">ENSG00000129535</span>"
description="<span style="color: rgb(255, 0, 0);">NRL</span>"
pazar_id="<span style="color: rgb(255, 0, 0);">gs_0002</span>"&gt;</span><br style="font-weight: bold;">

      <span style="font-weight: bold;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&lt;db_source db_name="<span style="color: rgb(255, 0, 0);">EnsEMBL</span>" assembly="<span style="color: rgb(255, 0, 0);">37_35j</span>"/&gt;</span><br style="font-weight: bold;">

      <span style="font-weight: bold;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&lt;transcript db_accn="<span style="color: rgb(255, 0, 0);">ENST00000250471</span>"
pazar_id="<span style="color: rgb(255, 0, 0);">tr_0002</span>"&gt;</span><br style="font-weight: bold;">

      <span style="font-weight: bold;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&lt;db_source db_name="<span style="color: rgb(255, 0, 0);">EnsEMBL</span>" assembly="<span style="color: rgb(255, 0, 0);">37_35j</span>"/&gt;</span><br style="font-weight: bold;">

      <span style="font-weight: bold;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&lt;tf class="<span style="color: rgb(255, 0, 0);">bZIP</span>"
family="<span style="color: rgb(255, 0, 0);">MAF</span>"
pazar_id="<span style="color: rgb(255, 0, 0);">tf_0001</span>"/&gt;</span><br style="font-weight: bold;">

      <span style="font-weight: bold;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&lt;/transcript&gt;</span><br style="font-weight: bold;">

      <span style="font-weight: bold;">&nbsp;&nbsp;&nbsp;
&lt;/gene_source&gt;</span><br style="font-weight: bold;">

      <span style="font-weight: bold;">&nbsp;&nbsp;&nbsp;
&lt;funct_tf funct_tf_name="<span style="color: rgb(255, 0, 0);">NRL</span>"
pazar_id="<span style="color: rgb(255, 0, 0);">fu_0001</span>"&gt;</span><br style="font-weight: bold;">

      <span style="font-weight: bold;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&lt;tf_unit pazar_id="<span style="color: rgb(255, 0, 0);">tu_0001</span>"
tf_id="<span style="color: rgb(255, 0, 0);">tf_0001</span>"/&gt;</span><br style="font-weight: bold;">

      <span style="font-weight: bold;">&nbsp;&nbsp;&nbsp;
&lt;/funct_tf&gt;<br>

      <br>

      </span></span><small>Replace the red values
with your own information.<br>

The pazar IDs are internal IDs that will not be stored. They can be
anything as long as they are unique throughout the file.<br>

      <br>

      </small><small><br>

      </small><span style="margin-left: 0.5in; text-decoration: underline;"><a name="Artificial_sequence">2.4 -
Annotating an Artificial Sequence</a></span><small><span style="margin-left: 0.1in;"> <a href="$pazar_cgi/step2.pl#Step2_TOP">TOP</a></span></small><br>

      <span></span>
      <div style="text-align: justify;">The
'construct' element can be used to describe any sequence without
specific genomic coordinates (e.g. a synthesized oligonucleotide
representing a consensus binding site).<br>

      </div>

      <span><br>

&nbsp; &nbsp;<span style="font-weight: bold;">
&lt;construct construct_name="<span style="color: rgb(255, 0, 0);">FN-13A</span>"
description="<span style="color: rgb(255, 0, 0);">random
oligo</span>" sequence="<span style="color: rgb(255, 0, 0);">gggtgagtcagcg</span>"
pazar_id="<span style="color: rgb(255, 0, 0);">co_0001</span>"/&gt;</span><br>

      <span style="font-weight: bold;">&nbsp;&nbsp;&nbsp;&nbsp;</span>&lt;</span><small>Replace
the red values
with your own information.<br>

The pazar IDs are internal IDs that will not be stored. They can be
anything as long as they are unique throughout the file.</small> <br>

      <br>

      <a style="text-decoration: none;" href="$pazar_cgi/step1.pl"><input value="&lt;- To Step 1" type="button"></a> <a style="text-decoration: none;" href="$pazar_cgi/step3.pl"><input value="To Step 3 -&gt;" type="button"></a><br><br>

page

# print out the html tail template
my $template_tail = HTML::Template->new(filename => "$pazarcgipath/tail.tmpl");
print $template_tail->output;
