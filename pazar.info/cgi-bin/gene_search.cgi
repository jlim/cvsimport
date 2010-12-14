#!/usr/bin/perl
use pazar;
use pazar::gene;
use pazar::talk;
use pazar::reg_seq;
use HTML::Template;
use CGI qw(:standard);
use CGI::Carp qw(fatalsToBrowser);

my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};

my $get = new CGI;
my %param = %{ $get->Vars };
our $searchtab = $param{"searchtab"} || "genes";

require "$pazarcgipath/getsession.pl";
require "$pazarcgipath/searchbox.pl";

my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");
$template->param(TITLE               => "Search for target genes | PAZAR");
$template->param(PAZAR_HTML          => $pazar_html);
$template->param(PAZAR_CGI           => $pazar_cgi);
$template->param(JAVASCRIPT_FUNCTION => qq{ });

if ($loggedin eq "true") {
	$template->param(LOGOUT => qq{<span class="b">You are signed in as $info{first} $info{last}.</span> 
	<a href="$pazar_cgi/logout.pl" class="b">Sign out</a>});
} else {
	$template->param(LOGOUT => qq{<a href="$pazar_cgi/login.pl"><span class="b">Sign in</span></a>});
}

sub pnum {
	my $num = shift;
	my @aum = split(//,$num);
	my $fnu;
	while (@aum) {
		my $len = @aum;
		if ($len > 3) {
			$fnu = pop(@aum) . $fnu;
			$fnu = pop(@aum) . $fnu;
			$fnu = pop(@aum) . $fnu;
			$fnu = "," . $fnu;
		} else {
			while (@aum) {
				$fnu = pop(@aum) . $fnu;
			}
		}
	}
	return $fnu;
}

print qq{Content-Type: text/html\n\n}, $template->output;

my $dbh = pazar->new(
	-host         => $ENV{PAZAR_host},
	-user         => $ENV{PAZAR_pubuser},
	-pass         => $ENV{PAZAR_pubpass},
	-dbname       => $ENV{PAZAR_name},
	-drv          => $ENV{PAZAR_drv},
	-globalsearch => "yes"
);
my $ensdb = pazar::talk->new(
	DB   => "ensembl",
	USER => $ENV{ENS_USER},
	PASS => $ENV{ENS_PASS},
	HOST => $ENV{ENS_HOST},
	PORT => $ENV{ENS_PORT},
	ENSEMBL_DATABASES_HOST => $ENV{ENSEMBL_DATABASES_HOST},
	ENSEMBL_DATABASES_USER => $ENV{ENSEMBL_DATABASES_USER},
	ENSEMBL_DATABASES_PASS => $ENV{ENSEMBL_DATABASES_PASS},
	DRV  => "mysql"
);
my $gkdb = pazar::talk->new(
	DB   => "genekeydb",
	USER => $ENV{GKDB_USER},
	PASS => $ENV{GKDB_PASS},
	HOST => $ENV{GKDB_HOST},
	DRV  => "mysql"
);
my @pubprojects = $dbh->public_projects;

print $bowz;

my $bg_color = 0;
my %colors = (
	0 => "#fffff0",
	1 => "#BDE0DC"
);

my $accn = $param{geneID};
$accn =~ s/\s//g;
my $dbaccn = $param{ID_list} || "PAZAR_gene";
my $gene;

if ($accn) {
	if ($dbaccn eq "GeneName") {
		$gene = "GeneName";
	} elsif ($dbaccn eq "PAZAR_gene") {
		unless ($accn =~ /GS\d{7}/i || $accn =~ /MK\d{7}/i) {
			print qq{<div class="emp">The $dbaccn ID you provided ($accn) could not be found. 
			Please check that the provided ID ($accn) is a $dbaccn ID.</div>};
		} else {$gene = "PAZARid";}
	} elsif ($dbaccn eq "EnsEMBL_gene") {
		my @gene = $ensdb->ens_transcripts_by_gene($accn);
		$gene = $gene[0];
		unless ($gene) {
			print qq{<div class="emp">The $dbaccn ID you provided ($accn) could not be found. 
			Please check that the provided ID ($accn) is a $dbaccn ID.</div>};
		} else {
			$gene = $accn;
		}
	} elsif ($dbaccn eq "EnsEMBL_transcript") {
		my @gene = $ensdb->ens_transcr_to_gene($accn);
		$gene = $gene[0];
		unless ($gene) {
			print qq{<div class="emp">The $dbaccn ID you provided ($accn) could not be found. 
			Please check that the provided ID ($accn) is a $dbaccn ID. 
			You will get the best results if you provide us with an Ensembl Gene ID.</div>};
		}
	} elsif ($dbaccn eq "EntrezGene") {
		my $spcs = $gkdb->llid_to_org($accn);
		if (!$spcs) {
			print qq{<div class="emp">The $dbaccn ID you provided ($accn) could not be found. 
			Please check that the provided ID ($accn) is a $dbaccn ID. 
			You will get the best results if you provide us with an Ensembl Gene ID.</div>};
		}
		$ensdb->change_mart_organism($spcs);
		my @gene = $ensdb->llid_to_ens($accn);
		$gene = $gene[0];
		unless ($gene) {
			print qq{<div class="emp">The $dbaccn ID you provided ($accn) could not be found. 
			Please check that the provided ID ($accn) is a $dbaccn ID. 
			You will get the best results if you provide us with an Ensembl Gene ID.</div>};
		}
	} else {
		my $ens = convert_id($ensdb, $gkdb, $dbaccn, $accn);
		if (!$ens) {
			print qq{<div class="emp">The $dbaccn ID you provided ($accn) could not be found. 
			Please check that the provided ID ($accn) is a $dbaccn ID. 
			You will get the best results if you provide us with an Ensembl Gene ID.</div>};
		} else {
			$gene = $ens;
		}
	}

	my %projects;
	my @exc_proj;
	my $excluded = "none";

	if ($param{excl_proj}) {
		foreach my $val ($get->param("excl_proj")) {
			push @exc_proj, $val;
		}
		$excluded = join("__", @exc_proj);
	} elsif ($param{excluded}) {
		$excluded = $param{excluded};
		@exc_proj = split(/__/, $excluded);
	}

	foreach my $project (@pubprojects) {
		my $projname = $dbh->get_project_name_by_ID($project);
		unless (grep(/^$projname$/, @exc_proj)) {
			$projects{$project} = $projname;
		}
	}

	if ($loggedin eq "true") {
		foreach my $proj (@projids) {
			my $projname = $dbh->get_project_name_by_ID($proj);
			unless (grep(/^$projname$/, @exc_proj)) {
				$projects{$proj} = $projname;
			}
		}
	}

	my $accntype = "";
	if ($accn =~ /GS\d{7}/i) {
		$accntype = "gene";
	}
	if ($accn =~ /MK\d{7}/i) {
		$accntype = "marker";
	}
	my $pazarsth   = undef;
	my $geneobj    = undef;
	my @geneobjs   = ();
	my $markersth  = undef;
	my $markerobj  = undef;
	my @markerobjs = ();
	if ($gene eq "PAZARid") {
		my $PZid = $accn;
		$PZid =~ s/^\D+0*//;
		if ($accntype eq "gene") {
			$geneobj = pazar::gene::get_by_id($PZid, "gene", $dbh);
		} elsif ($accntype eq "marker") {
			$markerobj = pazar::gene::get_by_id($PZid, "marker", $dbh);
		}
	} elsif ($gene eq "GeneName") {
		$pazarsth = $dbh->prepare(qq{SELECT * FROM gene_source WHERE description LIKE "\%$accn\%"});
		$pazarsth->execute();
		$markersth = $dbh->prepare(qq{SELECT * FROM marker WHERE description LIFE "\%$accn\%"});
		$markersth->execute();
	} else {
		@geneobjs   = pazar::gene::get_by_accn($dbh, $gene, "gene");
		@markerobjs = pazar::gene::get_by_accn($dbh, $gene, "marker");
	}
	my @gene_info;
	if (defined $geneobj) {
		my $pid = $geneobj->project->id;
		if (grep(/^$pid$/, (keys %projects))) {
			my $geneaccn = $geneobj->db_accn;
			my $gena = $geneobj->description || "-";
			my $geneid = $geneobj->id;
			my $pgid = write_pazarid($geneobj->id, "GS");
			my $proj = $projects{$pid};
			my @ens_coords  = $ensdb->get_ens_chr($geneaccn);
			$ens_coords[5] =~ s/\[.*\]//g;
			$ens_coords[5] =~ s/\(.*\)//g;
			$ens_coords[5] =~ s/\.//g;
			my $gede = $ens_coords[5] || "-";
			my $spcs = $ensdb->current_org();
			$spcs = ucfirst($spcs) || "-";
			push @gene_info,
			  {
				desc     => $gena,
				GID      => $geneid,
				ID       => $pgid,
				proj     => $proj,
				ens_desc => $gede,
				species  => $spcs,
				accn     => $geneaccn
			  };
		}
	}
	# If we have a gene accession...
	foreach $geneobj (@geneobjs) {
		my $pid = $geneobj->project->id;
		if (grep(/^$pid$/, (keys %projects))) {
			my $geneaccn    = $geneobj->db_accn;
			my $gena    = $geneobj->description || "-";
			my $geneid      = $geneobj->id;
			my $pgid = write_pazarid($geneobj->id, "GS");
			my $proj        = $projects{$pid};
			my @ens_coords  = $ensdb->get_ens_chr($geneaccn);
			$ens_coords[5] =~ s/\[.*\]//g;
			$ens_coords[5] =~ s/\(.*\)//g;
			$ens_coords[5] =~ s/\.//g;
			my $gede = $ens_coords[5] || '-';
			my $spcs = $ensdb->current_org();
			$spcs = ucfirst($spcs) || '-';
			push @gene_info,
			  {
				desc     => $gena,
				GID      => $geneid,
				ID       => $pgid,
				proj     => $proj,
				ens_desc => $gede,
				species  => $spcs,
				accn     => $geneaccn
			  };
		}
	}
	# If we are searching for a gene name...
	if (defined $pazarsth) {
		while (my $res = $pazarsth->fetchrow_hashref) {
			my $pid = $res->{project_id};
			if (grep(/^$pid$/, (keys %projects))) {
				my $geneaccn    = $res->{db_accn};
				my $gena    = $res->{description} || '-';
				my $geneid      = $res->{gene_source_id};
				my $pgid = write_pazarid($res->{gene_source_id}, 'GS');
				my $proj        = $projects{$pid};
				my @ens_coords  = $ensdb->get_ens_chr($geneaccn);
				$ens_coords[5] =~ s/\[.*\]//g;
				$ens_coords[5] =~ s/\(.*\)//g;
				$ens_coords[5] =~ s/\.//g;
				my $gede = $ens_coords[5] || '-';
				my $spcs = $ensdb->current_org();
				$spcs = ucfirst($spcs) || '-';
				push @gene_info,
				  {
					desc     => $gena,
					GID      => $geneid,
					ID       => $pgid,
					proj     => $proj,
					ens_desc => $gede,
					species  => $spcs,
					accn     => $geneaccn
				  };
			}
		}
	}
	# Get the marker information.
	my @marker_info;
	# If marker id was entered...
	if (defined $markerobj) {
		my $pid = $markerobj->project->id;
		if (grep(/^$pid$/, (keys %projects))) {
			my $geneaccn   = $markerobj->db_accn;
			my $gena   = $markerobj->description || "-";
			my $geneid     = $markerobj->id;
			my $pgid   = write_pazarid($markerobj->id, "MK");
			my $proj       = $projects{$pid};
			my @ens_coords = $ensdb->get_ens_chr($geneaccn);
			$ens_coords[5] =~ s/\[.*\]//g;
			$ens_coords[5] =~ s/\(.*\)//g;
			$ens_coords[5] =~ s/\.//g;
			my $gede = $ens_coords[5] || "-";
			my $spcs = $ensdb->current_org();
			$spcs = ucfirst($spcs) || "-";
			push @marker_info,
			  {
				desc     => $gena,
				GID      => $geneid,
				ID       => $pgid,
				proj     => $proj,
				ens_desc => $gede,
				species  => $spcs,
				accn     => $geneaccn
			  };
		}
	}
	foreach $markerobj (@markerobjs) {
		my $pid = $markerobj->project->id;
		if (grep(/^$pid$/, (keys %projects))) {
			my $geneaccn   = $markerobj->db_accn;
			my $gena   = $markerobj->description || "-";
			my $geneid     = $markerobj->id;
			my $pgid   = write_pazarid($markerobj->id, "MK");
			my $proj       = $projects{$pid};
			my @ens_coords = $ensdb->get_ens_chr($geneaccn);
			$ens_coords[5] =~ s/\[.*\]//g;
			$ens_coords[5] =~ s/\(.*\)//g;
			$ens_coords[5] =~ s/\.//g;
			my $gede = $ens_coords[5] || "-";
			my $spcs = $ensdb->current_org();
			$spcs = ucfirst($spcs) || "-";
			push @marker_info,
			  {
				desc     => $gena,
				GID      => $geneid,
				ID       => $pgid,
				proj     => $proj,
				ens_desc => $gede,
				species  => $spcs,
				accn     => $geneaccn
			  };
		}
	}
	# Find markers associated with gene name...
	if (defined $markersth) {
		while (my $res = $markersth->fetchrow_hashref) {
			my $pid = $res->{project_id};
			if (grep(/^$pid$/, (keys %projects))) {
				my $geneaccn   = $res->{db_accn};
				my $gena   = $res->{description} || "-";
				my $geneid     = $res->{marker_id};
				my $pgid   = write_pazarid($res->{marker_id}, "MK");
				my $proj       = $projects{$pid};
				my @ens_coords = $ensdb->get_ens_chr($geneaccn);
				$ens_coords[5] =~ s/\[.*\]//g;
				$ens_coords[5] =~ s/\(.*\)//g;
				$ens_coords[5] =~ s/\.//g;
				my $gede = $ens_coords[5] || "-";
				my $spcs = $ensdb->current_org();
				$spcs = ucfirst($spcs) || "-";
				push @marker_info,
				  {
					desc     => $gena,
					GID      => $geneid,
					ID       => $pgid,
					proj     => $proj,
					ens_desc => $gede,
					species  => $spcs,
					accn     => $geneaccn
				  };
			}
		}
	}
	
	my $exprint = "";
	unless ($excluded eq "none") {
		$exprint = qq{<div class="p10bo"><span class="b">Projects excluded from the search:</span> $excluded</div>};
	}
	
	my %nicename = (
		"GeneName" => "user-defined gene name",
		"EnsEMBL_gene" => "Ensembl gene ID",
		"EnsEMBL_transcript" => "Ensembl transcript ID",
		"EntrezGene" => "Entrez Gene ID",
		"nm" => "Refseq ID",
		"swissprot" => "Swissprot ID",
		"PAZAR_gene" => "PAZAR gene ID",
		"PAZAR_seq" => "PAZAR sequence ID"
	);
	
	print qq{
			<a name="top"></a>
			<h2>Matching genes <span class="txt-grey">($nicename{$dbaccn} "$accn")</span></h2>
			$exprint};

	if (!@gene_info && !@marker_info) {
		print qq{
			<div class="emp">No annotation could be found for the gene $accn. 
			Please do not hesitate to create your own project and enter information about this gene or any other gene.</div>};
	}

	my $stco;
	# Start with summary of genes...
	foreach my $gene_data (@gene_info) {
		my $tfproj = $gene_data->{proj};
		my $gndesc = $gene_data->{ens_desc};
		my $gnenid = uc($gene_data->{accn});
		my $gnname = $gene_data->{desc};
		my $gnpzid = $gene_data->{ID};
		if (length($tfproj) > 14) {
			$tfproj = qq{<a href="$pazar_cgi/project.pl?project_name=$tfproj">} . substr($tfproj,0,12) . "..." . qq{</a>};
		} else {
			$tfproj = qq{<a href="$pazar_cgi/project.pl?project_name=$tfproj">$tfproj</a>};
		}
		if (length($gndesc) > 20) {
			$gndesc = qq{<div onclick="popup(this,'$gndesc','rt');" class="popup">} . substr($gndesc,0,18) . "..." . qq{</div>};
		}
		if (length($gnname) > 12) {
			$gnname = qq{<div onclick="popup(this,'$gnname','rt');" class="popup">} . substr($gnname,0,10) . "..." . qq{</div>};
		}
		
		my $ensspecies = $gene_data->{species};
		$ensspecies =~ s/ /_/g;
		
		$stco .= qq{
			<tr style="background-color: $colors{$bg_color};">
				<td class="btc">$gene_data->{species}</td>
				<td class="btc">$gnpzid 
					<a href="#$gnpzid"><img src="$pazar_html/images/magni.gif" alt="View Details" align="bottom" width="10"></a></td>
				<td class="btc">$gnname</td>
				<td class="btc"><a target="_blank" href="http://www.ensembl.org/$ensspecies/Gene/Idhistory?db=core;g=$gnenid">$gnenid</a></td>
				<td class="btc">$gndesc</td>
				<td class="btc">$tfproj</td>
			</tr>};
		$bg_color = 1 - $bg_color;
	}

	# Then, summary of markers, all in the same table but different colors...
	my $marks = 0;
	my $warns = qq{<span class="warning">*</span>};
	foreach my $marker_data (@marker_info) {
		$marks++;
		my $tra = $marker_data->{accn};
		my $tfproj = $marker_data->{proj};
		my $gndesc = $marker_data->{ens_desc};
		my $gnenid = uc($marker_data->{accn});
		my $gnname = $marker_data->{desc};
		my $gnpzid = $marker_data->{ID};
		if (length($tfproj) > 14) {
			$tfproj = qq{<a href="$pazar_cgi/project.pl?project_name=$tfproj">} . substr($tfproj,0,12) . "..." . qq{</a>};
		} else {
			$tfproj = qq{<a href="$pazar_cgi/project.pl?project_name=$tfproj">$tfproj</a>};
		}
		if (length($gndesc) > 20) {
			$gndesc = qq{<div onclick="popup(this,'$gndesc','rt');" class="popup">} . substr($gndesc,0,18) . "..." . qq{</div>};
		}
		if (length($gnname) > 12) {
			$gnname = qq{<div onclick="popup(this,'$gnname','rt');" class="popup">} . substr($gnname,0,10) . "..." . qq{</div>};
		}
		my $ensspecies = $marker_data->{species};
		$ensspecies =~ s/ /_/g;
		$stco .= qq{
			<tr style="background-color: $colors{$bg_color};">
				<td class="btc">$marker_data->{species}</td>
				<td class="btc">$warns} . qq{$gnpzid
					<a href="#$gnpzid"><img src="$pazar_html/images/magni.gif" alt="View details" align="bottom" width="10"></a></td>
				<td class="btc">$gnname</td>
				<td class="btc"><a target="_blank" href="http://www.ensembl.org/$ensspecies/Gene/Idhistory?db=core;g=$tra">$tra</a></td>
				<td class="btc">$gndesc</td>
				<td class="btc">$tfproj</td>
			</tr>};
		$bg_color = 1 - $bg_color;
	}

	if ($stco) {	
		print qq{
			<div class="p10bo"><table class="summarytable tblw">
				<tbody><tr>
					<td class="gdtc w16p">Species</td>
					<td class="gdtc w12p">PAZAR gene</td>
					<td class="gdtc w16p">Gene name</td>
					<td class="gdtc ">Ensembl gene</td>
					<td class="gdtc w20p">Description</td>
					<td class="gdtc w16p">PAZAR project</td>
				</tr>$stco</tbody></table></div>
			};
		unless ($marks == 0) {
			print qq{<div class="p5to p10bo small b">Genes marked with a red asterisk <span class="warning">*</span> 
			are used as markers located in the vicinity of the regulatory region. 
			They have not been shown to be regulated by the associated sequence.</div>};
		}
	}
	
	print qq{<h2>Details</h2>};

	my $rs_counter = 0;

	foreach my $gene_data (@gene_info) {

		$spcs = $gene_data->{species};
		my $ensp = $spcs;
		$ensp =~ s/ /_/g;
		$pgid = $gene_data->{ID};
		$gena = $gene_data->{desc};
		$gene = uc($gene_data->{accn});
		$gede = $gene_data->{ens_desc};
		$proj = $gene_data->{proj};
		my $edit_ugn;
		my $gena_editable = "false";

		if ($loggedin eq "true") {
			my $genetype = "gene_source";
			if ($gene_data->{ID} =~ /MK/) {
				$genetype = "marker";
			}
			# Determine the project that this reg seq belongs to...
			my $genasth = "";
			my $genegid = $gene_data->{GID};
			if ($genetype eq "gene_source") {
				$genasth = &select($dbh,qq{SELECT project_id FROM gene_source WHERE gene_source_id="$genegid"});
			} else {
				$genasth = &select($dbh,qq{SELECT project_id FROM marker WHERE marker_id="$genegid"});
			}
			my $gene_namerh = $genasth->fetchrow_hashref;
			my $gene_projid = $gene_namerh->{"project_id"};
			foreach my $proj (@projids) {
				if ($proj == $gene_projid) {
					$gena_editable = "true";
				}
			}
			if ($gena_editable eq "true") {
				$edit_ugn = qq{<div class="p5to"><span class="txt-ora b">Editing options:</span> <input type="button" name="genenameupdatebutton" value="Update gene name" onClick="javascript:window.open('updategenename.pl?mode=form&pid=$gene_projid&genetype=$genetype&amp;gid=$genegid');"></div>};
			}
		}
		$bg_color = 0;

		# Generate a unique id for Orca...

		my $sid     = $$ . time;
		my $spcurlf = $spcs;
		$spcurlf    =~ s/ /%20/g;
		my $otktgne = trim($gene);
		
		my $final_gene_name = $gena;
		if ($final_gene_name eq "-") {
			$final_gene_name = $pgid;
		}
		print qq{<a name="$pgid"></a>
			<h3><div class="float-r"><a href="#top" class="ns">back to top</a></div><div class="inline" id="ajaxgenename"><a href="$pazar_cgi/gene_search.cgi?geneID=$pgid&amp;excluded=$excluded&amp;ID_list=PAZAR_gene">$final_gene_name</a></div> in the <a href="$pazar_cgi/project.pl?project_name=$proj">$proj</a> project<div class="clear-l"></div></h3>
			<div class="p20lo p40bo">
				<div class="float-r w240 b p10 bg-lg"><img src="http://burgundy.cmmt.ubc.ca/ORCAtk/images/ORCA.png" height="30" align="left" class="m10ro"><a href="http://www.cisreg.ca/cgi-bin/ORCAtk/orca?rm=select_gene1&species=$spcurlf&ensembl_id=$otktgne">Scan for transcription factor binding sites with ORCAtk</a></div>
				<div class="p5bo">
					<div>Species: <span class="b">$spcs</span></div>
					<div>PAZAR gene ID: <a href="$pazar_cgi/gene_search.cgi?geneID=$pgid&amp;excluded=$excluded&amp;ID_list=PAZAR_gene" class="b">$pgid</a></div>
					<div>Ensembl gene ID: <a target="_blank" href="http://www.ensembl.org/$ensp/Gene/Idhistory?db=core;g=$gene" class="b">$gene</a></div>
					<div>Ensembl gene description: <span class="b">$gede</span></div>
					$edit_ugn
				</div>
				<table class="searchtable tblw">
					<tbody><tr>
						<td class="gdtc w80">Regseq ID</td>
						<td class="gdtc w110">Seq name</td>
						<td class="gdtc">Sequence</td>
						<td class="gdtc w200">Coordinates</td>
						<td class="gdtc w90">Links</td>
					</tr>};

		my @regseqs = pazar::reg_seq::get_reg_seqs_by_gene_id($dbh, $gene_data->{GID});
		if (!$regseqs[0]) {
			print qq{</tbody></table></div><div class="emp">There is currently no available annotation for this gene. Please do not hesitate to create your own project and enter information about this gene or any other gene.</div>};
			next;
		} else {
			my @ens_coords = $ensdb->get_ens_chr($gene);
			foreach my $regseq (@regseqs) {
				$rs_counter = $rs_counter + 1;
				my $rs_accnumb = $regseq->accession_number;
				my $rs_chromos = $regseq->chromosome;
				my $rs_chstart = &pnum($regseq->start);
				my $rs_chbreak = &pnum($regseq->end);
				my $rs_csstart = $regseq->start;
				my $rs_csbreak = $regseq->end;
				my $rs_chstrnd = $regseq->strand;
				my $rs_seqdbnm = $regseq->seq_dbname;
				my $rs_dbassem = $regseq->seq_dbassembly;
				my $rs_binomsp = $regseq->binomial_species;
				my $id = write_pazarid($rs_accnumb, "RS");
				my $seqname = $regseq->id || "-";
				my $seqseq = $regseq->seq;
				my $seqlen = length($seqseq);
				my $seqstr = chopstr($seqseq, 20);
				my $rs_set = substr($seqstr,0,10);
				$rs_chstrnd = "&ndash;" if $rs_chstrnd eq "-";
				if ($seqlen > 10) {
					$seqlen = &pnum($seqlen);
					$rs_set .= "... ($seqlen bp)";
				}
				$seqstr = qq{<div class=""><div onclick="popup(this,'$seqstr','st');" class="popup">$rs_set</div></div>};
				my $prtchr = qq{chr$rs_chromos:$rs_chstart-$rs_chbreak 
				($rs_chstrnd)<div class="small">[$rs_seqdbnm $rs_dbassem]</div>};
				print qq|
					<tr style="background-color: $colors{$bg_color};">
						<td class="btc"><a class="b" href="$pazar_cgi/seq_search.cgi?regid=$rs_accnumb&amp;excluded=$excluded">$id</a></td>
						<td class="btc">$seqname</td>
						<td class="btc">$seqstr</td>
						<td class="btc">$prtchr</td>
						<td class="btc"><div class="p2to"><form name="display$rs_counter" method="POST" action="$pazar_cgi/gff_custom_track.cgi" enctype="multipart/form-data" target="_blank">
							<input type="hidden" name="excluded" value="$excluded">
							<input type="hidden" name="chr" value="$rs_chromos">
							<input type="hidden" name="start" value="$rs_csstart">
							<input type="hidden" name="end" value="$rs_csbreak">
							<input type="hidden" name="species" value="$rs_binomsp">
							<input type="hidden" name="resource" value="ucsc">
							<a href="#" onclick="javascript:document.display$rs_counter.resource.value='ucsc'; document.display$rs_counter.submit();"><img src="$pazar_html/images/ucsc_logo.png" alt="Go to UCSC Genome Browser"></a>
							<!--<input type="submit" name="ucsc" value="ucsc" onClick="javascript:document.display$rs_counter.resource.value='ucsc';">--> 
							<a href="#" onclick="javascript:document.display$rs_counter.resource.value='ensembl'; document.display$rs_counter.submit();"><img src="$pazar_html/images/ensembl_logo.gif" alt="Go to Ensembl Genome Browser"></a>
							<!--<input type="submit" name="ensembl" value="ensembl" onclick="javascript:document.display$rs_counter.resource.value='ensembl';">-->
						</form></div></td>
					</tr>|;
				$bg_color = 1 - $bg_color;
			}
		}
		print qq{</tbody></table></div>};
	}

	# Gene details for markers...

	foreach my $gene_data (@marker_info) {

		$spcs = $gene_data->{species};
		$pgid = $gene_data->{ID};
		$gena = $gene_data->{desc};
		$gene = $gene_data->{accn};
		$gede = $gene_data->{ens_desc};
		$proj = $gene_data->{proj};

		my $ensp = $spcs;
		$ensp =~ s/ /_/g;
		my $gena_editable = "false";

		# Make gene name editable if page viewed by project member...

		if ($loggedin eq "true") {
			my $genasth = &select($dbh,qq{SELECT project_id FROM marker WHERE marker_id="} . $gene_data->{GID} . qq{"});
			my $gene_namerh = $genasth->fetchrow_hashref;
			my $gene_projid = $gene_namerh->{"project_id"};
			foreach my $p (@projids) {
				if ($p == $gene_projid) {
					$gena_editable = "true";
				}
			}
		}

		$bg_color = 0;
		my $sid = $$ . time;
		my $spcurlf = $spcs;
		$spcurlf = trim($spcurlf);
		$spcurlf =~ s/ /%20/g;
		my $otktgne = trim($gene);

		print qq{<a name="$pgid"></a>
			<h3><div class="float-r"><a href="#top" class="ns">back to top</a></div><a href="$pazar_cgi/gene_search.cgi?geneID=$pgid&amp;excluded=$excluded&amp;ID_list=PAZAR_gene">$gena</a> in the <a href="$pazar_cgi/project.pl?project_name=$proj">$proj</a> project<div class="clear-l"></div></h3>
			<div class="p20lo p40bo">
				<div class="float-r w240 b p10 bg-lg"><img src="http://burgundy.cmmt.ubc.ca/ORCAtk/images/ORCA.png" height="30" align="left" class="m10ro"><a href="http://www.cisreg.ca/cgi-bin/ORCAtk/orca?rm=select_gene1&species=$spcurlf&ensembl_id=$otktgne">Scan for transcription factor binding sites with ORCAtk</a></div>
				<div class="p5bo">
					<div>Species: <span class="b">$spcs</span></div>
					<div>PAZAR gene ID: <a href="$pazar_cgi/gene_search.cgi?geneID=$pgid&amp;excluded=$excluded&amp;ID_list=PAZAR_gene" class="b">$pgid</a></div>
					<div>Ensembl gene ID: <a target="_blank" href="http://www.ensembl.org/$ensp/Gene/Idhistory?db=core;g=$gene" class="b">$gene</a></div>
					<div class="p5bo">Ensembl gene description: <span class="b">$gede</span></div>
					<div class="emp">This gene is used as a marker located in the vicinity of the regulatory region. It is not necessarily regulated by the described sequence.</div>
				</div>
				<table class="searchtable tblw">
					<tbody><tr>
						<td class="gdtc w80">Regseq ID</td>
						<td class="gdtc w110">Seq name</td>
						<td class="gdtc">Sequence</td>
						<td class="gdtc w200">Coordinates</td>
						<td class="gdtc w90">Links</td>
					</tr>};
		my @regseqs = pazar::reg_seq::get_reg_seqs_by_marker_id($dbh, $gene_data->{GID});
		if (!$regseqs[0]) {
			print qq{</tbody></table></div><div class="emp">There is currently no available annotation for this gene. Please do not hesitate to create your own project and enter information about this gene or any other gene.</div>};
			next;
		} else {
			my @ens_coords = $ensdb->get_ens_chr($gene);
			foreach my $regseq (@regseqs) {
				$rs_counter = $rs_counter + 1;
				my $rs_accnumb = $regseq->accession_number;
				my $rs_chromos = $regseq->chromosome;
				my $rs_chstart = &pnum($regseq->start);
				my $rs_chbreak = &pnum($regseq->end);
				my $rs_csstart = $regseq->start;
				my $rs_csbreak = $regseq->end;
				my $rs_chstrnd = $regseq->strand;
				my $rs_seqdbnm = $regseq->seq_dbname;
				my $rs_dbassem = $regseq->seq_dbassembly;
				my $rs_binomsp = $regseq->binomial_species;
				my $id = write_pazarid($rs_accnumb, "RS");
				my $seqname = $regseq->id || "-";
				my $seqseq = $regseq->seq;
				my $seqlen = length($seqseq);
				my $seqstr = chopstr($seqseq, 20);
				my $rs_set = substr($seqstr,0,10);
				$rs_chstrnd = "&ndash;" if $rs_chstrnd eq "-";
				if ($seqlen > 10) {$rs_set .= "&raquo; ($seqlen bp)";}
				$seqstr = qq{<div class="seqcellsml"><div onclick="popup(this,'$seqstr','st');" class="popup">$rs_set</div></div>};
				my $prtchr = qq{chr$rs_chromos:$rs_chstart-$rs_chbreak 
				($rs_chstrnd)<div class="small">[$rs_seqdbnm $rs_dbassem]</div>};

				print qq|
					<tr style="background-color: $colors{$bg_color};">
						<td class="btc"><a href="$pazar_cgi/seq_search.cgi?regid=$rs_accnumb&amp;excluded=$excluded">$id</a></td>
						<td class="btc">$seqname</td>
						<td class="btc">$seqstr</td>
						<td class="btc">$prtchr</td>
						<td class="btc"><div class="p2to"><form name="display$rs_counter" method="POST" action="$pazar_cgi/gff_custom_track.cgi" enctype="multipart/form-data" target="_blank">
							<input type="hidden" name="excluded" value="$excluded">
							<input type="hidden" name="chr" value="$rs_chromos">
							<input type="hidden" name="start" value="$rs_csstart">
							<input type="hidden" name="end" value="$rs_csbreak">
							<input type="hidden" name="species" value="$rs_binomsp">
							<input type="hidden" name="resource" value="ucsc">
							<a href="#" onclick="javascript:document.display$rs_counter.resource.value='ucsc'; document.display$rs_counter.submit();"><img src="$pazar_html/images/ucsc_logo.png" alt="Go to UCSC Genome Browser"></a>
							<!--<input type="submit" name="ucsc" value="ucsc" onClick="javascript:document.display$rs_counter.resource.value='ucsc';">--> 
							<a href="#" onclick="javascript:document.display$rs_counter.resource.value='ensembl'; document.display$rs_counter.submit();"><img src="$pazar_html/images/ensembl_logo.gif" alt="Go to Ensembl Genome Browser"></a>
							<!--<input type="submit" name="ensembl" value="ensembl" onclick="javascript:document.display$rs_counter.resource.value='ensembl';">-->
						</form></div></td>
					</tr>|;
				$bg_color = 1 - $bg_color;
			}
		}
		print qq{</tbody></table></div>};
	}
}

sub convert_id {
	my ($ensdb, $gkdb, $genedb, $geneid) = @_;
	undef my @id;
	my $add = $genedb . "_to_llid";
	@id = $gkdb->$add($geneid);
	my $ll = $id[0];
	my @gene;
	if ($ll) {
		my $spcs = $gkdb->llid_to_org($ll);
		if (!$spcs) {
			print qq{<div class="emp">The $genedb ID you provided ($geneid) could not be found. 
			Please check that the provided ID ($geneid) is a $genedb ID and try again.</div>};
		}
		$ensdb->change_mart_organism($spcs);
		@gene = $ensdb->llid_to_ens($ll);
	}
	return $gene[0];
}

sub trim($) {
	my $string = shift;
	$string =~ s/^\s+//;
	$string =~ s/\s+$//;
	return $string;
}

sub chopstr {
	my ($longstr,$intervl) = @_;
	my $newstr = "";
	while (length($longstr) > $intervl) {
		$newstr = $newstr . substr($longstr, 0, $intervl) . "<br>";
		$longstr = substr($longstr, $intervl);
	}
	$newstr = $newstr . $longstr;
	return $newstr;
}

sub select {
	my ($dbh,$sql) = @_;
	my $sth = $dbh->prepare($sql);
	$sth->execute or die "$dbh->errstr\n";
	return $sth;
}

sub write_pazarid {
	my ($id,$type) = @_;
	my $id7d = sprintf "%07d", $id;
	my $pzid = $type . $id7d;
	return $pzid;
}

my $tail = HTML::Template->new(filename => "$pazarcgipath/tail.tmpl");
print $tail->output;

exit;
