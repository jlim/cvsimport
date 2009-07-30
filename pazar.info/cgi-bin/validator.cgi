#!/usr/bin/perl

use HTML::Template;
use CGI qw(:standard);
use CGI::Carp qw(carpout);
use XML::Checker::Parser;
use CGI::Carp qw(fatalsToBrowser);

srand(time() ^ ($$ + ($$ << 15) ) );
my $file = "mycgi-log" . substr(rand() * 100,3);

my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};
my $pazarhtdocspath = $ENV{PAZARHTDOCSPATH};

open(LOG, ">>$pazarcgipath/cgi-logs/$file") or die("Unable to open mycgi-log: $!\n");
carpout(LOG);

my $max_allowed = 50000000;
my $total = 0;

my $get = new CGI;
my $xml_file = $get->param("xml_file");

my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");
my $temptail = HTML::Template->new(filename => "$pazarcgipath/tail.tmpl");

# fill in template parameters
$template->param(TITLE => "XML validator | PAZAR XML format | PAZAR");
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
		<a href="$pazar_cgi/dataformats.pl" class="b">Data formats</a> &raquo; <a href="$pazar_cgi/xml.pl" class="b">PAZAR XML format</a> &raquo; XML validator
		<div class="clear-r"></div>
	</div>
	<h1>PAZAR XML format</h1>
	<h2>XML validator</h2>};

if (!$xml_file) {
	print qq{<div class="emp">Please provide a XML file to validate.</div>};
} elsif (-e $xml_file) {
	open (OUTFILE,">$pazarhtdocspath/tmp/$xml_file");
	my ($bytesread, $buffer);
	binmode (OUTFILE);
	while ($bytesread = read($xml_file, $buffer, 4096)) { 
	if ($total + $bytesread > $max_allowed) {
	    $overflow = "true";
	    last;
	}
	$total += $bytesread;
	    print OUTFILE $buffer; 
	 } 
	close($xml_file);
	close(OUTFILE);
	if ($overflow eq "true") {
		print qq{<div class="emp">Sorry! Your file $xml_file is to big for this tool.</div>};
		unlink("$pazarhtdocspath/tmp/$xml_file");  
	}
	my $xp = new XML::Checker::Parser ( Handlers => { } );
	eval {
		local $XML::Checker::FAIL = \&my_fail;
		$xp->parsefile("$pazarhtdocspath/tmp/$xml_file");
	};
	close (LOG);

	if ($@) {
		print qq{<div class="emp">Sorry! Your file $xml_file failed validation.</div>};
		open(ERRLOG, "$pazarcgipath/cgi-logs/$file") or die("Unable to open mycgi-log: $!\n");
		print qq{<div class="p5to"><ul>};
		while (<ERRLOG>) {
			print qq{<li>$_</li>};
		}
		print qq{</ul></div>};
		close (ERRLOG);
		unlink("$pazarcgipath/cgi-logs/$file");
	} else {
		print qq{<div class="emp">Congratulations! Your file $xml_file passed validation.</div>};
	}
	unlink("$pazarhtdocspath/tmp/$xml_file");
} else {
	print qq{<div class="emp">Unable to open the file $xml_file.</div>};
}
print $temptail->output;

sub my_fail {
	my $code = shift;
	XML::Checker::print_error ($code, @_) if $code < 300;
	die XML::Checker::error_string ($code, @_) if $code < 200;
}

