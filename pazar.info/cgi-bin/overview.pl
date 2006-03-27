#!/usr/bin/perl

use HTML::Template;

# open the html header template
my $template = HTML::Template->new(filename => 'header.tmpl');

# fill in template parameters
$template->param(TITLE => 'PAZAR Project Outline');

# send the obligatory Content-Type and print the template output
print "Content-Type: text/html\n\n", $template->output;

print<<page;
          <p class="title1">PAZAR - Project Outline</p>
          <p class="title2">Introduction:</p>
          <p >Algorithms
and software for the analysis of transcription regulating sequences
have proliferated. Methods based on phylogenetic footprinting,
combinatorial interactions between transcription factors and genomics
data appear regularly. Unfortunately much of the research in the field
continues to re-analyze the same data. In order to advance this active
field, it is critical to gain unrestricted access to a broader range of
reference data. Such collections would be useful both for the
measurement of software performance and, most importantly, as fertile
ground for investigation. Small collections appear periodically in
independent databases, often as by-products of algorithm development
projects. For instance, the <a target="_blank" href="http://jaspar.cgb.ki.se/cgi-bin/jaspar_db.pl">JASPAR</a> database of binding profiles emerged
in this manner.</p>
          <p >PAZAR is a software
framework for the construction and maintenance of regulatory sequence
data annotations; a framework which allows multiple boutique databases
to function independently within a larger system (or information mall).
Our goal is to be the <b>public repository for regulatory data</b>.</p>
          <p ><a href="http://www.pazar.info/PAZARposter.pdf">Download PAZAR's poster</a></p>
          <p class="title2">PAZAR's principles:</p>
          <p >(1)
to be OPEN-ACCESS and OPEN-SOURCE, providing a completely transparent
development and data compilation. In this regard, the PAZAR project is
now hosted by <a target="_blank" href="http://sourceforge.net/projects/pazar">sourceforge.net</a>, where everyone can go and browse the <a href="http://cvs.sourceforge.net/viewcvs.py/pazar/" target="_blank">CVS
repository</a>. A mailing list <a href="http://lists.sourceforge.net/lists/listinfo/pazar-news" target="_blank">'News and Views'</a> is also available in which
every major development will be posted.</p>
          <p >(2) to function as a boutique system where curators own their data and can release it according to their own will.</p>
          <p >(3)
to be simple to use either in the curation process or the query of the
database. For this purpose we are currently developing an advanced API
to insulate the user from the underlying data model and to provide
simple methods for the user to deposit to or query from the database.</p>
          <p class="title2">Overview:</p>
          <p >The
PAZAR system is currently developed as a mySQL database featuring a
complex <a href="http://www.pazar.info/images/pazar_schema.png" target="_blank">schema</a> which allows for a high level of flexibility regarding
the type of information that can be captured. The database <a href="http://www.pazar.info/pazar_dictionary.html" target="_blank">dictionary</a>
and an explanation of the <a href="http://www.pazar.info/iosys.htm" target="_blank">input/output
system</a> can help you find out
some of the database constraints and internal structure.</p>
          <p >To
ease the insertion of data into the database, we are developing two
curation interfaces, one allowing the curator to capture higher levels
of details than the other. We have also designed an <a href="http://www.pazar.info/cgi-bin/xml.pl">XML exchange format</a> that can be used to format already existing datasets.</p>
          <p >As
an OPEN SYSTEM, each boutique operator within PAZAR is welcome to
participate in further API development and to create and maintain their
own annotation interfaces. Two forums are also available so that
everyone can ask for help (<a href="https://sourceforge.net/forum/forum.php?forum_id=520428" target="_blank">'Help' forum</a>) or make any comment or
suggestion (<a href="https://sourceforge.net/forum/forum.php?forum_id=512784" target="_blank">'Open Discussion' forum</a>).</p>

page

# print out the html tail template
my $template_tail = HTML::Template->new(filename => 'tail.tmpl');
print $template_tail->output;
