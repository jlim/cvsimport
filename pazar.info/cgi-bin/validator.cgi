#!/usr/local/bin/perl

use CGI qw(:standard);
use CGI::Carp qw(fatalsToBrowser);
use HTML::Template;
use CGI::Carp qw(carpout);
use XML::Checker::Parser;

srand(time() ^ ($$ + ($$ << 15) ) );
my $randnum = substr(rand() * 100,3);
my $file = "mycgi-log".$randnum;

my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};
my $pazarhtdocspath = $ENV{PAZARHTDOCSPATH};

open(LOG, ">>$pazarcgipath/cgi-logs/$file") or
    die("Unable to open mycgi-log: $!\n");
carpout(LOG);

my $max_allowed = 50000000;
my $total = 0;

my $get = new CGI;
my $xml_file = $get->param('xml_file');

# open the html header template
my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");

# fill in template parameters
$template->param(TITLE => 'PAZAR XML format');
$template->param(PAZAR_HTML => $pazar_html);
$template->param(PAZAR_CGI => $pazar_cgi);

# send the obligatory Content-Type and print the template output
print "Content-Type: text/html\n\n", $template->output;

print<<head_page;
          <p class="title1">PAZAR - XML format</p>

head_page

if (!$xml_file) {
    print "<p class=\"warning\">Please provide a XML file to validate!</p>\n";

} elsif (-e $xml_file) {

    open(OUTFILE,">$pazarhtdocspath/tmp/$xml_file");
    my($bytesread,$buffer);
    binmode(OUTFILE);
    while ($bytesread = read($xml_file, $buffer, 4096)) { 
	if ($total+$bytesread>$max_allowed)
	{
	    $overflow = "true";
	    last;
	}
	$total+=$bytesread;
        print OUTFILE $buffer; 
     } 

    close($xml_file);
     close(OUTFILE);
    if ($overflow eq "true") {
	print "<p class=\"title2\">Sorry!<br>";
	print "Your file $xml_file is to big for this tool!<br><br></p>\n";
	unlink("$pazarhtdocspath/tmp/$xml_file");  
    }

    my $xp = new XML::Checker::Parser ( Handlers => { } );

    eval {
     local $XML::Checker::FAIL = \&my_fail;
     $xp->parsefile("$pazarhtdocspath/tmp/$xml_file");
    };
    close (LOG);

    if ($@) {
    print "<p class=\"title2\">Sorry!<br>";
    print "Your file $xml_file failed validation!<br><br></p>\n";

    open(ERRLOG, "$pazarcgipath/cgi-logs/$file") or
     die("Unable to open mycgi-log: $!\n");
    while (<ERRLOG>) {
	print "$_ <br>";
    }
    close (ERRLOG);
    unlink("$pazarcgipath/cgi-logs/$file");

    } else {
	print "<p class=\"title2\">Congratulations!<br>";
	print "Your file $xml_file passed validation!<br><br></p>\n";
    }

    unlink("$pazarhtdocspath/tmp/$xml_file");

} else {
    print "<p class=\"warning\">Unable to open the file $xml_file</p>\n";
}

# print out the html tail template
my $template_tail = HTML::Template->new(filename => "$pazarcgipath/tail.tmpl");
print $template_tail->output;

sub my_fail {
     my $code = shift;
     XML::Checker::print_error ($code, @_) if $code < 300;
     die XML::Checker::error_string ($code, @_) if $code < 200;
 }

