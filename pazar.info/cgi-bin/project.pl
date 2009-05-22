#!/usr/bin/perl

use HTML::Template;
#use Data::Dumper;
use pazar;
use pazar::reg_seq;
use pazar::talk;
use pazar::tf::tfcomplex;
use pazar::tf::subunit;
use CGI qw(:standard);
use CGI::Carp qw(fatalsToBrowser);
#use CGI::Debug( report => 'everything', on => 'anything' );

my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};

require "$pazarcgipath/getsession.pl";
 
# open the html header template
my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");

# fill in template parameters
$template->param(TITLE => "PAZAR - Project View");
$template->param(PAZAR_HTML => $pazar_html);
$template->param(PAZAR_CGI => $pazar_cgi);
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
    $template->param(LOGOUT => "$info{first} $info{last} logged in. "."<a href=\'$pazar_cgi/logout.pl\'>Log Out</a>");
}
else
{
    #log in link
    $template->param(LOGOUT => "<a href=\'$pazar_cgi/login.pl\'>Log In</a>");
}

# send the obligatory Content-Type and print the template output
print "Content-Type: text/html\n\n", $template->output;

my $get = new CGI;
my %param = %{$get->Vars};

###getting the project_name
my $proj=$param{project_name};
unless ($proj) {
	print h2("Project name should be defined. Try again. If you believe this to be an error, contact the site administrators below");
	print '<a href="mailto:pazar@cmmt.ubc.ca?subject=Bug report on project.pl">Bug report</a>';
	print end_html;
	exit();
}

###database connection
my $dbh0= pazar->new( 
		       -host          =>    $ENV{PAZAR_host},
		       -user          =>    $ENV{PAZAR_pubuser},
		       -pass          =>    $ENV{PAZAR_pubpass},
		       -dbname        =>    $ENV{PAZAR_name},
		       -drv           =>    $ENV{PAZAR_drv},
		       -globalsearch  =>    'yes');


my $stat = &select($dbh0, "SELECT status, description FROM project WHERE project_name='$proj'");
my ($status, $descrip) = $stat->fetchrow_array;

my $dbh;
if ($status=~/open/i || $status=~/published/i) {
### global database connection
$dbh= pazar->new( 
		       -host          =>    $ENV{PAZAR_host},
		       -user          =>    $ENV{PAZAR_pubuser},
		       -pass          =>    $ENV{PAZAR_pubpass},
		       -dbname        =>    $ENV{PAZAR_name},
		       -drv           =>    $ENV{PAZAR_drv},
		       -project       =>    $proj);
} elsif ($status=~/restricted/i) {
### user specific database connection
$dbh= pazar->new( 
		       -host          =>    $ENV{PAZAR_host},
		       -user          =>    $ENV{PAZAR_pubuser},
		       -pass          =>    $ENV{PAZAR_pubpass},
		       -pazar_user    =>    $info{user},
		       -pazar_pass    =>    $info{pass},
		       -dbname        =>    $ENV{PAZAR_name},
		       -drv           =>    $ENV{PAZAR_drv},
		       -project       =>    $proj);
}

my $talkdb = pazar::talk->new(DB=>'ensembl',USER=>$ENV{ENS_USER},PASS=>$ENV{ENS_PASS},HOST=>$ENV{ENS_HOST},DRV=>'mysql');

my $projid = $dbh->get_projectid();

print "<h1>PAZAR Project View: \'$proj\' <a href='$pazar_cgi/help_FAQ.pl#5.%20Search%20within%20a%20specific%20Boutique%20Project' target='helpwin' onClick=\"window.open('about:blank','helpwin');\"><img src=\"$pazar_html/images/help.gif\" alt='Help' align='bottom' width=12></a></h1>";
print "<p><span class=\"title4\">Description</span><br>";
print $descrip."<br>";
print "</p>";

print "<p><span class=\"title4\">Statistics</span><br>";

my $mnb=&select($dbh, "SELECT count(distinct db_accn) FROM marker WHERE project_id='$projid'");
my $markernb=$mnb->fetchrow_array||'0';

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
my $refnb=&select($dbh, "SELECT count(ref_id) FROM ref WHERE project_id='$projid'");
my $refsnb=$refnb->fetchrow_array||'0';

