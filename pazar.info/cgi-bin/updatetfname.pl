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
    my $tfid = $params{tfid};
    my $projectid = $params{pid};
    my $mode = $params{mode};
    my $tfname = $params{tfname};
my $tfnameeditable = "false";

	foreach my $proj (@projids) {
	#see if $proj is the same as the analysis project or if my userid is same as analysis user_id
	    if($proj == $projectid)
	    {
		#comments are editable
		$tfnameeditable = "true";
	    }
	}
#make sure user is a member of the project

if($tfnameeditable eq "true")
{
#if yes,
# perform update mode pre-check
    if($mode eq "update")
    {
# make sure new tfname doesn't exist within this project
	my $tfnameinuse = "false";
	my $tfsth = $dbh->prepare("select * from funct_tf where funct_tf_name='$tfname' and project_id=$projectid");
	$tfsth->execute;
	
	if(my $tfhref = $tfsth->fetchrow_hashref)
	{
	    $tfnameinuse = "true";
	}


	if($tfnameinuse eq "true")
	{
	    $mode = "form";
	    print "<font color='red'>The TF name entered is already in use. Please use a different name.</font>";
	}
	#otherwise tfname is not in use and we can continue with update
    }

# peform action depending on mode

if($mode eq "form")
{
    print<<FORM_DONE;
    <form method="post" action="updatetfname.pl">
    <input type="hidden" name="mode" value="update">
<input type="hidden" name="tfid" value="$tfid">
<input type="hidden" name="pid" value="$projectid">
    <table><tr><td>Enter tf name here: </td><td><input type=text name="tfname" size=30></td></tr></table>
    <input type="submit" value="submit">
    </form>
FORM_DONE
}
elsif ($mode eq "update")
{

$dbh->do("update funct_tf set funct_tf_name='$tfname' where funct_tf_id=$tfid");

#more HTML
    print "<script>window.opener.document.getElementById('ajaxtfname').innerHTML=\"$tfname\"</script>";
    print "TF name updated<br><input type='button' value='Close window' onClick=javascript:window.close();>";

}


}
#if no, display error
else
{
    print "You are not authorized to update the name of this TF";
}
}
else
{
    print "You must be logged in to update TF name";
}
