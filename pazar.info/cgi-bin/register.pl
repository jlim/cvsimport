#!/usr/bin/perl
use DBI;
use Crypt::Imail;
use CGI qw( :all);
use HTML::Template;
use Digest::MD5 qw(md5_hex);
use CGI::HTMLError trace => 1;


my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};

require "$pazarcgipath/getsession.pl";

my $query=new CGI;
my %params = %{$query->Vars};

my $dbname = $ENV{PAZAR_name};
my $dbhost = $ENV{PAZAR_host};

my $DBUSER = $ENV{PAZAR_adminuser};
my $DBPASS = $ENV{PAZAR_adminpass};
my $DBDRV  = $ENV{PAZAR_drv};
my $DBPORT  = $ENV{PAZAR_port}||3306;
my $DBURL = "DBI:$DBDRV:dbname=$dbname;host=$dbhost;port=$DBPORT";

# open the html header template
my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");

# fill in template parameters
$template->param(TITLE => 'PAZAR User Registration');
$template->param(PAZAR_HTML => $pazar_html);
$template->param(PAZAR_CGI => $pazar_cgi);
$template->param(JAVASCRIPT_FUNCTION => q{function verify() {
	    var themessage = "You are required to complete the following fields: ";
	    
	    if (document.regform.username.value=="") {
		themessage = themessage + "\\n - User Name";
	    }
	    if (document.regform.password.value=="") {
		themessage = themessage + "\\n -  password";
	    }
	    if (document.regform.passwordcheck.value=="") {
		themessage = themessage + "\\n -  password re-entry";
	    }
	    if (document.regform.affiliation.value=="") {
		themessage = themessage + "\\n -  Affiliation";
	    }
	    if (document.regform.first.value=="") {
		themessage = themessage + "\\n -  First Name";
	    }
	    if (document.regform.last.value=="") {
		themessage = themessage + "\\n -  Last Name";
	    }
	    if (document.regform.code.value=="") {
		themessage = themessage + "\\n -  Verification Number";
	    }
	    if (document.regform.passwordcheck.value != document.regform.password.value)
	    {
		if (themessage == "You are required to complete the following fields: ") {
		    themessage = "Passwords do not match. Please check them";
		}
		else
		{
		    themessage = themessage + "\\n Passwords do not match, please check them";
		}
	    }

	var x = document.regform.username.value;
	var filter  = /^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/;
	if (filter.test(x))
	{
	    //username is a valid email address
	}
	else 
	{
	    if (themessage == "You are required to complete the following fields: ") {
		themessage = "Username is not a valid email address. Please re-enter it.";
	    }
	    else
	    {
		if (document.regform.username.value!="")
		{
		    themessage = themessage + "\\n Username is not a valid email address. Please re-enter it.";
		}
	    }
	}

	    //alert if fields are empty and cancel form submit
		if (themessage == "You are required to complete the following fields: ") {
		    document.regform.submit();
		}
	    else
	    {
		alert(themessage);
		return false;
	    }
	}});

