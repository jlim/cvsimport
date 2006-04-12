#!/usr/bin/perl

use HTML::Template;
use strict;
use Data::Dumper;
use pazar;
use pazar::reg_seq;
use pazar::talk;
use pazar::tf::tfcomplex;
use pazar::tf::subunit;
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
document.hidden_filters.action="http://www.pazar.info/cgi-bin/proj_gene_att.cgi";
document.hidden_filters.submit();
}
if (i==1) {
document.hidden_filters.action="http://www.pazar.info/cgi-bin/proj_tf_att.cgi";
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
function CheckBox(){
if (state == 1)
{
    document.attributes.at_analysis.checked=false;
    document.attributes.at_reference.checked=false;
    document.attributes.at_interaction.checked=false;
    document.attributes.at_evidence.checked=false;
    state=0;
}
if (state == 0)
{
    document.attributes.at_analysis.checked=true;
    document.attributes.at_reference.checked=true;
    document.attributes.at_interaction.checked=true;
    document.attributes.at_evidence.checked=true;
    state=1;
}
}});

# send the obligatory Content-Type and print the template output
print "Content-Type: text/html\n\n", $template->output;

###getting the project_name
my $proj='gffparsertest';

###database connection
my $dbh= pazar->new( 
		       -host          =>    $ENV{PAZAR_host},
		       -user          =>    $ENV{PAZAR_pubuser},
		       -pass          =>    $ENV{PAZAR_pubpass},
		       -pazar_user    =>    'elodie@cmmt.ubc.ca',
		       -pazar_pass    =>    'pazarpw',
		       -dbname        =>    $ENV{PAZAR_name},
		       -drv           =>    'mysql',
		       -project       =>    $proj);

my $talkdb = pazar::talk->new(DB=>'ensembl',USER=>$ENV{ENS_USER},PASS=>$ENV{ENS_PASS},HOST=>$ENV{ENS_HOST},DRV=>'mysql');

my $projid = $dbh->get_projectid();

my $get = new CGI;
my %param = %{$get->Vars};

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
        <option value="gene-centric"> Gene-Centric View </option>
        <option value="tf-centric" selected> TF-Centric View </option>
        </select>
        <br><br><hr>
      </td>
    </tr>
    <tr>
      <td colspan="2"><span class="title4"><input name="at_reg_seq" checked="checked" type="checkbox"> Genomic Target (reg_seq): </span></td>
    </tr>
    <tr>
      <td width="50%" valign="top" align="left">
      <p ><input name="at_reg_seq_name" type="checkbox"> Name (if any) </p>
      </td>
      <td width="50%" valign="top" align="left">
      <p ><input name="at_gene" type="checkbox"> Gene </p>
      </td>
    </tr>
    <tr>
      <td width="50%" valign="top" align="left">
      <p ><input name="at_coordinates" type="checkbox"> Coordinates </p>
      </td>
      <td width="50%" valign="top" align="left">
      <p ><input name="at_species" type="checkbox"> Species </p>
      </td>
    </tr>
    <tr>
      <td width="50%" valign="top" align="left">
      <p ><input name="at_quality" type="checkbox"> Quality </p>
      </td>
      <td width="50%" valign="top" align="left">
      </td>
    </tr>
    <tr>
      <td colspan="2"> <br>
      </td>
    </tr>
    <tr>
      <td colspan="2"> <span class="title4"><input name="at_construct" checked="checked" type="checkbox"> Artificial Target (construct): </span></td>
    </tr>
    <tr>
      <td width="50%" valign="top" align="left">
      <p ><input name="at_construct_name" type="checkbox"> Name </p>
      </td>
      <td width="50%" valign="top" align="left">
      <p ><input name="at_description" type="checkbox"> Description (if any) </p>
      </td>
    </tr>
    <tr>
      <td colspan="2"> <br>
      </td>
    </tr>
    <tr>
      <td colspan="2"> <span class="title4"><input name="at_ev" type="checkbox" onclick="javascript:CheckBox()"> Lines of evidence: </span></td>
    </tr>
    <tr>
      <td width="50%" valign="top" align="left">
      <p ><input name="at_analysis" type="checkbox"> Analysis Details </p>
      </td>
      <td width="50%" valign="top" align="left">
      <p ><input name="at_reference" type="checkbox"> Reference (PMID) </p>
      </td>
    </tr>
    <tr>
      <td width="50%" valign="top" align="left">
      <p ><input name="at_interaction" type="checkbox"> Interaction Description </p>
      </td>
      <td width="50%" valign="top" align="left">
      <p ><input name="at_evidence" type="checkbox"> Evidence </p>
      </td>
    </tr>
    <tr>
      <td colspan="2"> <br>
<input type="hidden" name="bp_filter" value=""><input type="hidden" name="chr_filter" value=""><input type="hidden" name="expression_filter" value=""><input type="hidden" name="interaction" value=""><input type="hidden" name="gene" value=""><input type="hidden" name="species_filter" value=""><input type="hidden" name="mutation_filter" value=""><input type="hidden" name="length_filter" value=""><input type="hidden" name="tf" value=""><input type="hidden" name="expression" value=""><input type="hidden" name="chromosome" value=""><input type="hidden" name="evidence" value=""><input type="hidden" name="interaction_filter" value=""><input type="hidden" name="method" value=""><input type="hidden" name="shorter_larger" value=""><input type="hidden" name="bp_end" value=""><input type="hidden" name="class_filter" value=""><input type="hidden" name="method_filter" value=""><input type="hidden" name="region_filter" value=""><input type="hidden" name="construct_filter" value=""><input type="hidden" name="species" value=""><input type="hidden" name="gene_filter" value=""><input type="hidden" name="length" value=""><input type="hidden" name="bp_start" value=""><input type="hidden" name="evidence_filter" value=""><input type="hidden" name="class" value=""><input type="hidden" name="tf_filter" value="">
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
       <form name="hidden_filters" METHOD="post" ACTION="" enctype="multipart/form-data" target="_self">
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

sub select {

    my ($dbh, $sql) = @_;
    my $sth=$dbh->prepare($sql);
    $sth->execute or die "$dbh->errstr\n";
    return $sth;
}
