#!/usr/bin/perl
use DBI;
use Crypt::Imail;
use CGI qw( :all);


my $query=new CGI;
my %params = %{$query->Vars};

my $DBUSER = "pazaradmin";
my $DBPASS = "32paz10";
my $DBURL = "DBI:mysql:dbname=pazar;host=napa.cmmt.ubc.ca";

my $dbh = DBI->connect($DBURL,$DBUSER,$DBPASS)
    or die "Can't connect to pazar database";

print "Content-type: text/html\n\n";

print<<template_header;
<html>
<head>
<meta http-equiv="Content-Language" content="fr">

<title>PAZAR Project Manager</title>
<script language="javascript">
<!--
function VersionNavigateur(Netscape, Explorer)
{
if ((navigator.appVersion.substring(0,3) >= Netscape && navigator.appName == 'Netscape') ||
(navigator.appVersion.substring(0,3) >= Explorer && navigator.appName.substring(0,9) == 'Microsoft'))
return true;
else return false;
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
template_header

if ($params{mode} eq 'add') 
{
#insert into project
    $dbh->do("insert into project values('','$params{projname}','','$params{projstatus}',null)");

#insert into user_project
    $dbh->do("insert into user_project values('',$params{uid},LAST_INSERT_ID())");

#show updated list
    $params{mode}='login';
}

if ($params{mode} eq 'delete') 
{
#delete from user_project
    my $delh=$dbh->prepare("delete from user_project where project_id=$params{pid}");
    $delh->execute();

#delete from project
    my $delh2=$dbh->prepare("delete from project where project_id=$params{pid}");
    $delh2->execute();
    
#show updated list
    $params{mode}='login';
}


if ($params{mode} eq 'login') 
{
#verify user name and password

    my $im = Crypt::Imail->new();
    my $encrypted_pass = $im->encrypt($params{username}, $params{password}); 
    my $chkh=$dbh->prepare("select user_id,aff,first_name,last_name from users where username=? and password=?")||die;
    $chkh->execute($params{username},$encrypted_pass)||die;
    my ($userid,$aff,$first,$last)=$chkh->fetchrow_array;
    
    if($userid ne '')
    {

#show projects

	print "<table border=1>\n";
#print projects
	my $sth=$dbh->prepare("select project_id from user_project where user_id=?");
	$sth->execute($userid);
	
	print "<tr><td>name</td><td>status</td><td>Last edited</td><td>&nbsp;</td></tr>";
	
	while(my @results = $sth->fetchrow_array)
	{
	    my $proj_id = $results[0];
	    #get project info
	    my $sth2 = $dbh->prepare("select * from project where project_id=?");
	    $sth2->execute($proj_id);
	    #print project entry
	    my @projdetails = $sth2->fetchrow_array;

	    print "<tr><td>$projdetails[1]</td><td>$projdetails[3]</td><td>$projdetails[4]</td><td><form method='post' action='editprojects.pl'><input type='hidden' name='username' value='$params{username}'><input type='hidden' name='password' value='$params{password}'><input type='hidden' name='mode' value='delete'><input type='hidden' name='pid' value='$proj_id'><input type='submit' value='delete'></form></td></tr>";
	}

	print "</table>\n";
print<<AddFormHead;
	<p>
	    <form method='post' action='editprojects.pl'>
	    <input type='hidden' name='mode' value='add'>
	    <input type='hidden' name='uid' value='$userid'>
AddFormHead

	    print "<input type='hidden' name='username' value='$params{username}'>";
	print "<input type='hidden' name='password' value='$params{password}'>";

print<<AddFormFoot;
	<table border=1>
	    <tr><td>name</td><td><input type="text" name="projname"></td></tr>
	    <tr><td>status</td><td><select name="projstatus"><option name="restricted" value="restricted">restricted<option name="published" value="published">published</select></td></tr>
	    </table>
	    <input type='submit' value='Add new project'>
	    </form>
AddFormFoot
	}
    else
    {
#print error
print<<Error_Page_1;

	    <h3>PAZAR Project Management</h3>
Error_Page_1

	    print "<font color='red'>Please check user name and password and try again</font>";
	print "<FORM method=\"POST\" action=\"editprojects.pl\">";
	print "<table>";
	print "<tr><td>User name</td><td> <input type=\"text\" name=\"username\"></td></tr>";
	print "<tr><td>Password</td><td><input type=\"password\" name=\"password\"></td></tr>";


print<<Error_Page_2;
	<tr><td colspan=2><input type="hidden" name="mode" value="login"></td></tr>
	    <tr><td></td><td><INPUT type="submit" name="login" value="login"></td></tr>

	    </table>
	    </FORM>

Error_Page_2
	}
    $dbh->disconnect;
}
else {      

print<<Page_Done;

	<h3>PAZAR User and Project creation</h3>


	<FORM method="POST" action="editprojects.pl">
	<table>
	<tr><td>User name</td><td> <input type="text" name="username"></td></tr>      
	<tr><td>Password</td><td> <input type="password" name="password"></td></tr>
	<tr><td colspan=2><input type="hidden" name="mode" value="login"></td></tr>
	<tr><td></td><td><INPUT type="submit" name="login" value="login"></td></tr>
	</table>
	</FORM>

Page_Done
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
