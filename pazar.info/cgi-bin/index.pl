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
$template->param(TITLE => 'PAZAR Mall');

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

#connect to the database
my $dbh = pazar->new( 
		      -host          =>    DB_HOST,
		      -user          =>    DB_USER,
		      -pass          =>    DB_PASS,
		      -dbname        =>    DB_NAME,
		      -drv           =>    DB_DRV,
                      -globalsearch  =>    'yes');

my $projects=&select($dbh, "SELECT * FROM project WHERE upper(status)='OPEN' OR upper(status)='PUBLISHED'");
my @desc;
while (my $project=$projects->fetchrow_hashref) {
    push @desc, {
	name => $project->{project_name},
        description => $project->{description}};
}

if ($loggedin eq 'true') {
    foreach my $proj (@projids) {
	my $restricted=&select($dbh, "SELECT * FROM project WHERE project_id='$proj' and upper(status)='RESTRICTED'");
	while (my $restr=$restricted->fetchrow_hashref) {
	    push @desc, {
		name => $restr->{project_name},
                description => $project->{description}};
	}
    }
}

undef(my $flashvars);
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

sub select {

    my ($dbh, $sql) = @_;
    my $sth=$dbh->prepare($sql);
    $sth->execute or die "$dbh->errstr\n";
    return $sth;
}
