#!/usr/bin/perl

use HTML::Template;

my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};

# open the html header template
my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");

# fill in template parameters
$template->param(TITLE => 'PAZAR XML format');
$template->param(PAZAR_HTML => $pazar_html);
$template->param(PAZAR_CGI => $pazar_cgi);

# send the obligatory Content-Type and print the template output
print "Content-Type: text/html\n\n", $template->output;

print<<page;
          <p class="title1">PAZAR - XML format</p>
          <p class="title2">Overview:</p>
          <p>To ease the insertion of data into the database, we have designed 
          an XML exchange format (<a href="http://www.w3schools.com/xml/default.asp" target="_blank">What is 
          XML?</a>) that can be used to format already existing datasets. The
          <a href="$pazar_html/pazar.dtd">PAZAR Document Type 
          Definition</a> (DTD) is now available as well as a
          <a href="$pazar_html/PAZAR_DTD_DOC.pdf">documentation</a> 
          explaining its use.&nbsp; Some examples are also provided to help the user 
          understand the XML format:</p>
          <p class="margin2">- 
            <a href="$pazar_html/pazarexample.xml">example 1</a> 
            describes an interaction between a transcription factor and a 
            binding site located upstream a gene, and a set of mutations 
            affecting this interaction.<br>- 
            <a href="$pazar_html/pazarexample2.xml">example 2</a> 
            describe a SELEX experiment with an heterodimer transcription factor 
            and the matrix built from the sequences.<br>- 
            <a href="$pazar_html/pazarexample3.xml">example 3</a> 
            describes a gene reporter assay and the influence of co-expression 
            with a transcription factor.
          <br><br></p>
          <p class="title2">
          <span class="red">NEW!!!</span> Try our 
          Step-by-step documentation:</p>
          <p>Our step-by-step documentation is meant to help users 
          write a backbone PAZAR XML file containing their data. It does not 
          include all the possibilities and details available through the 
          Document Type Definition, but is a good starting point to understand 
          its structure.
          </p>
          <p class="margin2"><a href="$pazar_cgi/step1.pl">1. Getting started</a><br>
          <a href="$pazar_cgi/step2.pl">2. Capturing the regulatory 
          sequence and/or TF basic information</a><br>
          <a href="$pazar_cgi/step3.pl">3. Capturing the evidence 
          Linking a sequence to a TF or to a specific expression</a><br>
&nbsp;</p>
          <p class="title2">XML Validator:</p>
          <p>Just upload your XML file below and Click on the "Validate" button 
          to check its validity against PAZAR DTD.
<form name="validator" method="post" action="$pazar_cgi/validator.cgi" enctype="multipart/form-data">
            <input name="xml_file" size="20" type="file"><br>
            <br>
            <input name="validate" value="Validate" type="submit">
          </form>
          </p>

page

# print out the html tail template
my $template_tail = HTML::Template->new(filename => "$pazarcgipath/tail.tmpl");
print $template_tail->output;
