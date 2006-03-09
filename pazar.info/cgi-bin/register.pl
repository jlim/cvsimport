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
<meta http-equiv="Content-Language" content="fr">

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
<link TYPE="text/css" rel="stylesheet" HREF="pazar.css">
</head>

<body bgcolor="#FFFFFF" leftmargin="0" topmargin="0" marginwidth="0" marginheight="0">

<div align="left">
  <table border="0" cellpadding="0" cellspacing="0" style="border-collapse: collapse" bordercolor="#111111" width="85%" height="100%">
    <tr>

      <td valign="top">
      <table border="0" cellpadding="0" cellspacing="0" style="border-collapse: collapse" bordercolor="#111111" width="660">
        <tr>
          <td width="143">
          <img border="0" src="../images/pazar_01.gif" width="143" height="102"></td>
          <td width="517">
          <img border="0" src="../images/pazar_02.gif" width="517" height="102"></td>
        </tr>
      </table>

      <table border="0" cellpadding="0" cellspacing="0" style="border-collapse: collapse" bordercolor="#111111" width="100%" id="AutoNumber3">
        <tr>
          <td width="143" background="../images/pazar_bg.gif" valign="top" align="center">
          <table border="0" cellpadding="0" cellspacing="0" style="border-collapse: collapse" bordercolor="#111111" width="100%" id="AutoNumber4">
            <tr>
              <td width="100%">
              <a href="" OnMouseOver="if (VersionNavigateur(3.0,4.0)) img1.src='../images/up_03.gif'" OnMouseOut="img1.src='../images/pazar_03.gif'"><img name="img1" width=143 height=51 border=0 src="../images/pazar_03.gif" OnLoad="tempImg=new Image(0,0); tempImg.src='../images/up_03.gif'"></a></td>
            </tr>
            <tr>

              <td width="100%">
              <a href="" OnMouseOver="if (VersionNavigateur(3.0,4.0)) img2.src='../images/up_05.gif'" OnMouseOut="img2.src='../images/pazar_05.gif'"><img name="img2" width=143 height=51 border=0 src="../images/pazar_05.gif" OnLoad="tempImg=new Image(0,0); tempImg.src='../images/up_05.gif'"></a></td>
            </tr>
            <tr>
              <td width="100%">
              <a href="" OnMouseOver="if (VersionNavigateur(3.0,4.0)) img3.src='../images/up_06.gif'" OnMouseOut="img3.src='../images/pazar_06.gif'"><img name="img3" width=143 height=51 border=0 src="../images/pazar_06.gif" OnLoad="tempImg=new Image(0,0); tempImg.src='../images/up_06.gif'"></a></td>
            </tr>
            <tr>
              <td width="100%">

              <a href="" OnMouseOver="if (VersionNavigateur(3.0,4.0)) img4.src='../images/up_07.gif'" OnMouseOut="img4.src='../images/pazar_07.gif'"><img name="img4" width=143 height=51 border=0 src="../images/pazar_07.gif" OnLoad="tempImg=new Image(0,0); tempImg.src='../images/up_07.gif'"></a></td>
            </tr>
            <tr>
              <td width="100%">
              <a href="" OnMouseOver="if (VersionNavigateur(3.0,4.0)) img5.src='../images/up_08.gif'" OnMouseOut="img5.src='../images/pazar_08.gif'"><img name="img5" width=143 height=51 border=0 src="../images/pazar_08.gif" OnLoad="tempImg=new Image(0,0); tempImg.src='../images/up_08.gif'"></a></td>
            </tr>
            <tr>
              <td width="100%">
              <img border="0" src="../images/pazar_09.gif" width="143" height="51"></td>

            </tr>
            <tr>
              <td width="100%">
              <a OnMouseOver="if (VersionNavigateur(3.0,4.0)) img6.src='../images/up_10.gif'" OnMouseOut="img6.src='../images/pazar_10.gif'" href="XMLtmp.htm"><img name="img6" width=143 height=51 border=0 src="../images/pazar_10.gif" OnLoad="tempImg=new Image(0,0); tempImg.src='../images/up_10.gif'"></a></td>
            </tr>
            <tr>
              <td width="100%">
              <a href="" OnMouseOver="if (VersionNavigateur(3.0,4.0)) img7.src='../images/up_11.gif'" OnMouseOut="img7.src='../images/pazar_11.gif'"><img name="img7" width=143 height=51 border=0 src="../images/pazar_11.gif" OnLoad="tempImg=new Image(0,0); tempImg.src='../images/up_11.gif'"></a></td>
            </tr>

            <tr>
              <td width="100%">
              <a href="" OnMouseOver="if (VersionNavigateur(3.0,4.0)) img8.src='../images/up_12.gif'" OnMouseOut="img8.src='../images/pazar_12.gif'"><img name="img8" width=143 height=51 border=0 src="../images/pazar_12.gif" OnLoad="tempImg=new Image(0,0); tempImg.src='../images/up_12.gif'"></a></td>
            </tr>
          </table>
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
</font>
          </td>
        </tr>
      </table>
      </td>

    </tr>
  </table>
</div>

</body>
</html>
template_tail

$dbh->disconnect;
