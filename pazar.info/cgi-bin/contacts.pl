#!/usr/bin/perl

use HTML::Template;

# open the html header template
my $template = HTML::Template->new(filename => 'header.tmpl');

# fill in template parameters
$template->param(TITLE => 'PAZAR Project Outline');

# send the obligatory Content-Type and print the template output
print "Content-Type: text/html\n\n", $template->output;

print<<page;
          <p class="title2">Project Members:</p>
          <p >Wyeth W. Wasserman, PI<br>
          Jay R. Snoddy, PI<br>
          Stefan Kirov, Postdoctoral fellow<br>
          Elodie Portales-Casamar, Postdoctoral fellow<br>
          Jonathan Lim, Software developer</p>
          <p class="title2">Team e-mail: &nbsp;&nbsp;<a href="mailto:pazar@cmmt.ubc.ca"><img style="border: 0px solid ; height: 12px;" src="http://www.pazar.info/images/email.gif"></a></p>

page

# print out the html tail template
my $template_tail = HTML::Template->new(filename => 'tail.tmpl');
print $template_tail->output;
