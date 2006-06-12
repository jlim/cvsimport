#!/usr/bin/perl

use HTML::Template;

# open the html header template
my $template = HTML::Template->new(filename => 'header.tmpl');

# fill in template parameters
$template->param(TITLE => 'PAZAR Contact Information');

# send the obligatory Content-Type and print the template output
print "Content-Type: text/html\n\n", $template->output;

print<<page;
          <p class="title1">PAZAR - Contact Information</p>
<table border="0" cellpadding="0" cellspacing="0" width="550">
<tbody><tr><td style='text-align: justify;'>PAZAR is hosted by <a target="_blank" href="http://sourceforge.net/projects/pazar">sourceforge.net</a>, where everyone can go and browse the <a href="http://cvs.sourceforge.net/viewcvs.py/pazar/" target="_blank">CVS repository</a>.<br>
A mailing list <a href="http://lists.sourceforge.net/lists/listinfo/pazar-news" target="_blank">'News and Views'</a> is available in which every major development will be posted.<br>
Two forums are also available so that everyone can ask for help (<a href="https://sourceforge.net/forum/forum.php?forum_id=520428" target="_blank">'Help' forum</a>) or make any comment or suggestion (<a href="https://sourceforge.net/forum/forum.php?forum_id=512784" target="_blank">'Open Discussion' forum</a>).<br>
If you want to contact us more directly, please use the e-mail below.<br><br><hr>
</td></tr></tbody></table>
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
