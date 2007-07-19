#!/usr/bin/perl


use pazar;
#use Bio::Matrix::PSM::SiteMatrix;
use TFBS::Matrix::PFM;

use HTML::Template;

use CGI qw(:standard);
use CGI::Carp qw(fatalsToBrowser);
#use CGI::Debug( report => 'everything', on => 'anything' );

my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};
my $pazarhtdocspath = $ENV{PAZARHTDOCSPATH};

require "$pazarcgipath/getsession.pl";

my $get = new CGI;
########### start of HTML table
    print $get->header("text/html");
my %param = %{$get->Vars};

if ($param{mode} eq 'list') {

# open the html header template
    my $template = HTML::Template->new(filename => 'header.tmpl');

# fill in template parameters
    $template->param(TITLE => 'PAZAR TF Profiles');
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
    #print "Content-Type: text/html\n\n",
print $template->output;


    my $dbh= pazar->new( 
		     -host          =>    $ENV{PAZAR_host},
		     -user          =>    $ENV{PAZAR_pubuser},
		     -pass          =>    $ENV{PAZAR_pubpass},
		     -dbname        =>    $ENV{PAZAR_name},
		     -drv           =>    $ENV{PAZAR_drv},
		     -globalsearch  =>    'yes'); #To

    my @projects=$dbh->public_projects;

    if($loggedin eq 'true') {
	foreach my $proj (@projids) {
	    unless (grep(/^$proj$/,@projects)) {
		push @projects, $proj;
	    }
	}
    }

########### start of HTML table

    print "<table width='600' bordercolor='white' bgcolor='white' border=1 cellspacing=0>\n";

print<<COLNAMES;
<tr>
    <td width="" align="center" valign="center" bgcolor="#e65656"><span class="title4">Project</span></td>
    <td align="center" width="" valign="center" bgcolor="#e65656"><span class="title4">Database::ID</span></td>
    <td align="center"  valign="center" bgcolor="#e65656"><span class="title4">Name</span>
    </td> 
    <td align="center"  valign="center" bgcolor="#e65656"><span class="title4">Description</span>
    </td> 
    <td align="center"  valign="center" bgcolor="#e65656"><span class="title4">Species</span>
    </td> 
    <td align="center" valign="center"  bgcolor="#e65656"><span class="title4">Class,Family</span>
    </td> 
    <td align="center" valign="center"  bgcolor="#e65656"><span class="title4">Logo</span>
    </td> 
    <td align="center"  valign="center" bgcolor="#e65656"><span class="title4"></span>
    </td> 
    </tr>
COLNAMES

    my @profiles;
    foreach my $projid (@projects) {
# get matrix
	my $matrixs = &select($dbh, "SELECT * FROM matrix WHERE project_id='$projid'"); 

	if ($matrixs) {
	    while (my ($mid,$name,$db,$acc,$a,$c,$g,$t,$desc)=$matrixs->fetchrow_array) {

# 		my @a=&uncompress($a);
# 		my @c=&uncompress($c);
# 		my @g=&uncompress($g);
# 		my @t=&uncompress($t);

# 		my $matrixref = join (' ',@a)."\n".join (' ',@c)."\n".join (' ',@g)."\n".join (' ',@t);

		my $matrixref = $a."\n".$c."\n".$g."\n".$t;
		my $pfm = TFBS::Matrix::PFM->new(-matrix => $matrixref);
#print a human readable format of the matrix
		my $prettystring = $pfm->prettyprint();
		my @matrixlines = split /\n/, $prettystring;
		$prettystring = join "<BR>\n", @matrixlines;
		$prettystring =~ s/ /\&nbsp\;/g;

#alter file name by adding random number with current time as seed
		srand(time() ^ ($$ + ($$ << 15) ) );
		my $randnum = substr(rand() * 100,3);
		my $logo = $acc.$randnum;
		my $gd_image = $pfm->draw_logo(-file=>$pazarhtdocspath.'/tmp/precomputed/'.$logo.'.png', -xsize=>130);
		my $gd_image2 = $pfm->draw_logo(-file=>$pazarhtdocspath.'/tmp/precomputed/'.$logo.'_400.png', -xsize=>400);

		my $proj_name=$dbh->get_project_name('matrix',$mid);

		my $db_source = &select($dbh, "SELECT * FROM db_source WHERE db_source_id='$db'")->fetchrow_hashref;
		my $dbname=$db_source->{db_name};

		my $matrix_info = &select($dbh, "SELECT * FROM matrix_info WHERE matrix_id='$mid'")->fetchrow_hashref;
		my ($species, $pmid, $exptype);
		if ($matrix_info) {
		    $species=$matrix_info->{species};
		    $pmid=$matrix_info->{pubmed};
		    $exptype=$matrix_info->{exptype};
		}
		my @tfs=$dbh->get_factor_by_matrix_id($mid);
		if (@tfs) {
		    foreach my $tf (@tfs) {
			my $classes;
			my $tfs;
			if ($tf->{tfcomplex}) {
			    my $tfh=$dbh->create_tf();
			    my $complex=$tfh->get_tfcomplex_by_id($tf->{tfcomplex},'notargets');
			    $subnb=0;
			    while (my $subunit=$complex->next_subunit) {
				my $tid = $subunit->get_transcript_accession($dbh);
				my $cl = $subunit->get_class; 
				if ($subunit->get_fam && $subunit->get_fam ne '') {
				    $cl.=','.$subunit->get_fam;
				}
				if ($subnb==0) {
				    $classes=$cl;
				    $tfs=$tid;
				    $subnb++;
				} else {
				    $classes.='<br>'.$cl;
				    $tfs.='<br>'.$tid;
				}
			    }
			}
			my @an=$dbh->get_data_by_primary_key('analysis',$tf->{aid});
			my @met=$dbh->get_data_by_primary_key('method',$an[3]);
			$exptype=$met[0];
			my @ref=$dbh->get_data_by_primary_key('ref',$an[6]);
			$pmid=$ref[0];
			push @profiles, { project => $proj_name,
					  dbid => $dbname."::".$acc,
					  name => $name,
					  desc => $desc,
					  species => $species,
					  class => $classes,
					  pmid => $pmid,
					  method => $exptype,
					  transcript => $tfs,
					  pfm => $prettystring,
					  pazar_id => $mid,
                                          logo => $logo};
		    }
		}
	    }
	}
    }

    my $bg_color = 0;
    my %colors = (0 => "#fffff0",
		  1 => "#9ad3e2"
		  );

    my @sorted;
    if ($param{BROWSE} eq 'Project') {
	@sorted=sort {$a->{project} cmp $b->{project} or $a->{name} cmp $b->{name}} @profiles;
    } elsif ($param{BROWSE} eq 'Name') {
	@sorted=sort {$a->{name} cmp $b->{name} or $a->{project} cmp $b->{project}} @profiles;
    } elsif ($param{BROWSE} eq 'Species') {
	@sorted=sort {$a->{species} cmp $b->{species} or $a->{name} cmp $b->{name} or $a->{project} cmp $b->{project}} @profiles;
    } elsif ($param{BROWSE} eq 'Class') {
	@sorted=sort {$a->{class} cmp $b->{class} or $a->{name} cmp $b->{name} or $a->{project} cmp $b->{project}} @profiles;
    }

    for (my $i=0;$i<@sorted;$i++) {
	my $logo = $sorted[$i]->{logo}.".png";

print<<ROWS;
<tr>
    <td width="" align="center" valign="center" bgcolor="$colors{$bg_color}">$sorted[$i]->{project}</td>
    <td align="center" width="" valign="center" bgcolor="$colors{$bg_color}">$sorted[$i]->{dbid}</td>
    <td align="center" width="" valign="center" bgcolor="$colors{$bg_color}">$sorted[$i]->{name}</td>
    <td align="center" width="" valign="center" bgcolor="$colors{$bg_color}">$sorted[$i]->{desc}</td>
    <td align="center" width="" valign="center" bgcolor="$colors{$bg_color}">$sorted[$i]->{species}</td>
    <td align="center" width="" valign="center" bgcolor="$colors{$bg_color}">$sorted[$i]->{class}</td>
    <td align="center" width="" valign="center" bgcolor="$colors{$bg_color}"><img src="$pazar_html/tmp/precomputed/$logo"></td>
    <td align="center" width="" valign="center" bgcolor="$colors{$bg_color}"><form name='$sorted[$i]->{logo}' method='post' action ="$pazar_cgi/export_profile.cgi" enctype="multipart/form-data" target='Detail_win'><input type="hidden" name="mode" value="details"><input type="hidden" name="project" value="$sorted[$i]->{project}"><input type="hidden" name="dbid" value="$sorted[$i]->{dbid}"><input type="hidden" name="name" value="$sorted[$i]->{name}"><input type="hidden" name="class" value="$sorted[$i]->{class}"><input type="hidden" name="species" value="$sorted[$i]->{species}"><input type="hidden" name="pmid" value="$sorted[$i]->{pmid}"><input type="hidden" name="method" value="$sorted[$i]->{method}"><input type="hidden" name="transcript" value="$sorted[$i]->{transcript}"><input type="hidden" name="pazar_id" value="$sorted[$i]->{pazar_id}"><input type="hidden" name="pfm" value="$sorted[$i]->{pfm}"><input type="hidden" name="logo" value="$sorted[$i]->{logo}"><input value="More" name="submit" type="submit" onClick="window.open('about:blank','Detail_win', 'resizable=1,scrollbars=yes, menubar=no, toolbar=no directories=no, height=800, width=450')"></form></td>
    </tr>
ROWS

$bg_color=1-$bg_color;
    }

###  print out the html tail template
  my $template_tail = HTML::Template->new(filename => "$pazarcgipath/tail.tmpl");
  print $template_tail->output;

} elsif ($param{mode} eq 'details') {

    my $logo = $param{logo}."_400.png";
    my $prettystring = $param{pfm};


print<<DETAILS;
<head><title>PAZAR - TF Profiles</title></head>
<body><table width='400' bordercolor='white' bgcolor='white' border=0 cellspacing=0>
<tr><td width="400" align="center" valign="center"><img src="$pazar_html/tmp/precomputed/$logo"></td></tr>
<tr><td width="400" align="center" valign="center"><span style="font-family: monospace;">$prettystring<br><br></span></td></tr>
<tr><td width="400" bgcolor="#e65656" align="center" valign="center"><span class="title4">Matrix Info</span></td></tr>
<tr><td><table width="400" bordercolor='white' bgcolor='white' border=1 cellspacing=0 cellpadding=2>
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
            <td bgcolor="#fffff0" align="left" valign="center">$param{pmid}</td>
            <td bgcolor="#9ad3e2" align="left" valign="center"><b>Experiment</b></td>
            <td bgcolor="#fffff0" align="left" valign="center">$param{method}</td>
        </tr>
DETAILS

    if ($param{desc} && $param{desc} ne '') {
	
print<<DESC;
    <tr><td bgcolor="#9ad3e2" align="left" valign="center"><b>Description</b></td>
            <td bgcolor="#fffff0" align="left" valign="center" colspan=3>$param{desc}</td>
        </tr>
DESC
    }

print<<TF; 
</table><br></td></tr>
<tr><td width="400" bgcolor="#e65656" align="center" valign="center"><span class="title4">Transcription Factor Info</span></td></tr>
<tr><td><table width="400" bordercolor='white' bgcolor='white' border=1 cellspacing=0 cellpadding=2>
        <tr><td bgcolor="#9ad3e2" align="left" valign="center"><b>Accession Number</b></td>
            <td bgcolor="#fffff0" align="left" valign="center">$param{transcript}</td>
            <td bgcolor="#9ad3e2" align="left" valign="center"><b>Class,Family</b></td>
            <td bgcolor="#fffff0" align="left" valign="center">$param{class}</td>
        </tr>
</table><br></td></tr>
TF
    my $dbh= pazar->new( 
		     -host          =>    $ENV{PAZAR_host},
		     -user          =>    $ENV{PAZAR_pubuser},
		     -pass          =>    $ENV{PAZAR_pubpass},
		     -dbname        =>    $ENV{PAZAR_name},
		     -drv           =>    $ENV{PAZAR_drv},
		     -globalsearch  =>    'yes'); #To

    my $seq_ids= &select($dbh, "SELECT * FROM reg_seq_set WHERE matrix_id='$param{pazar_id}'");
    if ($seq_ids) {

print<<SITES1; 
<tr><td width="400" bgcolor="#e65656" align="center" valign="center"><span class="title4">Individual Binding Sites</span></td></tr>
<tr><td><table width="400" bordercolor='white' bgcolor='white' border=1 cellspacing=0 cellpadding=2>
SITES1

        while (my $seq_id=$seq_ids->fetchrow_hashref) {
	    my $construct_id = $seq_id->{construct_id};
	    my $reg_seq_id = $seq_id->{reg_seq_id};
	    if ($construct_id && $construct_id ne '0' && $construct_id ne 'NULL') {
		my @dat=$dbh->get_data_by_primary_key('construct',$construct_id);
print<<SITES2;
        <tr><td bgcolor="#9ad3e2" align="left" valign="center"><b>Artificial Sequence</b></td>
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

###  print out the html tail template
my $template_tail = HTML::Template->new(filename => "$pazarcgipath/tail.tmpl");
print $template_tail->output;


sub select {

    my ($dbh, $sql) = @_;
    my $sth=$dbh->prepare($sql);
    $sth->execute or die "$dbh->errstr\n";
    return $sth;
}

sub uncompress {
    my $a=shift;
    my @ca = split (//, $a);
    my @a;
    foreach (@ca) {
	my $num=ord($_)/255;
	my $num2f=sprintf("%.2f",$num);
	push @a, $num2f;
    }
    return @a;
}


