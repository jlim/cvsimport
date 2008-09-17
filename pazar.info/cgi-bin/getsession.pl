#!/usr/bin/perl

use CGI;
use CGI::Cookie;
use CGI::Session;
$query = new CGI;

$loggedin = false;
%info = ();
@projids = ();
$sessionid = undef;
$session = undef;

%cookies = fetch CGI::Cookie;
$pazarCookie = $cookies{'PAZAR_COOKIE'};


if($pazarCookie)
{
#get the session
    $sessionid = $pazarCookie->value;
    $session = new CGI::Session("driver:File",$sessionid,{Directory=>"/tmp"});

#if session exists, populate %info and @projids
    if($session)
    {
	%info = %{ $session->param('info') };
	@projids = @{ $session->param('projects') };
	$loggedin = true;
    }
}


1;
