#!/usr/local/bin/perl

use DBI;

use CGI qw(:standard);
use CGI;
use CGI::Carp qw(fatalsToBrowser);
use pazar;
use pazar::talk;
use pazar::tf;

print "content-type:text/html\n\n";


$PAZARDBUSER = $ENV{PAZAR_pubuser};
$PAZARDBPASS = $ENV{PAZAR_pubpass};
$PAZARDBURL = "DBI:mysql:dbname=$ENV{PAZAR_name};host=$ENV{PAZAR_host}";


my $search_alpha = param("search_alpha");
local @results = ();
my @complexes = ();

#stores array refs of results from alphabetical search
my @alpharesults = ();


my $pazar = pazar->new(
                      -globalsearch  =>    'yes',
                      -host          =>    $ENV{PAZAR_host},
                      -user          =>    $ENV{PAZAR_pubuser},
                      -pass          =>    $ENV{PAZAR_pubpass},
                      -pazar_user    =>    'elodie@cmmt.ubc.ca',
                      -pazar_pass    =>    'pazarpw',
                      -dbname        =>    $ENV{PAZAR_name},
                      -drv           =>    'mysql');

#load tf from pazar
my $tf = $pazar->create_tf;

my $bg_color = 0;
my %colors = (0 => "#fffff0",
	      1 => "#dadce0"
	      );

#row background color flag for search results

#manual DBI query for letter
my $pazardbh = DBI->connect($PAZARDBURL,$PAZARDBUSER,$PAZARDBPASS)
    or die "Can't connect to pazar database";
my $pazarsth = $pazardbh->prepare("select * from funct_tf where funct_tf_name like '$search_alpha%'");
    $pazarsth->execute();
#pazar load tfs from results for each result
while(@res = $pazarsth->fetchrow_array)
{
    push(@alpharesults,[@res]);
}




print<<Page_Done;
<html>
<head>
  <title></title>
</head>
 <body bgcolor="#ffffff">
<p> <b><a href="tfbrowse_alpha.pl">Back</a></b> 
<table width="100%" border="0" cellspacing="1" cellpadding="3">
  <tbody>
    <tr>
      <td width="100" align="center" valign="top" bgcolor="#00007f"><b><font
 color="#ffffff">Project</font></b></td>
 <td align="center" width="187" valign="top" bgcolor="#00007f"><b><font
 color="#ffffff">Name</font></b></td>
      <td valign="top" bgcolor="#00007f"><b><font color="#ffffff">Classes</font></b><br>
      </td> 

<td valign="top" bgcolor="#00007f"><b><font color="#ffffff">Transcript Accessions</font></b><br>
      </td> 

<td valign="top" bgcolor="#00007f"><b><font color="#ffffff">Families</font></b><br>
      </td> 
  </tr>
Page_Done



#go through alphabetical results for pazar

    foreach my $arrayref (@alpharesults)
    {
    #get other info
    #retrieve for all public projects
    my @complex_ids = $pazar->get_complex_id_by_name($arrayref->[1]);
    my $projname = $pazar->get_project_name('funct_tf',$complex_ids[0]);
    print<<Page_Done;
    <tr>
      <td width="100" valign="top" bgcolor="$colors{$bg_color}">$projname</td>
 <td width="187" valign="top" bgcolor="$colors{$bg_color}"><a name="#$arrayref->[1]"><a href="#$arrayref->[1]" onClick="javascript:window.opener.document.tf_search.geneID.value='$arrayref->[1]';window.opener.document.tf_search.ID_list.options[5].selected=true;window.opener.focus();">$arrayref->[1]</a></td>
Page_Done

    #get classes,families, transcript accessions
    my @classes = ();
    my @families = ();
    my @transcript_accessions = ();

    foreach my $complex_id (@complex_ids)
    {
	my $tfcomplex = $tf->get_tfcomplex_by_id($complex_id,'notargets');
	while (my $subunit=$tfcomplex->next_subunit) {
		push(@classes,$subunit->{class});
		push(@families,$subunit->{family});
		push(@transcript_accessions, $subunit->get_transcript_accession($pazar));
            }
    }

    #print subunit information
    print "<td bgcolor=\"$colors{$bg_color}\">";
    #class
    foreach my $c (@classes)
    {
	print $c."<br>";
    }
    print "&nbsp;</td>";
    print "<td bgcolor=\"$colors{$bg_color}\">";
    #transcript accession
    foreach my $ta (@transcript_accessions)
    {
	print "<a href=\"#$arrayref->[1]\" onClick=\"javascript:window.opener.document.tf_search.geneID.value='$ta';window.opener.document.tf_search.ID_list.options[1].selected=true;window.opener.focus();\">".$ta."</a><br>";
    }
    print  "&nbsp;</td>";
    print "<td bgcolor=\"$colors{$bg_color}\">";
    #family
    foreach my $f (@families)
    {
	print $f."<br>";
    }
    print "&nbsp;</td>";
    print  "</tr>";
    $bg_color = 1 - $bg_color;
}

    print<<Page_Done;
  </tbody>
</table>
 <br>
</body>
</html>
Page_Done
