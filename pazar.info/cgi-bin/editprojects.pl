#!/usr/bin/perl
use DBI;
use Crypt::Imail;
use CGI qw( :all);
use CGI::Session;
use HTML::Template;

require 'getsession.pl';

my $query=new CGI;
my %params = %{$query->Vars};

my $dbname = $ENV{PAZAR_name};
my $dbhost = $ENV{PAZAR_host};

my $DBUSER = $ENV{PAZAR_adminuser};
my $DBPASS = $ENV{PAZAR_adminpass};
my $DBURL = "DBI:mysql:dbname=$dbname;host=$dbhost";

my $dbh = DBI->connect($DBURL,$DBUSER,$DBPASS)
    or die "Can't connect to pazar database";


my $statusmsg = "";

# open the html header template
my $template = HTML::Template->new(filename => 'header.tmpl');

# fill in template parameters
$template->param(TITLE => 'PAZAR Project Manager');

$template->param(JAVASCRIPT_FUNCTION => q{function verifyProjectCreate() {
	    var themessage = "You are required to complete the following fields: ";
	    var iChars = "!@#$%^&*()+=-[]\\\';,./{}|\":<>?";	    
	    // might want to be less strict with the description later
	    var iChars_desc = "!@#$%^&*()+=-[]\\\';,./{}|\":<>";
	    var pnameSpecialChar = 0;


	    if (document.createprojectform.projname.value=="") {
		themessage = themessage + "\\n - User Name";
	    }
	    if (document.createprojectform.projpass.value=="") {
		themessage = themessage + "\\n -  Project password";
	    }
	    if (document.createprojectform.projpasscheck.value=="") {
		themessage = themessage + "\\n -  Project password re-entry";
	    }	   

	    // if no empty fields, change error message
	    if (themessage == "You are required to complete the following fields: ") {
		themessage = "";
	    }
 
	    if (document.createprojectform.projpasscheck.value != document.createprojectform.projpass.value)
	    {
		if (themessage == "") {
		    themessage = "Passwords do not match. Please check them";
		}
		else
		{
		    themessage = themessage + "\\n Passwords do not match, please check them";
		}
	    }


	    for (var i = 0; i < document.createprojectform.projname.value.length; i++) {
		if (iChars.indexOf(document.createprojectform.projname.value.charAt(i)) != -1) {
		    pnameSpecialChar = 1;	   
		}
	    }

	    if(pnameSpecialChar == 1)
	    {
		themessage = themessage + "\\nThe entered project name contains special characters. \nThese are not allowed. Please choose a different project name\n";
	    }

	    var pdescSpecialChar = 0;
	    for (var i = 0; i < document.createprojectform.projdesc.value.length; i++) {
		if (iChars_desc.indexOf(document.createprojectform.projdesc.value.charAt(i)) != -1) {
		    pdescSpecialChar = 1;
		}
	    }
	    if (pdescSpecialChar == 1)
	    {
		themessage = themessage +  "\nThe entered project description contains special characters. \nThese are not allowed. Please choose a different project description\n";	 
	    }  

	    //alert if fields are empty and cancel form submit
		if (themessage == "") {
		    var descLength = document.createprojectform.projdesc.value.length;
		    if(descLength < 301)
		    {
			document.createprojectform.submit();
		    }
		    else
		    {
			alert("Please ensure that description is no more than 300 characters (Currently "+descLength+" characters)");
		    }
		}
	    else
	    {
		alert(themessage);
		return false;
	    }
	}});

if($loggedin eq 'true')
{
    #log out link
    $template->param(LOGOUT => "$info{first} $info{last} logged in. ".'<a href=\'logout.pl\'>Log Out</a>');

    $params{username}=$info{user};
    $params{password}=$info{pass};
}
else
{
    #log in link
    $template->param(LOGOUT => '<a href=\'login.pl\'>Log In</a>');
}

# send the obligatory Content-Type and print the template output
print "Content-Type: text/html\n\n", $template->output;

print<<javascript;
<script language="JavaScript">

