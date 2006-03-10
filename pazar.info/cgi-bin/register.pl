#!/usr/bin/perl
use DBI;
use Crypt::Imail;
use CGI qw( :all);

my $query=new CGI;
my %params = %{$query->Vars};

my $DBUSER = "pazaradmin";
my $DBPASS = "32paz10";
my $DBURL = "DBI:mysql:dbname=pazar;host=napa.cmmt.ubc.ca";

    print "Content-type: text/html\n\n";
print<<template_head;
<html>
<head>
<title>PAZAR User and Project creation</title>
<script language="javascript">
<!--
function VersionNavigateur(Netscape, Explorer)
{
if ((navigator.appVersion.substring(0,3) >= Netscape && navigator.appName == 'Netscape') ||
(navigator.appVersion.substring(0,3) >= Explorer && navigator.appName.substring(0,9) == 'Microsoft'))
return true;
else return false;
}

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
//-->
</script>
<link type="text/css" rel="stylesheet" href="pazar.css"></head>
<body leftmargin="0" topmargin="0" bgcolor="#ffffff" marginheight="0" marginwidth="0">
<div align="left">
  <table border="0" cellpadding="0" cellspacing="0" height="100%" width="85%">
    <tbody><tr>
      <td valign="top">
      <table border="0" cellpadding="0" cellspacing="0" width="660">
        <tbody><tr>
          <td width="143">
          <img src="images/pazar_01.gif" border="0" height="102" width="143"></td>
          <td width="517">
          <img src="images/pazar_02.gif" border="0" height="102" width="517"></td>
        </tr>
      </tbody></table>
      <table border="0" cellpadding="0" cellspacing="0" width="100%" height="100%">
        <tbody><tr>
          <td align="center" background="images/pazar_bg.gif" valign="top" width="143">
          <table border="0" cellpadding="0" cellspacing="0" width="100%">
            <tbody><tr>
              <td width="100%">
              <a href="" onmouseover="if (VersionNavigateur(3.0,4.0)) img1.src='images/up_03.gif'" onmouseout="img1.src='images/pazar_03.gif'"><img name="img1" src="images/pazar_03.gif" onload="tempImg=new Image(0,0); tempImg.src='images/up_03.gif'" border="0" height="51" width="143"></a></td>
            </tr>
            <tr>
              <td width="100%">
              <a href="cgi-bin/register.pl" onmouseover="if (VersionNavigateur(3.0,4.0)) img2.src='images/up_05.gif'" onmouseout="img2.src='images/pazar_05.gif'"><img name="img2" src="images/pazar_05.gif" onload="tempImg=new Image(0,0); tempImg.src='images/up_05.gif'" border="0" height="51" width="143"></a></td>
            </tr>
            <tr>
              <td width="100%">
              <a href="cgi-bin/editprojects.pl" onmouseover="if (VersionNavigateur(3.0,4.0)) img3.src='images/up_06.gif'" onmouseout="img3.src='images/pazar_06.gif'"><img name="img3" src="images/pazar_06.gif" onload="tempImg=new Image(0,0); tempImg.src='images/up_06.gif'" border="0" height="51" width="143"></a></td>
            </tr>
            <tr>
              <td width="100%">
              <a href="" onmouseover="if (VersionNavigateur(3.0,4.0)) img4.src='images/up_07.gif'" onmouseout="img4.src='images/pazar_07.gif'"><img name="img4" src="images/pazar_07.gif" onload="tempImg=new Image(0,0); tempImg.src='images/up_07.gif'" border="0" height="51" width="143"></a></td>
            </tr>
            <tr>
              <td width="100%">
              <a href="search.htm" onmouseover="if (VersionNavigateur(3.0,4.0)) img5.src='images/up_08.gif'" onmouseout="img5.src='images/pazar_08.gif'"><img name="img5" src="images/pazar_08.gif" onload="tempImg=new Image(0,0); tempImg.src='images/up_08.gif'" border="0" height="51" width="143"></a></td>
            </tr>
            <tr>
              <td width="100%">
              <img src="images/pazar_09.gif" border="0" height="51" width="143"></td>
            </tr>
            <tr>
              <td width="100%">
              <a href="XML.htm" onmouseover="if (VersionNavigateur(3.0,4.0)) img6.src='images/up_10.gif'" onmouseout="img6.src='images/pazar_10.gif'"><img name="img6" src="images/pazar_10.gif" onload="tempImg=new Image(0,0); tempImg.src='images/up_10.gif'" border="0" height="51" width="143"></a></td>
            </tr>
            <tr>
              <td width="100%">
              <a href="" onmouseover="if (VersionNavigateur(3.0,4.0)) img7.src='images/up_11.gif'" onmouseout="img7.src='images/pazar_11.gif'"><img name="img7" src="images/pazar_11.gif" onload="tempImg=new Image(0,0); tempImg.src='images/up_11.gif'" border="0" height="51" width="143"></a></td>
            </tr>
            <tr>
              <td width="100%">
              <a href="" onmouseover="if (VersionNavigateur(3.0,4.0)) img8.src='images/up_12.gif'" onmouseout="img8.src='images/pazar_12.gif'"><img name="img8" src="images/pazar_12.gif" onload="tempImg=new Image(0,0); tempImg.src='images/up_12.gif'" border="0" height="51" width="143"></a></td>
            </tr>
          </tbody></table>
          </td>
          <td align="left" valign="top">
          <font><br>
template_head



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
	print "User account successfully created";
	print "<p>To begin creating projects for this user, click the button below<br><form method='post' action='editprojects.pl'><input type='hidden' name='mode' value='login'><input type='hidden' name='username' value='$params{username}'><input type='hidden' name='password' value='$params{password}'><input type='submit' name='submit' value='Add Projects'></form></body></html>";

    }
    else
    {
#print error

    print "<h3>PAZAR User and Project creation</h3>";
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

Error_Page_2
	}
}
else {      
print<<Page_Done;

	<h3>PAZAR User and Project creation</h3>

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

Page_Done
#log in to edit user details or manage projects
    }

print<<template_tail;
          <p class="marge">&nbsp;</p>
          </font>
          </td>
        </tr>
      </tbody></table>
      </td>
    </tr>
  </tbody></table>
</div>
</body></html>
template_tail

$dbh->disconnect;
