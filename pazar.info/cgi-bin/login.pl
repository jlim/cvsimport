#!/usr/bin/perl
use DBI;
use Crypt::Imail;
use CGI qw( :all);
use HTML::Template;

my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};

require "$pazarcgipath/getsession.pl";

my $query = new CGI;
my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");
my $temptail = HTML::Template->new(filename => "$pazarcgipath/tail.tmpl");
$template->param(TITLE => "Sign in | PAZAR");
$template->param(PAZAR_HTML => $pazar_html);
$template->param(PAZAR_CGI => $pazar_cgi);
my $msg;

if ($loggedin eq "true") {
	$template->param(LOGOUT => qq{<span class="b">You are signed in as $info{first} $info{last}.</span> <a href="$pazar_cgi/logout.pl" class="b">Sign out</a>});
	$msg = qq{
		<h1>Sign in</h1>
		<div class="b">You are currently signed in as $info{first} $info{last} (<a href="mailto:$info{user}">$info{user}</a>). <a href="$pazar_cgi/logout.pl" class="b">Click here to sign out</a></div>};
} else {
	$template->param(LOGOUT => qq{<a href="$pazar_cgi/login.pl"><span class="b">Sign in</span></a>});
	$msg = qq{
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
		<div class="b">Forgotten password? <a href="mailto:pazar\@cmmt.ubc.ca">Click here to request a new password.</a></div>
	};
}

print "Content-Type: text/html\n\n", $template->output;
print $msg . $temptail->output;
