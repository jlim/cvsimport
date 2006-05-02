#!/usr/local/bin/perl

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

print $query->header(-cookie=>$pazarCookie);
my $template = HTML::Template->new(filename => 'header.tmpl');
# fill in template parameters
$template->param(TITLE => 'PAZAR Logout');

print $template->output;
print $query->h3('You are now logged out');

#-------------------------#
#  5. End the HTML page.  #
#-------------------------#
my $template_tail = HTML::Template->new(filename => 'tail.tmpl');
print $template_tail->output;
