#!/usr/bin/perl

use HTML::Template;
my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};

my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");
my $temptail = HTML::Template->new(filename => "$pazarcgipath/tail.tmpl");
$template->param(TITLE => "Step 1 - Getting Started | PAZAR XML format | PAZAR");
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
		<a href="$pazar_cgi/dataformats.pl" class="b">Data formats</a> &raquo; <a href="$pazar_cgi/xml.pl" class="b">PAZAR XML format</a> &raquo; Step-by-step documentation
		<div class="clear-r"></div>
	</div>
	<h1>PAZAR XML format</h1>
	<h2>Step 1 &mdash; Getting Started</h2>
	<div class="">
		<p>Each XML file starts with the project and curator descriptions. Please keep the project status as open while in our testing phase. You will be able to choose any of our options described in more details in the DTD Documentation later on.</p>
		<div class="p5bo"><div class="p10 bg-lg monospace b">
			&lt;?xml version="1.0" encoding="UTF-8"?&gt;
			<br>&lt;!DOCTYPE pazar SYSTEM "$pazar_html/pazar.dtd"&gt;
			<br>&lt;pazar&gt;
			<br>&nbsp;&nbsp;&nbsp; &lt;project edit_date="<span class="red">dd-mm-yy</span>" pazar_id="<span class="red">p_0001</span>"
			<br>&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp; project_name="<span class="red">example_project</span>" status="<span class="red">open</span>"&gt;
			<br>&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp; &lt;user affiliation="<span class="red">affiliation</span>" first_name="<span class="red">first_name</span>"
			<br>&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp; last_name="<span class="red">last_name</span>" pazar_id="<span class="red">u_0001</span>" username="<span class="red">user</span>"/&gt;
			<br>&nbsp;&nbsp;&nbsp; &lt;/project&gt;
		</div></div>
		<p><span class="b">Note: replace the red values with your own information.</span> The pazar IDs are internal IDs that will not be stored. They can be anything as long as they are unique throughout the file.</p>
		<p><a href="$pazar_cgi/step2.pl" class="b">Go to Step 2 &raquo;</a></p>
	</div>};
print $temptail->output;
