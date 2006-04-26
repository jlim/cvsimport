#!/usr/bin/perl

use HTML::Template;

# open the html header template
my $template = HTML::Template->new(filename => 'header.tmpl');

# fill in template parameters
$template->param(TITLE => 'PAZAR Gene Search');
$template->param(JAVASCRIPT_FUNCTION => q{
function setCount(target){

if(target == 0) 
{
document.gene_search.action="http://www.pazar.info/cgi-bin/gene_list.cgi";
document.gene_search.target="Window1";
window.open('about:blank','Window1', 'scrollbars=yes, menubar=no, toolbar=no directories=no, height=600, width=400');
}
if(target == 1) 
{
document.gene_search.target="_self";
document.gene_search.action="http://www.pazar.info/cgi-bin/gene_search.cgi";
}
if(target == 2) 
{
document.gene_search.action="http://www.pazar.info/cgi-bin/genebrowse_alpha.pl";
document.gene_search.target="Window1";
window.open('about:blank','Window1', 'scrollbars=yes, menubar=no, toolbar=no directories=no, height=600, width=600');
}
}
var state=0;
function CheckBox(cat){
if (cat == 1)
{
if (state == 1)
{
    document.gene_search.tf.checked=false;
    document.gene_search.tf_analysis.checked=false;
    document.gene_search.tf_reference.checked=false;
    document.gene_search.tf_interaction.checked=false;
    document.gene_search.tf_evidence.checked=false;
    state=0;
}
if (state == 0)
{
    document.gene_search.tf.checked=true;
    document.gene_search.tf_analysis.checked=true;
    document.gene_search.tf_reference.checked=true;
    document.gene_search.tf_interaction.checked=true;
    document.gene_search.tf_evidence.checked=true;
    state=1;
}}
if (cat == 0)
{
if (state == 1)
{
    document.gene_search.other_analysis.checked=false;
    document.gene_search.other_reference.checked=false;
    document.gene_search.other_effect.checked=false;
    document.gene_search.other_evidence.checked=false;
    state=0;
}
if (state == 0)
{
    document.gene_search.other_analysis.checked=true;
    document.gene_search.other_reference.checked=true;
    document.gene_search.other_effect.checked=true;
    document.gene_search.other_evidence.checked=true;
    state=1;
}}
}});

# send the obligatory Content-Type and print the template output
print "Content-Type: text/html\n\n", $template->output;

print<<page;
          <table border="0" cellpadding="0" cellspacing="0" width="100%">
            <tbody><tr>
              <td colspan="2">
      <p class="title1">PAZAR - Search by Gene</p><br>
      </td>
    </tr>
<form name="gene_search" method="post" action="" enctype="multipart/form-data" target="">
    <tr align="left">
      <td colspan="2">
<p > Please enter a &nbsp;
      <select name="ID_list">
      <option selected="selected" value="EnsEMBL_gene">EnsEMBL
gene ID</option>
      <option value="EnsEMBL_transcript"> EnsEMBL
transcript
ID</option>
      <option value="EntrezGene"> Entrezgene ID</option>
      <option value="nm"> RefSeq ID</option>
      <option value="swissprot"> Swissprot ID</option>
      </select>
&nbsp; <input value="" name="geneID" type="text">&nbsp; <input value="Submit" name="submit" type="submit" onClick="setCount(1)"><br></p>
      <br>
      </td>
    </tr>
    <tr align="left">
      <td colspan="2"><p > Or browse the current list of annotated genes
&nbsp;
      <input value="View Gene List" name="submit" type="submit"  onClick="setCount(0)"><input value="View Alphabetical Gene List" name="submit" type="submit"  onClick="setCount(2)"><br></p>
      <br>
      </td>
    </tr>
    <tr>
      <td colspan="2">
      <hr><p class="title3">Select
the Attributes to Display</p><br></td>
    </tr>
