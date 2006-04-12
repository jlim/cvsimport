#!/usr/local/bin/perl

use CGI qw(:standard);
use CGI::Carp qw(fatalsToBrowser);

BEGIN {
            use CGI::Carp qw(carpout);
            open(LOG, ">>/usr/local/apache/pazar.info/cgi-bin/cgi-logs/mycgi-log") or
              die("Unable to open mycgi-log: $!\n");
            carpout(LOG);
          }


use XML::Checker::Parser;


my $max_allowed = 50000000;
my $total = 0;

my $get = new CGI;
my $xml_file = $get->param('xml_file');

#print the output
print $get->header("text/html");
print "<head>
  <title>PAZAR XML format</title>
</head>


<body style=\"background-color: rgb(255, 255, 255);\">

<center>
<table width=\"600\">

  <tbody>

    <tr>

      <td width=\"600\">
      <center>

<p><b><i><span style=\"font-size: 20pt;\"><a style=\"text-decoration: none;\" href=\"/XML.html\">PAZAR XML format</a></span></i></b><br>
      </center>

      <hr><br><br><br>";

if (!$xml_file) {
    print "<big>Please provide a XML file to validate!</big>\n";

} elsif (-e $xml_file) {

    open(OUTFILE,">/usr/local/apache/pazar.info/tmp/$xml_file");
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
	print "<b><big>Sorry!</big></b><br>";
	print "<big>Your file $xml_file is to big for this tool!</big><br><br>\n";
	unlink("/usr/local/apache/pazar.info/tmp/$xml_file");  
    }

    my $xp = new XML::Checker::Parser ( Handlers => { } );

    eval {
     local $XML::Checker::FAIL = \&my_fail;
     $xp->parsefile("/usr/local/apache/pazar.info/tmp/$xml_file");
    };
    close (LOG);

    if ($@) {
    print "<b><big>Sorry!</big></b><br>";
    print "<big>Your file $xml_file failed validation!</big><br><br>\n";

    open(ERRLOG, "/usr/local/apache/pazar.info/cgi-bin/cgi-logs/mycgi-log") or
     die("Unable to open mycgi-log: $!\n");
    while (<ERRLOG>) {
	print "$_ <br>";
    }
    close (ERRLOG);
    unlink("/usr/local/apache/pazar.info/cgi-bin/cgi-logs/mycgi-log");

    } else {
	print "<b><big>Congratulations!</big></b><br>";
	print "<big>Your file $xml_file passed validation!</big>\n";
    }

    unlink("/usr/local/apache/pazar.info/tmp/$xml_file");

} else {
    print "<big>Unable to open the file $xml_file</big>\n";
}

print "</td></tr></tbody></table></center></body></html>";

sub my_fail {
     my $code = shift;
     XML::Checker::print_error ($code, @_) if $code < 300;
     die XML::Checker::error_string ($code, @_) if $code < 200;
 }

