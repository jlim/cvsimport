#!/usr/bin/perl
use pazar;
use pazar::gene;
use pazar::talk;
use pazar::reg_seq;
use HTML::Template;
use CGI qw(:standard);
use CGI::Carp qw(fatalsToBrowser);
use CGI::HTMLError trace => 1;

# use CGI::Debug( report => 'everything', on => 'anything' );

my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};

require "$pazarcgipath/getsession.pl";
require "$pazarcgipath/searchbox.pl";

my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");
$template->param(TITLE => "Sequence view | PAZAR");
$template->param(PAZAR_HTML => $pazar_html);
$template->param(PAZAR_CGI => $pazar_cgi);
$template->param(JAVASCRIPT_FUNCTION => qq{ });

if ($loggedin eq "true") {
	$template->param(LOGOUT => qq{<span class="b">You are signed in as $info{first} $info{last}.</span> 
	<a href="$pazar_cgi/logout.pl" class="b">Sign out</a>});
} else {
	$template->param(LOGOUT => qq{<a href="$pazar_cgi/login.pl"><span class="b">Sign in</span></a>});
}

sub pnum {
	my $num = shift;
	my $fnu = $num;
	unless ($num =~ /\D/) {
		my @aum = split(//,$num);
		$fnu = "";
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
	}
	return $fnu;
}

print "Content-Type: text/html\n\n", $template->output;
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
	DRV  => "mysql"
);

my @pubprojects = $dbh->public_projects;

print $bowz;

my $bg_color = 0;
my %colors = (
	0 => "#fffff0",
	1 => "#ffbd83");

my $get = new CGI;
my %params = %{$get->Vars};
my $regid = $params{regid};

unless ($regid) {
	$regid = $params{geneID};
	$regid =~ s/^\D+0*//;
}
unless ($regid) {
	print qq{<div class="emp">You do not have access to view this sequence. Please sign in and try again.</div>};
}

my $xc = $params{excluded} || "none";
my $projstat = &select($dbh,qq{SELECT b.project_name,b.status FROM reg_seq a,project b WHERE a.reg_seq_id="$regid" AND a.project_id=b.project_id});
my @res = $projstat->fetchrow_array;

if ($res[1] =~ /restricted/i) {
	$dbh = pazar->new(
		-globalsearch => "no",		      
		-host         => $ENV{PAZAR_host},
		-user         => $ENV{PAZAR_pubuser},
		-pass         => $ENV{PAZAR_pubpass},
		-dbname       => $ENV{PAZAR_name},
		-pazar_user   => $info{user},
		-pazar_pass   => $info{pass},
		-drv          => $ENV{PAZAR_drv},
		-project      => $res[0]);
} elsif (($res[1] =~ /published/i) or ($res[1] =~ /open/i)) {
	$dbh = pazar->new(
		-globalsearch => "no",		      
		-host         => $ENV{PAZAR_host},
		-user         => $ENV{PAZAR_pubuser},
		-pass         => $ENV{PAZAR_pubpass},
		-dbname       => $ENV{PAZAR_name},
		-drv          => $ENV{PAZAR_drv},
		-project      => $res[0]);
}

my $reg_seq = undef;
if ($regid ne "") {
	$reg_seq = pazar::reg_seq::get_reg_seq_by_regseq_id($dbh,$regid);
} else {
	$reg_seq = undef;
}

