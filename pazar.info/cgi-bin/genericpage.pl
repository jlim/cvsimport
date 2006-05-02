#!/usr/local/bin/perl

use HTML::Template;
use CGI::Cookie;
use CGI::Session;

require 'getsession.pl';

# open the html header template
my $template = HTML::Template->new(filename => 'header.tmpl');

# fill in template parameters
$template->param(TITLE => 'PAZAR Project Outline');

# send the obligatory Content-Type and print the template output
print "Content-Type: text/html\n\n", $template->output;
print "value of logged in variable: ".$loggedin."<br>";

if($loggedin eq 'true')
{

#get cookie and session values
    print "session id: ".$sessionid."<br>";
    print "number of session projects:".@projids."<br>";
    print "projects:";
    foreach my $proj (@projids)
    {
	print $proj."<br>";
    }
    print "session info number of keys:".(keys %info)."<br>";

    foreach $key (sort keys %info)
    {
	print "$key -> $info{$key}<br>";
    }
#add another name-value pair into session
    $session->param('test2','test2info');

    print "added value to session: ".$session->param('test2');
}

# print out the html tail template
my $template_tail = HTML::Template->new(filename => 'tail.tmpl');
print $template_tail->output;
