#!/usr/bin/perl
#
#  PROGRAM:	cookie-get.cgi
#
#  PURPOSE:	session information retrieval, to be included in all web pages
#		
#
#  Copyright DevDaily Interactive, Inc., 1998. All Rights Reserved.
#

#------------------------------#
#  1. Create a new CGI object  #
#------------------------------#

use CGI;
use CGI::Cookie;
$query = new CGI;

$cookieExists = false;
%info = ();
@projids = ();

#$theCookie = $query->cookie('MY_COOKIE');
%cookies = fetch CGI::Cookie;
$pazarCookie = $cookies{'PAZAR_COOKIE'};
$pazarProjectCookie = $cookies{'PAZAR_PROJECT_COOKIE'};
#--------------------------------------------------------------#
#  2. Create the HTTP header and print the doctype statement.  #
#--------------------------------------------------------------#

#print $query->header(-cookie=>[$theCookie])

#print $query->header();
#----------------------------------------------------#
#  3. Start the HTML doc, and give the page a title  #
#----------------------------------------------------#

#print $query->start_html('My cookie-get.cgi program');


#----------------------------------------------------------------------#
#  4. Retrieve the cookie. Do this by using the cookie method without  #
#     the -value parameter.                                            #
#----------------------------------------------------------------------#

if($pazarCookie && $pazarProjectCookie)
{
    $cookieExists = true;
#    print $query->h3('Cookie exists');

#retrieve cook information into variables

%info = $pazarCookie->value;

@projids = $query->cookie('PAZAR_PROJECT_COOKIE');
}
else
{
    $cookieExists=false;
#    print $query->h3('Cookie not found');

}



#print $query->h3('The cookie is ...');


#print "

#    \n"; print $theCookie->value; print "

#\n";



#-------------------------#
#  5. End the HTML page.  #
#-------------------------#

#print $query->end_html;

1;
