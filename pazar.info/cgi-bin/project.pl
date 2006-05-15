#!/usr/bin/perl

use HTML::Template;
use Data::Dumper;
use pazar;
use pazar::reg_seq;
use pazar::talk;
use pazar::tf::tfcomplex;
use pazar::tf::subunit;
use CGI qw(:standard);
use CGI::Carp qw(fatalsToBrowser);
#use CGI::Debug( report => 'everything', on => 'anything' );

require 'getsession.pl';
 
# open the html header template
my $template = HTML::Template->new(filename => 'header.tmpl');

# fill in template parameters
$template->param(TITLE => "PAZAR - Project Search Engine");
$template->param(JAVASCRIPT_FUNCTION => q{
var state=0;
function CheckBox(){
if (state == 1)
{
    document.filters.chr_filter.checked=false;
    state=0;
}
if (state == 0)
{
    document.filters.chr_filter.checked=true;
    state=1;
}
}});

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

my $get = new CGI;
my %param = %{$get->Vars};

###getting the project_name
my $proj=$param{project_name};

###database connection
my $dbh0= pazar->new( 
		       -host          =>    $ENV{PAZAR_host},
		       -user          =>    $ENV{PAZAR_pubuser},
		       -pass          =>    $ENV{PAZAR_pubpass},
		       -dbname        =>    $ENV{PAZAR_name},
		       -drv           =>    'mysql',
		       -globalsearch  =>    'yes');

my $stat = &select($dbh0, "SELECT status FROM project WHERE project_name='$proj'");
my $status=$stat->fetchrow_array;

### add description when the schema is changed
#my $stat = &select($dbh, "SELECT status, description FROM project WHERE project_name='$proj'");
#my ($status, $descrip) = $stat->fetchrow_array;

my $dbh;
if ($status eq 'open' || $status eq 'published') {
### global database connection
$dbh= pazar->new( 
		       -host          =>    $ENV{PAZAR_host},
		       -user          =>    $ENV{PAZAR_pubuser},
		       -pass          =>    $ENV{PAZAR_pubpass},
		       -dbname        =>    $ENV{PAZAR_name},
		       -drv           =>    'mysql',
		       -project       =>    $proj);
} elsif ($status eq 'restricted') {
### user specific database connection
$dbh= pazar->new( 
		       -host          =>    $ENV{PAZAR_host},
		       -user          =>    $ENV{PAZAR_pubuser},
		       -pass          =>    $ENV{PAZAR_pubpass},
		       -pazar_user    =>    $info{user},
		       -pazar_pass    =>    $info{pass},
		       -dbname        =>    $ENV{PAZAR_name},
		       -drv           =>    'mysql',
		       -project       =>    $proj);
}

my $talkdb = pazar::talk->new(DB=>'ensembl',USER=>$ENV{ENS_USER},PASS=>$ENV{ENS_PASS},HOST=>$ENV{ENS_HOST},DRV=>'mysql');

my $projid = $dbh->get_projectid();

print "<p class=\"title1\">PAZAR - $proj</p>";
print "<p><span class=\"title4\">Description</span><br>";
### add description when the schema is changed
#print $descrip."<br>";
print "</p>";

print "<p><span class=\"title4\">Statistics</span><br>";
my $gnb=&select($dbh, "SELECT count(distinct db_accn) FROM gene_source a, tsr b WHERE a.project_id='$projid' and a.gene_source_id=b.gene_source_id");
my $genenb=$gnb->fetchrow_array||'0';
my $rnb=&select($dbh, "SELECT count(reg_seq_id) FROM reg_seq WHERE project_id='$projid'");
my $regseqnb=$rnb->fetchrow_array||'0';
my $cnb=&select($dbh, "SELECT count(construct_id) FROM construct WHERE project_id='$projid'");
my $constrnb=$cnb->fetchrow_array||'0';
my $tnb=&select($dbh, "SELECT count(funct_tf_id) FROM funct_tf WHERE project_id='$projid'");
my $tfnb=$tnb->fetchrow_array||'0';
my $mnb=&select($dbh, "SELECT count(matrix_id) FROM matrix WHERE project_id='$projid'");
my $matrixnb=$mnb->fetchrow_array||'0';

print "Regulated Genes: ".$genenb."<br>";
print "Regulatory sequence (genomic): ".$regseqnb."<br>";
print "Regulatory sequence (artificial): ".$constrnb."<br>";
print "Transcription Factors: ".$tfnb."<br>";
print "Transcription Factor Profiles: ".$matrixnb."<br></p>";

