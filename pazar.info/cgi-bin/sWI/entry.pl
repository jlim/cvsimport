#!/usr/bin/perl

use HTML::Template;
use CGI qw( :all);
#use CGI::Debug( report => 'everything', on => 'anything' );
use pazar;

require '/usr/local/apache/pazar.info/cgi-bin/getsession.pl';

# open the html header template
my $template = HTML::Template->new(filename => '/usr/local/apache/pazar.info/cgi-bin/header.tmpl');

# fill in template parameters
$template->param(TITLE => 'Submission entry form');
$template->param(JAVASCRIPT_FUNCTION => q{
function MM_findObj(n, d) { //v4.01
  var p,i,x;  if(!d) d=document; if((p=n.indexOf("?"))>0&&parent.frames.length) {
    d=parent.frames[n.substring(p+1)].document; n=n.substring(0,p);}
  if(!(x=d[n])&&d.all) x=d.all[n]; for (i=0;!x&&i<d.forms.length;i++) x=d.forms[i][n];
  for(i=0;!x&&d.layers&&i<d.layers.length;i++) x=MM_findObj(n,d.layers[i].document);
  if(!x && d.getElementById) x=d.getElementById(n); return x;
}

function MM_validateForm() { //v4.0
  var i,p,q,nm,test,num,min,max,errors='',args=MM_validateForm.arguments;
  for (i=0; i<(args.length-2); i+=3) { test=args[i+2]; val=MM_findObj(args[i]);
    if (val) { nm=val.name; if ((val=val.value)!="") {
      if (test.indexOf('isEmail')!=-1) { p=val.indexOf('@');
        if (p<1 || p==(val.length-1)) errors+='- '+nm+' must contain an e-mail address.\n';
      } else if (test!='R') { num = parseFloat(val);
        if (isNaN(val)) errors+='- '+nm+' must contain a number.\n';
        if (test.indexOf('inRange') != -1) { p=test.indexOf(':');
          min=test.substring(8,p); max=test.substring(p+1);
          if (num<min || max<num) errors+='- '+nm+' must contain a number between '+min+' and '+max+'.\n';
    } } } else if (test.charAt(0) == 'R') errors += '- '+nm+' is required.\n'; }
  } if (errors) alert('The following error(s) occurred:\n'+errors);
  document.MM_returnValue = (errors == '');
}

resetMenu = function() {
   var ddm=document.getElementsByTagName("select");
   for (var n=0; n<ddm.length; n++) {
      ddm[n].selectedIndex=0;
   }
}

function verifyProjectCreate() {
	var themessage = "You are required to complete the following fields: ";
	var iChars = "!@#$%^&*()+=-[]\\\';,./{}|\":<>?";	    
	// might want to be less strict with the description later
	    var iChars_desc = "!@$^*()+[]\\\'=&{}|\"<>";
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
    }
});

if($loggedin eq 'true')
{
    #log out link
    $template->param(LOGOUT => "$info{first} $info{last} logged in. ".'<a href=\'http://www.pazar.info/cgi-bin/logout.pl\'>Log Out</a>');
}
else
{
    #log in link
    $template->param(LOGOUT => '<a href=\'http://www.pazar.info/cgi-bin/login.pl\'>Log In</a>');
}

# send the obligatory Content-Type and print the template output
print "Content-Type: text/html\n\n", $template->output;

my $cgiroot=$ENV{SERVER_NAME}.$ENV{PAZARCGI}.'/sWI';
my $docroot=$ENV{PAZARHTDOCSPATH}.'/sWI';

my $query= new CGI;
my %params = %{$query->Vars};
my $npage="$docroot/entryform1.htm";

if($loggedin eq 'true') {
    my $pazar = pazar->new( 
			    -host          =>    $ENV{PAZAR_host},
			    -user          =>    $ENV{PAZAR_pubuser},
			    -pass          =>    $ENV{PAZAR_pubpass},
			    -dbname        =>    $ENV{PAZAR_name},
			    -drv           =>    'mysql');
    my @projnames;
    foreach my $pid (@projids) {
	my $sth=$pazar->prepare("select project_name from project where project_id=?");
	$sth->execute($pid);
	my $result = $sth->fetchrow_array;
	if ($result ne '') { push @projnames,$result;}
    }

    open (NPAGE,$npage)||die;
    while (my $buf=<NPAGE>) {
	if ($buf=~/action/i) {
	    $buf=~s/serverpath/$cgiroot/i;
	}
	print $buf;
	if ($buf=~/<hr><br><p><b>Submit to Project/i) {
	    print $query->scrolling_list('project',\@projnames,1,'true');
	}
    }
	print "<font color='red'>$params{statusmsg}</font>";
print<<AddFormHead;
	    <form name='createprojectform' method='post' action='http://www.pazar.info/cgi-bin/editprojects.pl'>
	    <input type='hidden' name='mode' value='add'>
	    <input type='hidden' name='uid' value='$info{userid}'>
AddFormHead

print "<input type='hidden' name='username' value='$info{user}'>";
print "<input type='hidden' name='password' value='$info{password}'>";
print "<input type='hidden' name='submission' value='true'>";
print<<AddFormFoot;
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

} else {
print<<Page_Done;

	<p class="title1">PAZAR Submission Interface</p>
        <p class="warning">You need to login in order to submit data!</p>

	<FORM  method="POST" action="http://www.pazar.info/cgi-bin/dologin.pl">
	<table>
	<tr><td >User name</td><td> <input type="text" name="username"></td></tr>      
	<tr><td >Password</td><td> <input type="password" name="password"></td></tr>
	<tr><td colspan=2><input type="hidden" name="mode" value="login"></td></tr>
        <tr><td colspan=2><input type="hidden" name="submission" value="true"></td></tr>
	<tr><td></td><td><INPUT type="submit" name="login" value="login"></td></tr>
	</table>
	</FORM>

Page_Done

}

# print out the html tail template
my $template_tail = HTML::Template->new(filename => '/usr/local/apache/pazar.info/cgi-bin/tail.tmpl');
print $template_tail->output;
