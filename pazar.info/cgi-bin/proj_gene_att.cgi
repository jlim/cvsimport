#!/usr/bin/perl -w

use HTML::Template;
use strict;
use CGI qw(:standard);
use CGI::Carp qw(fatalsToBrowser);
use CGI::Debug( report => 'everything', on => 'anything' );


 
# open the html header template
my $template = HTML::Template->new(filename => 'header.tmpl');

# fill in template parameters
$template->param(TITLE => "PAZAR - Project Search Engine");
$template->param(JAVASCRIPT_FUNCTION => q{
var state=0;
function CreateForm(){
var i = document.attributes.view.selectedIndex;
if (i==0) {
document.hidden_filters.action = "http://www.pazar.info/cgi-bin/proj_gene_att.cgi";
document.hidden_filters.submit();
}
if (i==1) {
document.hidden_filters.action = "http://www.pazar.info/cgi-bin/proj_tf_att.cgi";
document.hidden_filters.submit();
}
}
function CopyHidden(){
var hid=document.hidden_filters.getElementsByTagName('input');
var tempobj;
for(var i = 0, inp; inp = hid[i]; i++) 
{
    tempobj = eval("document.attributes." + inp.name);
    tempobj.value = inp.value;
}
}
function CheckBox(cat){
if (cat == 1)
{
if (state == 1)
{
    document.attributes.at_tf.checked=false;
    document.attributes.at_tf_analysis.checked=false;
    document.attributes.at_tf_reference.checked=false;
    document.attributes.at_tf_interaction.checked=false;
    document.attributes.at_tf_evidence.checked=false;
    state=0;
}
if (state == 0)
{
    document.attributes.at_tf.checked=true;
    document.attributes.at_tf_analysis.checked=true;
    document.attributes.at_tf_reference.checked=true;
    document.attributes.at_tf_interaction.checked=true;
    document.attributes.at_tf_evidence.checked=true;
    state=1;
}}
if (cat == 0)
{
if (state == 1)
{
    document.attributes.at_other_analysis.checked=false;
    document.attributes.at_other_reference.checked=false;
    document.attributes.at_other_effect.checked=false;
    document.attributes.at_other_evidence.checked=false;
    state=0;
}
if (state == 0)
{
    document.attributes.at_other_analysis.checked=true;
    document.attributes.at_other_reference.checked=true;
    document.attributes.at_other_effect.checked=true;
    document.attributes.at_other_evidence.checked=true;
    state=1;
}}
}});

# send the obligatory Content-Type and print the template output
print "Content-Type: text/html\n\n", $template->output;

my $get = new CGI;
my %param = %{$get->Vars};
my $proj = $param{project_name};

print "<p class=\"title1\">PAZAR - Project $proj Search Engine</p>";

print<<page;
<table border="0" cellpadding="0" cellspacing="0" width="100%">
<tbody>
<form name="attributes" METHOD="post" ACTION="http://www.pazar.info/cgi-bin/proj_res.cgi" enctype="multipart/form-data" target="_self">
    <tr>
      <td colspan="2">
