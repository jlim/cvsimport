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
#my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");

#$template->param(TITLE => 'PAZAR Analysis Comments update');
#$template->param(PAZAR_CGI => $pazar_cgi);
# send the obligatory Content-Type and print the template output
#print "Content-Type: text/html\n\n", $template->output;
print "Content-Type: text/html\n\n";
#get userinfo
my $get = new CGI;
my %params = %{$get->Vars};


if($loggedin eq 'true')
{

#    $dbh = pazar->new( 
#		       -globalsearch  =>    'no',		      
#		       -host          =>    $ENV{PAZAR_host},
#		       -user          =>    $ENV{PAZAR_pubuser},
#		       -pass          =>    $ENV{PAZAR_pubpass},
#		       -dbname        =>    $ENV{PAZAR_name},
#		       -pazar_user    =>    $info{user},
#		       -pazar_pass    =>    $info{pass},
#		       -drv           =>    $ENV{PAZAR_drv},
#		       -project       =>    $res[0]);

my $dbname = $ENV{PAZAR_name};
my $dbhost = $ENV{PAZAR_host};

my $DBUSER = $ENV{PAZAR_adminuser};
my $DBPASS = $ENV{PAZAR_adminpass};
my $DBDRV  = $ENV{PAZAR_drv};

my $DBURL  = "DBI:$DBDRV:dbname=$dbname;host=$dbhost";

my $dbh = DBI->connect($DBURL,$DBUSER,$DBPASS)
    or die "Can't connect to pazar database";

#get analysis id and project id
    my $analysisid = $params{aid};
    my $projectid = $params{pid};
    my $mode = $params{mode};
    my $analysiscomments = $params{analysiscomments};
my $commentseditable = "false";

	foreach my $proj (@projids) {
	#see if $proj is the same as the analysis project or if my userid is same as analysis user_id
	    if($proj == $projectid)
	    {
		#comments are editable
		$commentseditable = "true";
	    }
	}
#make sure user is a member of the project

if($commentseditable eq "true")
{
#if yes, check mode


if($mode eq "form")
{
    print<<FORM_DONE;
    <form method="post" action="updateanalysiscomments.pl">
    <input type="hidden" name="mode" value="update">
<input type="hidden" name="aid" value="$analysisid">
<input type="hidden" name="pid" value="$projectid">
   <table><tr><td> Enter Analysis comments here: </td><td><textarea name="analysiscomments" cols=30 rows=10></textarea></td></tr></table>
    <input type="submit" value="submit">
    </form>
FORM_DONE
}
elsif ($mode eq "update")
{
$dbh->do("update analysis set comments='$analysiscomments' where analysis_id=$analysisid");
#more HTML
    print "<script>window.opener.document.getElementById('ajaxcomment').innerHTML=\"$analysiscomments\"</script>";
    print "Comments updated<br><input type='button' value='Close window' onClick=javascript:window.close();>";

}


}
#if no, display error
else
{
    print "You are not authorized to update comments for this analysis";
}
}
else
{
    print "You must be logged in to update analysis comments";
}
