#!/usr/local/bin/perl
use DBI;
use Crypt::Imail;
use CGI qw( :all);
use HTML::Template;

require 'getsession.pl';

my $query=new CGI;

# open the html header template
my $template = HTML::Template->new(filename => 'header.tmpl');

# fill in template parameters
$template->param(TITLE => 'PAZAR Login');

if($loggedin eq 'true') {
    #log out link
    $template->param(LOGOUT => "$info{first} $info{last} logged in. ".'<a href=\'logout.pl\'>Log Out</a>');
    # send the obligatory Content-Type and print the template output
    print "Content-Type: text/html\n\n", $template->output;
    #print logout message if user already logged in
    print "<p class=\"warning\">You are already logged in!</p>";
} else {
    #log in link
    $template->param(LOGOUT => '<a href=\'login.pl\'>Log In</a>');

# send the obligatory Content-Type and print the template output
print "Content-Type: text/html\n\n", $template->output;


 print<<Page_Done;

	<p class="title1">PAZAR Login</p>
	<FORM  method="POST" action="dologin.pl">
	<table>
	<tr><td >User name</td><td> <input type="text" name="username"></td></tr>      
	<tr><td >Password</td><td> <input type="password" name="password"></td></tr>
	<tr><td></td><td><INPUT type="submit" name="login" value="login"></td></tr>
	</table>
	</FORM>

Page_Done
}

# print out the html tail template
my $template_tail = HTML::Template->new(filename => 'tail.tmpl');
print $template_tail->output;
