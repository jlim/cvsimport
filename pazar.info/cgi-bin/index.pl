#!/usr/bin/perl

use HTML::Template;

use pazar;

use constant DB_DRV  => $ENV{PAZAR_drv};
use constant DB_NAME => $ENV{PAZAR_name};
use constant DB_USER => $ENV{PAZAR_pubuser};
use constant DB_PASS => $ENV{PAZAR_pubpass};
use constant DB_HOST => $ENV{PAZAR_host};

my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};

require "$pazarcgipath/getsession.pl";

# open the html header template
my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");

# fill in template parameters
$template->param(TITLE => 'PAZAR Mall');
$template->param(PAZAR_HTML => $pazar_html);
$template->param(PAZAR_CGI => $pazar_cgi);
$template->param(JAVASCRIPT_FUNCTION => q{
function showHide(inputID) {
	theObj = document.getElementById(inputID)
	theDisp = theObj.style.display == 'none' ? 'block' : 'none'
	theObj.style.display = theDisp
}
});

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

#connect to the database
my $dbh = pazar->new( 
		      -host          =>    DB_HOST,
		      -user          =>    DB_USER,
		      -pass          =>    DB_PASS,
		      -dbname        =>    DB_NAME,
		      -drv           =>    DB_DRV,
                      -globalsearch  =>    'yes');

