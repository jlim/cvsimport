#!/usr/bin/perl
use pazar;
use HTML::Template;
use CGI qw(:standard);
use TFBS::Matrix::PFM;
use CGI::Carp qw(fatalsToBrowser);

# use CGI::Debug( report => 'everything', on => 'anything' );

my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};
my $pazarhtdocspath = $ENV{PAZARHTDOCSPATH};
our $searchtab = $param{"searchtab"} || "profiles";

require "$pazarcgipath/getsession.pl";
require "$pazarcgipath/searchbox.pl";

my $get = new CGI;
my %param = %{$get->Vars};
print $get->header("text/html");

if ($param{mode} eq "list") {
	my $template = HTML::Template->new(filename => "header.tmpl");
	$template->param(TITLE => "Pre-computed TF profiles | PAZAR");
	$template->param(PAZAR_HTML => $pazar_html);
	$template->param(PAZAR_CGI => $pazar_cgi);
	if ($loggedin eq "true") {
		$template->param(LOGOUT => qq{<span class="b">You are signed in as $info{first} $info{last}.</span> 
		<a href="$pazar_cgi/logout.pl" class="b">Sign out</a>});
	} else {
		$template->param(LOGOUT => qq{<a href="$pazar_cgi/login.pl"><span class="b">Sign in</span></a>});
	}
	print $template->output;
	print $bowz;
	my $dbh = pazar->new( 
		-host         => $ENV{PAZAR_host},
		-user         => $ENV{PAZAR_pubuser},
		-pass         => $ENV{PAZAR_pubpass},
		-dbname       => $ENV{PAZAR_name},
		-drv          => $ENV{PAZAR_drv},
		-globalsearch => "yes");
	my @projects = $dbh->public_projects;
	if ($loggedin eq "true") {
		foreach my $proj (@projids) {
			unless (grep(/^$proj$/,@projects)) {
				push @projects, $proj;
			}
		}
	}
	print qq{
		<h2>Pre-computed TF profiles</h2>
		<table class="tblw sta" cellspacing="0" cellpadding="0">
			<tr style="background-color: #cccccc;">
				<td class="btc b w100">Project</td>
				<td class="btc b w100">Database ID</td>
				<td class="btc b w100">Name</td> 
				<td class="btc b">Description</td> 
				<td class="btc b w100">Species</td> 
				<td class="btc b w140">Logo</td> 
				<td class="btc b w80"></td> 
			</tr>};
	my @profiles;
	foreach my $projid (@projects) {
		my $matrixs = &select($dbh,qq{SELECT * FROM matrix WHERE project_id="$projid"}); 
		if ($matrixs) {
			while (my($mid,$name,$db,$acc,$a,$c,$g,$t,$desc) = $matrixs->fetchrow_array) {
				my $matrixref = $a."\n".$c."\n".$g."\n".$t;
				my $pfm = TFBS::Matrix::PFM->new(-matrix => $matrixref);
				my $prettystring = $pfm->prettyprint();
				my @matrixlines = split /\n/, $prettystring;
				$prettystring = join "<BR>\n", @matrixlines;
				$prettystring =~ s/ /\&nbsp\;/g;
				srand(time() ^ ($$ + ($$ << 15)));
				my $randnum = substr(rand()*100,3);
				my $logo = $acc.$randnum;
				my $gd_image = $pfm->draw_logo(-file=>$pazarhtdocspath.'/tmp/precomputed/'.$logo.'.png', -xsize=>130);
				my $gd_image2 = $pfm->draw_logo(-file=>$pazarhtdocspath.'/tmp/precomputed/'.$logo.'_400.png', -xsize=>400);
				my $proj_name= $ dbh->get_project_name('matrix',$mid);
				my $db_source = &select($dbh, "SELECT * FROM db_source WHERE db_source_id='$db'")->fetchrow_hashref;
				my $dbname = $db_source->{db_name};
				my $matrix_info = &select($dbh, "SELECT * FROM matrix_info WHERE matrix_id='$mid'")->fetchrow_hashref;
				my ($species,$pmid,$exptype);
				if ($matrix_info) {
					$species = $matrix_info->{species};
					$exptype = $matrix_info->{exptype};
					$pmid = $matrix_info->{pubmed};
				}
				push @profiles, { project => $proj_name,
					dbid => $dbname . " " . $acc,
					name => $name,
					desc => $desc,
					species => $species,
					pmid => $pmid,
					method => $exptype,
					pfm => $prettystring,
					pazar_id => $mid,
					logo => $logo};
			}
		}
	}
	my $bg_color = 0;
	my %colors = (
		0 => "#ffffff",
		1 => "#ffffff");
	my @sorted;
	if ($param{BROWSE} eq "Project") {
		@sorted = sort {$a->{project} cmp $b->{project} or $a->{name} cmp $b->{name}} @profiles;
	} elsif ($param{BROWSE} eq "Name") {
		@sorted = sort {$a->{name} cmp $b->{name} or $a->{project} cmp $b->{project}} @profiles;
	} elsif ($param{BROWSE} eq "Species") {
		@sorted = sort {$a->{species} cmp $b->{species} or $a->{name} cmp $b->{name} or $a->{project} cmp $b->{project}} @profiles;
	} elsif ($param{BROWSE} eq "Class") {
		@sorted = sort {$a->{class} cmp $b->{class} or $a->{name} cmp $b->{name} or $a->{project} cmp $b->{project}} @profiles;
	}
	for (my $i=0; $i<@sorted; $i++) {
		my $logo = $sorted[$i]->{logo}.".png";
		my $so_pro = $sorted[$i]->{project};
		my $so_did = $sorted[$i]->{dbid};
		my $so_nam = $sorted[$i]->{name};
		my $so_des = $sorted[$i]->{desc};
		my $so_der = $so_des;
		my $so_spc = ucfirst(lc($sorted[$i]->{species}));
		my $so_log = $sorted[$i]->{logo};
		my $so_pmd = $sorted[$i]->{pmid};
		my $so_met = $sorted[$i]->{method};
		my $so_pid = $sorted[$i]->{pazar_id};
		my $so_pfm = $sorted[$i]->{pfm};
		$so_des =~ s/JASPAR TF DESCRIPTION\: //g;
		$so_des =~ s/SWISSPROT:; //g;
		$so_des =~ s/:; //g;
		$so_des =~ s/:-; -//g;
		$so_spc = "(not provided)" if $so_spc eq "0";
		if ($so_des =~ /; /) {
			my ($db,$fa) = split(/; /,$so_des);
			if ($db) {
				my ($dn,$id) = split(/:/,$db);
				if ((($dn eq "SWISSPROT") or ($dn eq "SWISSPPROT")) or (($dn eq "") and $id)) {
					$so_des = qq{<div class="b">$fa</div><div>$dn <a href="http://www.uniprot.org/uniprot/$id">$id</a></div>};
				} elsif ($dn eq "EMBL") {
					$so_des = qq{<div class="b">$fa</div><div>$dn <a href="http://www.ebi.ac.uk/cgi-bin/expasyfetch?$id">$id</a></div>};
				} elsif ($dn eq "GENBANK") {
					$so_des = qq{<div class="b">$fa</div><div>$dn <a href="http://www.ebi.ac.uk/cgi-bin/dbfetch?db=emblcds&id=$id">$id</a></div>};
				} elsif ($dn eq "FLYBASE") {
					$id =~ s/FBGN/FBgn/g;
					$so_des = qq{<div class="b">$fa</div><div>$dn <a href="http://www.flybase.org/reports/$id.html">$id</a></div>};
				}
			}
		}
		print qq{
			<tr style="background-color: $colors{$bg_color};">
				<td class="btc">$so_pro</td>
				<td class="btc">$so_did</td>
				<td class="btc">$so_nam</td>
				<td class="btc">$so_des</td>
				<td class="btc">$so_spc</td>
				<td class="btc"><img src="$pazar_html/tmp/precomputed/$logo"></td>
				<td class="btc"><form name="$so_log" method="post" action="$pazar_cgi/export_profile.cgi" enctype="multipart/form-data" target="Detail_win"><input type="hidden" name="mode" value="details"><input type="hidden" name="project" value="$so_pro"><input type="hidden" name="desc" value="$so_der"><input type="hidden" name="dbid" value="$so_did"><input type="hidden" name="name" value="$so_nam"><input type="hidden" name="species" value="$so_spc"><input type="hidden" name="pmid" value="$so_pmd"><input type="hidden" name="method" value="$so_met"><input type="hidden" name="pazar_id" value="$so_pid"><input type="hidden" name="pfm" value="$so_pfm"><input type="hidden" name="logo" value="$so_log"><input value="more" name="submit" type="submit" onclick="window.open("about:blank","Detail_win", "resizable=1,scrollbars=yes,menubar=no,toolbar=no directories=no,height=800,width=500")"></form></td>
			</tr>};
		$bg_color = 1-$bg_color;
	}
	print "</table>";
	my $temptail = HTML::Template->new(filename => "$pazarcgipath/tail.tmpl");
	print $temptail->output;
} elsif ($param{mode} eq "details") {
	print qq{
	<html>
	<head>
		<title>Pre-computed TF profile | PAZAR</title>
	</head>
	<body>};
	my $dbh = pazar->new( 
		-host         => $ENV{PAZAR_host},
		-user         => $ENV{PAZAR_pubuser},
		-pass         => $ENV{PAZAR_pubpass},
		-dbname       => $ENV{PAZAR_name},
		-drv          => $ENV{PAZAR_drv},
		-globalsearch => "yes");
	my $logo = $param{logo} . "_400.png";
	my $prettystring = $param{pfm};
	my $method = $param{method};
	my $pmid = $param{pmid};
	my @tfs = $dbh->get_factor_by_matrix_id($param{pazar_id});
	my $classes = "-";
	my $tfs = "-";
	if (@tfs) {
		if (@tfs > 1) {
			print qq{<div class="emp">Warning: more than one TF is linked to this matrix. This page displays information on only one of them.</div>};
		}
		if ($tfs[0]->{tfcomplex}) {
			my $tfh = $dbh->create_tf();
			my $complex = $tfh->get_tfcomplex_by_id($tfs[0]->{tfcomplex},"notargets");
			$subnb = 0;
			while (my $subunit=$complex->next_subunit) {
				my $tid = $subunit->get_transcript_accession($dbh);
				my $cl = $subunit->get_class; 
				if ($subunit->get_fam and ($subunit->get_fam ne "")) {
					$cl .= "," . $subunit->get_fam;
				}
				if ($subnb == 0) {
					$classes = $cl;
					$tfs = $tid;
					$subnb++;
				} else {
					$classes .= "<br>" . $cl;
					$tfs .= "<br>" . $tid;
				}
			}
		}
		my @an = $dbh->get_data_by_primary_key("analysis",$tfs[0]->{aid});
		my @met = $dbh->get_data_by_primary_key("method",$an[3]);
		$method = $met[0] if ($met[0]);
		my @ref = $dbh->get_data_by_primary_key("ref",$an[6]);
		$pmid = $ref[0] if ($ref[0]);
	}
print<<DETAILS;
<head><title>PAZAR - TF Profiles</title></head>
<body><table width='400' bordercolor='white' bgcolor='white' border=0 cellspacing=0>
<tr><td width="400" class="mm"><img src="$pazar_html/tmp/precomputed/$logo"></td></tr>
<tr><td width="400" class="mm"><span style="font-family: monospace;">$prettystring<br><br></span></td></tr>
<tr><td width="400" bgcolor="#e65656" class="mm"><span class="title4">Matrix Info</span></td></tr>
<tr width='100%'><td width='100%'><table width='100%' bordercolor='white' bgcolor='white' border=1 cellspacing=0 cellpadding=2>
		<tr><td bgcolor="#9ad3e2" align="left" valign="center"><b>Project</b></td>
			<td bgcolor="#fffff0" align="left" valign="center">$param{project}</td>
			<td bgcolor="#9ad3e2" align="left" valign="center"><b>Database::ID</b></td>
			<td bgcolor="#fffff0" align="left" valign="center">$param{dbid}</td>
		</tr>
		<tr><td bgcolor="#9ad3e2" align="left" valign="center"><b>Name</b></td>
			<td bgcolor="#fffff0" align="left" valign="center">$param{name}</td>
			<td bgcolor="#9ad3e2" align="left" valign="center"><b>Species</b></td>
			<td bgcolor="#fffff0" align="left" valign="center">$param{species}</td>
		</tr>
	<tr><td bgcolor="#9ad3e2" align="left" valign="center"><b>PubmedID</b></td>
			<td bgcolor="#fffff0" align="left" valign="center">$pmid</td>
			<td bgcolor="#9ad3e2" align="left" valign="center"><b>Experiment</b></td>
			<td bgcolor="#fffff0" align="left" valign="center">$method</td>
		</tr>
DETAILS
	if ($param{desc} && $param{desc} ne '') {
	
print<<DESC;
	<tr><td bgcolor="#9ad3e2" align="left" valign="center"><b>Description</b></td>
			<td bgcolor="#fffff0" align="left" valign="center" colspan=3>$param{desc}</td>
		</tr>
DESC
	}
print "</table><br></td></tr>";
if ($tfs ne '-') {
print<<TF; 
<tr><td width="400" bgcolor="#e65656" class="mm"><span class="title4">Transcription Factor Info</span></td></tr>
<tr width='100%'><td width='100%'><table width='100%' bordercolor='white' bgcolor='white' border=1 cellspacing=0 cellpadding=2>
		<tr width='100%'><td bgcolor="#9ad3e2" align="left" valign="center"><b>Accession Number</b></td>
			<td bgcolor="#fffff0" align="left" valign="center">$tfs</td>
			<td bgcolor="#9ad3e2" align="left" valign="center"><b>Class,Family</b></td>
			<td bgcolor="#fffff0" align="left" valign="center">$classes</td>
		</tr>
</table><br></td></tr>
TF
}
	my $seq_ids= &select($dbh, "SELECT * FROM reg_seq_set WHERE matrix_id='$param{pazar_id}'");
	if ($seq_ids) {
print<<SITES1; 
<tr><td width="400" bgcolor="#e65656" class="mm"><span class="title4">Individual Binding Sites</span></td></tr>
<tr width='100%'><td width='100%'><table width='100%' bordercolor='white' bgcolor='white' border=1 cellspacing=0 cellpadding=2>
SITES1
		while (my $seq_id=$seq_ids->fetchrow_hashref) {
		my $construct_id = $seq_id->{construct_id};
		my $reg_seq_id = $seq_id->{reg_seq_id};
		if ($construct_id && $construct_id ne '0' && $construct_id ne 'NULL') {
		my @dat=$dbh->get_data_by_primary_key('construct',$construct_id);
print<<SITES2;
		<tr width='100%'><td bgcolor="#9ad3e2" align="left" valign="center"><b>Artificial Sequence</b></td>
			<td bgcolor="#fffff0" align="left" valign="center">$dat[2]</td>
		</tr>
SITES2
		}
		if ($reg_seq_id && $reg_seq_id ne '0' && $reg_seq_id ne 'NULL') {
		my @dat=$dbh->get_data_by_primary_key('reg_seq',$reg_seq_id);
print<<SITES3;
		<tr><td bgcolor="#9ad3e2" align="left" valign="center"><b>Genomic Sequence</b></td>
			<td bgcolor="#fffff0" align="left" valign="center">$dat[2]</td>
		</tr>
SITES3
		}
		}
	print "</table><br></td></tr>";
	}
print "</table></body></html>";
}
sub select {
	my ($dbh,$sql) = @_;
	my $sth = $dbh->prepare($sql);
	$sth->execute or die "$dbh->errstr\n";
	return $sth;
}
sub uncompress {
	my $a = shift;
	my @ca = split (//,$a);
	my @a;
	foreach (@ca) {
		my $num = ord($_)/255;
		my $num2f = sprintf("%.2f",$num);
		push @a, $num2f;
	}
	return @a;
}