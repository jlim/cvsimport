#!/usr/bin/perl
use DBI;
use Crypt::Imail;
use CGI qw( :all);
use HTML::Template;

my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};

require "$pazarcgipath/getsession.pl";

my $query=new CGI;

# open the html header template
my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");

# fill in template parameters
$template->param(TITLE => 'PAZAR Login');
$template->param(PAZAR_HTML => $pazar_html);
$template->param(PAZAR_CGI => $pazar_cgi);

if($loggedin eq 'true') {
    #log out link
    $template->param(LOGOUT => "$info{first} $info{last} logged in. "."<a href=\'$pazar_cgi/logout.pl\'>Log Out</a>");
    # send the obligatory Content-Type and print the template output
    print "Content-Type: text/html\n\n", $template->output;
    #print logout message if user already logged in
    print "<p class=\"warning\">You are already logged in!</p>";
} else {
    #log in link
    $template->param(LOGOUT => "<a href=\'$pazar_cgi/login.pl\'>Log In</a>");

# send the obligatory Content-Type and print the template output
print "Content-Type: text/html\n\n", $template->output;


 print<<Page_Done;

	<p class="title1">PAZAR Login</p>
	<FORM  method="POST" action="$pazar_cgi/dologin.pl">
	<table>
	<tr><td >Email</td><td> <input type="text" name="username"></td></tr>      
	<tr><td >Password</td><td> <input type="password" name="password"></td></tr>
	<tr><td></td><td><INPUT type="submit" name="login" value="login"></td></tr>
	</table>
	</FORM>
<p>
<table>
<tr><td>New User?</td><td><a href="$pazar_cgi/register.pl">Click here to REGISTER</a></td></tr>

<tr><td>Forgotten Password?</td><td><a href="mailto:pazar\@cmmt.ubc.ca">Click here to EMAIL US</a></td></tr>
</table>
</p>
Page_Done
}

# print out the html tail template
my $template_tail = HTML::Template->new(filename => "$pazarcgipath/tail.tmpl");
print $template_tail->output;