<tr>
      <td colspan="2"><span class="title4"><input name="reg_seq" checked="checked" type="checkbox"> Regulatory Sequence: </span></td>
    </tr>
    <tr>
      <td width="50%" valign="top" align="left">
      <p ><input name="gene" checked="checked" type="checkbox"> Gene/Transcript ID </p>
      </td>
      <td width="50%" valign="top" align="left">
      <p ><input name="tss" type="checkbox"> Transcription Start Site </p>
      </td>
    </tr>
    <tr>
      <td width="50%" valign="top" align="left">
      <p ><input name="reg_seq_name" checked="checked" type="checkbox"> Name (if any) </p>
      </td>
      <td width="50%" valign="top" align="left">
      <p ><input name="sequence" checked="checked" type="checkbox"> Sequence </p>
      </td>
    </tr>
    <tr>
      <td width="50%" valign="top" align="left">
      <p ><input name="coordinates" checked="checked" type="checkbox"> Coordinates </p>
      </td>
      <td width="50%" valign="top" align="left">
      <p ><input name="species" checked="checked" type="checkbox"> Species </p>
      </td>
    </tr>
    <tr>
    <tr>
      <td width="50%" valign="top" align="left">
      <p ><input name="quality" type="checkbox"> Quality </p>
      </td>
      <td width="50%" valign="top" align="left">
      </td>
    </tr>
    <tr>
    <tr>
      <td colspan="2"> <br>
      </td>
    </tr>
    <tr>
      <td colspan="2"> <br>
      </td>
    </tr>
    <tr>
      <td colspan="2"> <span class="title4"><input name="ev" type="checkbox" onclick="javascript:CheckBox(1)"> Interacting Evidence: </span></td>
    </tr>
    <tr>
      <td width="50%" valign="top" align="left">
      <p ><input name="tf" type="checkbox"> Transcription Factor </p>
      </td>
      <td width="50%" valign="top" align="left">
      <p ><input name="tf_interaction" type="checkbox"> Interaction Description </p>     </td>
    </tr>
    <tr>
      <td width="50%" valign="top" align="left">
      <p ><input name="tf_analysis" type="checkbox"> Analysis Details </p>
      </td>
      <td width="50%" valign="top" align="left">
      <p ><input name="tf_reference" type="checkbox"> Reference (PMID) </p>
      </td>
    </tr>
    <tr>
      <td width="50%" valign="top" align="left">
      <p ><input name="tf_evidence" type="checkbox"> Evidence </p>
      </td>
    </tr>
    <tr>
      <td colspan="2"> <br>
      </td>
    </tr>
    <tr>
      <td colspan="2"> <br>
      </td>
    </tr>
    <tr>
      <td colspan="2"> <span class="title4"><input name="other" type="checkbox" onclick="javascript:CheckBox(0)"> Other Evidence: </span></td>
    </tr>
    <tr>
      <td width="50%" valign="top" align="left">
      <p ><input name="other_analysis" type="checkbox"> Analysis Details </p>
      </td>
      <td width="50%" valign="top" align="left">
      <p ><input name="other_reference" type="checkbox"> Reference (PMID) </p>
      </td>
    </tr>
    <tr>
      <td width="50%" valign="top" align="left">
      <p ><input name="other_effect" type="checkbox"> Effect Description </p>
      </td>
      <td width="50%" valign="top" align="left">
      <p ><input name="other_evidence" type="checkbox"> Evidence </p>
      </td>
    </tr>
    <tr>
      <td colspan="2"> <br>
      <hr><br>
      </td>
    </tr>
    <tr>
      <td align="right" valign="top" width="50%">
      <input value="Reset" type="reset"> </td>
      <td width="50%"> <input value="Submit" type="submit"  onClick="setCount(1)"> </td>
    </tr>
</form>
    <tr>
      <td colspan="2"> <br>
      </td>
    </tr>
  </tbody>
</table>

page

# print out the html tail template
my $template_tail = HTML::Template->new(filename => 'tail.tmpl');
print $template_tail->output;
