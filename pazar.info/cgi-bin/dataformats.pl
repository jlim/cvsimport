#!/usr/bin/perl

use HTML::Template;

my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};

# open the html header template
my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");

# fill in template parameters
$template->param(TITLE => 'PAZAR Data Formats');
$template->param(PAZAR_HTML => $pazar_html);
$template->param(PAZAR_CGI => $pazar_cgi);

# send the obligatory Content-Type and print the template output
print "Content-Type: text/html\n\n", $template->output;

print<<page;
          <p class="title1">PAZAR - Data Formats</p>
<p class="title2"><a href="GFF.pl">PAZAR GFF format</a></p>
<p>PAZAR GFF format is intended to capture simple annotations. It is not meant to record a detailed annotation. Please use the XML format if you want more options.

<br><br>

</p>


          <p class="title2"><a href="xml.pl">PAZAR XML format</a></p>
          <p>To ease the insertion of data into the database, we have designed 
          an XML exchange format that can be used to format already existing datasets. The
          PAZAR Document Type 
          Definition</a> (DTD) is now available as well as a
          documentation
          explaining its use.
<br><br>

</p>
page

# print out the html tail template
my $template_tail = HTML::Template->new(filename => "$pazarcgipath/tail.tmpl");
print $template_tail->output;
