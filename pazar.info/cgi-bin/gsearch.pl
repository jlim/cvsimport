#!/usr/bin/perl

use HTML::Template;

require 'getsession.pl';

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
window.open('about:blank','Window1', 'scrollbars=yes, menubar=no, toolbar=no directories=no, height=800, width=800');
}
if(target == 1) 
{
var myTextField = document.getElementById('ID_list');

if(myTextField.value == "PAZAR_seq") {
document.gene_search.target="_self";
document.gene_search.action="http://www.pazar.info/cgi-bin/seq_search.cgi";
} else {
document.gene_search.target="_self";
document.gene_search.action="http://www.pazar.info/cgi-bin/gene_search.cgi";
}
}
if(target == 2) 
{
document.gene_search.action="http://www.pazar.info/cgi-bin/genebrowse_alpha.pl";
document.gene_search.target="Window2";
window.open('about:blank','Window2', 'resizable=1,scrollbars=yes, menubar=no, toolbar=no directories=no, height=600, width=650');
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
<h1>PAZAR Gene View</h1>
          <table border="0" cellpadding="0" cellspacing="0" width="100%">
            <tbody><tr>
              <td colspan="2">
      <p class="title2">Search by Gene or Sequence</p>
      </td>
    </tr>
<form name="gene_search" method="post" action="" enctype="multipart/form-data" target="">
    <tr align="left">
      <td colspan="2">
<p > Please enter a &nbsp;
      <select name="ID_list" id="ID_list">
      <option selected="selected" value="EnsEMBL_gene">EnsEMBL gene ID</option>
      <option value="EnsEMBL_transcript">EnsEMBL transcript ID</option>
      <option value="GeneName">User Defined Gene Name</option>
      <option value="EntrezGene">Entrezgene ID</option>
      <option value="nm">RefSeq ID</option>
      <option value="swissprot">Swissprot ID</option>
      <option value="PAZAR_gene">PAZAR Gene ID</option>
      <option value="PAZAR_seq">PAZAR Sequence ID</option>
      </select>
&nbsp; <input value="" name="geneID" type="text">&nbsp; <input value="Submit" name="submit" type="submit" onClick="setCount(1)"><br></p>
      </td>
    </tr>
    <tr align="left">
      <td colspan="2"><p > Or browse the current list of annotated genes
&nbsp;
      <input value="View Gene List" name="submit" type="submit"  onClick="setCount(0)"><br></p>
      </td>
    </tr>
   </form>
  </tbody>
</table>
<hr color='black'>
page

# print out the html tail template
my $template_tail = HTML::Template->new(filename => 'tail.tmpl');
print $template_tail->output;
