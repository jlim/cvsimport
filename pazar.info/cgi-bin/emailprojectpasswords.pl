#!/usr/bin/perl
use DBI;
use HTML::Template;
use CGI::Cookie;
use CGI::Session;
use Mail::Mailer;


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
#get project passwords

my $username = $info{"user"};
my $uid = $info{"userid"};

my $msgtext = "";
    foreach my $proj (@projids)
    {
	#use $proj to retrieve encrypted pass from db
	my $name = "defaultuser";

	my $projectcreator = 0; #whether current user owns the project. default is no

	#do the rest only if current user created the project (user_project_id is the lowest)
	my $upsth=$dbh->prepare("select * from user_project where project_id=? order by user_project_id");
	#the first userid should equal $uid
	$upsth->execute($proj);
	if (my $href = $upsth->fetchrow_hashref)
	{
		if($href->{user_id}==$uid)
		{
			$projectcreator = 1;
		}
	}
	if ($projectcreator==1)
	{
		my $sth = $dbh->prepare(qq{SELECT password,project_name from project where project_id=?});
		$sth->execute($proj);
		my ($encrypted_pass,$pname) = $sth->fetchrow_array;
		my $password = $im->decrypt($name,$encrypted_pass);
		$msgtext .= "$pname : $password\n";
	}
    }

#send the email



    my $from_address = "admin\@pazar.info";
    my $to_address = $username;
    my $subject = "PAZAR project passwords request";
    my $body = "Dear PAZAR user, here are the project passwords that you requested:\n\n$msgtext\n\nPlease do not reply to this message. For additional help, send email to pazar\@cmmt.ubc.ca";

    my $mailer = Mail::Mailer->new("sendmail");
    $mailer->open({From => $from_address,
                   To => $to_address,
                   Subject => $subject})
    or die "Can't open: $!\n";

    print $mailer $body;
    $mailer->close;

########################


print "<br>Your project passwords have all been sent to the email address that you have entered in your account information ($username). You should receive them shortly.";
##############

# print out the html tail template
my $temptail = HTML::Template->new(filename => "$pazarcgipath/tail.tmpl");
print $temptail->output;
