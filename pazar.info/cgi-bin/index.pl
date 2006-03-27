#!/usr/bin/perl

use HTML::Template;

# open the html header template
my $template = HTML::Template->new(filename => 'header.tmpl');

# fill in template parameters
$template->param(TITLE => 'PAZAR Mall');

# send the obligatory Content-Type and print the template output
print "Content-Type: text/html\n\n", $template->output;

print<<page;
<object classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000" codebase="http://fpdownload.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=7,0,0,0" width="600" height="700" id="TF_Mall" align="middle">
<param name="allowScriptAccess" value="sameDomain" />
<param name="movie" value="http://www.pazar.info/images/TF_Mall.swf" /><param name="quality" value="high" /><param name="bgcolor" value="#ffffff" /><embed src="http://www.pazar.info/images/TF_Mall.swf" quality="high" bgcolor="#ffffff" width="600" height="700" name="TF_Mall" align="middle" allowScriptAccess="sameDomain" type="application/x-shockwave-flash" pluginspage="http://www.macromedia.com/go/getflashplayer" />
</object>
page

# print out the html tail template
my $template_tail = HTML::Template->new(filename => 'tail.tmpl');
print $template_tail->output;
