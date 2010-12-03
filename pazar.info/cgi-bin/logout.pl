#!/usr/bin/perl

use CGI;
use CGI::Cookie;
use CGI::Session;
use HTML::Template;
use CGI::Carp qw(fatalsToBrowser);

$query = new CGI;
%cookies = fetch CGI::Cookie;
$pazarCookie = $cookies{'PAZAR_COOKIE'};
$pazarCookie->expires('-1d');
$sessionid = $pazarCookie->value;
CGI::Session->name("PAZAR_COOKIE");
my $session = new CGI::Session();
if ($session) {
	$session->delete();
}
my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};
print $query->header(-cookie=>$pazarCookie);
my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");
my $temptail = HTML::Template->new(filename => "$pazarcgipath/tail.tmpl");
$template->param(TITLE => "Sign out | PAZAR");
$template->param(PAZAR_HTML => $pazar_html);
$template->param(PAZAR_CGI => $pazar_cgi);
if ($loggedin eq "true") {
	$template->param(LOGOUT => qq{<span class="b">You are signed in as $info{first} $info{last}.</span> <a href="$pazar_cgi/logout.pl" class="b">Sign out</a>});
} else {
	$template->param(LOGOUT => qq{<a href="$pazar_cgi/login.pl"><span class="b">Sign in</span></a>});
}
print $template->output;
print qq{<div class="emp">You've successfully signed out.</div>};
print qq{
		<h1>Sign in</h1>
		<div class="p10bo">
			<form method="POST" action="$pazar_cgi/dologin.pl">
				<table cellspacing="0" cellpadding="0" border="0">
					<tbody>
						<tr>
							<td class="p10ro p5bo b">Email</td>
							<td class="p10ro p5bo"><input type="text" name="username"></td>
						</tr><tr>
							<td class="p10ro p5bo b">Password</td>
							<td class="p10ro p5bo"><input type="password" name="password"></td>
						</tr><tr>
							<td class="p10ro p5bo">&nbsp;</td>
							<td class="p10ro p5bo"><input type="submit" name="login" value="Sign in"></td>
						</tr>
					</tbody>
				</table>
			</form>
		</div>
		<div class="b">New User? <a href="$pazar_cgi/register.pl" class="b">Click here to register.</a></div>
		<div class="b">Forgotten password? <a href="recoveruserpass.pl">Click here to request password.</a></div>
	};
print $temptail->output;
