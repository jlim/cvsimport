#!/usr/bin/perl

use HTML::Template;
my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};

my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");
my $temptail = HTML::Template->new(filename => "$pazarcgipath/tail.tmpl");
$template->param(TITLE => "Data formats | PAZAR");
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
	<div class="docp">
		<div class="float-r b txt-grey">PAZAR Documentation</div>
		<div class="clear-r"></div>
	</div>
	<h1>Data formats</h1>
	<div class="float-l w50p">
		<div class="p10ro">
			<h3>The <a href="GFF.pl">PAZAR GFF</a> format</h3>
			<div class="p5bo">PAZAR GFF format is intended to capture simple annotations. It is not meant to record a detailed annotation. Please use the PAZAR XML format if you want more options.</div>
			<div><a href="GFF.pl" class="b">Learn more about this format &raquo;</a></div>
		</div>
	</div>
	<div class="float-l w50p">
		<div class="p10lo">
			<h3>The <a href="xml.pl">PAZAR XML</a> format</h3>
			<div class="p5bo">To ease the insertion of data into the database, we have designed an XML exchange format that can be used to format already existing datasets. The PAZAR Document Type Definition</a> (DTD) is now available as well as a documentation explaining its use.</div>
			<div><a class="b" href="xml.pl">Learn more about this format &raquo;</a></div>
		</div>
	</div>
	<div class="clear-l"></div>};
print $temptail->output;