function doDelete(pid)
{
    var decision = confirm("Do you really want to delete this project? Doing so will remove all public and private stored data for this project as well.");
   
    if (decision == true)
    {
	eval("document.deleteform"+pid+".submit();");       
    }
}

function doUserAdd(pid)
{
    var decision = confirm("This will permanently add this user to the project. He/she will be able to change the project status. Do you wish to continue?");
    if (decision == true)
    {	
	eval("document.useraddform"+pid+".submit();");
    }

}

function doUpdateDesc(pid)
{
    var decision = confirm("This will permanently change the project description. Do you wish to continue?");
    var descLength = eval("document.updatedescform"+pid+".projdesc.value.length");
    if (decision == true)
    {	
	if(descLength <301)
	{
	    eval("document.updatedescform"+pid+".submit();");
	}
	else
	{
	    alert("Please ensure that description is no more than 300 characters (Currently "+descLength+" characters)");
	}
    }
}

/*
function CheckMaxLength(Object, MaxLen)
{
  if(Object.value.length > MaxLen)
  {     
    alert
  }
  else
  {
      form.submit();
  }
}
*/

</script>
javascript



if ($params{mode} eq 'add') 
{
#make sure that project name is not in use by another project already

    my $sth = $dbh->prepare("select count(*) from project where project_name='$params{projname}'");
    $sth->execute();
    my @res = $sth->fetchrow_array;


    if($res[0] == 0)
    {
#make sure passwords match before creating project
	if ($params{projpass} eq $params{projpasscheck})
	{
	    
#encrypt password and insert
	    my $im = Crypt::Imail->new();
	    my $encrypted_pass = $im->encrypt('defaultuser', $params{projpass});	

#delimit quotes in project name and description
	    my $pname = $params{projname};
	    $pname =~ s/'/\\'/g;
	    $pname =~ s/"/\\"/g;
	    
	    my $pdesc = $params{projdesc};
	    $pdesc =~ s/'/\\'/g;
	    $pdesc =~ s/"/\\"/g;
	    
#insert into project
	    $dbh->do("insert into project(project_id,project_name,password,status,description,edit_date) values('','$pname','$encrypted_pass','$params{projstatus}','$pdesc',null)");

#get id of newly created project
    $sth = $dbh->prepare("select LAST_INSERT_ID()");
    $sth->execute();
    my @rs = $sth->fetchrow_array;

#insert into user_project
	    $dbh->do("insert into user_project(user_project_id,user_id,project_id) values('',$params{uid},LAST_INSERT_ID())");

#update session to include newly created project id

	    push(@projids,$rs[0]);
	    $session->param('projects', \@projids);
	}
	else
	{
	    $statusmsg = "Paswords do not match. Please re-enter them.";
	}
    }
    else
    {
	$statusmsg = "Project name is already in use. Please choose a different project name.";
    }

#show updated list
    $params{mode}='login';
}

if($params{mode} eq 'adduser') 
{
#check project password
    my $im = Crypt::Imail->new();
    my $encrypted_pass = $im->encrypt('defaultuser', $params{projpass}); 
    my $chkh=$dbh->prepare("select password from project where project_id=?")||die;
    $chkh->execute($params{pid})||die;
    my ($dbpass) = $chkh->fetchrow_array;
    
    if($dbpass eq $encrypted_pass)
    {

# check if user exists
	my $sth = $dbh->prepare("select user_id from users where username='$params{usertoadd}'");
	$sth->execute();
	if (my @userinfo = $sth->fetchrow_array)
	{
	    my $uid = $userinfo[0];
	    $dbh->do("insert into user_project(user_project_id,user_id,project_id) values('',$uid,$params{pid})");
	}
	else
	{
	    $statusmsg = "Invalid username entered. User not added to project.";
	}
    }
    else
    {
	$statusmsg = "Incorrect project administrator password entered. Please check password and try again";
    }
#show updated list
    $params{mode}='login';
}

