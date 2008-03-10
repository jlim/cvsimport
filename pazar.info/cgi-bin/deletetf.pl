#!/usr/local/bin/perl

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
my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");

# fill in template parameters
$template->param(TITLE => 'PAZAR Gene View');
$template->param(PAZAR_HTML => $pazar_html);
$template->param(PAZAR_CGI => $pazar_cgi);
print "Content-Type: text/html\n\n", $template->output;

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
#if yes, check mode

=pod
if($mode eq "form")
{
    print<<FORM_DONE;
    <form method="post" action="updategenename.pl">
    <input type="hidden" name="mode" value="update">
<input type="hidden" name="gid" value="$geneid">
<input type="hidden" name="pid" value="$projectid">
    <table><tr><td>Enter gene name here: </td><td><textarea name="genename" cols=30 rows=10></textarea></td></tr></table>
    <input type="submit" value="submit">
    </form>
FORM_DONE
}
elsif ($mode eq "update")
{
$dbh->do("update gene_source set description='$genename' where gene_source_id=$geneid");

#more HTML
    print "<script>window.opener.document.getElementById('ajaxgenename').innerHTML=\"$genename\"</script>";
    print "Gene name updated<br><input type='button' value='Close window' onClick=javascript:window.close();>";

}

=cut
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
