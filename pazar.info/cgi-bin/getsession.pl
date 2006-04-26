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


%cookies = fetch CGI::Cookie;
$pazarCookie = $cookies{'PAZAR_COOKIE'};
$pazarProjectCookie = $cookies{'PAZAR_PROJECT_COOKIE'};


if($pazarCookie && $pazarProjectCookie)
{
    $cookieExists = true;

    #retrieve cook information into variables
    %info = $pazarCookie->value;
    @projids = $query->cookie('PAZAR_PROJECT_COOKIE');
}
else
{
    $cookieExists=false;
}



1;
