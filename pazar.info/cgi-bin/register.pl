#!/usr/bin/perl
use DBI;
use Crypt::Imail;
use CGI qw( :all);

my $query=new CGI;
my %params = %{$query->Vars};

my $DBUSER = "pazaradmin";
my $DBPASS = "32paz10";
my $DBURL = "DBI:mysql:dbname=pazar;host=napa.cmmt.ubc.ca";

if ($params{mode} eq 'register') {

    my $dbh = DBI->connect($DBURL,$DBUSER,$DBPASS)
    or die "Can't connect to pfam database";

#make sure passwords match
    my $pwmatch = "false";
    if ($params{password} eq $params{passwordcheck})
    {
	$pwmatch = "true";
    }

    
#check for duplicate user name
    my $query1 = "select username from users where username='$params{username}'";

    my $sth1=$dbh->prepare($query1);
    $sth1->execute();

    @res1 = $sth1->fetchrow_array;

    print "Content-type: text/html\n\n";
    my $duplicates = scalar(@res1);
    if($duplicates == 0 && $pwmatch eq "true")
    {
#    #perform insert

#encrypt password
	my $im = Crypt::Imail->new();
        my $encrypted_pass = $im->encrypt($params{username}, $params{password});
	my $userinsert = "insert into users(user_id,first_name,last_name,edit_date,password,username,aff) values('','$params{first}','$params{last}',null,'$encrypted_pass','$params{username}','$params{affiliation}')";

	my $sth = $dbh->prepare($userinsert);
	$sth->execute();

#print confirmation
	print "<html><head><title>account creation successful</title></head><body>User account successfully created";
	print "<p>To begin creating projects for this user, click the button below<br><form method='post' action='editprojects.pl'><input type='hidden' name='mode' value='login'><input type='hidden' name='username' value='$params{username}'><input type='hidden' name='password' value='$params{password}'><input type='submit' name='submit' value='Add Projects'></form></body></html>";

    }
    else
    {
#print error
print<<Error_Page_1;
	<html>
	<head>
	<title>PAZAR User and Project creation</title>

	<script language='JavaScript'>
	function verify() {
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

	    //alert if fields are empty and cancel form submit
		if (themessage == "You are required to complete the following fields: ") {
		    document.regform.submit();
		}
	    else
	    {
		alert(themessage);
		return false;
	    }
	}
	</script>
	    </head>
	    <body>
	    <h2>PAZAR User and Project creation</h2>
Error_Page_1
	    if($duplicates != 0)
	{
	    print "<font color='red'>Please choose another user name</font>";
	}
	if($pwmatch ne "true")
	{
	    print "<br><font color='red'>Passwords do not match. Please re-enter passwords</font>";
	}


	print "<FORM name=\"regform\" method=\"POST\" action=\"register.pl\">";
	print "<table>";
	print "<tr><td>User name</td><td> <input type=\"text\" name=\"username\"";

	if($duplicates == 0)
	{
	    print " value=\"$params{username}\"";
	}
	print "></td></tr>";
	print "<tr><td>Password</td><td><input type=\"password\" name=\"password\"";
	if($pwmatch eq "true")
	{
	    print " value=\"$params{password}\"";
	}
	print "></td></tr>";
	print "<tr><td>Re-enter password</td><td> <input type=\"password\" name=\"passwordcheck\"";
	if($pwmatch eq "true")
	{
	    print " value=\"$params{passwordcheck}\"";
	}
print<<Error_Page_2;
	></td></tr>
	    
	    <tr><td>Affiliation</td><td><input type="text" name="affiliation" value=$params{affiliation}></td></tr>
	    <tr><td>First name</td><td><input type="text" name="first" value=$params{first}></td></tr>
	    <tr><td>Last name</td><td><input type="text" name="last" value=$params{last}></td></tr>
	    <tr><td colspan=2><input type="hidden" name="mode" value="register"></td></tr>
	    <tr><td></td><td><INPUT type="button" onClick="verify();" name="Register" value="Register">
	    <INPUT type="reset" name="Reset" value="Reset"></td></tr>
	    </table>
	    </FORM>
	    </body>
	    </html>
Error_Page_2
	}
}
else {      
    print "Content-type: text/html\n\n";
print<<Page_Done;
    <html>
	<head>
	<title>PAZAR User and Project creation</title>
	
	<script language='JavaScript'>
	function verify() {
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

	    //alert if fields are empty and cancel form submit
		if (themessage == "You are required to complete the following fields: ") {
		    document.regform.submit();
		}
	    else {
		alert(themessage);
		return false;
	    }
	}
    </script>
	</head>
	<body>
	<h2>PAZAR User and Project creation</h2>

	<FORM name="regform" method="POST" action="register.pl">
	<table>
	<tr><td>User name</td><td> <input type="text" name="username"></td></tr>      
	<tr><td>Password</td><td> <input type="password" name="password"></td></tr>
	<tr><td>Re-enter password</td><td> <input type="password" name="passwordcheck"></td></tr>
	<tr><td>Affiliation</td><td><input type="text" name="affiliation"></td></tr>
	<tr><td>First name</td><td><input type="text" name="first"></td></tr>
	<tr><td>Last name</td><td><input type="text" name="last"></td></tr>
	<tr><td colspan=2><input type="hidden" name="mode" value="register"></td></tr>
	<tr><td></td><td><INPUT type="button" onClick="verify();" name="Register" value="Register">
	<INPUT type="reset" name="Reset" value="Reset"></td></tr>
	</table>
	</FORM>
	</body>
	</html>
Page_Done
#log in to edit user details or manage projects
    }
$dbh->disconnect;