if($params{mode} eq 'updatedesc') 
{
#check project password
    my $im = Crypt::Imail->new();
    my $encrypted_pass = $im->encrypt('defaultuser', $params{projpass}); 
    my $chkh=$dbh->prepare("select password from project where project_id=?")||die;
    $chkh->execute($params{pid})||die;
    my ($dbpass) = $chkh->fetchrow_array;
    
    if($dbpass eq $encrypted_pass)
    {

# perform update
	my $pdesc = $params{projdesc};
	$pdesc =~ s/'/\\'/g;
	$pdesc =~ s/"/\\"/g;
	$dbh->do("update project set description='$pdesc' where project_id=$params{pid}");
    }
    else
    {
	$statusmsg = "Incorrect project administrator password entered. Please check password and try again";
    }
#show updated list
    $params{mode}='login';
}

if ($params{mode} eq 'updatestatus') 
{
    $dbh->do("update project set status='$params{projstatus}' where project_id=$params{pid}");
#show updated list
    $params{mode}='login';
}

if ($params{mode} eq 'useremove') 
{
#check number of users in project
    my $sth = $dbh->prepare("select count(*) from user_project where project_id=$params{pid}");
    $sth->execute();
    my @usercount = $sth->fetchrow_array;
    my $numusers = $usercount[0];

    if($numusers > 1)
    {
	my $rh = $dbh->prepare("delete from user_project where user_id=$params{uid} and project_id=$params{pid}");
	$rh->execute();
    }
    else
    {
	$statusmsg = "No other users in this project. There must be 2 or more users in a project before you can remove yourself";
    }
#show updated list
    $params{mode}='login';
}

if ($params{mode} eq 'delete') 
{
    my $project_id = $params{pid};

#check project password
    my $im = Crypt::Imail->new();
    my $encrypted_pass = $im->encrypt('defaultuser', $params{projpass}); 
    my $chkh=$dbh->prepare("select password from project where project_id=?")||die;
    $chkh->execute($params{pid})||die;
    my ($dbpass) = $chkh->fetchrow_array;
    
    if($dbpass eq $encrypted_pass)
    {

#select all ids from project specific records
    $sth=$dbh->prepare("show tables");
    $sth->execute()||die;
    my %table_ids;
    my @tables;
    while (my $table  = $sth->fetchrow_array) {
	my $table_id = $table."_id";
	my $clh=$dbh->prepare("desc $table");
	$clh->execute()||die;
	my $i=0;
	while (my $col  = $clh->fetchrow_hashref) {
	    if ($col->{Field} eq 'project_id') {
		$i=1;
	    }
	}
	if ($i == 1) {
	    my $prh=$dbh->prepare("select $table_id from $table where project_id=?")||die;
	    $prh->execute($project_id)||die;
	    while (my ($id)  = $prh->fetchrow_array) {
		push (@{$table_ids{$table}},$id);
	    }
	    my $delh=$dbh->prepare("delete from $table where project_id=?");
	    $delh->execute($project_id)||die;
	} else {
	    push (@tables, $table);
	}
    }

    foreach (@tables) {
	if ($_ eq 'analysis_i_link') {
	    foreach my $tbl_id (@{$table_ids{'analysis_input'}}) {
		my $delh=$dbh->prepare("delete from analysis_i_link where analysis_input_id=?");
		$delh->execute($tbl_id)||die;
	    }
	} elsif ($_ eq 'analysis_o_link') {
	    foreach my $tbl_id (@{$table_ids{'analysis_output'}}) {
		my $delh=$dbh->prepare("delete from analysis_o_link where analysis_output_id=?");
		$delh->execute($tbl_id)||die;
	    }
	} elsif ($_ eq 'anchor_reg_seq') {
	    foreach my $tbl_id (@{$table_ids{'reg_seq'}}) {
		my $delh=$dbh->prepare("delete from anchor_reg_seq where reg_seq_id=?");
		$delh->execute($tbl_id)||die;
	    }
	} elsif ($_ eq 'matrix_info') {
	    foreach my $tbl_id (@{$table_ids{'matrix'}}) {
		my $delh=$dbh->prepare("delete from matrix_info where matrix_id=?");
		$delh->execute($tbl_id)||die;
	    }
	} elsif ($_ eq 'mutation') {
	    foreach my $tbl_id (@{$table_ids{'mutation_set'}}) {
		my $delh=$dbh->prepare("delete from mutation where mutation_set_id=?");
		$delh->execute($tbl_id)||die;
	    }
	} elsif ($_ eq 'reg_seq_set') {
	    foreach my $tbl_id (@{$table_ids{'matrix'}}) {
		my $delh=$dbh->prepare("delete from reg_seq_set where matrix_id=?");
		$delh->execute($tbl_id)||die;
	    }
	} elsif ($_ eq 'tf_complex') {
	    foreach my $tbl_id (@{$table_ids{'funct_tf'}}) {
		my $delh=$dbh->prepare("delete from tf_complex where funct_tf_id=?");
		$delh->execute($tbl_id)||die;
	    }
	}
    }
}
else
{
    $statusmsg = "Incorrect project administrator password entered. Please check password and try again";
}
#show updated list
    $params{mode}='login';
}


