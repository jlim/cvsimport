#!/usr/local/bin/perl

use DBI;
use Crypt::Imail;
use CGI qw( :all);
use HTML::Template;

my $query=new CGI;
my %params = %{$query->Vars};

my $dbname = $ENV{PAZAR_name};
my $dbhost = $ENV{PAZAR_host};

my $DBUSER = $ENV{PAZAR_adminuser};
my $DBPASS = $ENV{PAZAR_adminpass};
my $DBURL = "DBI:mysql:dbname=$dbname;host=$dbhost";


my $dbh = DBI->connect($DBURL,$DBUSER,$DBPASS)
    or die "Can't connect to pazar database";

    my $im = Crypt::Imail->new();
    my $encrypted_pass = $im->encrypt($params{username}, $params{password}); 
    my $chkh=$dbh->prepare("select user_id,aff,first_name,last_name from users where username=? and password=?")||die;
    $chkh->execute($params{username},$encrypted_pass)||die;
    my ($userid,$aff,$first,$last)=$chkh->fetchrow_array;
    
    if($userid ne '')
{
    my %info = (userid=>$userid,aff=>$aff,first=>$first,last=>$last);


#store project ids
    my @projids = ();
	my $sth=$dbh->prepare("select project_id from user_project where user_id=?");
	$sth->execute($userid);
		while(my @results = $sth->fetchrow_array)
	{
	    #my $proj_id = $results[0];
	    push(@projids,$results[0]);
	    #get project info
	}

#create cookie
# values can be arrayref, hashref or scalar
#\@arrayref, \%hashref, [@array]
# NOTE: complex data structures eg. hash of arrays, hash of hashes will not work properly with cookies
$cookie = $query->cookie(-name=>'PAZAR_COOKIE',
			 -value=>\%info,
			 -expires=>'+4h',
			 -path=>'/');

$project_cookie = $query->cookie(-name=>'PAZAR_PROJECT_COOKIE',
			 -value=>\@projids,
			 -expires=>'+4h',
			 -path=>'/');

print $query->header(-cookie=>[$cookie,$project_cookie]);
#store other attributes
# open the html header template
my $template = HTML::Template->new(filename => 'header.tmpl');

# fill in template parameters
$template->param(TITLE => 'PAZAR Login');


# send the obligatory Content-Type and print the template output
#print "Content-Type: text/html\n\n", $template->output;

print $template->output;

#return to main page 
    print<<refresh;
<script language='JavaScript'>
    document.location.href='http://www.pazar.info/cgi-bin/index.pl';
</script>

refresh

}
else
{
# open the html header template
my $template = HTML::Template->new(filename => 'header.tmpl');

# fill in template parameters
$template->param(TITLE => 'PAZAR Login');


# send the obligatory Content-Type and print the template output
print "Content-Type: text/html\n\n", $template->output;
    print "<font color='red'>Login unsuccessful. Please try again.</font>";
#print login form again
 print<<Page_Done;

	<p class="title1">PAZAR Login</p>
	<FORM  method="POST" action="dologin.pl">
	<table>
	<tr><td >User name</td><td> <input type="text" name="username"></td></tr>      
	<tr><td >Password</td><td> <input type="password" name="password"></td></tr>
	<tr><td></td><td><INPUT type="submit" name="login" value="login"></td></tr>
	</table>
	</FORM>

Page_Done
}

my $template_tail = HTML::Template->new(filename => 'tail.tmpl');
print $template_tail->output;