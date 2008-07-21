#!/usr/bin/perl

use HTML::Template;

my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};
my $pazarhtdocspath = $ENV{PAZARHTDOCSPATH};

# open the html header template
my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");

# fill in template parameters
$template->param(TITLE => 'PAZAR Downloads');
$template->param(PAZAR_HTML => $pazar_html);
$template->param(PAZAR_CGI => $pazar_cgi);

# send the obligatory Content-Type and print the template output
print "Content-Type: text/html\n\n", $template->output;

print<<page_start;
          <p class="title1">PAZAR - Downloads</p>
<p>An XML dump of the data in each public project is generated every week if new data has been added since the last dump.<br>The resulting XML files are available below.</p><br>
<table border=1 cellspacing=0 cellpadding=2><tbody>
<tr><td><b>Project name</b></td><td><b>File</b></td><td><b>Last saved</b></td></tr>
page_start

my $dir=chdir("$pazarhtdocspath/XML_data/");
my $file_list=`ls *.xml`;
my @files=split("\n",$file_list);

foreach my $file (@files) {
    my $proj_name=$file;
    $proj_name=~s/pazar_//;
    $proj_name=~s/\.xml//;
    my $date=substr($proj_name, -9, 9, '');
    $date=~s/_//;

print<<table_content;
<tr><td>$proj_name</td><td><a target="_blank" href="http://www.pazar.info/XML_data/$file">$file</a></td><td><center>$date</center></td></tr>
table_content
   
}

print<<page_end;
</tbody>
</table>
page_end

# print out the html tail template
my $template_tail = HTML::Template->new(filename => "$pazarcgipath/tail.tmpl");
print $template_tail->output;
