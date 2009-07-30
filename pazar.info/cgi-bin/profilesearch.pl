#!/usr/bin/perl
use HTML::Template;
use CGI qw(:standard);
use CGI::Carp qw(fatalsToBrowser);
my $pazar_cgi    = $ENV{PAZAR_CGI};
my $pazar_html   = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};

my $get = new CGI;
my %param = %{ $get->Vars };
our $searchtab = $param{"searchtab"} || "profiles";
require "$pazarcgipath/getsession.pl";
require "$pazarcgipath/searchbox.pl";

my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");
$template->param(TITLE      => "View pre-computed profiles | PAZAR");
$template->param(PAZAR_HTML => $pazar_html);
$template->param(PAZAR_CGI  => $pazar_cgi);
if ($loggedin eq "true") {
	$template->param(LOGOUT => qq{<span class="b">You are signed in as $info{first} $info{last}.</span> 
	<a href="$pazar_cgi/logout.pl" class="b">Sign out</a>});
} else {
	$template->param(LOGOUT => qq{<a href="$pazar_cgi/login.pl"><span class="b">Sign in</span></a>});
}
print "Content-Type: text/html\n\n", $template->output;
print $bowz;
my $tplt = HTML::Template->new(filename => "$pazarcgipath/tail.tmpl");
print $tplt->output;
