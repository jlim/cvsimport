#!/usr/bin/perl

use HTML::Template;

# open the html header template
my $template = HTML::Template->new(filename => 'header.tmpl');

# fill in template parameters
$template->param(TITLE => 'PAZAR TF Search');
$template->param(JAVASCRIPT_FUNCTION => q{
function setCount(target){

if(target == 0) 
{
document.tf_search.action="http://www.pazar.info/cgi-bin/tf_list.cgi";
document.tf_search.target="Window1";
window.open('about:blank','Window1', 'scrollbars=yes, menubar=no, toolbar=no directories=no, height=600, width=400');
}
if(target == 1) 
{
document.tf_search.action="http://www.pazar.info/cgi-bin/tf_search.cgi";
document.tf_search.target="_self";
}
}});

# send the obligatory Content-Type and print the template output
print "Content-Type: text/html\n\n", $template->output;

print<<page;
          <table border="0" cellpadding="0" cellspacing="0" width="100%">
            <tbody><tr>
              <td colspan="2">
      <p class="title1">PAZAR - Search by TF</p><br>
      </td>
    </tr>
<form name="tf_search" method="post" action="" enctype="multipart/form-data" target="">
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
           <option value="tf_name"> functional name</option>
</select>
&nbsp; <input value="" name="geneID" type="text">&nbsp; <input value="Submit" name="submit" type="submit" onClick="setCount(1)"><br></p>
      <br>
      </td>
    </tr>
    <tr align="left">
      <td colspan="2"><p > Or browse the current list of reported TFs
&nbsp;
      <input value="View TF List" name="submit" type="submit"  onClick="setCount(0)"><br></p>
      <br>
      </td>
    </tr>
    <tr>
      <td colspan="2">
      <hr><p class="title3">Select
the Attributes to Display</p><br></td>
    </tr>
    <tr>
      <td colspan="2"><p class="title4">
Genomic Coordinates: </p></td>
    </tr>
    <tr>
      <td width="50%" valign="top" align="left">
      <p ><br><input name="chr_name" checked="checked" type="checkbox"> Chromosome Name </p>
      </td>
      <td width="50%" valign="top" align="left">
      <p ><br><input name="species" checked="checked" type="checkbox"> Species </p>
      </td>
    </tr>
    <tr>
      <td width="50%" valign="top" align="left">
      <p ><input name="start" checked="checked" type="checkbox"> Start Position (bp) </p>
      </td>
      <td width="50%" valign="top" align="left">
      <p ><input name="strand" checked="checked" type="checkbox"> Strand </p>
      </td>
    </tr>
    <tr>
      <td width="50%" valign="top" align="left">
      <p ><input name="end" checked="checked" type="checkbox"> End Position (bp) </p>
      </td>
      <td width="50%" valign="top" align="left">
      <p ><input name="band" type="checkbox">
Band </p>
      </td>
    </tr>
    <tr>
      <td colspan="2"> <br>
      </td>
    </tr>
    <tr>
      <td colspan="2"> <p class="title4">
Gene: </p> </td>
    </tr>
    <tr>
      <td width="50%" valign="top" align="left">
      <p ><br><input name="EnsEMBL_gene" checked="checked" type="checkbox"> EnsEMBL Gene ID </p>
      </td>
      <td width="50%" valign="top" align="left">
      <p ><br><input name="EnsEMBL_transcript" type="checkbox"> EnsEMBL Transcript ID (if any) </p>
      </td>
    </tr>
    <tr>
      <td width="50%" valign="top" align="left">
      <p ><input name="EnsEMBL_gene" type="checkbox">
EnsEMBL Gene Description </p>
      </td>
      <td width="50%" valign="top" align="left">
      <p ><input name="EnsEMBL_transcript" type="checkbox"> Annotator Description </p>
      </td>
    </tr>
    <tr>
      <td width="50%" valign="top" align="left">
      <p ><input name="tss" type="checkbox">
Transcription Start Site </p>
      </td>
    </tr>
    <tr>
      <td colspan="2"> <br>
      </td>
    </tr>
    <tr>
      <td colspan="2"> <p class="title4">
Sequence: </p> </td>
    </tr>
    <tr>
      <td width="50%" valign="top" align="left">
      <p ><br><input name="sequence" checked="checked" type="checkbox"> Sequence </p>
      </td>
      <td width="50%" valign="top" align="left">
      <p ><br><input name="seq_length" type="checkbox"> Length </p>
      </td>
    </tr>
    <tr>
      <td width="50%" valign="top" align="left">
      <p ><input name="TFBS_name" type="checkbox"> TFBS name (if any) </p>
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
      <td colspan="2"> <p class="title4">Interacting Transcription Factor (if any): </p> </td>
    </tr>
    <tr>
      <td width="50%" valign="top" align="left">
      <p ><br><input name="factor_gene" checked="checked" type="checkbox"> EnsEMBL Gene ID </p>
      </td>
      <td width="50%" valign="top" align="left">
      <p ><br><input name="factor_transcript" type="checkbox"> EnsEMBL Transcript ID </p>
      </td>
    </tr>
    <tr>
      <td width="50%" valign="top" align="left">
      <p ><input name="TF_name" checked="checked" type="checkbox"> Name </p>
      </td>
      <td width="50%" valign="top" align="left">
      <p ><input name="TF_class" type="checkbox"> Class </p>
      </td>
    </tr>
    <tr>
      <td width="50%" valign="top" align="left">
      <p ><input name="TF_family" type="checkbox"> Family </p>
      </td>
      <td width="50%" valign="top" align="left">
      <p ><input name="TF_modif" type="checkbox"> Modifications </p>
      </td>
    </tr>
    <tr>
     <td colspan="2"> <br>
      </td>
    </tr>
    <tr>
      <td colspan="2"> <p class="title4">
Experiment: </p> </td>
    </tr>
    <tr>
      <td width="50%" valign="top" align="left">
      <p ><br><input name="method" checked="checked" type="checkbox"> Method </p>
      </td>
      <td width="50%" valign="top" align="left">
      <p ><br><input name="cell" type="checkbox"> Cell </p>
      </td>
    </tr>
    <tr>
      <td width="50%" valign="top" align="left">
      <p ><input name="time" type="checkbox"> Time </p>
      </td>
      <td width="50%" valign="top" align="left">
      <p ><input name="condition" type="checkbox"> Condition </p>
      </td>
    </tr>
    <tr>
      <td width="50%" valign="top" align="left">
      <p ><input name="expression" type="checkbox"> Expression Result </p>
      </td>
      <td width="50%" valign="top" align="left">
      <p ><input name="interaction" type="checkbox"> Interaction Result </p>
      </td>
    </tr>
    <tr>
      <td width="50%" valign="top" align="left">
      <p ><input name="pmid" type="checkbox"> Pubmed ID </p>
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