if ($genenb==0&&$regseqnb==0&&$constrnb==0&&$tfnb==0&&$matrixnb!=0) {
    print "<p class=\"warning\"> This project only holds pre-computed profiles.<br>Please use the TF PROFILES search engine to look at those profiles.</p>";
} else {
print "<span class=\"title4\">Search Engine</span><br>";

print<<page1;
<table>
<tbody>
<form name="filters" METHOD="post" ACTION="http://www.pazar.info/cgi-bin/proj_gene_att.cgi" enctype="multipart/form-data" target="_self">
    <tr>
      <td colspan="2">
<span class="title3">Filters: </span><br>
      </td>
    </tr>
page1

print "<tr><td><input type=\"hidden\" name=\"project_name\" value=\"$proj\"</td></tr>";

my @species;
my $species = &select($dbh, "SELECT species FROM location WHERE project_id=$projid");
if ($species) {
    while (my $sp=$species->fetchrow_array) {
	if (!grep(/$sp/i,@species)) {
	    push (@species,$sp);
	}
    }
}
my @functs = $dbh->get_all_complex_ids($projid);
foreach my $funct_tf (@functs) {
    my $tf = $dbh->create_tf;
    my $tfcomplex = $tf->get_tfcomplex_by_id($funct_tf,'notargets');
    while (my $subunit=$tfcomplex->next_subunit) {
	my $trans=$subunit->get_transcript_accession($dbh);
        my $gene=$talkdb->ens_transcr_to_gene($trans);
        my $sp=$talkdb->current_org();
	if (!grep(/$sp/i,@species)) {
	    push (@species,$sp);
	}
    }
}

if (@species) {
    my @sortedsp=sort(@species);

print<<page1b;
    <tr>
      <td align="left" valign="top" width="50%">
        <input type="checkbox" name="species_filter"><b> Restrict to one or more species: </b>
      </td>
      <td align="left" valign="top" width="50%">
        <select name="species" size="3" multiple="multiple">
page1b

    foreach (@sortedsp) {
	print "<option value=\"$_\"> $_ </option>";
    }
print "</select></td></tr><tr><td colspan=\"2\"><br></td></tr>";
}

my $chr = &select($dbh, "SELECT chr FROM location WHERE project_id=$projid");
if ($chr) {

print<<page2;
    <tr>
      <td align="left" valign="top" width="50%">
      <input type="checkbox" name="region_filter" onclick="javascript:CheckBox()"><b> Restrict to a specific region: </b>
      </td>
      <td style="text-align:left;" width="50%">
	<input type="checkbox" name="chr_filter">chromosome:&nbsp;
        <select name="chromosome">
page2

    my @chr;
    while (my $ch=$chr->fetchrow_array) {
	if (!grep(/$ch/i,@chr)) {
            push (@chr,$ch); 
        }
    }
    my @sortedch=sort(@chr);
    foreach (@sortedch) {
	print "<option value=\"$_\"> $_ </option>";
    }

print<<page2b;
        </select><br>
	<input type="checkbox" name="bp_filter">base pair: start 
	<input name="bp_start" value="" type="text">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;end
	<input name="bp_end" value="" type="text">
      </td>
    </tr>
    <tr>
      <td colspan="2"> <br>
      </td>
    </tr>
page2b
}

my $genes = &select($dbh, "SELECT * FROM gene_source WHERE project_id=$projid");
my %gene;
if ($genes) {
    while (my $gene=$genes->fetchrow_hashref) {
	my $seq=0;
	my $tsrs = &select($dbh, "SELECT * FROM tsr WHERE gene_source_id='$gene->{gene_source_id}'");
	if ($tsrs) {
	    while (my $tsr=$tsrs->fetchrow_hashref) {
		my $reg_seqs = &select($dbh, "SELECT distinct reg_seq.* FROM reg_seq, anchor_reg_seq, tsr WHERE reg_seq.reg_seq_id=anchor_reg_seq.reg_seq_id AND anchor_reg_seq.tsr_id='$tsr->{tsr_id}'");
		if ($reg_seqs) {
		    $seq=1;
		}
	    }
	}
	if ($seq==1) {
	    my @coords = $talkdb->get_ens_chr($gene->{db_accn});
	    my @des = split('\(',$coords[5]);
	    my @desc = split('\[',$des[0]);
	    $gene{$gene->{db_accn}}=$desc[0];
	}
    }
}
if (%gene) {

print<<page3;
    <tr>
      <td align="left" valign="top" width="50%">
      <input type="checkbox" name="gene_filter"><b> Restrict to one or more Regulated Gene: </b>
      </td>
      <td align="left" valign="top" width="50%">
        <select name="gene" size="3" multiple="multiple">
page3

my @accns = keys %gene;
my @sortedaccn=sort(@accns);
foreach my $accn (@sortedaccn) {
	print "<option value=\"$accn\"> $gene{$accn} ($accn) </option>";
    }
print "</select></td></tr><tr><td colspan=\"2\"><br></td></tr>";
}

print<<page4;
    <tr>
      <td colspan="2">
      <input type="checkbox" name="length_filter"><b> Restrict to sequences </b>
        <select name="shorter_larger">
        <option value="greater_than" selected> Greater than </option>
        <option value="less_than" > Less than </option>
        <option value="equal_to" > Equal to </option>
        </select>
	<input type="text" name="length"><b> bases </b>
      </td>
    </tr>
    <tr>
      <td colspan="2"> <br>
      </td>
    </tr>
page4

my @funct_tfs = $dbh->get_all_complex_ids($projid);
my %tf_subunit;
my $ftf=0;
foreach my $funct_tf (@funct_tfs) {
    $ftf=1;
    my $funct_name = $dbh->get_complex_name_by_id($funct_tf);
    my $tf = $dbh->create_tf;
    my $tfcomplex = $tf->get_tfcomplex_by_id($funct_tf,'notargets');
    while (my $subunit=$tfcomplex->next_subunit) {
	push (@{$tf_subunit{$funct_name}}, $subunit->get_transcript_accession($dbh));
    }
}
if ($ftf==1) {

print<<page4b;
    <tr>
      <td align="left" valign="top" width="50%">
      <input type="checkbox" name="tf_filter"><b> Restrict to one or more Regulating Factor: </b>
      </td>
      <td align="left" valign="top" width="50%">
        <select name="tf" size="3" multiple="multiple">
page4b

my @tfnames = keys %tf_subunit;
my @sortedtfname=sort(@tfnames);
    foreach my $name (@sortedtfname) {
	print "<option value=\"$name\"> $name (";
	foreach my $su (@{$tf_subunit{$name}}) {
	    print "$su ";
	}
	print ")</option>";
    }
print "</select></td></tr><tr><td colspan=\"2\"><br></td></tr>";
}

my $classes = &select($dbh, "SELECT class, family FROM tf WHERE project_id=$projid");
if ($classes) {

print<<page5;
    <tr>
      <td align="left" valign="top" width="50%">
      <div><input type="checkbox" name="class_filter"><b> Restrict to a specific class/family: </b></div>
      </td>
      <td align="left" valign="top" width="50%">
        <select name="classes">
page5

    my $cf;
    my @classes;
    while (my ($class,$fam)=$classes->fetchrow_array) {
	if ($class && $fam) {
	    $cf=$class."/".$fam;
	} elsif ($class && !$fam) {
	    $cf=$class;
	}
	if (!grep(/$cf/i,@classes)) {
	    push @classes,$cf;
	}
    }
    my @sortedcf=sort(@classes);
    foreach (@sortedcf) {
	print "<option value=\"$_\"> $_ </option>";
    }
print "</select></td></tr><tr><td colspan=\"2\"><br></td></tr>";
}

print<<page6;
    <tr>
      <td colspan="2">
      <input type="checkbox" name="interaction_filter"><b> Restrict to sequences when interaction is </b>
        <select name="interaction">
        <option value="not_null" selected> Not NULL </option>
        <option value="none" > NULL </option>
        <option value="poor" > poor </option>
        <option value="marginal" > marginal </option>
        <option value="good" > good </option>
        <option value="saturation" > saturation </option>
        </select>
      </td>
    </tr>
    <tr>
      <td colspan="2"> <br>
      </td>
    </tr>
    <tr>
      <td colspan="2">
      <input type="checkbox" name="expression_filter"><b> Restrict to sequences when expression is </b>
        <select name="expression">
        <option value="change" selected> changed </option>
        <option value="no change" > not changed </option>
        <option value="highly induced" > highly induced </option>
        <option value="induced" > induced </option>
        <option value="repressed" > repressed </option>
        <option value="strongly repressed" > strongly repressed </option>
        </select>
      </td>
    </tr>
    <tr>
      <td colspan="2"> <br>
      </td>
    </tr>
    <tr>
      <td align="left" valign="top" width="50%">
      <div><input type="checkbox" name="evidence_filter"><b> Restrict to
one or more evidence type(s): </b></div>
      </td>
      <td width="50%">
        <select name="evidence" size="3" multiple="multiple">
        <option value="ADMC"> ADMC </option>
        <option value="curated"> curated </option>
        <option value="predicted"> predicted </option>
        </select>
      </td>
    </tr>
    <tr>
      <td colspan="2"> <br>
      </td>
    </tr>
    <tr>
      <td align="left" valign="top" width="50%">
      <div><input type="checkbox" name="method_filter"><b>Restrict to
one or more method(s): </b></div>
      </td>
      <td width="50%">
        <select name="method" size="3" multiple="multiple">
page6

my @methods = $dbh->get_method_names();
my @sortedmet=sort(@methods);
foreach (@sortedmet) {
    print "<option value=\"$_\"> $_ </option>";
}


print<<page7;
        </select>
      </td>
    </tr>
    <tr>
      <td colspan="2"> <br><hr><br>
      </td>
    </tr>
    <tr>
      <td align="right" valign="top" width="50%">
        <input type="reset" VALUE="Reset">
      </td>
      <td width="50%">
        <input type="submit" VALUE="Next">
      </td>
    </tr>
    </form>
</tbody>
</table>
page7
}

###  print out the html tail template
  my $template_tail = HTML::Template->new(filename => 'tail.tmpl');
  print $template_tail->output;

sub select {

    my ($dbh, $sql) = @_;
    my $sth=$dbh->prepare($sql);
    $sth->execute or die "$dbh->errstr\n";
    return $sth;
}