if ($params{mode} eq 'login' || $loggedin eq 'true') 
{
#verify user name and password
    my $im = Crypt::Imail->new();
    my $encrypted_pass = $im->encrypt($params{username}, $params{password}); 
    my $chkh=$dbh->prepare("select user_id,aff,first_name,last_name from users where username=? and password=?")||die;
    $chkh->execute($params{username},$encrypted_pass)||die;
    my ($userid,$aff,$first,$last)=$chkh->fetchrow_array;

    if($userid ne '')
    {
#show any status messages
	print "<center><font color='red'>$statusmsg</font></center>";

#show projects

	print "<table border=1 cellspacing=0 cellpadding=2>\n";
#print projects
	my $sth=$dbh->prepare("select project_id from user_project where user_id=?");
	$sth->execute($userid);
	
	print "<tr><td><b>Project ID</b></td><td><b>Project Name</b></td><td><b>Project Description</b></td><td><b>Project Status</b></td><td><b>Last Edited</b></td><td><b>Project Users</b></td><td>&nbsp;</td><td>&nbsp;</td></tr>";
	
	while(my @results = $sth->fetchrow_array)
	{
	    my $proj_id = $results[0];
	    #get project info
	    my $sth2 = $dbh->prepare("select * from project where project_id=?");
	    $sth2->execute($proj_id);
	    #print project entry
	    my @projdetails = $sth2->fetchrow_array;

	    print "<tr><td>$proj_id</td><td>$projdetails[1]</td>";

#project description
	    print "<form name=\"updatedescform$proj_id\" id=\"updatedescform$proj_id\" method='post' action='editprojects.pl'><td><textarea name='projdesc' cols=40 rows=6>$projdetails[4]</textarea>";
print "<input type='hidden' name='username' value='$params{username}'><input type='hidden' name='password' value='$params{password}'><input type='hidden' name='pid' value='$proj_id'><input type='hidden' name='mode' value='updatedesc'>Project Password: <br><input type='password' name='projpass'><input type='button' onClick='doUpdateDesc($proj_id);' value='Update Project Description'></form>";
print "</td>";

#project status update form

	    print "<td><form method='post' action='editprojects.pl'>";

	    print "<select name='projstatus'>";
	    print "<option ";
	    if(lc($projdetails[3]) eq "restricted")
	    {
		print "selected ";
	    }
	    print "name='restricted' value='restricted'>restricted";

	    print "<option ";
	    if(lc($projdetails[3]) eq "open")
	    {
		print "selected ";
	    }
	    print "name='open' value='open'>open";
	    
	    print "<option ";
	    
	    if(lc($projdetails[3]) eq "published")
	    {
		print "selected ";
	    }
	    print "name='published' value='published'>published</select>";
	    
	    print "<input type='hidden' name='username' value='$params{username}'><input type='hidden' name='password' value='$params{password}'><input type='hidden' name='mode' value='updatestatus'><input type='hidden' name='pid' value='$proj_id'><input type='submit' value='Update Project \nStatus'></form>";
	    
	    print "</td><td>$projdetails[5]</td><td>";

#retrieve users
	    my $userlisthandle = $dbh->prepare("select username from users,user_project where users.user_id=user_project.user_id and user_project.project_id=?");
	    $userlisthandle->execute($proj_id);
	    my $userstring = "";
	    while(my @users = $userlisthandle->fetchrow_array)
	    {
		my $user = $users[0];
		$userstring = $userstring . ", ". $user;
	    }
	    $userstring = substr($userstring,2);
	    print $userstring;
#form: add user to this project
	    print "</td><td><form name=\"useraddform$proj_id\" id=\"useraddform$proj_id\" method='post' action='editprojects.pl'><input type='hidden' name='username' value='$params{username}'><input type='hidden' name='password' value='$params{password}'><input type='hidden' name='pid' value='$proj_id'><input type='hidden' name='mode' value='adduser'>Registered Username: <br><input type='text' name='usertoadd' size=25><br>Project Password: <br><input type='password' name='projpass'><input type='button' onClick='doUserAdd($proj_id);' value='Add User To This Project'></form></td>";


#delete project form
	    print "<td><form name=\"deleteform$proj_id\" id=\"deleteform$proj_id\" method='post' action='editprojects.pl'><input type='hidden' name='username' value='$params{username}'><input type='hidden' name='password' value='$params{password}'><input type='hidden' name='mode' value='delete'><input type='hidden' name='pid' value='$proj_id'>Project Password: <br><input type='password' name='projpass'><br><input type='button' onClick='doDelete($proj_id);' value='Delete This Project' ></form><hr>";

#remove myself from this project
print "<form method='post' action='editprojects.pl'><input type='hidden' name='username' value='$params{username}'><input type='hidden' name='password' value='$params{password}'><input type='hidden' name='mode' value='useremove'><input type='hidden' name='pid' value='$proj_id'><input type='hidden' name='uid' value='$userid'><input type='submit' value='Remove Myself \nFrom This Project'></form></td>";
	}

	print "</tr></table>\n";
print<<AddFormHead;
	<p>
	    <form name='createprojectform' method='post' action='editprojects.pl'>
	    <input type='hidden' name='mode' value='add'>
	    <input type='hidden' name='uid' value='$userid'>
AddFormHead

print "<input type='hidden' name='username' value='$params{username}'>";
print "<input type='hidden' name='password' value='$params{password}'>";

print<<AddFormFoot;

<!-- Form to add a new project -->
	<table border=1 cellspacing=0 cellpadding=2>
	    <tr><td colspan=2 align='center'><b>Create A New Project</b></td></tr>
	    <tr><td >Name</td><td><input type="text" name="projname" maxlength=20></td></tr>
	    <tr><td >Status</td><td><select name="projstatus"><option name="restricted" value="restricted">restricted<option name="published" value="published">published<option name="open" value="open">open</select></td></tr>
<tr><td>Description</td><td><textarea name="projdesc" cols=40 rows=6></textarea></td></tr>
<tr><td >Administrator Password</td><td><input type="password" name="projpass" maxlength=20></td></tr>
<tr><td >Re-enter Admin Password</td><td><input type="password" name="projpasscheck" maxlength=20></td></tr>
<tr><td colspan=2><input type="button" onClick="verifyProjectCreate();" value='Create New Project'></td></tr>
	    </table>	    
	    </form>
AddFormFoot
}
    else
    {
#print error
print<<Error_Page_1;

	    <p class="title1">PAZAR Project Management</p>
Error_Page_1

	    print "<p class=\"warning\">Could not log you in. Please check user name and password and try again</p>";
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

	<p class="title1">PAZAR Project Manager</p>


	<FORM  method="POST" action="dologin.pl">
	<table>
	<tr><td >User name</td><td> <input type="text" name="username"></td></tr>      
	<tr><td >Password</td><td> <input type="password" name="password"></td></tr>
	<tr><td colspan=2><input type="hidden" name="mode" value="login"></td></tr>
        <tr><td colspan=2><input type="hidden" name="project" value="true"></td></tr>
	<tr><td></td><td><INPUT type="submit" name="login" value="login"></td></tr>
	</table>
	</FORM>

Page_Done
    }

# print out the html tail template
my $template_tail = HTML::Template->new(filename => 'tail.tmpl');
print $template_tail->output;
