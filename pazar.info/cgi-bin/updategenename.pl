#!/usr/bin/perl

use pazar;
use pazar::gene;
use pazar::talk;

use HTML::Template;

use CGI qw(:standard);
use CGI::Carp qw(fatalsToBrowser);
###use CGI::Debug( report => 'everything', on => 'anything' );

#use Data::Dumper;

my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};

require "$pazarcgipath/getsession.pl";

# open the html header template
print "Content-Type: text/html\n\n";
#get userinfo
my $get = new CGI;
my %params = %{$get->Vars};

if($loggedin eq 'true')
{

my $dbname = $ENV{PAZAR_name};
my $dbhost = $ENV{PAZAR_host};

my $DBUSER = $ENV{PAZAR_adminuser};
my $DBPASS = $ENV{PAZAR_adminpass};
my $DBDRV  = $ENV{PAZAR_drv};

my $DBURL  = "DBI:$DBDRV:dbname=$dbname;host=$dbhost";

my $dbh = DBI->connect($DBURL,$DBUSER,$DBPASS)
    or die "Can't connect to pazar database";

#get analysis id and project id
    my $geneid = $params{gid};

    my $genetype = $params{genetype};

    my $projectid = $params{pid};
    my $mode = $params{mode};
    my $genename = $params{genename};
    my $genenameeditable = "false";

	foreach my $proj (@projids) {
	#see if $proj is the same as the analysis project or if my userid is same as analysis user_id
	    if($proj == $projectid)
	    {
		#comments are editable
		$genenameeditable = "true";
	    }
	}
#make sure user is a member of the project

if($genenameeditable eq "true")
{
=pod
#if yes,
# perform update mode pre-check
    if($mode eq "update")
    {
# make sure new tfname doesn't exist within this project
	my $genenameinuse = "false";
	my $genesth = $dbh->prepare("select * from gene_source where description='$genename' and project_id=$projectid");
	$genesth->execute;
	
	if(my $genehref = $genesth->fetchrow_hashref)
	{
	    $genenameinuse = "true";
	}
	if($genenameinuse eq "true")
	{
	    $mode = "form";
	    print "<font color='red'>The gene name entered is already in use. Please use a different name.</font>";
	}
	#otherwise genename is not in use and we can continue with update
    }
=cut
# perform action depending on mode

if($mode eq "form")
{
    print<<FORM_DONE;
    <form method="post" action="updategenename.pl">
    <input type="hidden" name="mode" value="update">
<input type="hidden" name="gid" value="$geneid">
<input type="hidden" name="pid" value="$projectid">
    <table><tr><td>Enter gene name here: </td><td><input type=text size=30 name="genename"></td></tr></table>
    <input type="submit" value="submit">
    </form>
FORM_DONE
}
elsif ($mode eq "update")
{

	if($genetype eq "marker")
	{
		$dbh->do("update marker set description='$genename' where marker_id=$geneid");
	}
	else
	{
		$dbh->do("update gene_source set description='$genename' where gene_source_id=$geneid");
	}

#more HTML
    print "<script>window.opener.document.getElementById('ajaxgenename').innerHTML=\"$genename\"</script>";
    print "Gene name updated<br><input type='button' value='Close window' onClick=javascript:window.close();>";

}


}
#if no, display error
else
{
    print "You are not authorized to update the name of this gene";
}
}
else
{
    print "You must be logged in to update gene name";
}