print "Regulated Genes (or markers): ". ($genenb + $markernb)."<br>";
print "Regulatory sequence (genomic): ".$regseqnb."<br>";
print "Regulatory sequence (artificial): ".$constrnb."<br>";
print "Transcription Factors: ".$tfnb."<br>";
print "Transcription Factor Profiles: ".$matrixnb."<br>";
print "Annotated Publications: ".$refsnb."<br>";
print "</p><br>";
if ($genenb==0&&$regseqnb==0&&$constrnb==0&&$tfnb==0&&$matrixnb!=0) {
    print "<p class=\"warning\"> This project only holds pre-computed profiles.<br>Please use the TF PROFILES search engine to look at those profiles.</p>";
} else {
print "<span class=\"title4\">Search Engine</span><br>";

print<<page1;
<table>
<tbody>
<form name="filters" METHOD="post" ACTION="$pazar_cgi/proj_res.cgi" enctype="multipart/form-data" target="_self">
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
      <td class='basictdnoborder'>
      <input type="checkbox" name="species_filter"></td>
<td class='basictdnoborder'><b> Restrict to one or more species: </b></td></tr>
         <tr><td class='basictdnoborder'> <br> </td>
<td class='basictdnoborder'>
<select name="species" size="3" multiple="multiple">
page1b

    foreach (@sortedsp) {
	print "<option value=\"$_\"> $_ </option>";
    }
print "</select><br><br></td></tr>";
}

my $chr = &select($dbh, "SELECT chr FROM location WHERE project_id=$projid");
if ($chr) {

print<<page2;
    <tr>
      <td class='basictdnoborder'>
      <input type="checkbox" name="region_filter" onclick="javascript:CheckBox()"></td>
<td class='basictdnoborder'><b> Restrict to a specific region: </b></td></tr>
         <tr><td class='basictdnoborder'> <br> </td>
<td class='basictdnoborder'>
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
	<input name="bp_start" value="" type="text"><br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;end
	<input name="bp_end" value="" type="text"><br><br>
      </td>
    </tr>
page2b
}

my $markercount=$dbh->prepare("SELECT count(*) FROM marker WHERE project_id='$projid'")||die DBI::errstr;
$markercount->execute||die;

my $mc = $markercount->fetchrow_array;

my $checkcount=$dbh->prepare("SELECT count(*) FROM gene_source a, tsr b WHERE a.project_id='$projid' and a.gene_source_id=b.gene_source_id")||die DBI::errstr;
$checkcount->execute||die;

my $gc=$checkcount->fetchrow_array;

unless (($gc+$mc)>1000) {

	#display both genes and markers

my $mh=$dbh->prepare("SELECT * FROM marker WHERE project_id=?")||die DBI::errstr;
        $mh->execute($projid)||die DBI::errstr;

	my $gh=$dbh->prepare("SELECT * FROM gene_source a, tsr b WHERE a.project_id=? and a.gene_source_id=b.gene_source_id")||die DBI::errstr;
	$gh->execute($projid)||die DBI::errstr;

	while (my $gene=$gh->fetchrow_hashref) {
	    my @coords = $talkdb->get_ens_chr($gene->{db_accn});
	    $coords[5]=~s/\[.*\]//g;
	    $coords[5]=~s/\(.*\)//g;
	    $coords[5]=~s/\.//g;
	    $gene{$gene->{db_accn}}=$coords[5]||'-';
	}

	#now add markers tp $gene hashtable
        while (my $marker=$mh->fetchrow_hashref) {
            my @coords = $talkdb->get_ens_chr($marker->{db_accn});
            $coords[5]=~s/\[.*\]//g;
            $coords[5]=~s/\(.*\)//g;
            $coords[5]=~s/\.//g;
            $gene{$marker->{db_accn}}=$coords[5]||'-';
        }


	if (%gene) {

print<<page3;
    <tr>
      <td class='basictdnoborder'>
      <input type="checkbox" name="gene_filter"></td>
<td class='basictdnoborder'><b> Restrict to one or more Regulated Genes (or markers): </b></td></tr>
         <tr><td class='basictdnoborder'> <br> </td>
<td class='basictdnoborder'>
        <select name="gene" size="3" multiple="multiple">
page3

	my @sortedaccn=sort {lc($gene{$a}) cmp lc($gene{$b})} (keys %gene);
	foreach my $accn (@sortedaccn) {
		print "<option value=\"$accn\"> $gene{$accn} ($accn) </option>";
	    }
	print "</select><br><br></td></tr>";
	}
} #unless > 1000
else  {
print<<page3a;
<tr><td></td><td>
<span style="color:red">Browse by gene disabled- over 1000 genes in this project</span>
</td></tr>
page3a
}

print<<page4;
    <tr>
      <td class='basictdnoborder'>
      <input type="checkbox" name="length_filter"></td>
