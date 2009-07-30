#!/usr/bin/perl

use HTML::Template;
my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};

my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");
my $temptail = HTML::Template->new(filename => "$pazarcgipath/tail.tmpl");

$template->param(TITLE => "PAZAR XML format | PAZAR");
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
		<a href="$pazar_cgi/dataformats.pl" class="b">Data formats</a> &raquo; PAZAR XML format
		<div class="clear-r"></div>
	</div>
	<h1>PAZAR XML format</h1>
	<h2>Overview</h2>
	<div class="">
		<p>To ease the insertion of data into the database, we have designed an XML exchange format (<a href="http://www.w3schools.com/xml/default.asp" target="_blank">What is XML?</a>) that can be used to format already existing datasets. The <a href="$pazar_html/pazar.dtd">PAZAR Document Type Definition</a> (DTD) is now available as well as a <a href="$pazar_html/PAZAR_DTD_DOC.pdf">documentation</a> explaining its use. Here are some examples to help you understand the XML format:</p>
		<div class="">
			<ul>
				<li><a href="$pazar_html/pazarexample.xml">Example 1</a> &mdash; an interaction between a TF and an upstream binding site, and a set of mutations that affect this interaction</li>
				<li><a href="$pazar_html/pazarexample2.xml">Example 2</a> &mdash; a SELEX experiment with an heterodimer transcription factor and the matrix built from the sequences</li>
				<li><a href="$pazar_html/pazarexample3.xml">Example 3</a> &mdash; a gene reporter assay and the influence of co-expression with a transcription factor</li>
			</ul>
		</div>
		<p>Note: the XML examples above may be displayed as blank pages in certain web browsers, such as Safari. In these cases, the example files can be opened in a text editor and viewed on the user\'s computer after being downloaded and saved.</p>
	</div>
	<h2>Step-by-step guide</h2>
	<div class="">
		<p>Our step-by-step documentation is meant to help users write a backbone PAZAR XML file containing their data. It does not include all the possibilities and details available through the Document Type Definition, but is a good starting point to understand its structure.</p>
		<ul>
			<li><a href="$pazar_cgi/step1.pl">Step 1</a> &mdash; getting started</li>
			<li><a href="$pazar_cgi/step2.pl">Step 2</a> &mdash; capturing the regulatory sequence and (or) TF basic information</li>
			<li><a href="$pazar_cgi/step3.pl">Step 3</a> &mdash; capturing the evidence Linking a sequence to a TF or to a specific expression</li>
		</ul>
	</div>
	<h2>XML validator</h2>
	<div class="">
		<p>Just upload your XML file below and Click on the "Validate" button to check its validity against PAZAR DTD.</p>
		<form name="validator" method="post" action="$pazar_cgi/validator.cgi" enctype="multipart/form-data">
			<input name="xml_file" size="20" type="file">
			<input name="validate" value="Validate" type="submit">
		</form>
	</div>};

print $temptail->output;
