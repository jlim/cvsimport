#!/usr/bin/perl

use HTML::Template;
use CGI::Cookie;
use CGI::Session;

my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};

require "$pazarcgipath/getsession.pl";

# open the html header template
my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");

# fill in template parameters
$template->param(TITLE => 'PAZAR Project Outline');
$template->param(PAZAR_HTML => $pazar_html);
$template->param(PAZAR_CGI => $pazar_cgi);

# send the obligatory Content-Type and print the template output
print "Content-Type: text/html\n\n", $template->output;


print<<RECOVERYFORM;
<h1>Forgot Your Password?</h1>
<br>
You may recover it by submitting the email address that you used to register.
<br><br>
<form name="pwrecovery" method="post" action="emailuserpassword.pl">
Email address: <input type="textbox" name=username size="30">
<input type="submit" value="Submit">
</form></p>
RECOVERYFORM

# print out the html tail template
my $temptail = HTML::Template->new(filename => "$pazarcgipath/tail.tmpl");
print $temptail->output;
