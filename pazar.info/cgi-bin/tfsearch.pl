#!/usr/bin/perl

use HTML::Template;

require 'getsession.pl';

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
window.open('about:blank','Window1', 'resizable=1,scrollbars=yes, menubar=no, toolbar=no directories=no, height=600, width=400');
}
if(target == 1) 
{
document.tf_search.action="http://www.pazar.info/cgi-bin/tf_search.cgi";
document.tf_search.target="_self";
}
if(target == 2) 
{
document.tf_search.action="http://www.pazar.info/cgi-bin/tfbrowse_alpha.pl";
document.tf_search.target="Window2";
window.open('about:blank','Window2', 'resizable=1,scrollbars=yes, menubar=no, toolbar=no directories=no, height=600, width=650');
}
}
var evstate=0; // Lines of evidence initially off
var gtstate=1; // genomic target checkboxes
var atstate=1; // artificial target checkboxes

function evCheckBox(){
    if (evstate==1)
    {
	document.tf_search.analysis.checked=false;
	document.tf_search.reference.checked=false;
	document.tf_search.interaction.checked=false;
	document.tf_search.evidence.checked=false;
	evstate=0;
    }
    else
    { 
	document.tf_search.analysis.checked=true;
	document.tf_search.reference.checked=true;
	document.tf_search.interaction.checked=true;
	document.tf_search.evidence.checked=true;
	evstate=1;
    }
}

function atCheckBox(){
    if (atstate==1)
    {
	document.tf_search.construct_name.checked=false;
	document.tf_search.description.checked=false;
	atstate=0;
    }
    else
    { 
	document.tf_search.construct_name.checked=true;
	document.tf_search.description.checked=true;
	atstate=1;
    }
}


function gtCheckBox(){
    if (gtstate==1)
    {
	document.tf_search.reg_seq_name.checked=false;
	document.tf_search.gene.checked=false;
	document.tf_search.species.checked=false;
	document.tf_search.coordinates.checked=false;
	document.tf_search.quality.checked=false;
	gtstate=0;
    }
    else
    { 
	document.tf_search.reg_seq_name.checked=true;
	document.tf_search.gene.checked=true;
	document.tf_search.species.checked=true;
	document.tf_search.coordinates.checked=true;
	document.tf_search.quality.checked=true;
	gtstate=1;
    }
}

});

if($loggedin eq 'true')
{
    #log out link
    $template->param(LOGOUT => "$info{first} $info{last} logged in. ".'<a href=\'logout.pl\'>Log Out</a>');
}
else
{
    #log in link
    $template->param(LOGOUT => '<a href=\'login.pl\'>Log In</a>');
}

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
      <input value="View TF List" name="submit" type="submit"  onClick="setCount(0)">     <input value="View Alphabetical TF List" name="submit" type="submit"  onClick="setCount(2)"><br></p>
      <br>
      </td>
    </tr>
    <tr>
      <td colspan="2">
      <hr><p class="title3">Select
the Attributes to Display</p><br></td>
    </tr>
    <tr>
      <td colspan="2"><span class="title4"><input name="reg_seq" checked type="checkbox" onclick="gtCheckBox();"> Genomic Target (reg_seq): </span></td>
    </tr>
    <tr>
      <td width="50%" valign="top" align="left">
      <p ><input name="reg_seq_name" type="checkbox" checked> Name (if any) </p>
      </td>
      <td width="50%" valign="top" align="left">
      <p ><input name="gene" type="checkbox" checked> Gene </p>
      </td>
    </tr>
    <tr>
      <td width="50%" valign="top" align="left">
      <p ><input name="coordinates" type="checkbox" checked> Coordinates </p>
      </td>
      <td width="50%" valign="top" align="left">
      <p ><input name="species" type="checkbox" checked> Species </p>
      </td>
    </tr>
    <tr>
      <td width="50%" valign="top" align="left">
      <p ><input name="quality" type="checkbox" checked> Quality </p>
      </td>
      <td width="50%" valign="top" align="left">
      </td>
    </tr>
    <tr>
      <td colspan="2"> <br>
      </td>
    </tr>
    <tr>
      <td colspan="2"> <span class="title4"><input name="construct" checked type="checkbox" onclick="atCheckBox();"> Artificial Target (construct): </span></td>
    </tr>
    <tr>
      <td width="50%" valign="top" align="left">
      <p ><input name="construct_name" type="checkbox" checked> Name </p>
      </td>
      <td width="50%" valign="top" align="left">
      <p ><input name="description" type="checkbox" checked> Description (if any) </p>
      </td>
    </tr>
    <tr>
      <td colspan="2"> <br>
      </td>
    </tr>
    <tr>
      <td colspan="2"> <span class="title4"><input name="ev" type="checkbox" onclick="evCheckBox();"> Lines of evidence: </span></td>
    </tr>
    <tr>
      <td width="50%" valign="top" align="left">
      <p ><input name="analysis" type="checkbox"> Analysis Details </p>
      </td>
      <td width="50%" valign="top" align="left">
      <p ><input name="reference" type="checkbox"> Reference (PMID) </p>
      </td>
    </tr>
    <tr>
      <td width="50%" valign="top" align="left">
      <p ><input name="interaction" type="checkbox"> Interaction Description </p>
      </td>
      <td width="50%" valign="top" align="left">
      <p ><input name="evidence" type="checkbox"> Evidence </p>
      </td>
    </tr>
    <tr>
      <td colspan="2"> <br>
      </td>
    </tr>
    <tr>
      <td colspan="2"> <span class="title4"><input name="profile" type="checkbox" checked> Dynamically computed profile </span></td>
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
