#!/usr/local/bin/perl

use CGI;
use CGI::Cookie;
use HTML::Template;

$query = new CGI;

%cookies = fetch CGI::Cookie;
$pazarCookie = $cookies{'PAZAR_COOKIE'};
$pazarProjectCookie = $cookies{'PAZAR_PROJECT_COOKIE'};
$pazarCookie->expires('now');
$pazarProjectCookie->expires('now');

#--------------------------------------------------------------#
#  2. Create the HTTP header and print the doctype statement.  #
#--------------------------------------------------------------#

print $query->header(-cookie=>[$pazarCookie, $pazarProjectCookie]);

my $template = HTML::Template->new(filename => 'header.tmpl');

# fill in template parameters
$template->param(TITLE => 'PAZAR Login');

print $template->output;
print $query->h3('You are now logged out');


#-------------------------#
#  5. End the HTML page.  #
#-------------------------#
my $template_tail = HTML::Template->new(filename => 'tail.tmpl');
print $template_tail->output;
