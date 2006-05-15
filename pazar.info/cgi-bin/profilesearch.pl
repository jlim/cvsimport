#!/usr/bin/perl

use HTML::Template;

use pazar;

use constant DB_DRV  => 'mysql';
use constant DB_NAME => $ENV{PAZAR_name};
use constant DB_USER => $ENV{PAZAR_pubuser};
use constant DB_PASS => $ENV{PAZAR_pubpass};
use constant DB_HOST => $ENV{PAZAR_host};

require 'getsession.pl';

# open the html header template
my $template = HTML::Template->new(filename => 'header.tmpl');

# fill in template parameters
$template->param(TITLE => 'PAZAR Profile Search');

if($loggedin eq 'true')
{
    #log out link
    $template->param(LOGOUT => "$info{first} $info{last} logged in. ".'<a href=\'logout.pl\'>Log Out</a>');
}
else
{
    #log in link
    $template->param(LOGOUT => '<a href=\'login.pl\'>Log In</a>');
}

# send the obligatory Content-Type and print the template output
print "Content-Type: text/html\n\n", $template->output;

print<<PAGE;
<p class="title1">PAZAR Profile Search</p>
<p><span class="title4">Description</span><br>
This search engine is for pre-computed profiles stored in the PAZAR boutiques.<br>They might not be linked to the sequences used to built them and even not to an identifiable transcription factor. For instance, they might have been built from multiple species and/or multiple factors presenting similar binding properties.<br>If you want to build a profile from a specific Transcription Factor using all its annotated binding sites, use the <a href="http://www.pazar.info/cgi-bin/tfsearch.pl">TF Search Engine</a> where profiles are generated dynamically.</p>
<p><span class=\"title4\">Search Engine</span><br>
<FORM method='post' action ='http://www.pazar.info/cgi-bin/export_profile.cgi' enctype="multipart/form-data" target="_self">Sort Profiles by: 
<input type="hidden" name="mode" value="list">
<input type="submit" name="BROWSE" value="Project">
<input type="submit" name="BROWSE" value="Name">
<input type="submit" name="BROWSE" value="Species">
<input type="submit" name="BROWSE" value="Class">
</form></p>
PAGE

# print out the html tail template
my $template_tail = HTML::Template->new(filename => 'tail.tmpl');
print $template_tail->output;