<td class='basictdnoborder'><b> Restrict to sequences </b>
        <select name="shorter_larger">
        <option value="greater_than" selected> Greater than </option>
        <option value="less_than" > Less than </option>
        <option value="equal_to" > Equal to </option>
        </select>
	<input type="text" name="length"><b> bases </b><br><br>
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
      <td class='basictdnoborder'>
      <input type="checkbox" name="tf_filter"></td>
<td class='basictdnoborder'><b> Restrict to one or more Regulating Factor: </b></td></tr>
         <tr><td class='basictdnoborder'> <br> </td>
<td class='basictdnoborder'>
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
print "</select><br><br></td></tr>";
}

my $classes = &select($dbh, "SELECT class, family FROM tf WHERE project_id=$projid");
if ($classes) {

print<<page5;
    <tr>
      <td class='basictdnoborder'>
      <div><input type="checkbox" name="class_filter"></td>
<td class='basictdnoborder'><b> Restrict to a specific class/family: </b></div></td></tr>
         <tr><td class='basictdnoborder'> <br> </td>
<td class='basictdnoborder'>
        <select name="classes">
page5

    my @classes;
    while (my ($class,$fam)=$classes->fetchrow_array) {
	    my $fam2=!$fam?'':'/'.$fam;
	    my $cf=!$class?'':$class.$fam2;
	unless (grep(/$cf/i,@classes)||!$cf) {
	    push @classes,$cf;
	}
    }
    my @sortedcf=sort(@classes);
    foreach (@sortedcf) {
	print "<option value=\"$_\"> $_ </option>";
    }
print "</select><br><br></td></tr>";
}

print<<page6;
    <tr>
      <td class='basictdnoborder'>
      <input type="checkbox" name="interaction_filter"></td>
<td class='basictdnoborder'><b> Restrict to sequences when interaction is </b>
        <select name="interaction">
        <option value="not_null" selected> Not NULL </option>
        <option value="none" > NULL </option>
        <option value="poor" > poor </option>
        <option value="marginal" > marginal </option>
        <option value="good" > good </option>
        <option value="saturation" > saturation </option>
        </select><br><br>
      </td>
    </tr>
    <tr>
      <td class='basictdnoborder'>
      <input type="checkbox" name="expression_filter"></td>
<td class='basictdnoborder'><b> Restrict to sequences when expression is </b>
        <select name="expression">
        <option value="change" selected> changed </option>
        <option value="no change" > not changed </option>
        <option value="highly induced" > highly induced </option>
        <option value="induced" > induced </option>
        <option value="repressed" > repressed </option>
        <option value="strongly repressed" > strongly repressed </option>
        </select><br><br>
      </td>
    </tr>
    <tr>
      <td class='basictdnoborder'>
      <div><input type="checkbox" name="evidence_filter"></td>
<td class='basictdnoborder'><b> Restrict to
one or more evidence type(s): </b></div></td></tr>
         <tr><td class='basictdnoborder'> <br> </td>
<td class='basictdnoborder'>
        <select name="evidence" size="3" multiple="multiple">
        <option value="ADMC"> ADMC </option>
        <option value="curated"> curated </option>
        <option value="predicted"> predicted </option>
        </select><br><br>
      </td>
    </tr>
    <tr>
      <td class='basictdnoborder'>
      <div><input type="checkbox" name="method_filter"></td>
<td class='basictdnoborder'><b>Restrict to
one or more method(s): </b></div></td></tr>
         <tr><td class='basictdnoborder'> <br> </td>
<td class='basictdnoborder'>
        <select name="method" size="3" multiple="multiple">
page6

my @methods = $dbh->get_method_names();
my @sortedmet=sort(@methods);
foreach (@sortedmet) {
    print "<option value=\"$_\"> $_ </option>";
}


print<<page7;
        </select><br><br>
      </td>
    </tr>
    <tr>
      <td class='basictdnoborder'><br></td>
<td class='basictdnoborder'>
<input type="reset" VALUE="Reset">&nbsp;&nbsp;&nbsp;&nbsp;
<input type="submit" name="submit" VALUE="Submit to Gene View">&nbsp;&nbsp;&nbsp;&nbsp;
<input type="submit" name="submit" VALUE="Submit to TF View">
      </td>
    </tr>
    </form>
</tbody>
</table>
page7
}

###  print out the html tail template
  my $template_tail = HTML::Template->new(filename => "$pazarcgipath/tail.tmpl");
  print $template_tail->output;

sub select {

    my ($dbh, $sql) = @_;
    my $sth=$dbh->prepare($sql);
    $sth->execute or die "$dbh->errstr\n";
    return $sth;
}
