#!/usr/bin/perl

use HTML::Template;

# open the html header template
my $template = HTML::Template->new(filename => 'header.tmpl');

# fill in template parameters
$template->param(TITLE => 'PAZAR Search');

# send the obligatory Content-Type and print the template output
print "Content-Type: text/html\n\n", $template->output;

print<<page;
          <p class="title1">PAZAR - Search</p>
<p class="margin2"><a href="http://www.pazar.info/cgi-bin/gsearch.pl"><b> Search by Gene </b></a><br>
      <br>
<a href="http://www.pazar.info/cgi-bin/tfsearch.pl"><b> Search by Transcription Factor </b></a><br>
      <br>
<a href=""><b> Advanced Search </b></a><br>
      <br>
</p>

page

# print out the html tail template
my $template_tail = HTML::Template->new(filename => 'tail.tmpl');
print $template_tail->output;
