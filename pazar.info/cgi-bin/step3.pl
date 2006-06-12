#!/usr/bin/perl

use HTML::Template;

# open the html header template
my $template = HTML::Template->new(filename => 'header.tmpl');

# fill in template parameters
$template->param(TITLE => 'PAZAR XML writing Step 3');

# send the obligatory Content-Type and print the template output
print "Content-Type: text/html\n\n", $template->output;

print<<page;
          <span class="title1">PAZAR - XML format</span><br>
          <span class="title2">Step-by-Step Documentation</span><br><br>
          <p class="title3"><a name="Step3_TOP"></a>Step3: Capturing the evidence linking a sequence to a TF or to a specific expression</p>
      <div style="text-align: justify;">This step starts inside an existing 'data'
element. At this point, the 'reg_seq', 'funct_tf' and/or 'construct' elements
should have been defined in this 'data' element (<a href="step2.pl">see Step 2</a>).<br>

      <br>



      </div>



      <span style="margin-left: 0.5in; text-decoration: underline;">3.1-
Capturing the experiment information<br>



      </span>
      
      
      <div style="text-align: justify;">The 'data' element
stores all the annotations describing the cell,
time, condition,... <span style="font-weight: bold;">&nbsp;&nbsp;&nbsp;
      <br>



      <br>



      </span>
      
      
      <div style="text-align: left;"><span style="font-weight: bold;">&nbsp;
&nbsp; &nbsp; &lt;cell name="<span style="color: rgb(255, 0, 0);">Y79</span>" pazar_id="<span style="color: rgb(255, 0, 0);">ce_0001</span>"
species="<span style="color: rgb(255, 0, 0);">Homo sapiens</span>"
status="<span style="color: rgb(255, 0, 0);">cell__line</span>"/&gt;</span><br style="font-weight: bold;">



      <span style="font-weight: bold;">&nbsp;&nbsp;&nbsp;
&nbsp; &lt;time name="<span style="color: rgb(255, 0, 0);">24-28</span>"
pazar_id="<span style="color: rgb(255, 0, 0);">ti_0001</span>"
scale="<span style="color: rgb(255, 0, 0);">stages of
embryogenesis</span>"/&gt;</span><br style="font-weight: bold;">



      <span style="font-weight: bold;">&nbsp;
&nbsp; &nbsp; &lt;condition pazar_id="<span style="color: rgb(255, 0, 0);">cd_0001</span>"
cond_type="<span style="color: rgb(255, 0, 0);">coexpression</span>"
molecule="<span style="color: rgb(255, 0, 0);">transcription
factor</span>" concentration="<span style="color: rgb(255, 0, 0);">1:1</span>" scale="<span style="color: rgb(255, 0, 0);">ratio</span>"/&gt;</span><br style="font-weight: bold;">



      </div>



      <br>



      <small>Replace
the red values
with your own information.<br>



The pazar IDs are internal IDs that will not be stored. They can be
anything as long as they are unique throughout the file.</small> <br>



      <br>



      <span style="margin-left: 0.5in; text-decoration: underline;">3.2-
Capturing the interaction/expression information<br>



      </span> The 'data' element&nbsp;also <span style="font-weight: bold;"></span>stores&nbsp;the
description of the interaction and/or expression quality.<br>



      <br>



      <span style="font-weight: bold;">&nbsp;&nbsp;&nbsp;
&lt;expression pazar_id="<span style="color: rgb(255, 0, 0);">ex_0001</span>"
quantitative="<span style="color: rgb(255, 0, 0);">23</span>"
scale="<span style="color: rgb(255, 0, 0);">percent</span>"/&gt;</span><br style="font-weight: bold;">



      <span style="font-weight: bold;">&nbsp;&nbsp;&nbsp;
&lt;interaction pazar_id="<span style="color: rgb(255, 0, 0);">in_0001</span>"
qualitative="<span style="color: rgb(255, 0, 0);">good</span>"/&gt;</span><br style="font-weight: bold;">



      <span style="font-weight: bold;">&nbsp;&nbsp;&nbsp;
&lt;interaction pazar_id="<span style="color: rgb(255, 0, 0);">in_0002</span>"
qualitative="<span style="color: rgb(255, 0, 0);">none</span>"/&gt;</span><br style="font-weight: bold;">



      <span style="font-weight: bold;">&nbsp;&nbsp;&nbsp;
&lt;interaction pazar_id="<span style="color: rgb(255, 0, 0);">in_0003</span>"
quantitative="<span style="color: rgb(255, 0, 0);">14</span>"
scale="<span style="color: rgb(255, 0, 0);">percent</span>"/&gt;</span><br style="font-weight: bold;">



      <br>



      <small>Replace
the red values
with your own information.<br>