my $projects=&select($dbh, "SELECT * FROM project WHERE status='open' OR status='published' ORDER BY project_id");
my @desc;
while (my $project=$projects->fetchrow_hashref) {
    my $flashdesc=$project->{description};
    $flashdesc=~s/<(.*?)>//gi;
    $flashdesc=~s/[!@\$\^\*\(\)\+\[\]\\\'=&\{\}\|\"\?]/ /g;
    my $truncflashdesc=substr($flashdesc,0,300);
    push @desc, {
	name => $project->{project_name},
        description => $truncflashdesc};
}

if ($loggedin eq 'true') {
    foreach my $proj (@projids) {
	my $restricted=&select($dbh, "SELECT * FROM project WHERE project_id='$proj' and upper(status)='RESTRICTED'");
	while (my $restr=$restricted->fetchrow_hashref) {
	    my $flashdesc=$restr->{description};
	    $flashdesc=~s/<(.*?)>//gi;
	    $flashdesc=~s/[!@\$\^\*\(\)\+\[\]\\\'=&\{\}\|\"\?]/ /g;
	    my $truncflashdesc=substr($flashdesc,0,300);
	    push @desc, {
		name => $restr->{project_name},
                description => $truncflashdesc};
	}
    }
}

undef(my $flashvars);
$flashvars='cgiPath='.$pazar_cgi;
my $i=0;
while ($i<10) {
    my $num=sprintf("%02d",($i+1));
    if ($desc[$i]) {
	my $PTtag='PTM'.$num;
	my $PTval=$desc[$i]->{name};
	my $PDtag='PDM'.$num;
	my $PDval=$desc[$i]->{description}||'No description available';
	my $PUtag='PUM'.$num;
	my $PUval='project.pl';
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
    $i++;
}
my $j=0;
while (10<=$i&&$i<20) {
    my $num=sprintf("%02d",($j+1));
    if ($desc[$i]) {
	my $PTtag='PT1'.$num;
	my $PTval=$desc[$i]->{name};
	my $PDtag='PD1'.$num;
	my $PDval=$desc[$i]->{description}||'No description available';
	my $PUtag='PU1'.$num;
	my $PUval='project.pl';
	if (!$flashvars) {
	    $flashvars=$PTtag."=".$PTval."&".$PDtag."=".$PDval."&".$PUtag."=".$PUval;
	} else {
	    $flashvars.="&".$PTtag."=".$PTval."&".$PDtag."=".$PDval."&".$PUtag."=".$PUval;
	}
    } else {
	my $PTtag='PT1'.$num;
	my $PTval='For Lease';
	my $PDtag='PD1'.$num;
	my $PDval='This space is currently unoccupied. Open your own store in this great location. Rent is free.';
	my $PUtag='PU1'.$num;
	my $PUval='register.pl';
	if (!$flashvars) {
	    $flashvars=$PTtag."=".$PTval."&".$PDtag."=".$PDval."&".$PUtag."=".$PUval;
	} else {
	    $flashvars.="&".$PTtag."=".$PTval."&".$PDtag."=".$PDval."&".$PUtag."=".$PUval;
	}
    }
    $i++;
    $j++;
}
$j=0;
while (20<=$i&&$i<30) {
    my $num=sprintf("%02d",($j+1));
    if ($desc[$i]) {
	my $PTtag='PT2'.$num;
	my $PTval=$desc[$i]->{name};
	my $PDtag='PD2'.$num;
	my $PDval=$desc[$i]->{description}||'No description available';
	my $PUtag='PU2'.$num;
	my $PUval='project.pl';
	if (!$flashvars) {
	    $flashvars=$PTtag."=".$PTval."&".$PDtag."=".$PDval."&".$PUtag."=".$PUval;
	} else {
	    $flashvars.="&".$PTtag."=".$PTval."&".$PDtag."=".$PDval."&".$PUtag."=".$PUval;
	}
    } else {
	my $PTtag='PT2'.$num;
	my $PTval='For Lease';
	my $PDtag='PD2'.$num;
	my $PDval='This space is currently unoccupied. Open your own store in this great location. Rent is free.';
	my $PUtag='PU2'.$num;
	my $PUval='register.pl';
	if (!$flashvars) {
	    $flashvars=$PTtag."=".$PTval."&".$PDtag."=".$PDval."&".$PUtag."=".$PUval;
	} else {
	    $flashvars.="&".$PTtag."=".$PTval."&".$PDtag."=".$PDval."&".$PUtag."=".$PUval;
	}
    }
    $i++;
    $j++;
}
$j=0;
while (30<=$i&&$i<40) {
    my $num=sprintf("%02d",($j+1));
    if ($desc[$i]) {
	my $PTtag='PT3'.$num;
	my $PTval=$desc[$i]->{name};
	my $PDtag='PD3'.$num;
	my $PDval=$desc[$i]->{description}||'No description available';
	my $PUtag='PU3'.$num;
	my $PUval='project.pl';
	if (!$flashvars) {
	    $flashvars=$PTtag."=".$PTval."&".$PDtag."=".$PDval."&".$PUtag."=".$PUval;
	} else {
	    $flashvars.="&".$PTtag."=".$PTval."&".$PDtag."=".$PDval."&".$PUtag."=".$PUval;
	}
    } else {
	my $PTtag='PT3'.$num;
	my $PTval='For Lease';
	my $PDtag='PD3'.$num;
	my $PDval='This space is currently unoccupied. Open your own store in this great location. Rent is free.';
	my $PUtag='PU3'.$num;
	my $PUval='register.pl';
	if (!$flashvars) {
	    $flashvars=$PTtag."=".$PTval."&".$PDtag."=".$PDval."&".$PUtag."=".$PUval;
	} else {
	    $flashvars.="&".$PTtag."=".$PTval."&".$PDtag."=".$PDval."&".$PUtag."=".$PUval;
	}
    }
    $i++;
    $j++;
}
$j=0;
 while (40<=$i&&$i<50) {
    my $num=sprintf("%02d",($j+1));
    if ($desc[$i]) {
	my $PTtag='PT4'.$num;
	my $PTval=$desc[$i]->{name};
	my $PDtag='PD4'.$num;
	my $PDval=$desc[$i]->{description}||'No description available';
	my $PUtag='PU4'.$num;
	my $PUval='project.pl';
	if (!$flashvars) {
	    $flashvars=$PTtag."=".$PTval."&".$PDtag."=".$PDval."&".$PUtag."=".$PUval;
	} else {
	    $flashvars.="&".$PTtag."=".$PTval."&".$PDtag."=".$PDval."&".$PUtag."=".$PUval;
	}
    } else {
	my $PTtag='PT4'.$num;
	my $PTval='For Lease';
	my $PDtag='PD4'.$num;
	my $PDval='This space is currently unoccupied. Open your own store in this great location. Rent is free.';
	my $PUtag='PU4'.$num;
	my $PUval='register.pl';
	if (!$flashvars) {
	    $flashvars=$PTtag."=".$PTval."&".$PDtag."=".$PDval."&".$PUtag."=".$PUval;
	} else {
	    $flashvars.="&".$PTtag."=".$PTval."&".$PDtag."=".$PDval."&".$PUtag."=".$PUval;
	}
    }
    $i++;
    $j++;
}
$j=0;
while (50<=$i&&$i<60) {
    my $num=sprintf("%02d",($j+1));
    if ($desc[$i]) {
	my $PTtag='PT5'.$num;
	my $PTval=$desc[$i]->{name};
	my $PDtag='PD5'.$num;
	my $PDval=$desc[$i]->{description}||'No description available';
	my $PUtag='PU5'.$num;
	my $PUval='project.pl';
	if (!$flashvars) {
	    $flashvars=$PTtag."=".$PTval."&".$PDtag."=".$PDval."&".$PUtag."=".$PUval;
	} else {
	    $flashvars.="&".$PTtag."=".$PTval."&".$PDtag."=".$PDval."&".$PUtag."=".$PUval;
	}
    } else {
	my $PTtag='PT5'.$num;
	my $PTval='For Lease';
	my $PDtag='PD5'.$num;
	my $PDval='This space is currently unoccupied. Open your own store in this great location. Rent is free.';
	my $PUtag='PU5'.$num;
	my $PUval='register.pl';
	if (!$flashvars) {
	    $flashvars=$PTtag."=".$PTval."&".$PDtag."=".$PDval."&".$PUtag."=".$PUval;
	} else {
	    $flashvars.="&".$PTtag."=".$PTval."&".$PDtag."=".$PDval."&".$PUtag."=".$PUval;
	}
    }
    $i++;
    $j++;
}
                 
print<<page;
<table border="0" cellpadding="0" cellspacing="0" width="550">
<tbody><tr><td style="text-align:justify"><b>WELCOME TO PAZAR MALL!</b>&nbsp&nbsp&nbsp<a href="#" onclick = "showHide('details');"><small>Learn More</small></a>&nbsp;&nbsp;<a target="publication" href="$pazar_cgi/overview.pl#publications"><small>Publications</small></a><br>
<div id="details" style='display:none'>
PAZAR is your one stop shopping experience for transcription factors and regulatory sequence annotations. PAZAR can be searched by <a href="$pazar_cgi/gene_search.cgi">Gene</a>, <a href="$pazar_cgi/tf_search.cgi">Transcription Factor</a> or <a href="$pazar_cgi/profilesearch.pl">Profile</a> by clicking on one of the department stores below.<br>
Each project in PAZAR is a boutique in the mall. You can limit your search to a specific project by clicking on the corresponding boutique on the mall map.<br>
If you own restricted projects, log in and they will appear in the mall map. If you just created a project and it does not appear on the mall map, please log out and log in again.<br><br>
<a href="$pazar_html/tutorials/Overview.htm" target='tutwin' onClick="window.open('about:blank','tutwin');">Mall Overview and Introduction Tutorial</a>  (2 min)</td></tr></tbody></table>
<object classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000" codebase="http://fpdownload.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=7,0,0,0" width="600" height="700" id="TF_Mall" align="middle">
<param name="allowScriptAccess" value="sameDomain" />
page

    print "<PARAM NAME=FlashVars VALUE=\"".$flashvars."\">";

print<<page2;
<param name="movie" value="$pazar_html/images/TF_Mall.swf" /><param name="quality" value="high" /><param name="bgcolor" value="#ffffff" />
page2

    print "<embed src=\"$pazar_html/images/TF_Mall.swf\" FlashVars=\"".$flashvars."\" quality=\"high\" bgcolor=\"#ffffff\" width=\"600\" height=\"700\" name=\"TF_Mall\" align=\"middle\" allowScriptAccess=\"sameDomain\" type=\"application/x-shockwave-flash\" pluginspage=\"http://www.macromedia.com/go/getflashplayer\"/></object>";


# print out the html tail template
my $template_tail = HTML::Template->new(filename => "$pazarcgipath/tail.tmpl");
print $template_tail->output;

sub select {

    my ($dbh, $sql) = @_;
    my $sth=$dbh->prepare($sql);
    $sth->execute or die "$dbh->errstr\n";
    return $sth;
}
