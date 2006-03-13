#!/usr/bin/perl
use DBI;
use Crypt::Imail;
use CGI qw( :all);
use HTML::Template;

my $query=new CGI;
my %params = %{$query->Vars};

my $DBUSER = "pazaradmin";
my $DBPASS = "32paz10";
my $DBURL = "DBI:mysql:dbname=pazar;host=napa.cmmt.ubc.ca";

my $dbh = DBI->connect($DBURL,$DBUSER,$DBPASS)
    or die "Can't connect to pazar database";

# open the html header template
my $template = HTML::Template->new(filename => 'header.tmpl');

# fill in template parameters
$template->param(TITLE => 'PAZAR Project Manager');

# send the obligatory Content-Type and print the template output
print "Content-Type: text/html\n\n", $template->output;

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
	    <tr><td >name</td><td><input type="text" name="projname"></td></tr>
	    <tr><td >status</td><td><select name="projstatus"><option name="restricted" value="restricted">restricted<option name="published" value="published">published</select></td></tr>
	    </table>
	    <input type='submit' value='Add new project'>
	    </form>
AddFormFoot
	}
    else
    {
#print error
print<<Error_Page_1;

	    <p class="title1">PAZAR Project Management</p>
Error_Page_1

	    print "<p class=\"warning\">Please check user name and password and try again</p>";
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

	<p class="title1">PAZAR User and Project creation</p>


	<FORM  method="POST" action="editprojects.pl">
	<table>
	<tr><td >User name</td><td> <input type="text" name="username"></td></tr>      
	<tr><td >Password</td><td> <input type="password" name="password"></td></tr>
	<tr><td colspan=2><input type="hidden" name="mode" value="login"></td></tr>
	<tr><td></td><td><INPUT type="submit" name="login" value="login"></td></tr>
	</table>
	</FORM>

Page_Done
    }

# print out the html tail template
my $template_tail = HTML::Template->new(filename => 'tail.tmpl');
print $template_tail->output;
