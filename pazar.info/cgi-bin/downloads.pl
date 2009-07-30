#!/usr/bin/perl

use HTML::Template;
my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};
my $pazarhtdocspath = $ENV{PAZARHTDOCSPATH};

my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");
my $temptail = HTML::Template->new(filename => "$pazarcgipath/tail.tmpl");
$template->param(TITLE => "Downloads | PAZAR");
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
	<h1>Downloads</h1>
	<p>An XML dump of the data in each public project is generated every week if new data has been added since the last dump. The resulting XML files are available below.</p>};

my $tc;

my $dir=chdir("$pazarhtdocspath/XML_data/");
my $file_list=`ls *.xml`;
my @files=split("\n",$file_list);

my $bg_color = 0;
my %colors = (
	0 => "#fffff0",
	1 => "#BDE0DC"
);

foreach my $file (@files) {
    my $proj_name = $file;
    $proj_name =~ s/pazar_//;
    $proj_name =~ s/\.xml//;
    my $date = substr($proj_name, -9, 9, "");
    $date =~ s/_//;
	$tc .= qq{
		<tr style="background-color: $colors{$bg_color};">
			<td class="tm">$proj_name</td>
			<td class="tm"><a target="_blank" href="http://www.pazar.info/XML_data/$file">$file</a></td>
			<td class="tm">$date</td>
		</tr>};
	$bg_color = 1 - $bg_color;
}

if ($tc) {
	print qq{
		<table class="summarytable w100p" cellspacing="0" cellpadding="0" border="0">
			<tbody>
				<tr>
					<td class="gdtc">Project name</td>
					<td class="gdtc">File</td>
					<td class="gdtc">Last saved</td>
				</tr>
				$tc
			</tbody>
		</table>};
} else {
	print qq{<div class="emp">There are currently no downloads available here. Please check back soon...</div>};
}

print $temptail->output;
