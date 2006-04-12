#!/usr/bin/perl

use HTML::Template;

use pazar;

use constant DB_DRV  => 'mysql';
use constant DB_NAME => $ENV{PAZAR_name};
use constant DB_USER => $ENV{PAZAR_pubuser};
use constant DB_PASS => $ENV{PAZAR_pubpass};
use constant DB_HOST => $ENV{PAZAR_host};

# open the html header template
my $template = HTML::Template->new(filename => 'header.tmpl');

# fill in template parameters
$template->param(TITLE => 'PAZAR Mall');

# send the obligatory Content-Type and print the template output
print "Content-Type: text/html\n\n", $template->output;

#connect to the database
my $dbh = pazar->new( 
		      -host          =>    DB_HOST,
		      -user          =>    DB_USER,
		      -pass          =>    DB_PASS,
		      -dbname        =>    DB_NAME,
		      -drv           =>    DB_DRV,
                      -globalsearch  =>    'yes');

my $projects=&select($dbh, "SELECT * FROM project WHERE status='open' OR status='published'");
my @desc;
while (my $project=$projects->fetchrow_hashref) {
    push @desc, {
	name => $project->{project_name}};
#       description => $project->{description}}
###Add description when the schema is changed
}
my $flashvars;
for (my $i=0;$i<10;$i++) {
    my $num=sprintf("%02d",$i);
    if ($desc[$i]) {
	my $PTtag='PTM'.$num;
	my $PTval=$desc[i]->{name};
	my $PDtag='PDM'.$num;
	my $PDval=$desc[i]->{description};
	my $PUtag='PUM'.$num;
	my $PUval='project.pl&name='.$PTval;
	if (!$flashvars) {
	    $flashvars=$PTtag."=".$PTval."&".$PDtag."=".$PDval."&".$PUtag."=".$PUval;
	} else {
	    $flashvars.="&".$PTtag."=".$PTval."&".$PDtag."=".$PDval."&".$PUtag."=".$PUval;
	}
    } else {
	my $PTtag='PTM'.$num;
	my $PTval='For Lease';
	my $PDtag='PDM'.$num;
	my $PDval='This space is currently unoccupied. Open your own store in this great location. Rent is free.';
	my $PUtag='PUM'.$num;
	my $PUval='register.pl';
	if (!$flashvars) {
	    $flashvars=$PTtag."=".$PTval."&".$PDtag."=".$PDval."&".$PUtag."=".$PUval;
	} else {
	    $flashvars.="&".$PTtag."=".$PTval."&".$PDtag."=".$PDval."&".$PUtag."=".$PUval;
	}
    }
}
 

                 
print<<page;
<object classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000" codebase="http://fpdownload.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=7,0,0,0" width="600" height="700" id="TF_Mall" align="middle">
<param name="allowScriptAccess" value="sameDomain" />
page

    print "<PARAM NAME=FlashVars VALUE=\"".$flashvars."\">";

print<<page2;
<param name="movie" value="http://www.pazar.info/images/TF_Mall.swf" /><param name="quality" value="high" /><param name="bgcolor" value="#ffffff" />
page2

    print "<embed src=\"http://www.pazar.info/images/TF_Mall.swf\" FlashVars=\"".$flashvars."\" quality=\"high\" bgcolor=\"#ffffff\" width=\"600\" height=\"700\" name=\"TF_Mall\" align=\"middle\" allowScriptAccess=\"sameDomain\" type=\"application/x-shockwave-flash\" pluginspage=\"http://www.macromedia.com/go/getflashplayer\"/></object>";


# print out the html tail template
my $template_tail = HTML::Template->new(filename => 'tail.tmpl');
print $template_tail->output;
