#!/usr/bin/perl

use CGI;
use CGI::Cookie;
use CGI::Session;
use HTML::Template;

$query = new CGI;

%cookies = fetch CGI::Cookie;
$pazarCookie = $cookies{'PAZAR_COOKIE'};

$pazarCookie->expires('-1d');

#remove session from server
$sessionid = $pazarCookie->value;

CGI::Session->name("PAZAR_COOKIE");
my $session = new CGI::Session();

if($session)
{
    $session->delete();
}

#--------------------------------------------------------------#
#  2. Create the HTTP header and print the doctype statement.  #
#--------------------------------------------------------------#

my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};

print $query->header(-cookie=>$pazarCookie);
my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");
# fill in template parameters
$template->param(TITLE => 'PAZAR Logout');
$template->param(PAZAR_HTML => $pazar_html);
$template->param(PAZAR_CGI => $pazar_cgi);

print $template->output;
print $query->h3('You are now logged out');

#-------------------------#
#  5. End the HTML page.  #
#-------------------------#
my $template_tail = HTML::Template->new(filename => "$pazarcgipath/tail.tmpl");
print $template_tail->output;
