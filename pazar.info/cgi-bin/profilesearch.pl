#!/usr/bin/perl

use HTML::Template;

my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};

require "$pazarcgipath/getsession.pl";

# open the html header template
my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");

# fill in template parameters
$template->param(TITLE => 'PAZAR Profile Search');
$template->param(PAZAR_HTML => $pazar_html);
$template->param(PAZAR_CGI => $pazar_cgi);

if($loggedin eq 'true')
{
    #log out link
    $template->param(LOGOUT => "$info{first} $info{last} logged in. "."<a href=\'$pazar_cgi/logout.pl\'>Log Out</a>");
}
else
{
    #log in link
    $template->param(LOGOUT => "<a href=\'$pazar_cgi/login.pl\'>Log In</a>");
}

# send the obligatory Content-Type and print the template output
print "Content-Type: text/html\n\n", $template->output;

print<<PAGE;
<p class="title1">PAZAR Profile Search</p>
<p><span class="title4">Description</span><br>
This search engine is for pre-computed profiles stored in the PAZAR boutiques.<br>They might not be linked to the sequences used to built them and even not to an identifiable transcription factor. For instance, they might have been built from multiple species and/or multiple factors presenting similar binding properties.<br>If you want to build a profile from a specific Transcription Factor using all its annotated binding sites, use the <a href="$pazar_cgi/tfsearch.pl">TF Search Engine</a> where profiles are generated dynamically.</p>
<p><span class=\"title4\">Search Engine</span><br>
<FORM method='post' action ="$pazar_cgi/export_profile.cgi" enctype="multipart/form-data" target="_self">Sort Profiles by: 
<input type="hidden" name="mode" value="list">
<input type="submit" name="BROWSE" value="Project">
<input type="submit" name="BROWSE" value="Name">
<input type="submit" name="BROWSE" value="Species">
<input type="submit" name="BROWSE" value="Class">
</form></p>
PAGE

# print out the html tail template
my $template_tail = HTML::Template->new(filename => "$pazarcgipath/tail.tmpl");
print $template_tail->output;