if($loggedin eq 'true') {
    #log out link
    $template->param(LOGOUT => "$info{first} $info{last} logged in. "."<a href=\'$pazar_cgi/logout.pl\'>Log Out</a>");
    # send the obligatory Content-Type and print the template output
    print "Content-Type: text/html\n\n", $template->output;
    #print logout message if user already logged in
    print "<p class=\"warning\">You are already logged in.<br>Please logout before registering a new user!</p>";
} else {
    #log in link
    $template->param(LOGOUT => "<a href=\'$pazar_cgi/login.pl\'>Log In</a>");
    # send the obligatory Content-Type and print the template output
    print "Content-Type: text/html\n\n", $template->output;

if ($params{mode} eq 'register') {

    my $dbh = DBI->connect($DBURL,$DBUSER,$DBPASS)
    or die "Can't connect to the database";

#make sure user name is not empty
    my $usernamenull = "false";
    if ($params{username} eq "")
    {
	$usernamenull = "true";
    }

#make sure passwords are not empty fields
    my $passwordsnull = "false";
    if ($params{password} eq "" || $params{passwordcheck} eq "")
    {
	$passwordnull = "true";
    }

#make sure passwords match
    my $pwmatch = "false";
    if ($params{password} eq $params{passwordcheck})
    {
	$pwmatch = "true";
    }

#check verification code
    my $sessionexpired = "false";
    my $verified = "true";

    my $skey    = 'ChangeIt';         # secret key
    my $code    = $params{'code'};  # user put code
    my $session = $params{'hv_sess'};
    my $hash    = $params{'hv_hash'};
    my $expire  = 60*2;   # seconds expire session
    
    if (time - $session > $expire ) {
#session expired
	$sessionexpired = "true";
    }
    if ($hash ne md5_hex($code,$skey,$session) ) {
#verification incorrect
	$verified = "false";
    }
    else
    {
	#verification correct
	$verified = "true";
    }

#check for duplicate user name
    my $query1 = "select username from users where username='$params{username}'";

    my $sth1=$dbh->prepare($query1);
    $sth1->execute();

    @res1 = $sth1->fetchrow_array;

    my $duplicates = scalar(@res1);


#check if all conditions met before creating account
    if($duplicates == 0 && $pwmatch eq "true" && $passwordnull ne "true" && $usernamenull ne "true" && $sessionexpired eq "false" && $verified eq "true")
    {
#    #perform insert

#encrypt password
	my $im = Crypt::Imail->new();
        my $encrypted_pass = $im->encrypt($params{username}, $params{password});

#delimit single quotes and double quotes for first name, last name, username and affiliation

	my $fn = $params{first};
	$fn =~ s/'/\\'/g;
	$fn =~ s/"/\\"/g;

	my $ln = $params{last};
	$ln =~ s/'/\\'/g;
	$ln =~ s/"/\\"/g;

	my $un = $params{username};
	$un =~ s/'/\\'/g;
	$un =~ s/"/\\"/g;

	my $af = $params{affiliation};
	$af =~ s/'/\\'/g;
	$af =~ s/"/\\"/g;

	my $userinsert = "insert into users(user_id,first_name,last_name,edit_date,password,username,aff) values('','$fn','$ln',null,'$encrypted_pass','$un','$af')";

	my $sth = $dbh->prepare($userinsert);
	$sth->execute();

#print confirmation
	print "<p >User account successfully created";
	print "<br>To begin creating projects for this user, click the button below<br><form   method='post' action='$pazar_cgi/dologin.pl'><input type='hidden' name='project' value='true'><input type='hidden' name='mode' value='login'><input type='hidden' name='username' value='$params{username}'><input type='hidden' name='password' value='$params{password}'><input type='submit' name='submit' value='Add Projects'></form></p></body></html>";

    }
    else
    {
#print error

    print "<p class=\"title1\">PAZAR User and Project creation</p>";
    if($sessionexpired eq "true" )
    {
	print "<p class=\"warning\">The verification code has expired</p>";
    }

    if($verified eq "false")
    {
	print "<p class=\"warning\">The verification code entered is incorrect</p>";
    }

	    if($duplicates != 0)
	{
	    print "<p class=\"warning\">The entered user name is already in use. Please choose another user name</p>";
	}
	if($pwmatch ne "true")
	{
	    print "<p class=\"warning\">Passwords do not match. Please re-enter passwords</p>";
	}
        #if username and passwords not filled in
        if($usernamenull eq "true")
	{
	    print "<p class=\"warning\">User name not entered. Please enter a user name</p>";
	}
    
        if ($passwordnull eq "true" )
	{
	    print "<p class=\"warning\">No password entered. Please enter a password</p>";
	}

	print "<FORM  name=\"regform\" method=\"POST\" action=\"$pazar_cgi/register.pl\">";
	print "<table>";
	print "<tr><td valign='top'>User name <br>(use a valid email address; <br>pazar messages will be sent here)</td><td valign='top'> <input type=\"text\" name=\"username\" maxlength=64";

	if($duplicates == 0)
	{
	    print " value=\"$params{username}\"";
	}
	print "></td></tr>";
	print "<tr><td >Password</td><td><input type=\"password\" name=\"password\" maxlength=20";
	if($pwmatch eq "true")
	{
	    print " value=\"$params{password}\"";
	}
	print "></td></tr>";
	print "<tr><td >Re-enter password</td><td><input type=\"password\" name=\"passwordcheck\" maxlength=20";
	if($pwmatch eq "true")
	{
	    print " value=\"$params{passwordcheck}\"";
	}
print<<Error_Page_2;
	></td></tr>
	    
	    <tr><td >Affiliation</td><td><input type="text" name="affiliation" maxlength=64 value=$params{affiliation}></td></tr>
	    <tr><td >First name</td><td><input type="text" name="first" maxlength=32 value=$params{first}></td></tr>
	    <tr><td >Last name</td><td><input type="text" name="last" maxlength=32 value=$params{last}></td></tr>
	    <tr><td>Verification image</td><td><script src="captcha/hv.pl"></script></td></tr>
	    <tr><td>Verification number<br>(from image above)</td><td><input type="text" name="code" size="10"></td></tr>

	    <tr><td colspan=2><input type="hidden" name="mode" value="register"></td></tr>
	    <tr><td></td><td><INPUT type="button" onClick="verify();" name="Register" value="Register">
	    <INPUT type="reset" name="Reset" value="Reset"></td></tr>
	    </table>
	    </FORM>

Error_Page_2
	}
$dbh->disconnect;
}
else {      
print<<Page_Done;

	<p class="title1">PAZAR User Registration</p>

	<FORM  name="regform" method="POST" action="$pazar_cgi/register.pl">
	<table>
	<tr><td valign="top">User name <br>(use a valid email address; <br>pazar messages will be sent here)</td><td valign='top'> <input type="text" name="username" maxlength=64></td></tr>
	<tr><td >Password</td><td> <input type="password" name="password" maxlength=20></td></tr>
	<tr><td >Re-enter password</td><td> <input type="password" name="passwordcheck" maxlength=20></td></tr>
	<tr><td >Affiliation</td><td><input type="text" name="affiliation" maxlength=64></td></tr>
	<tr><td >First name</td><td><input type="text" name="first" maxlength=32></td></tr>
	<tr><td >Last name</td><td><input type="text" name="last" maxlength=32></td></tr>
	<tr><td>Verification image</td><td><script src="captcha/hv.pl"></script></td></tr>
	<tr><td>Verification number<br>(from image above)</td><td><input type="text" name="code" size="10"></td></tr>
	<tr><td colspan=2><input type="hidden" name="mode" value="register"></td></tr>
	<tr><td></td><td><INPUT type="button" onClick="verify();" name="Register" value="Register">
	<INPUT type="reset" name="Reset" value="Reset"></td></tr>
	</table>
	</FORM>

Page_Done
#log in to edit user details or manage projects
    }

}

# print out the html tail template
my $temptail = HTML::Template->new(filename => "$pazarcgipath/tail.tmpl");
print $temptail->output;