<span class="title3">Attributes to Display: </span><br><br>
      </td>
    </tr>
    <tr>
      <td colspan="2">
        <select name="view" onchange="CreateForm()">
        <option value="gene-centric" selected> Gene-Centric View </option>
        <option value="tf-centric" > TF-Centric View </option>
        </select>
        <br><br><hr>
      </td>
    </tr>
    <tr>
      <td colspan="2"><span class="title4"><input name="at_reg_seq" checked="checked" type="checkbox"> Regulatory Sequence: </span></td>
    </tr>
    <tr>
      <td width="50%" valign="top" align="left">
      <p ><input name="at_gene" checked="checked" type="checkbox"> Gene/Transcript ID </p>
      </td>
      <td width="50%" valign="top" align="left">
      <p ><input name="at_tss" type="checkbox"> Transcription Start Site </p>
      </td>
    </tr>
    <tr>
      <td width="50%" valign="top" align="left">
      <p ><input name="at_reg_seq_name" checked="checked" type="checkbox"> Name (if any) </p>
      </td>
      <td width="50%" valign="top" align="left">
      <p ><input name="at_sequence" checked="checked" type="checkbox"> Sequence </p>
      </td>
    </tr>
    <tr>
      <td width="50%" valign="top" align="left">
      <p ><input name="at_coordinates" checked="checked" type="checkbox"> Coordinates </p>
      </td>
      <td width="50%" valign="top" align="left">
      <p ><input name="at_species" checked="checked" type="checkbox"> Species </p>
      </td>
    </tr>
    <tr>
    <tr>
      <td width="50%" valign="top" align="left">
      <p ><input name="at_quality" type="checkbox"> Quality </p>
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
      <td colspan="2"> <span class="title4"><input name="at_ev" type="checkbox" onclick="javascript:CheckBox(1)"> Interacting Evidence: </span></td>
    </tr>
    <tr>
      <td width="50%" valign="top" align="left">
      <p ><input name="at_tf" type="checkbox"> Transcription Factor </p>
      </td>
      <td width="50%" valign="top" align="left">
      <p ><input name="at_tf_interaction" type="checkbox"> Interaction Description </p>     </td>
    </tr>
    <tr>
      <td width="50%" valign="top" align="left">
      <p ><input name="at_tf_analysis" type="checkbox"> Analysis Details </p>
      </td>
      <td width="50%" valign="top" align="left">
      <p ><input name="at_tf_reference" type="checkbox"> Reference (PMID) </p>
      </td>
    </tr>
    <tr>
      <td width="50%" valign="top" align="left">
      <p ><input name="at_tf_evidence" type="checkbox"> Evidence </p>
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
      <td colspan="2"> <span class="title4"><input name="at_other" type="checkbox" onclick="javascript:CheckBox(0)"> Other Evidence: </span></td>
    </tr>
    <tr>
      <td width="50%" valign="top" align="left">
      <p ><input name="at_other_analysis" type="checkbox"> Analysis Details </p>
      </td>
      <td width="50%" valign="top" align="left">
      <p ><input name="at_other_reference" type="checkbox"> Reference (PMID) </p>
      </td>
    </tr>
    <tr>
      <td width="50%" valign="top" align="left">
      <p ><input name="at_other_effect" type="checkbox"> Effect Description </p>
      </td>
      <td width="50%" valign="top" align="left">
      <p ><input name="at_other_evidence" type="checkbox"> Evidence </p>
      </td>
    </tr>
    <tr>
      <td colspan="2"> <br>
<input type="hidden" name="bp_filter" value=""><input type="hidden" name="chr_filter" value=""><input type="hidden" name="expression_filter" value=""><input type="hidden" name="interaction" value=""><input type="hidden" name="gene" value=""><input type="hidden" name="species_filter" value=""><input type="hidden" name="mutation_filter" value=""><input type="hidden" name="length_filter" value=""><input type="hidden" name="tf" value=""><input type="hidden" name="expression" value=""><input type="hidden" name="chromosome" value=""><input type="hidden" name="evidence" value=""><input type="hidden" name="interaction_filter" value=""><input type="hidden" name="method" value=""><input type="hidden" name="shorter_larger" value=""><input type="hidden" name="bp_end" value=""><input type="hidden" name="class_filter" value=""><input type="hidden" name="method_filter" value=""><input type="hidden" name="region_filter" value=""><input type="hidden" name="construct_filter" value=""><input type="hidden" name="species" value=""><input type="hidden" name="gene_filter" value=""><input type="hidden" name="length" value=""><input type="hidden" name="bp_start" value=""><input type="hidden" name="evidence_filter" value=""><input type="hidden" name="classes" value=""><input type="hidden" name="tf_filter" value=""><input type="hidden" name="project_name" value="">
      <hr><br>
      </td>
    </tr>
    <tr>
      <td align="right" valign="top" width="50%">
      <input value="Reset" type="reset"> </td>
      <td width="50%"> <input value="Submit" type="submit" onClick="CopyHidden()"> </td>
    </tr>
</form>
    <tr>
      <td colspan="2"> <br>
       <form name="hidden_filters" method="post" action="" enctype="multipart/form-data" target="_self">
page

foreach my $item (keys %param) {
    my @vals;
    foreach my $val ($get->param($item)) {
	push @vals, $val;
    }
    print "<input type=\"hidden\" name=\"$item\" value=\"".join(';',@vals)."\">";
}
print "</form></td></tr></tbody></table>";


###  print out the html tail template
  my $template_tail = HTML::Template->new(filename => 'tail.tmpl');
  print $template_tail->output;
