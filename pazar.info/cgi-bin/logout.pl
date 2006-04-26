#!/usr/bin/perl
#
#  PROGRAM:	cookie-get.cgi
#
#  PURPOSE:	Demonstrate how to GET a cookie through a Perl/CGI program
#		using the CGI.pm module.
#
#  Copyright DevDaily Interactive, Inc., 1998. All Rights Reserved.
#

#------------------------------#
#  1. Create a new CGI object  #
#------------------------------#

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
#print $query->header(-cookie=>$pazarCookie);
#----------------------------------------------------#
#  3. Start the HTML doc, and give the page a title  #
#----------------------------------------------------#
#print $query->start_html;
# open the html header template
my $template = HTML::Template->new(filename => 'header.tmpl');

# fill in template parameters
$template->param(TITLE => 'PAZAR Login');

print $template->output;

#----------------------------------------------------------------------#
#  4. Retrieve the cookie. Do this by using the cookie method without  #
#     the -value parameter.                                            #
#----------------------------------------------------------------------#


print $query->h3('You are now logged out');


#-------------------------#
#  5. End the HTML page.  #
#-------------------------#
my $template_tail = HTML::Template->new(filename => 'tail.tmpl');
print $template_tail->output;
#print $query->end_html;
