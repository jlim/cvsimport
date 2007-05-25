#!/usr/bin/perl

use HTML::Template;

my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};

# open the html header template
my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");

# fill in template parameters
$template->param(TITLE => 'PAZAR XML writing Step 1');
$template->param(PAZAR_HTML => $pazar_html);
$template->param(PAZAR_CGI => $pazar_cgi);

# send the obligatory Content-Type and print the template output
print "Content-Type: text/html\n\n", $template->output;

print<<page;
          <span class="title1">PAZAR - XML format</span><br>
          <span class="title2">Step-by-Step Documentation</span><br><br>
          <p class="title3">Step1: Getting started</p>
          <p>Each XML file starts with the project and curator
descriptions. Please keep the project status as open while in our
testing phase. You will be able to choose any of our options described
in more details in the DTD Documentation later on.</p>
      <p class="bold">&lt;?xml
version="1.0" encoding="UTF-8"?&gt;<br> 
&lt;!DOCTYPE pazar SYSTEM "$pazar_html/pazar.dtd"&gt;<br>
&lt;pazar&gt;<br>
&nbsp;&lt;project edit_date="<span class="red">dd-mm-yy</span>" pazar_id="<span class="red">p_0001</span>"<br>
&nbsp;&nbsp;&nbsp;project_name="<span class="red">example_project</span>" status="<span class="red">open</span>"&gt;<br>
&nbsp;&nbsp;&nbsp;&lt;user affiliation="<span class="red">affiliation</span>" first_name="<span class="red">first_name</span>"<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;last_name="<span class="red">last_name</span>" pazar_id="<span class="red">u_0001</span>" username="<span class="red">user</span>"/&gt;<br>
&nbsp;&lt;/project&gt;</p>
        <p class="small">Replace the red values with your own information.<br>
The pazar IDs are internal IDs that will not be stored. They can be
anything as long as they are unique throughout the file. 
      <br><br>
      <a style="text-decoration: none;" href="$pazar_cgi/step2.pl"><input value="To Step 2 -&gt;" type="button"></a></p>

page

# print out the html tail template
my $template_tail = HTML::Template->new(filename => "$pazarcgipath/tail.tmpl");
print $template_tail->output;
