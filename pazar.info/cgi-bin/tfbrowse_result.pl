#!/usr/local/bin/perl

use DBI;

use CGI qw(:standard);
use CGI;
#use CGI::Carp qw(fatalsToBrowser);
use pazar;
use pazar::talk;
use pazar::tf;

require 'getsession.pl';

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
                      -host          =>    $ENV{PAZAR_host},
                      -user          =>    $ENV{PAZAR_pubuser},
                      -pass          =>    $ENV{PAZAR_pubpass},
                      -dbname        =>    $ENV{PAZAR_name},
                      -drv           =>    'mysql');

my $bg_color = 0;
my %colors = (0 => "#fffff0",
	      1 => "#dadce0"
	      );

#row background color flag for search results

#manual DBI query for letter
my $pazardbh = DBI->connect($PAZARDBURL,$PAZARDBUSER,$PAZARDBPASS)
    or die "Can't connect to pazar database";
my $pazarsth = $pazardbh->prepare("select * from funct_tf a, project b where funct_tf_name like '$search_alpha%' and a.project_id=b.project_id and upper(status)<>'RESTRICTED'");
$pazarsth->execute();
#pazar load tfs from results for each result
while(my @res = $pazarsth->fetchrow_array) {
    push(@alpharesults,[@res]);
}
if ($loggedin eq 'true') {
    foreach my $proj (@projids) {
	my $pazarsth2 = $pazardbh->prepare("select * from funct_tf a, project b where funct_tf_name like '$search_alpha%' and a.project_id='$proj' and a.project_id=b.project_id and upper(status)='RESTRICTED'");
        $pazarsth2->execute();
#pazar load tfs from results for each result
	while(my @res2 = $pazarsth2->fetchrow_array) {
	    push(@alpharesults,[@res2]);
	}
    }
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
 <td width="100" align="center" valign="top" bgcolor="#61b9cf"><b><font
 color="#ffffff">Project</font></b></td>
 <td align="center" width="187" valign="top" bgcolor="#61b9cf"><b><font
 color="#ffffff">Name</font></b></td>
 <td valign="top" bgcolor="#61b9cf"><b><font color="#ffffff">Transcript Accession</font></b><br></td> 
 <td valign="top" bgcolor="#61b9cf"><b><font color="#ffffff">Class</font></b><br></td> 
 <td valign="top" bgcolor="#61b9cf"><b><font color="#ffffff">Family</font></b><br></td> 
 </tr>
Page_Done

#set globalsearch to no
    $pazar->{globalsearch}='no';

#go through alphabetical results for pazar

    foreach my $arrayref (@alpharesults)
    {
    #get other info
    #retrieve for all public projects
    my @complex_ids = $pazar->get_complex_id_by_name($arrayref->[1],$arrayref->[4]);
    my $projname = $pazar->get_project_name('funct_tf',$complex_ids[0]);
    print<<Page_Done;
    <tr>
      <td width="100" valign="top" bgcolor="$colors{$bg_color}">$projname</td>
 <td width="187" valign="top" bgcolor="$colors{$bg_color}"><a name="#$arrayref->[1]"><a href="#$arrayref->[1]" onClick="javascript:window.opener.document.tf_search.geneID.value='$arrayref->[1]';window.opener.document.tf_search.ID_list.options[5].selected=true;window.opener.focus();window.close();">$arrayref->[1]</a></td>
Page_Done

    #get classes,families, transcript accessions
    my @classes = ();
    my @families = ();
    my @transcript_accessions = ();
    my $tf=$pazar->create_tf();
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
    #transcript accession
    my @accns;
    foreach my $ta (@transcript_accessions)
    {
	my $ta_link="<a href=\"#$arrayref->[1]\" onClick=\"javascript:window.opener.document.tf_search.geneID.value='$ta';window.opener.document.tf_search.ID_list.options[1].selected=true;window.opener.focus();window.close();\">".$ta."</a>";
	push @accns, $ta_link;
    }
    print join('<br>',@accns);
    print  "&nbsp;</td>";
    print "<td bgcolor=\"$colors{$bg_color}\">";
    #class
    print join('<br>',@classes);
    print "&nbsp;</td>";
    print "<td bgcolor=\"$colors{$bg_color}\">";
    #family
    print join('<br>',@families);
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
