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
my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");
$template->param(TITLE => "The PAZAR Mall | PAZAR");
$template->param(PAZAR_HTML => $pazar_html);
$template->param(PAZAR_CGI => $pazar_cgi);
$template->param(JAVASCRIPT_FUNCTION => qq{});

if ($loggedin eq "true") {
	$template->param(LOGOUT => qq{<span class="b">You are signed in as $info{first} $info{last}.</span> <a href="$pazar_cgi/logout.pl" class="b">Sign out</a>});
} else {
	$template->param(LOGOUT => qq{<a href="$pazar_cgi/login.pl"><span class="b">Sign in</span></a>});
}

print "Content-Type: text/html\n\n", $template->output;
my $dbh = pazar->new( 
	-host   => DB_HOST,
	-user   => DB_USER,
	-pass   => DB_PASS,
	-dbname => DB_NAME,
	-drv    => DB_DRV,
	-globalsearch => "yes");

my $projects = &select($dbh,qq{SELECT * FROM project WHERE status="open" OR status="published" ORDER BY project_id});
my @desc;

while (my $project = $projects->fetchrow_hashref) {
	my $flashdesc = $project->{description};
	$flashdesc =~ s/<(.*?)>//gi;
	$flashdesc =~ s/[!@\$\^\*\(\)\+\[\]\\\'=&\{\}\|\"\?]/ /g;
	my $truncflashdesc = substr($flashdesc,0,300);
	push @desc, {
		name => $project->{project_name},
		description => $truncflashdesc
	};
}

if ($loggedin eq "true") {
	foreach my $proj (@projids) {
		my $restricted = &select($dbh,qq{SELECT * FROM project WHERE project_id="$proj" and upper(status)="RESTRICTED"});
		while (my $restr = $restricted->fetchrow_hashref) {
			my $flashdesc = $restr->{description};
			$flashdesc =~ s/<(.*?)>//gi;
			$flashdesc =~ s/[!@\$\^\*\(\)\+\[\]\\\'=&\{\}\|\"\?]/ /g;
			my $truncflashdesc = substr($flashdesc,0,300);
			push @desc, {
				name => $restr->{project_name},
				description => $truncflashdesc
			};
		}
	}
}

undef(my $flashvars);
$flashvars = "cgiPath=" . $pazar_cgi;
my $i = 0;
while ($i<10) {
	my $num = sprintf("%02d",($i+1));
	if ($desc[$i]) {
		my $PTtag = "PTM" . $num;
		my $PTval = $desc[$i]->{name};
		my $PDtag = "PDM" . $num;
		my $PDval = $desc[$i]->{description} || "No description available";
		my $PUtag = "PUM" . $num;
		my $PUval = "project.pl";
		if (!$flashvars) {
			$flashvars = $PTtag . "=" . $PTval . "&" . $PDtag . "=" . $PDval. "&" . $PUtag. "=" . $PUval;
		} else {
			$flashvars .= "&" . $PTtag . "=" . $PTval . "&" . $PDtag . "=" . $PDval. "&" . $PUtag. "=" . $PUval;
		}
	} else {
		my $PTtag = "PTM" . $num;
		my $PTval = "For Lease";
		my $PDtag = "PDM" . $num;
		my $PDval = "This space is currently unoccupied. Open your own store in this great location. Rent is free.";
		my $PUtag = "PUM" . $num;
		my $PUval = "register.pl";
		if (!$flashvars) {
			$flashvars = $PTtag . "=" . $PTval . "&" . $PDtag . "=" . $PDval. "&" . $PUtag. "=" . $PUval;
		} else {
			$flashvars .= "&" . $PTtag . "=" . $PTval . "&" . $PDtag . "=" . $PDval. "&" . $PUtag. "=" . $PUval;
		}
	}
	$i++;
}
my $j=0;
while (10<=$i&&$i<20) {
	my $num = sprintf("%02d",($j+1));
	if ($desc[$i]) {
		my $PTtag = "PT1" . $num;
		my $PTval = $desc[$i]->{name};
		my $PDtag = "PD1" . $num;
		my $PDval = $desc[$i]->{description} || "No description available";
		my $PUtag = "PU1" . $num;
		my $PUval = "project.pl";
		if (!$flashvars) {
			$flashvars = $PTtag . "=" . $PTval . "&" . $PDtag . "=" . $PDval. "&" . $PUtag. "=" . $PUval;
		} else {
			$flashvars .= "&" . $PTtag . "=" . $PTval . "&" . $PDtag . "=" . $PDval. "&" . $PUtag. "=" . $PUval;
		}
	} else {
		my $PTtag = "PT1" . $num;
		my $PTval = "For Lease";
		my $PDtag = "PD1" . $num;
		my $PDval = "This space is currently unoccupied. Open your own store in this great location. Rent is free.";
		my $PUtag = "PU1" . $num;
		my $PUval = "register.pl";
		if (!$flashvars) {
			$flashvars = $PTtag . "=" . $PTval . "&" . $PDtag . "=" . $PDval. "&" . $PUtag. "=" . $PUval;
		} else {
			$flashvars .= "&" . $PTtag . "=" . $PTval . "&" . $PDtag . "=" . $PDval. "&" . $PUtag. "=" . $PUval;
		}
	}
	$i++;
	$j++;
}
$j=0;
while (20<=$i&&$i<30) {
	my $num = sprintf("%02d",($j+1));
	if ($desc[$i]) {
		my $PTtag = "PT2" . $num;
		my $PTval = $desc[$i]->{name};
		my $PDtag = "PD2" . $num;
		my $PDval = $desc[$i]->{description} || "No description available";
		my $PUtag = "PU2" . $num;
		my $PUval = "project.pl";
		if (!$flashvars) {
			$flashvars = $PTtag . "=" . $PTval . "&" . $PDtag . "=" . $PDval. "&" . $PUtag. "=" . $PUval;
		} else {
			$flashvars .= "&" . $PTtag . "=" . $PTval . "&" . $PDtag . "=" . $PDval. "&" . $PUtag. "=" . $PUval;
		}
	} else {
		my $PTtag = "PT2" . $num;
		my $PTval = "For Lease";
		my $PDtag = "PD2" . $num;
		my $PDval = "This space is currently unoccupied. Open your own store in this great location. Rent is free.";
		my $PUtag = "PU2" . $num;
		my $PUval = "register.pl";
		if (!$flashvars) {
			$flashvars = $PTtag . "=" . $PTval . "&" . $PDtag . "=" . $PDval. "&" . $PUtag. "=" . $PUval;
		} else {
			$flashvars .= "&" . $PTtag . "=" . $PTval . "&" . $PDtag . "=" . $PDval. "&" . $PUtag. "=" . $PUval;
		}
	}
	$i++;
	$j++;
}
$j=0;
while (30<=$i&&$i<40) {
	my $num = sprintf("%02d",($j+1));
	if ($desc[$i]) {
		my $PTtag = "PT3" . $num;
		my $PTval = $desc[$i]->{name};
		my $PDtag = "PD3" . $num;
		my $PDval = $desc[$i]->{description} || "No description available";
		my $PUtag = "PU3" . $num;
		my $PUval = "project.pl";
		if (!$flashvars) {
			$flashvars = $PTtag . "=" . $PTval . "&" . $PDtag . "=" . $PDval. "&" . $PUtag. "=" . $PUval;
		} else {
			$flashvars .= "&" . $PTtag . "=" . $PTval . "&" . $PDtag . "=" . $PDval. "&" . $PUtag. "=" . $PUval;
		}
	} else {
		my $PTtag = "PT3" . $num;
		my $PTval = "For Lease";
		my $PDtag = "PD3" . $num;
		my $PDval = "This space is currently unoccupied. Open your own store in this great location. Rent is free.";
		my $PUtag = "PU3" . $num;
		my $PUval = "register.pl";
		if (!$flashvars) {
			$flashvars = $PTtag . "=" . $PTval . "&" . $PDtag . "=" . $PDval. "&" . $PUtag. "=" . $PUval;
		} else {
			$flashvars .= "&" . $PTtag . "=" . $PTval . "&" . $PDtag . "=" . $PDval. "&" . $PUtag. "=" . $PUval;
		}
	}
	$i++;
	$j++;
}
$j=0;
 while (40<=$i&&$i<50) {
	my $num = sprintf("%02d",($j+1));
	if ($desc[$i]) {
		my $PTtag = "PT4" . $num;
		my $PTval = $desc[$i]->{name};
		my $PDtag = "PD4" . $num;
		my $PDval = $desc[$i]->{description} || "No description available";
		my $PUtag = "PU4" . $num;
		my $PUval = "project.pl";
		if (!$flashvars) {
			$flashvars = $PTtag . "=" . $PTval . "&" . $PDtag . "=" . $PDval. "&" . $PUtag. "=" . $PUval;
		} else {
			$flashvars .= "&" . $PTtag . "=" . $PTval . "&" . $PDtag . "=" . $PDval. "&" . $PUtag. "=" . $PUval;
		}
	} else {
		my $PTtag = "PT4" . $num;
		my $PTval = "For Lease";
		my $PDtag = "PD4" . $num;
		my $PDval = "This space is currently unoccupied. Open your own store in this great location. Rent is free.";
		my $PUtag = "PU4" . $num;
		my $PUval = "register.pl";
		if (!$flashvars) {
			$flashvars = $PTtag . "=" . $PTval . "&" . $PDtag . "=" . $PDval. "&" . $PUtag. "=" . $PUval;
		} else {
			$flashvars .= "&" . $PTtag . "=" . $PTval . "&" . $PDtag . "=" . $PDval. "&" . $PUtag. "=" . $PUval;
		}
	}
	$i++;
	$j++;
}
$j=0;
while (50<=$i&&$i<60) {
	my $num = sprintf("%02d",($j+1));
	if ($desc[$i]) {
		my $PTtag = "PT5" . $num;
		my $PTval = $desc[$i]->{name};
		my $PDtag = "PD5" . $num;
		my $PDval = $desc[$i]->{description} || "No description available";
		my $PUtag = "PU5" . $num;
		my $PUval = "project.pl";
		if (!$flashvars) {
			$flashvars = $PTtag . "=" . $PTval . "&" . $PDtag . "=" . $PDval. "&" . $PUtag. "=" . $PUval;
		} else {
			$flashvars .= "&" . $PTtag . "=" . $PTval . "&" . $PDtag . "=" . $PDval. "&" . $PUtag. "=" . $PUval;
		}
	} else {
		my $PTtag = "PT5" . $num;
		my $PTval = "For Lease";
		my $PDtag = "PD5" . $num;
		my $PDval = "This space is currently unoccupied. Open your own store in this great location. Rent is free.";
		my $PUtag = "PU5" . $num;
		my $PUval = "register.pl";
		if (!$flashvars) {
			$flashvars = $PTtag . "=" . $PTval . "&" . $PDtag . "=" . $PDval. "&" . $PUtag. "=" . $PUval;
		} else {
			$flashvars .= "&" . $PTtag . "=" . $PTval . "&" . $PDtag . "=" . $PDval. "&" . $PUtag. "=" . $PUval;
		}
	}
	$i++;
	$j++;
}
				 
print qq{
	<div class="p20to p10bo"><span class="welcometext">Welcome to the PAZAR Mall!</span></div>
	<div><span class="b">PAZAR is your one stop shopping experience for transcription factors and regulatory sequence annotations.</span> PAZAR can be searched by <a href="$pazar_cgi/gene_search.cgi" class="b">gene</a>, <a href="$pazar_cgi/tf_search.cgi" class="b">transcription factor</a> or <a href="$pazar_cgi/profilesearch.pl" class="b">profile</a> by clicking on one of the department stores below. Each project in PAZAR is a boutique in the mall. You can limit your search to a specific project by clicking on the corresponding boutique on the mall map. If you own restricted projects, log in and they will appear in the mall map. If you just created a project and it does not appear on the mall map, please log out and log in again.</div>
	<div class="p5to p10bo"><a target="publication" href="$pazar_cgi/overview.pl#publications" class="b">View our publications</a> &bull; <a href="$pazar_html/tutorials/Overview.htm" target='tutwin' onClick="window.open('about:blank','tutwin');" class="b">view the mall overview and introduction tutorial</a> (2 minutes)</div>
	<div class="p10 tm">
		<object 
			classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000" 
			codebase="http://fpdownload.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=7,0,0,0" 
			width="600" 
			height="700" 
			id="TF_Mall" 
			align="middle">
			<param name="allowScriptAccess" value="sameDomain" />
			<param name="FlashVars" value="$flashvars" />
			<param name="movie" value="$pazar_html/images/TF_Mall.swf" />
			<param name="quality" value="high" />
			<param name="bgcolor" value="#ffffff" />
			<embed src="$pazar_html/images/TF_Mall.swf" FlashVars="$flashvars" quality="high" bgcolor="#ffffff" width="600" height="700" name="TF_Mall" align="middle" allowScriptAccess="sameDomain" type="application/x-shockwave-flash" pluginspage="http://www.macromedia.com/go/getflashplayer"/>
		</object>
	</div>};

my $temptail = HTML::Template->new(filename => "$pazarcgipath/tail.tmpl");
print $temptail->output;

sub select {
	my ($dbh,$sql) = @_;
	my $sth = $dbh->prepare($sql);
	$sth->execute or die "$dbh->errstr\n";
	return $sth;
}