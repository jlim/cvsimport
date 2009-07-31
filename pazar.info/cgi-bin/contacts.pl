#!/usr/bin/perl

use HTML::Template;
my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};

my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");
my $temptail = HTML::Template->new(filename => "$pazarcgipath/tail.tmpl");
$template->param(TITLE => "Contact information | PAZAR");
$template->param(PAZAR_HTML => $pazar_html);
$template->param(PAZAR_CGI => $pazar_cgi);

require "$pazarcgipath/getsession.pl";
if ($loggedin eq "true") {
	$template->param(LOGOUT => qq{<span class="b">You are signed in as $info{first} $info{last}.</span> <a href="$pazar_cgi/logout.pl" class="b">Sign out</a>});
} else {
	$template->param(LOGOUT => qq{<a href="$pazar_cgi/login.pl"><span class="b">Sign in</span></a>});
}


print "Content-Type: text/html\n\n", $template->output;
print qq{
	<h1>Contact information</h1>
	<p>PAZAR is hosted by <a target="_blank" href="http://sourceforge.net/projects/pazar">SourceForge</a>, where everyone can go and browse the <a href="http://pazar.cvs.sourceforge.net/pazar/" target="_blank">CVS repository</a>. Our mailing list, "<a href="http://lists.sourceforge.net/lists/listinfo/pazar-news" target="_blank">News and Views</a>", is available in which every major development will be posted. Two forums are also available so that everyone can ask for help (at the <a href="https://sourceforge.net/forum/forum.php?forum_id=520428" target="_blank">PAZAR SourceForge help forum</a>) or make any comment or suggestion (at the <a href="https://sourceforge.net/forum/forum.php?forum_id=512784" target="_blank">PAZAR SourceForge open discussion forum</a>). If you want to contact us more directly, please use the e-mail below.</p>
	<h3>Current project members (alphabetical order)</h3>
	<ul>
		<li><span class="b">Jonathan Lim</span>, developer</li>
		<li><span class="b">Anthony McCallum</span>, developer</li>
		<li><span class="b">Elodie Portales-Casamar</span>, developer</li>
		<li><span class="b">Wyeth W. Wasserman</span>, PI</li>
		<li><span class="b">Dimas Yusuf</span>, developer</li>
		<li><span class="b">Cindy Zhang</span>, data curator</li>
		<li>Team e-mail: <img style="border:0; height:10px;" src="$pazar_html/images/email.gif"> <a href="mailto:pazar\@cmmt.ubc.ca">pazar\@cmmt.ubc.ca</a></li>
	</ul>
	<h3>Alumni (alphabetical order)</h3>
	<ul>
		<li><span class="b">Christopher Dickman</span>, data curator</li>
		<li><span class="b">Steven Jiang</span>, data curator</li>
		<li><span class="b">Stefan Kirov</span>, developer</li>
		<li><span class="b">Stuart Lithwick</span>, data curator</li>
		<li><span class="b">Jay R. Snoddy</span>, PI</li>
		<li><span class="b">Magdalena Swanson</span>, data curator</li>
		<li><span class="b">Amy Ticoll</span>, data curator</li>
	</ul>};

print $temptail->output;
