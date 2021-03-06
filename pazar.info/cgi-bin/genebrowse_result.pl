#!/usr/bin/perl

use DBI;

use CGI qw(:standard);
use CGI;
use CGI::Carp qw(fatalsToBrowser);
use pazar;
use pazar::talk;
use pazar::tf;

my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazarcgipath = $ENV{PAZARCGIPATH};

require "$pazarcgipath/getsession.pl";

print "content-type:text/html\n\n";


my $PAZARDBUSER = $ENV{PAZAR_pubuser};
my $PAZARDBPASS = $ENV{PAZAR_pubpass};
my $DBDRV  = $ENV{PAZAR_drv};
my $PAZARDBURL = "DBI:$DBDRV:dbname=$ENV{PAZAR_name};host=$ENV{PAZAR_host}";


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
                      -dbname        =>    $ENV{PAZAR_name},
                      -drv           =>    $ENV{PAZAR_drv});

my $bg_color = 0;
my %colors = (0 => "#fffff0",
	      1 => "#dadce0"
	      );

#row background color flag for search results

#manual DBI query for letter
my $pazardbh = DBI->connect($PAZARDBURL,$PAZARDBUSER,$PAZARDBPASS)
    or die "Can't connect to pazar database";

my $talkdb = pazar::talk->new(DB=>'ensembl',USER=>$ENV{ENS_USER},PASS=>$ENV{ENS_PASS},HOST=>$ENV{ENS_HOST},PORT => $ENV{ENS_PORT},ENSEMBL_DATABASES_HOST => $ENV{ENSEMBL_DATABASES_HOST},ENSEMBL_DATABASES_USER => $ENV{ENSEMBL_DATABASES_USER},ENSEMBL_DATABASES_PASS => $ENV{ENSEMBL_DATABASES_PASS},DRV=>'mysql');

#use open and published projects for searching
my %gene_project;
my $projects=&select($pazardbh, "SELECT * FROM project WHERE upper(status)='OPEN' OR upper(status)='PUBLISHED'");
if ($projects) {
    my $node=0;
    while (my $project=$projects->fetchrow_hashref) {
	my $pazarsth = $pazardbh->prepare("select * from gene_source where description like '$search_alpha%' and project_id=$project->{project_id}");
	$pazarsth->execute();
#pazar load tfs from results for each result
	while(@res = $pazarsth->fetchrow_array)
	{
	    push(@alpharesults,[@res]);
	}
    }
}

if ($loggedin eq 'true') {
    foreach my $proj (@projids) {
	my $pazarsth2 = $pazardbh->prepare("select * from gene_source where description like '$search_alpha%' and a.project_id='$proj' and a.project_id=b.project_id and upper(status)='RESTRICTED'");
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
<p> <b><a href="$pazar_cgi/genebrowse_alpha.pl">Back</a></b> 
<table width="100%" border="0" cellspacing="1" cellpadding="3">
  <tbody>
    <tr>
      <td width="100" align="center" valign="top" bgcolor="#61b9cf"><b><font
 color="#ffffff">Project</font></b></td>
 <td align="center" width="187" valign="top" bgcolor="#61b9cf"><b><font
 color="#ffffff">Name</font></b></td>    
<td valign="top" bgcolor="#61b9cf"><b><font color="#ffffff">Accession</font></b><br>
      </td> 

<td valign="top" bgcolor="#61b9cf"><b><font color="#ffffff">EnsEMBL Description</font></b><br>
      </td> 
  </tr>
Page_Done



#go through alphabetical results for pazar

foreach my $arrayref (@alpharesults)
{
    #get other info
    my $projname = $pazar->get_project_name('gene_source',$arrayref->[0]);
    my $description;

#get description for this gene
		my $tsrs = &select($pazardbh, "SELECT * FROM tsr WHERE gene_source_id=$arrayref->[0]");
		if ($tsrs) {
		    while (my $tsr=$tsrs->fetchrow_hashref) {
			my $reg_seqs = &select($pazardbh, "SELECT distinct reg_seq.* FROM reg_seq, anchor_reg_seq, tsr WHERE reg_seq.reg_seq_id=anchor_reg_seq.reg_seq_id AND anchor_reg_seq.tsr_id='$tsr->{tsr_id}'");
			if ($reg_seqs) {
			    my @coords = $talkdb->get_ens_chr($arrayref->[2]);
			    my @des = split('\(',$coords[5]);
			    my @desc = split('\[',$des[0]);
			    $description = $desc[0];
			}
		    }
		}


    print<<Page_Done;
    <tr>
 <td width="100" valign="top" bgcolor="$colors{$bg_color}">$projname</td>
<td width="100" valign="top" bgcolor="$colors{$bg_color}">$arrayref->[3]</td>
 <td width="187" valign="top" bgcolor="$colors{$bg_color}"><a name="#$arrayref->[2]"><a href="#$arrayref->[2]" onClick="javascript:window.opener.document.gene_search.geneID.value='$arrayref->[2]';window.opener.document.gene_search.ID_list.options[0].selected=true;window.opener.focus();window.close();">$arrayref->[2]</a></td><td width="100" valign="top" bgcolor="$colors{$bg_color}">$description</td>
Page_Done

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

sub select {

    my ($dbh, $sql) = @_;
    my $sth=$dbh->prepare($sql);
    $sth->execute or die "$dbh->errstr\n";
    return $sth;
}
