#!/usr/bin/perl
use DBI;
use HTML::Template;
use CGI::Cookie;
use CGI::Session;
use Mail::Mailer;

use CGI qw( :all);
my $query = new CGI;
my %params = %{$query->Vars};



my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};
my $dbname = $ENV{PAZAR_name};
my $dbhost = $ENV{PAZAR_host};
my $DBUSER = $ENV{PAZAR_adminuser};
my $DBPASS = $ENV{PAZAR_adminpass};
my $DBPORT = $ENV{PAZAR_port}||3306;
my $DBDRV = $ENV{PAZAR_drv};
my $DBURL = qq{DBI:$DBDRV:dbname=$dbname;host=$dbhost;port=$DBPORT};


require "$pazarcgipath/getsession.pl";

# open the html header template
my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");

# fill in template parameters
$template->param(TITLE => 'PAZAR Project Outline');
$template->param(PAZAR_HTML => $pazar_html);
$template->param(PAZAR_CGI => $pazar_cgi);

# send the obligatory Content-Type and print the template output
print "Content-Type: text/html\n\n", $template->output;
#print "value of logged in variable: ".$loggedin."<br>";
=pod
if($loggedin eq 'true')
{

#get cookie and session values
    print "session id: ".$sessionid."<br>";
    print "number of session projects:".@projids."<br>";
    print "projects:";
    foreach my $proj (@projids)
    {
	print $proj."<br>";
    }
    print "session info number of keys:".(keys %info)."<br>";

    foreach $key (sort keys %info)
    {
	print "$key -> $info{$key}<br>";
    }
#add another name-value pair into session
    #$session->param('test2','test2info');

    #print "added value to session: ".$session->param('test2');
}
=cut
###########
use Crypt::Imail;

$im = Crypt::Imail->new();
############## user info fields from session
=pod
    my %info = (
        user => $params{username},
        pass => $params{password},
        userid => $userid,
        aff => $aff,
        first => $first,
        last => $last);
=cut
###############
my $dbh = DBI->connect($DBURL,$DBUSER,$DBPASS);

#get username as parameter
#my $username = "jlim\@cmmt.ubc.ca";
my $username = $params{username};

#get the encrypted password from DB

my $msgtext = "";

	my $sth = $dbh->prepare(qq{SELECT password from users where username=?});
	$sth->execute($username);

#check whether username actually exists in users table

if (my ($encrypted_pass) = $sth->fetchrow_array)
{

	my $password = $im->decrypt($username,$encrypted_pass);

#send the email


    my $from_address = "admin\@pazar.info";
    my $to_address = $username;
    my $subject = "PAZAR user password recovery";
    my $body = "Dear PAZAR user, here is the password you requested:\n\n$password\n\nPlease do not reply to this message.  For additional help, send email to pazar\@cmmt.ubc.ca";

    my $mailer = Mail::Mailer->new("sendmail");
    $mailer->open({From => $from_address,
                   To => $to_address,
                   Subject => $subject})
    or die "Can't open: $!\n";

    print $mailer $body;
    $mailer->close;

########################


print "<br>Your password has been sent to $username";
##############
}
else
{
	print "<br>The email address you have entered does not exist in PAZAR.  Please ensure that it was spelled correctly and try again, or <a href=\"mailto:pazar\@cmmt.ubc.ca\">contact us</a> for help.";
}
# print out the html tail template
my $temptail = HTML::Template->new(filename => "$pazarcgipath/tail.tmpl");
print $temptail->output;