The pazar IDs are internal IDs that will not be stored. They can be
anything as long as they are unique throughout the file.</small> <br>



      <br>



      <span style="margin-left: 0.5in; text-decoration: underline;">3.3-
Linking all together<br>



      </span> The 'data' element can now be closed. All the data
stored in it will&nbsp;be linked through&nbsp; 'analysis'
elements using the pazar_ids as IDREFS.<br>



An 'analysis' element stores an experiment information, linking
sequences and factors (inputs) to an interaction or expression result
(output). There can be as many 'analysis' element in a 'pazar' element
as needed.<br>



The cell and time are called as attributes of the 'analysis'
element. The evidence, method and ref are children elements of the 'analysis'
element.<br>



The sequences and factors (always use a 'funct_tf' element) studied are
called as attributes of the 'input' element. The interaction or
expression descriptions are called as attributes of the 'output'
element.<br>



Thus the example below describe a SELEX experiment with a TF
(pazar_id="fu_0001") binding to 2 different artificial sequences
(pazar_ids="co_0001" and "co_0002"), with 2 different levels of
interaction (pazar_ids="in_0001" and "in_0002") -&gt; 2
'input_ouput' elements: the first describes the interaction of the TF
with the first sequence, the other describes its interaction with the
second sequence.<br>



Please look at the 3 PAZAR XML examples available on the <a href="/xml.pl">main page</a> if
you need other examples.<br>
      <br>



      <span style="font-weight: bold;">&nbsp;
&lt;/data&gt;</span><br>



      <span style="font-weight: bold;">&nbsp;
&lt;analysis name="<span style="color: rgb(255, 0, 0);">analysis_example1</span>"</span><br style="font-weight: bold;">



      <span style="font-weight: bold;">&nbsp;&nbsp;&nbsp;
&lt;evidence type_evid="<span style="color: rgb(255, 0, 0);">curated</span>" status_evid="<span style="color: rgb(255, 0, 0);">provisional</span>"/&gt;</span><br style="font-weight: bold;">



      <span style="font-weight: bold;">&nbsp;&nbsp;&nbsp;
&lt;method method="<span style="color: rgb(255, 0, 0);">SELEX</span>"/&gt;</span><br style="font-weight: bold;">



      <span style="font-weight: bold;">&nbsp;&nbsp;&nbsp;
&lt;ref pmid="<span style="color: rgb(255, 0, 0);">7936637</span>"/&gt;</span><br style="font-weight: bold;">



      <span style="font-weight: bold;">&nbsp;&nbsp;&nbsp;
&lt;input_output&gt;</span><br style="font-weight: bold;">



      <span style="font-weight: bold;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&lt;input inputs="<span style="color: rgb(255, 0, 0);">fu_0001
co_0001</span>"/&gt;</span><br style="font-weight: bold;">



      <span style="font-weight: bold;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&lt;output outputs="<span style="color: rgb(255, 0, 0);">in_0001</span>"/&gt;</span><br style="font-weight: bold;">



      <span style="font-weight: bold;">&nbsp;&nbsp;&nbsp;
&lt;/input_output&gt;</span><br style="font-weight: bold;">



      <span style="font-weight: bold;">&nbsp;&nbsp;&nbsp;
&lt;input_output&gt;</span><br style="font-weight: bold;">



      <span style="font-weight: bold;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&lt;input inputs="<span style="color: rgb(255, 0, 0);">fu_0001
co_0002</span>"/&gt;</span><br style="font-weight: bold;">



      <span style="font-weight: bold;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&lt;output outputs="<span style="color: rgb(255, 0, 0);">in_0002</span>"/&gt;</span><br style="font-weight: bold;">



      <span style="font-weight: bold;">&nbsp;&nbsp;&nbsp;
&lt;/input_output&gt;</span><br style="font-weight: bold;">



      <span style="font-weight: bold;">&nbsp;
&lt;/analysis&gt;<br>



      <br>



      </span><small>Replace
the red values
with your own information.<br>



The pazar IDs are internal IDs that will not be stored. They can be
anything as long as they are unique throughout the file.</small> <br>



      <br>



      <span style="margin-left: 0.5in; text-decoration: underline;">3.4-
The end<br>



      </span><span>Once
all the data has been entered in the 'data' element and linked together
through multiple 'analysis' elements, the 'pazar' element can be closed
and the XML file is finished.<br>


      <br>


      </span><span style="font-weight: bold;">&nbsp;&lt;/pazar&gt;<br>


      <br>


      </span></div>


      <a style="text-decoration: none;" href="step2.pl"><input value="&lt;- To Step 2" type="button"></a>
page

# print out the html tail template
my $template_tail = HTML::Template->new(filename => 'tail.tmpl');
print $template_tail->output;