if (!defined $reg_seq) {
	print qq{<div class="emp">PAZAR is unable to retrieve the requested sequence because the provided ID ($regid) does not seem to be a current PAZAR sequence ID.</div>};
} else {
	my $geneName = $reg_seq->gene_description || "(not provided)";
	my $gid = $reg_seq->PAZAR_gene_ID;

	my $idprefix = "GS";
	my $asterisk = "";
	my $genetype = $reg_seq->gene_type;
	if ($genetype eq "marker") {
		$idprefix = "MK";
		$asterisk = qq{<span class="warning">*</span>};
	}

	my $pazargeneid = write_pazarid($gid,$idprefix);
	my @ec = $ensdb->get_ens_chr($reg_seq->gene_accession);
	$ec[5] =~ s/\[.*\]//g;
	$ec[5] =~ s/\(.*\)//g;
	$ec[5] =~ s/\.//g;
	my $geneDescription = $ec[5] || "(not provided)";
	my $gene_accession = $reg_seq->gene_accession || "(not provided)";
	my $seqname = $reg_seq->id || "(not provided)";
	
	# Make seq name editable if page viewd by project member...

	my $seq_projid = "";
	my $seqname_editable = "false";
	
	my $edito;
	if ($loggedin eq "true") {
		# Determine the project that this reg seq belongs to...
		my $regseqsth = &select($dbh,qq{SELECT project_id FROM reg_seq WHERE reg_seq_id="$regid"});
		my $regseqresultshref = $regseqsth->fetchrow_hashref;
		$seq_projid = $regseqresultshref->{"project_id"};
		foreach my $proj (@projids) {
			if ($proj == $seq_projid) {
				$seqname_editable = "true";
			}
		}
		if ($seqname_editable eq "true") {
			$edito = qq{<div class="p5to"><span class="txt-ora b">Editing options:</span> <input type="button" name="seqnameupdatebutton" value="Update sequence name" onclick="javascript:window.open('updatesequencename.pl?mode=form&pid=$seq_projid&sid=$regid');"> <input type="button" value="Delete this sequence" onclick="confirm_entry_seq_search('$regid','$seq_projid');"></div>};
		}
	}
	
	my $rs_chr = $reg_seq->chromosome;
	my $rs_sta = &pnum($reg_seq->start);
	my $rs_end = &pnum($reg_seq->end);
	my $rs_str = $reg_seq->strand;
	my $rs_dbn = $reg_seq->seq_dbname;
	my $rs_dba = $reg_seq->seq_dbassembly;
	my $rs_bsp = $reg_seq->binomial_species;
	$rs_str = "&ndash;" if $rs_str eq "-";
	
	my $coord = qq{chr$rs_chr:$rs_sta-$rs_end ($rs_str) <span class="sml">[$rs_dbn $rs_dba]</span>};
	my $quality = $reg_seq->quality || "(not provided)";
	
	my $species = $ensdb->current_org();
	$species = ucfirst($species) || "(not provided)";
	my $ensspecies = $species;
	$ensspecies =~ s/ /_/g;
	
	my $transcript = $reg_seq->transcript_accession || "(not provided)";
	
	my $tss;
	if ($reg_seq->transcript_fuzzy_start == $reg_seq->transcript_fuzzy_end) {
		$tss = $reg_seq->transcript_fuzzy_start || "(not provided)";
	} else {
		$tss = $reg_seq->transcript_fuzzy_start . "-" . $reg_seq->transcript_fuzzy_end || "(not provided)";
	}
	my $id = write_pazarid($regid,"RS");
	my $seqlen = &pnum(length($reg_seq->seq));
	my $seqstr = chopstr($reg_seq->seq,50) || "(not provided)";

	my $plainstr = $seqstr;
	$plainstr =~ s/<br>//g;
	
	$tss = &pnum($tss);

	my $species_fixed = $species;
	$species_fixed =~ s/ /%20/g;
	
	my $revcomp = "yes";
	if ($rs_str eq "+") {
		$revcomp = "no";
	}
	
	my $species2 = "mouse";
	if ($species eq "mus musculus") {
		$species2 = "human";
	} else {
		$species2 = "mouse";
	}
	
	my $otktsf = &trim($species_fixed);
	my $otkrsc = &trim($rs_chr);
	my $otksta = &trim($rs_sta);
	my $otkend = &trim($rs_end);
	
	my $gn_marker_warning;
	if ($genetype eq "marker") {
		$gn_marker_warning = qq{<div class="p5to"><div class="emp">This gene is used as a marker located in the vicinity of the regulatory region. It is not necessarily regulated by the described sequence.</div></div>};
	}
	
	my $rs_sta_nocomma = $rs_sta;
	my $rs_end_nocomma = $rs_end;
	$rs_sta_nocomma =~ s/,//g;
	$rs_end_nocomma =~ s/,//g;
	
	print qq{<h2>Sequence <a class="b" href="$pazar_cgi/seq_search.cgi?regid=$regid&amp;excluded=$xc">$id</a> in the <a class="b" href="$pazar_cgi/project.pl?project_name=$res[0]">$res[0]</a> project <a href="$pazar_cgi/help_FAQ.pl#2.4%20Sequence%20View" target="helpwin" onclick="window.open('about:blank','helpwin');"><img src="$pazar_html/images/help.gif" alt="Help" align="bottom" width="10"></a></h2>
	
	<div class="w50p float-l">
		<h3>Sequence details</h3>
		<div class="p10lo">
			<div>Sequence name: <div id="ajaxseqname" class="inline"><span class="b">$seqname</span></div></div>
			<div>Coordinates: <span class="b">$coord</span></div>
			<div>Ensembl transcript ID: <span class="b">$transcript</span></div>
			<div>TSS: <span class="b">$tss</span></div>
			<div>Quality: <span class="b">$quality</span></div>
			$edito
		</div>
	</div>
	<div class="w50p float-l">
		<h3>Gene details</h3>
		<div class="p10lo">
			<div>Species: <span class="b">$species</span></div>
			<div>PAZAR gene ID: <a class="b" href="$pazar_cgi/gene_search.cgi?geneID=$pazargeneid&amp;ID_list=PAZAR_gene&amp;excluded=$xc">$pazargeneid</a></div>
			<div>User-defined gene name: <span class="b">$geneName</span></div>
			<div>Ensembl gene ID: <a target="_blank" class="b" href="http://www.ensembl.org/$ensspecies/Gene/Idhistory?db=core;g=$gene_accession">$gene_accession</a></div>
			<div>Ensembl gene description: <span class="b">$geneDescription</span></div>
			$gn_marker_warning
		</div>
	</div>
	<div class="clear-l"></div>
	<h3>Sequence ($seqlen bp)</h3>
		
	 <div class="float-r w50p b">
	 	<div class="p10lo">
			<div class="bg-lg p10">
				<div class="float-l p5to p5ro b">
					<form name="display" method="POST" action="$pazar_cgi/gff_custom_track.cgi" enctype="multipart/form-data" target="_blank">View in&nbsp;
					<input type="hidden" name="excluded" value="$xc"><input type="hidden" name="chr" value="$rs_chr"><input type="hidden" name="start" value="$rs_sta_nocomma"><input type="hidden" name="end" value="$rs_end_nocomma"><input type="hidden" name="species" value="$rs_bsp"><input type="hidden" name="resource" value="ucsc"><a href="#" onclick="javascript:document.display.resource.value='ucsc'; document.display.submit();"><img align="absmiddle" src="$pazar_html/images/ucsc_logo.png" alt="Go to UCSC Genome Browser"></a><!--<input type="submit" name="ucsc" value="ucsc" onClick="javascript:document.display.resource.value='ucsc';">--> <a href="#" onClick="javascript:document.display.resource.value='ensembl'; document.display.submit();"><img align="absmiddle" src="$pazar_html/images/ensembl_logo.gif" alt="Go to EnsEMBL Genome Browser"></a><!--<input type="submit" name="ensembl" value="ensembl" onClick="javascript:document.display.resource.value='ensembl';">-->
					</form>
				</div>
				<div class="float-l w210 p5lo br-l"><img src="http://burgundy.cmmt.ubc.ca/ORCAtk/images/ORCA.png" height="30" align="left" class="m5ro"><a href="http://burgundy.cmmt.ubc.ca/cgi-bin/ORCAtk/orca?rm=select_seq1_coords&amp;species=$otktsf&amp;chr=$otkrsc&amp;start=$otksta&amp;end=$otkend">Scan for transcription factor binding sites with ORCAtk</a></div>
				<div class="clear-l"></div>
			</div>
		</div>
	</div>
	<div class="p10lo">
		<div><span class="b monospace">$seqstr</span></div>
		<div class="clear-r"></div>
	</div>};
	
	my @interactors = $dbh->get_interacting_factor_by_regseq_id($regid);
	my @expressors = $dbh->get_expression_by_regseq_id($regid);
	
	$bg_color = 0;
	my $count = 1;
	
	if (scalar(@interactors) > 0) {
		print qq{
		<h3>Interaction evidence</h3>
		<div class="p10lo">
		<table class="evidencetableborder tblw"><tr>
			<td class="ett w140">Analysis ID and method</td>
			<td class="ett w140">Cell type</td>
			<td class="ett">Interactor</td>
			<td class="ett w80">Interaction</td>
			<td class="ett w80">Pubmed</td>
			<td class="ett w140">Mutants (interaction)</td>
		</tr>};
	}
	
	foreach my $inter (@interactors) {
		my $an_ina = $inter->{aid};
		my @an = $dbh->get_data_by_primary_key("analysis",$an_ina);
		my $pazaranid = write_pazarid($an_ina,"AN");
		my @met = $dbh->get_data_by_primary_key("method",$an[3]);
		my @cell = $dbh->get_data_by_primary_key("cell",$an[4]);
		my $cellinfo;
		my @cell_cols = ("Cell","Tissue","Status","Description","Species");
		for (my $i = 0; $i < 5; $i++) {
			if ($cell[$i] and ($cell[$i] ne "") and ($cell[$i] ne "0") and ($cell[$i] ne "NA")) {
				if ($cell_cols[$i] eq "Species") {
					$cell[$i] = lc($cell[$i]);
					$cell[$i] = ucfirst($cell[$i]);
				}
				if ($cell_cols[$i] eq "Status") {
					$cell[$i] = lc($cell[$i]);
				}
				$cellinfo .= qq{<div>$cell_cols[$i]: <span class="b">$cell[$i]</span></div>};
			}
		}
		unless ($cellinfo) {
			$cellinfo = "(not provided)";
		}
		my $m = $met[0];
		my $fets;
		if (length($m) > 20) {
			$m = qq{<div onclick="popup(this,'$m','rt');" class="popup small">} . substr($m,0,18) . "..." . qq{</div>};
		} else {
			$m = qq{<div class="small">$m</div>};
		}
		$fets .= $m;
		print qq{
		<tr style="background-color: $colors{$bg_color};">
			<td class="btc"><a class="b" href="$pazar_cgi/exp_search.cgi?excluded=$xc&amp;aid=$an_ina">$pazaranid</a>$fets</td>
			<td class="btc small">$cellinfo</td>};
	
		if ($inter->{tftype} eq "funct_tf") {
			my $tf = $dbh->create_tf;
			my $cmpx = $tf->get_tfcomplex_by_id($inter->{tfcomplex},"notargets");
			my $tfid = $inter->{tfcomplex};
			my $ptid = write_pazarid($tfid,"TF");
			my $cpxn = $cmpx->name;
			print qq{<td class="btc small"><a class="b" href="$pazar_cgi/tf_search.cgi?ID_list=PAZAR_TF&amp;excluded=$xc&amp;geneID=$ptid">$ptid</a><div>$cpxn</div></td>};
		} elsif ($inter->{tftype} eq 'sample') {
			my @sample=$dbh->get_data_by_primary_key('sample',$inter->{tfcomplex});
			my @samplecell=$dbh->get_data_by_primary_key('cell',$sample[1]);
			print qq{<td class="btc small">$sample[0] $samplecell[0]</td>};
		} else {
			print qq{<td class="btc small">(unknown)</td>};
		}
	
		my ($table,$pazarid,@dat) = $dbh->links_to_data($inter->{olink},"output");
		if ($table eq "interaction") {
			print qq{<td class="btc small">};
			my @data;
			for (my $i=0; $i<(@dat-3); $i++) {
				if ($dat[$i] and ($dat[$i] ne "0")) {
					push (@data,$dat[$i]);
				}
			}
			my $blag = join(" ",@data);
			if (length($blag) > 14) {
				$blag = qq{<div onclick="popup(this,'$blag','rt');" class="popup small">} . substr($blag,0,12) . "..." . qq{</div>};
			}
			print qq{$blag</td>};
		}
	
		my @ref = $dbh->get_data_by_primary_key("ref",$an[6]);
		print qq{
			<td class="btc"><a href="http://www.ncbi.nlm.nih.gov/pubmed/$ref[0]" target="_blank">$ref[0]</a></td>
			<td class="btc small">};
		my @mutants = $dbh->get_mutants_by_analysis_id($inter->{aid});
		my $mutnb = 0;
		foreach my $mutant (@mutants) {
			my @mut = $dbh->get_data_by_primary_key("mutation_set",$mutant->{mutid});
			unless ($mut[0] == $regid) {
				next;
			}
			$mutnb++;
			print qq{<div><span class="b">$mut[1]</span> };
			my ($table,$pazarid,@dat) = $dbh->links_to_data($mutant->{olink},"output");
			if ($table eq "interaction") {
				my @data;
				for (my $i=0; $i<(@dat-3); $i++) {
					if ($dat[$i] and ($dat[$i] ne "0")) {
						push (@data,$dat[$i]);
					}
				}
				print qq{(} . join(":",@data) . qq{)};
			}
			print qq{</div>};
		}
		if ($mutnb == 0) {
			print qq{(none described)};
		}
		print qq{</td></tr>};
		$count++;
		$bg_color = 1-$bg_color;
	}
	
	if(scalar(@interactors) > 0) {
		print qq{</table></div>};
	}		    

	$bg_color = 0;
	if (scalar(@expressors) > 0) {
		print qq{<h3>Cis-regulation evidence</h3>
			<div class="p10lo">
			<table class="evidencetableborder tblw">
				<tr>
					<td class="ett w140">Analysis ID and method</span></td>
					<td class="ett w160">Cell type</span></td>
					<td class="ett">Conditions</span></td>
					<td class="ett w100">Expr level</td>
					<td class="ett w80">Pubmed</td>
					<td class="ett w100">Mutants (effect)</td>
				</tr>};
	}
	
	foreach my $exp (@expressors) {
		my $expaid = $exp->{aid};
		my @an = $dbh->get_data_by_primary_key("analysis",$expaid);
		my $pazaranid = write_pazarid($expaid,"AN");
		my @met = $dbh->get_data_by_primary_key("method",$an[3]);
		my @cell = $dbh->get_data_by_primary_key("cell",$an[4]);
		my $cellinfo;
		my @cell_cols = ("Cell","Tissue","Status","Description","Species");
		for (my $i=0; $i<5; $i++) {
			if ($cell[$i] and ($cell[$i] ne "") and ($cell[$i] ne "0") and ($cell[$i] ne "NA")) {
				if ($cell_cols[$i] eq "Species") {
					$cell[$i] = lc($cell[$i]);
					$cell[$i] = ucfirst($cell[$i]);
				}
				if ($cell_cols[$i] eq "Status") {
					$cell[$i] = lc($cell[$i]);
				}
				$cellinfo .= qq{<div>$cell_cols[$i]: <span class="b">$cell[$i]</span></div>};
			}
		}
		unless ($cellinfo) {
			$cellinfo = "(not provided)";
		}
		my @conds = @{$exp->{iotype}};
		my @condids = @{$exp->{ioid}};
		my $nocond = 0;
		my $condinfo;
		for (my $i=0; $i<@conds; $i++) {
			if ($i > 0) {
				$condinfo .= qq{<div class="p3to p5bo"><div class="br-b"></div></div>};
			}
			$nocond = 1;
			my @dat = $dbh->get_data_by_primary_key($conds[$i],$condids[$i]);
			my @cond_cols = ("Type","Molecule","Description","Concentration","Scale");
			for (my $j=0; $j<5; $j++) {
				if ((lc($dat[0]) eq "co-expression") and ($j == 2)) {
					next;
				}
				if ($dat[$j] and ($dat[$j] ne "") and ($dat[$j] ne "NA")) {
					$condinfo .= qq{<div>$cond_cols[$j]: <span class="b">$dat[$j]</span></div>};
				}
			}
			if (lc($dat[0]) eq "co-expression") {
				my $tfid = $dat[2];
				my $tf = $dbh->create_tf;
				my $complex = $tf->get_tfcomplex_by_id($tfid,"notargets");
				my $pazartfid = write_pazarid($tfid,"TF");
				my $cpxn = $complex->name;
				$condinfo .= qq{<a href="$pazar_cgi/tf_search.cgi?ID_list=PAZAR_TF&amp;excluded=$xc&amp;geneID=$pazartfid" class="b">$pazartfid</a><div>$cpxn</div>};
			}
		}
		if ($nocond == 0) {
			$condinfo .= qq{(none)};
		}
		my ($table,$tableid,@dat) = $dbh->links_to_data($exp->{olink},"output");
		my @data;
		my $blag;
		for (my $i=0; $i<(@dat-3); $i++) {
			if ($dat[$i] and ($dat[$i] ne "0")) {
				push (@data,$dat[$i]);
			}
		}
		my $mutmut;
		my $nomut = 0;
		$blag = join(" ",@data);
		if (length($blag) > 14) {
			$blag = qq{<div onclick="popup(this,'$blag','rt');" class="popup small">} . substr($blag,0,12) . "..." . qq{</div>};
		}
		
		my @ref = $dbh->get_data_by_primary_key("ref",$an[6]);
		my @mutants = $dbh->get_mutants_by_analysis_id($exp->{aid});
		foreach my $mutant (@mutants) {
			my @mut_condids = @{$mutant->{ioid}};
			my $nomatch = 0;
			if (@mut_condids != @condids) {
				$nomatch = 1;
			}
			if ((@mut_condids == @condids) and (@mut_condids != 0)) {
				for (my $j=0; $j<@mut_condids; $j++) {
					unless (grep(/^$mut_condids[$j]$/,@condids)) {
						$nomatch = 1;
					}
				}
			}
			next if ($nomatch == 1);
			my @mut = $dbh->get_data_by_primary_key("mutation_set",$mutant->{mutid});
			$nomut = 1;
			$mutmut .= qq{<div><span class="b">$mut[1]</span> };
			my ($table,$pazarid,@dat) = $dbh->links_to_data($mutant->{olink},"output");
			if ($table eq "expression") {
				my @data;
				for (my $i=0; $i<(@dat-3); $i++) {
					if ($dat[$i] && $dat[$i] ne '0') {
						push @data,$dat[$i];
					}
				}
				$mutmut .= qq{(} . join(", ",@data) . qq{)};
			}
			$mutmut .= qq{</div>};
		}
		if ($nomut == 0) {
			$mutmut .= qq{(none described)};
		}
		my $m = $met[0];
		my $fets;
		if (length($m) > 20) {
			$m = qq{<div onclick="popup(this,'$m','rt');" class="popup small">} . substr($m,0,18) . "..." . qq{</div>};
		} else {
			$m = qq{<div class="small">$m</div>};
		}
		$fets .= $m;
		print qq{
			<tr style="background-color: $colors{$bg_color};">
				<td class="btc"><a class="b" href="$pazar_cgi/exp_search.cgi?aid=$expaid&amp;excluded=$xc">$pazaranid</a>$fets</td>
				<td class="btc small">$cellinfo</td>
				<td class="btc small">$condinfo</td>
				<td class="btc small">$blag</td>
				<td class="btc"><a href="http://www.ncbi.nlm.nih.gov/pubmed/$ref[0]" target="_blank">$ref[0]</a></td>
				<td class="btc small">$mutmut</td>
			</tr>};
		$count++;
		$bg_color = 1 - $bg_color;
	}
	if (scalar(@expressors) > 0) {
		print qq{</table></div>};
	}
}

print qq{</div>};
my $temptail = HTML::Template->new(filename => "tail.tmpl");
print $temptail->output;

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

sub convert_id {
	my ($auxdb,$genedb,$geneid,$ens) = @_;
	undef my @id;
	my @ensembl;
	my $add = $genedb . "_to_llid";
	@id = $auxdb->$add($geneid);
	my $ll = $id[0];
	@ensembl = $ens?$ens:$auxdb->llid_to_ens($ll) if ($ll);
	return $ensembl[0];
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

sub trim($) {
	my $string = shift;
	$string =~ s/^\s+//;
	$string =~ s/\s+$//;
	return $string;
}
