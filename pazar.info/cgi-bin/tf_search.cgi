#!/usr/bin/perl
use pazar;
use pazar::gene;
use pazar::talk;
use pazar::reg_seq;
use HTML::Template;
use TFBS::Matrix::PFM;
use TFBS::PatternGen::MEME;
use CGI qw(:standard);
use CGI::Carp qw(fatalsToBrowser);

my $pazar_cgi       = $ENV{PAZAR_CGI};
my $pazar_html      = $ENV{PAZAR_HTML};
my $pazarcgipath    = $ENV{PAZARCGIPATH};
my $pazarhtdocspath = $ENV{PAZARHTDOCSPATH};

my $get = new CGI;
my %param = %{ $get->Vars };
our $searchtab = $param{"searchtab"} || "tfs";
my $MEssages;

require "$pazarcgipath/getsession.pl";
require "$pazarcgipath/searchbox.pl";

my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");
$template->param(TITLE => "Search for transcription factors (TFs) | PAZAR");
$template->param(PAZAR_HTML          => $pazar_html);
$template->param(PAZAR_CGI           => $pazar_cgi);
#disable onload function to disable automatic meme display generation
#$template->param(ONLOAD_FUNCTION     => "init();");
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

print "Content-Type: text/html\n\n", $template->output;
my @pubprojects = $dbh->public_projects;

print $bowz;
my $numresults = $param{results};

my $accn  = $param{geneID};
$accn =~ s/[\s]//g;
my $dbaccn = $param{ID_list} || "PAZAR_TF";
my $tfname;
my @trans;
if ($accn) {
	if ($dbaccn eq "PAZAR_TF") {
		@trans = ("PAZARid");
	}
	if ($dbaccn eq "EnsEMBL_gene") {
		@trans = $ensdb->ens_transcripts_by_gene($accn);
		unless ($trans[0]) {
			print qq{<div class="emp">The Ensembl Gene ID you provided ($accn) could not be found. 
			Please check that the provided ID ($accn) is an Ensembl Gene ID.</div>};
			&exitscr();
		}
	} elsif ($dbaccn eq "EnsEMBL_transcript") {
		my @gene = $ensdb->ens_transcr_to_gene($accn);
		unless ($gene[0]) {
			print qq{<div class="emp">The Ensembl Transcript ID you provided ($accn) could not be found. 
			Please check that the provided ID ($accn) is an Ensembl Transcript ID. 
			You will get the best results if you provide us with an Ensembl Gene ID.</div>};
			&exitscr();
		}
		push @trans, $accn;
	} elsif ($dbaccn eq "EntrezGene") {
		my $species = $gkdb->llid_to_org($accn);
		if (!$species) {
			print qq{<div class="emp">The Entrez Gene ID you provided ($accn) could not be found. 
			Please check that the provided ID ($accn) is an Entrez Gene ID. 
			You will get the best results if you provide us with an Ensembl Gene ID.</div>};
			&exitscr();
		}
		$ensdb->change_mart_organism($species);
		my @gene = $ensdb->llid_to_ens($accn);
		unless ($gene[0]) {
			print qq{<div class="emp">The $dbaccn ID you provided ($accn) could not be found. 
			Please check that the provided ID ($accn) is a $dbaccn ID. 
			You will get the best results if you provide us with an Ensembl Gene ID.</div>};
			&exitscr();
		}
		@trans = $ensdb->ens_transcripts_by_gene($gene[0]);
	} elsif ($dbaccn eq "nm") {
		my $sp =
		  $gkdb->{dbh}->prepare("select organism from ll_locus a, ll_refseq_nm b where a.ll_id=b.ll_id and b.nm_accn=?");
		$sp->execute($accn);
		my $species = $sp->fetchrow_array();
		if (!$species) {
			print qq{<div class="emp">The $dbaccn ID you provided ($accn) could not be found. 
			Please check that the provided ID ($accn) is a $dbaccn ID. 
			You will get the best results if you provide us with an Ensembl Gene ID.</div>};
			&exitscr();
		}
		$ensdb->change_mart_organism($species);
		my @gene = $ensdb->nm_to_ens($accn);
		unless ($gene[0]) {
			print qq{<div class="emp">The $dbaccn ID you provided ($accn) could not be found. 
			Please check that the provided ID ($accn) is a $dbaccn ID. 
			You will get the best results if you provide us with an Ensembl Gene ID.</div>};
			&exitscr();
		}
		@trans = $ensdb->ens_transcripts_by_gene($gene[0]);
		unless ($trans[0]) {
			print qq{<div class="emp">The $dbaccn ID you provided ($accn) could not be found. 
			Please check that the provided ID ($accn) is a $dbaccn ID. 
			You will get the best results if you provide us with an Ensembl Gene ID.</div>};
			&exitscr();
		}
	} elsif ($dbaccn eq "swissprot") {
		my $sp =
		  $gkdb->{dbh}->prepare("select organism from ll_locus a, gk_ll2sprot b where a.ll_id=b.ll_id and sprot_id=?") || die;
		$sp->execute($accn) || die;
		my $species = $sp->fetchrow_array();
		if (!$species) {
			print qq{<div class="emp">The $dbaccn ID you provided ($accn) could not be found. 
			Please check that the provided ID ($accn) is a $dbaccn ID. 
			You will get the best results if you provide us with an Ensembl Gene ID.</div>};
			&exitscr();
		}
		$ensdb->change_mart_organism($species);
		@gene = $ensdb->swissprot_to_ens($accn);
		unless ($gene[0]) {
			print qq{<div class="emp">The $dbaccn ID you provided ($accn) could not be found. 
			Please check that the provided ID ($accn) is a $dbaccn ID. 
			You will get the best results if you provide us with an Ensembl Gene ID.</div>};
			&exitscr();
		}
		@trans = $ensdb->ens_transcripts_by_gene($gene[0]);
		unless ($trans[0]) {
			print qq{<div class="emp">The $dbaccn ID you provided ($accn) could not be found. 
			Please check that the provided ID ($accn) is a $dbaccn ID. 
			You will get the best results if you provide us with an Ensembl Gene ID.</div>};
			&exitscr();
		}
	} elsif ($dbaccn eq "tf_name") {
		@trans  = ("none");
		$tfname = qq{\%$accn\%};
	}
	my ($tfcount,$seqcounter) = (0,0);
	my @tfcomplexes;
	foreach my $trans (@trans) {
		my $tf;
		if ($trans eq "none") {
			$tf = $dbh->create_tf;
			@tfcomplexes = $tf->get_tfcomplex_by_name($tfname,undef,$numresults);
		} elsif ($trans eq "PAZARid") {
			my @ids;
			if ($accn=~m/,/) {
				@ids = split(/,/,$accn);
			} else {
				@ids = ($accn);
			}
			foreach my $PZid (@ids) {
				$PZid =~ s/^\D+0*//;
				$tf = $dbh->create_tf;
				my @tfcomp = $tf->get_tfcomplex_by_id($PZid,undef,$numresults);
				if ($tfcomp[0]) {
					push @tfcomplexes, $tfcomp[0];
				}
			}
		} else {
			$tf = $dbh->create_tf;
			my @tfcomp = $tf->get_tfcomplex_by_transcript($trans,undef,$numresults);
			foreach my $comp (@tfcomp) {
				if ($comp) {
					push @tfcomplexes, $comp;
				}
			}
		}
		if ($loggedin eq "true") {
			foreach my $proj (@projids) {
				my $restricted = &select($dbh, "SELECT project_name FROM project WHERE project_id='$proj' and upper(status)='RESTRICTED'");
				my $restr_proj = $restricted->fetchrow_array();
				if ($restr_proj) {
					my $dbhandle = pazar->new(
						-host       => $ENV{PAZAR_host},
						-user       => $ENV{PAZAR_pubuser},
						-pass       => $ENV{PAZAR_pubpass},
						-dbname     => $ENV{PAZAR_name},
						-pazar_user => $info{user},
						-pazar_pass => $info{pass},
						-drv        => $ENV{PAZAR_drv},
						-project    => $restr_proj
					);
					my @complexes;
					if ($trans eq "none") {
						$tf = $dbhandle->create_tf;
						@complexes = $tf->get_tfcomplex_by_name($tfname,undef,$numresults);
					} elsif ($trans eq "PAZARid") {
						my @ids;
						if ($accn=~m/,/) {
							@ids = split(/,/,$accn);
						} else {
							@ids = ($accn);
						}
						foreach my $PZid (@ids) {
							$PZid =~ s/^\D+0*//;
							$tf = $dbhandle->create_tf;
							my @tfcomp = $tf->get_tfcomplex_by_id($PZid,undef,$numresults);
							if ($tfcomp[0]) {
								push @complexes, $tfcomp[0];
							}
						}
					} else {
						$tf = $dbhandle->create_tf;
						@complexes = $tf->get_tfcomplex_by_transcript($trans,undef,$numresults);
					}
					foreach my $comp (@complexes) {
						push @tfcomplexes, $comp;
					}
				}
			}
		}
	}
	my @excluded_proj;
	my $excluded = "none";
	if ($param{excl_proj}) {
		foreach my $val ($get->param("excl_proj")) {
			push @excluded_proj, $val;
		}
		$excluded = join("__", @excluded_proj);
	} elsif ($param{excluded}) {
		$excluded = $param{excluded};
		@excluded_proj = split(/__/, $excluded);
	}
	my $exprint = "";
	unless ($excluded eq "none") {
		$exprint = qq{<div class="p10bo"><span class="b">Projects excluded from the search:</span> $excluded</div>};
	}
	
	my %nicename = (
		"tf_name" => "user-defined TF name",
		"EnsEMBL_gene" => "Ensembl gene ID",
		"EnsEMBL_transcript" => "Ensembl transcript ID",
		"EntrezGene" => "Entrez Gene ID",
		"nm" => "Refseq ID",
		"swissprot" => "Swissprot ID",
		"PAZAR_TF" => "PAZAR TF ID"
	);
	print qq{
		<a name="top"></a>
		<h2>Matching TFs <span class="txt-grey">($nicename{$dbaccn} "$accn")</span></h2>
		$exprint};
	my $bg_color = 0;
	my %colors   = (
		0 => "#fffff0",
		1 => "#FFB5AF"
	);
	my $suta;
	foreach my $complex (@tfcomplexes) {
		my $tfproj = $dbh->get_project_name("funct_tf", $complex->dbid);
		if (grep(/^$tfproj$/, @excluded_proj) ) {
			next;
		}
		my $pazartfid = write_pazarid($complex->dbid, "TF");
		my $tf_name = $complex->name;
		my @families = ();
		my @classes = ();
		my @traccs = ();
		my $species;
		while (my $subunit = $complex->next_subunit) {
			my $fam   = !$subunit->get_fam   ? "" : "/" . $subunit->get_fam;
			my $class = !$subunit->get_class ? "" : $subunit->get_class . $fam;
			push(@classes, $class);
			my $tr_accn = $subunit->get_transcript_accession($dbh);
			push(@traccs, $tr_accn);
			unless ($species) {
				my @enco = $ensdb->get_ens_chr($tr_accn);
				$enco[5] =~ s/\[.*\]//g;
				$enco[5] =~ s/\(.*\)//g;
				$enco[5] =~ s/\.//g;
				$species = $ensdb->current_org();
				$species = ucfirst($species);
			}
		}
		my $ensspecies = $species;
		$ensspecies =~ s/ /_/g;

		unless ($species) { $species = "-"; }
		my $tfclass = join(" ", @classes);
		if (length($species) > 18) {
			$species =~ s/\'/\&\#39\;/g;
			$species = qq{<div onclick="popup(this,'$species','rt');" class="popup">} . substr($species,0,16) . "..." . qq{</div>};
		}
		if (length($tf_name) > 12) {
			$tf_name =~ s/\'/\&\#39\;/g;
			$tf_name = qq{<div onclick="popup(this,'$tf_name','rt');" class="popup">} . substr($tf_name,0,10) . "..." . qq{</div>};
		}
		if (length($tfclass) > 18) {
			$tfclass =~ s/\'/\&\#39\;/g;
			$tfclass = qq{<div onclick="popup(this,'$tfclass','rt');" class="popup">} . substr($tfclass,0,16) . "..." . qq{</div>};
		}
		if (length($tfproj) > 16) {
			$tfproj =~ s/\'/\&\#39\;/g;
			$tfproj = qq{<a href="$pazar_cgi/project.pl?project_name=$tfproj">} . substr($tfproj,0,14) . "..." . qq{</a>};
		} else {
			$tfproj = qq{<a href="$pazar_cgi/project.pl?project_name=$tfproj">$tfproj</a>};
		}
		my $traccns;
		foreach my $t (@traccs) {$traccns .= qq{<a target="_blank" href="http://www.ensembl.org/$ensspecies/Gene/Idhistory?db=core;t=$t">$t</a> };}
		$suta .= qq{
				<tr style="background-color: $colors{$bg_color};">
					<td class="btc">$species</td>
					<td class="btc">$pazartfid&nbsp;<a href="#$pazartfid"><img src="$pazar_html/images/magni.gif" alt="View Details" align="bottom" width="10"></a></td>
					<td class="btc">$tf_name</td>
					<td class="btc">$traccns</td>
					<td class="btc">$tfclass</td>
					<td class="btc">$tfproj</td>
				</tr>};
		$bg_color = 1 - $bg_color;
	}
	if ($suta) {
		print qq{
			<div class="p10bo"><table class="summarytable tblw">
				<tbody><tr>
					<td class="tfdst w16p">Species</td>
					<td class="tfdst w12p">PAZAR TF</td>
					<td class="tfdst w16p">TF name</td>
					<td class="tfdst ">Transcript accession</td>
					<td class="tfdst w20p">Class and family</td>
					<td class="tfdst w16p">PAZAR project</td>
				</tr>$suta</tbody></table></div>};
	}
	print qq{
		<h2>Details</h2>
		<div class="p10 bg-lg small b">
			Note: genes marked with a red asterisk [ <span class="warning">*</span> ] 
			are used as markers located in the vicinity of the regulatory region.<br>
			They have not been shown to be regulated by the associated sequence.
		</div>
		};
	foreach my $complex (@tfcomplexes) {
		$bg_color = 0;
		my $tfid = $complex->dbid;
		my $tfproj = $dbh->get_project_name("funct_tf", $tfid);
		if (grep(/^$tfproj$/, @excluded_proj) ) {
			next;
		}
		$tfcount++;
		my $tf_name = $complex->name;
		my $pazartfid = write_pazarid($tfid, "TF");
		my $file = "$pazarhtdocspath/tmp/" . $pazartfid . ".fa";
		open(TMP, ">$file");
		my @classes               = ();
		my @families              = ();
		my @traccs = ();
		my $species;
		while (my $subunit = $complex->next_subunit) {
			my $class = !$subunit->get_class ? "-" : $subunit->get_class;
			my $fam   = !$subunit->get_fam   ? "-" : $subunit->get_fam;
			push(@classes,  $class);
			push(@families, $fam);
			my $tr_accn = $subunit->get_transcript_accession($dbh);
			unless ($species) {
				my @enco = $ensdb->get_ens_chr($tr_accn);
				$enco[5] =~ s/\[.*\]//g;
				$enco[5] =~ s/\(.*\)//g;
				$enco[5] =~ s/\.//g;
				$species = $ensdb->current_org();
				$species = ucfirst($species);
			}
			my $ensspecies = $species;
			$ensspecies =~ s/ /_/g;
			my $link_tr_accn = qq{<a href="http://www.ensembl.org/$ensspecies/Gene/Idhistory?db=core;t=$tr_accn" 
				target="enswin" onClick="window.open('about:blank','enswin');">$tr_accn</a>};
			push(@traccs, $link_tr_accn);
		}
		unless ($species) { $species = "-"; }
		my $traccns = join(" ", @traccs);
		my $tfclass = join(" ", @classes);
		my $trfamil = join(" ", @families);
		my $tf_editable = "false";
		my $tfsth = &select($dbh, "select project_id from funct_tf where funct_tf_id=" . $tfid);
		my $tfresultshref = $tfsth->fetchrow_hashref;
		my $tf_projid = $tfresultshref->{"project_id"};
		my $tf_name_edit = "";
		if ($loggedin eq "true") {
			foreach my $proj (@projids) {
				if ($proj == $tf_projid) {
					$tf_editable = "true";
				}
			}
			if ($tf_editable eq "true") {
				$tf_name_edit = qq{
					<div class="p5to">
					<span class="txt-ora b">Editing options: </span> 
					<input type="button" name="tfnameupdatebutton" value="Update TF name" onclick="window.open('$pazar_cgi/updatetfname.pl?mode=form&pid=$tf_projid&tfid=$tfid');"></div>};
			}
		}
		my $dp = qq{
			<a name="$pazartfid"></a>
			<h3><div class="float-r"><a href="#top" class="ns">back to top</a></div><a href="$pazar_cgi/tf_search.cgi?geneID=$pazartfid&excluded=$excluded">$tf_name</a> in the <a href="$pazar_cgi/project.pl?project_name=$tfproj">$tfproj</a> project<div class="clear-l"></div></h3>
			<div class="p20lo p40bo"><div>
				<div>Species: <span class="b">$species</span></div>
				<div>PAZAR TF ID: <span class="b"><a href="$pazar_cgi/tf_search.cgi?geneID=$pazartfid&excluded=$excluded">$pazartfid</a></span></div>
				<div>Transcript accession: <span class="b">$traccns</span></div>
				<div>Class and family: <span class="b">$tfclass $trfams</span></div>
				<div>$tf_name_edit</div>
				<div id="Hidden$pazartfid\_$tf_projid" class="hide">$tf_name</div>};
		my $dc;

		if (!$complex->{targets}) {
			$dc .= qq{<div class="emp">No target could be found for this transcription factor.</div>};
			next;
		}
		my $count = 0;
		my @rsids;
		my @coids;
		my ($bigrow,$smlrow);
		my $dh;
		my $fasta;
#by default, complex has 200 targets unless numresults parameter specified with  a numeric value or 'all'
		while (my $site = $complex->next_target) {
			my $type = $site->get_type;
			if ($type eq "matrix") {
				next;
			} elsif ($type eq "reg_seq") {
				my $rsid = $site->get_dbid;
				if (grep /^$rsid$/, @rsids) { next; }
				push @rsids, $rsid;
				my $id = write_pazarid($rsid, "RS");
				my $seqname = !$site->get_name ? "" : $site->get_name;
				my $reg_seq = pazar::reg_seq::get_reg_seq_by_regseq_id($dbh,
					$site->get_dbid);
				my $gid = $reg_seq->PAZAR_gene_ID;
				my $gidprefix = "GS";
				my $asterisk  = "";
				my $genetype  = $reg_seq->gene_type;
				if ($genetype eq "marker") {
					$gidprefix = "MK";
					$asterisk  = qq{<span class="warning">*</span>};
				}
				my $pazargeneid = write_pazarid($gid, $gidprefix);
				my $gene_accession = $reg_seq->gene_accession;
				my @enco =
				  $ensdb->get_ens_chr($reg_seq->gene_accession);
				$enco[5] =~ s/\[.*\]//g;
				$enco[5] =~ s/\(.*\)//g;
				$enco[5] =~ s/\.//g;
				my $species = $ensdb->current_org();
				$species = ucfirst($species) || "-";
				$seqcounter++;
				$count++;
				
				my $rs_binomial_species = $reg_seq->binomial_species;
				my $rs_assembly = $reg_seq->seq_dbassembly;
				my $rs_chromosome = $reg_seq->chromosome;
				my $rs_dbname = $reg_seq->seq_dbname;
				my $rs_start = &pnum($reg_seq->start);
				my $rs_break = &pnum($reg_seq->end);
				my $uc_start = $reg_seq->start;
				my $uc_break = $reg_seq->end;
				my $rs_strand = $reg_seq->strand;
				my $rs_site = $site->get_seq;
				my $rs_gene = $enco[5];
				my $rs_seq = chopstr($rs_site,20);
				$fasta.=">$id\n$rs_site\n";
				$rs_strand = "&ndash;" if $rs_strand eq "-";
				if (length($seqname) > 10) {
					$seqname =~ s/\'/\&\#39\;/g;
					$seqname = qq{<div onclick="popup(this,'$seqname','rt');" class="popup">} . substr($seqname,0,8) . "..." . qq{</div>};
				}
				if (length($rs_gene) > 16) {
					$rs_gene =~ s/\'/\&\#39\;/g;
					$rs_gene = qq{<div onclick="popup(this,'$rs_gene','rt');" class="popup">} . substr($rs_gene,0,14) . "..." . qq{</div>};
				}
				my $big_coord = qq{chr$rs_chromosome:$rs_start-$rs_break ($rs_strand)<div class="small">[$rs_dbname $rs_assembly]</div>};
				my $sml_coord = qq{chr$rs_chromosome:$rs_start-$rs_break ($rs_strand)};
				my $link_ucsc = qq{href="$pazar_cgi/gff_custom_track.cgi?resource=ucsc&chr=$rs_chromosome&start=$uc_start&end=$uc_break&species=$rs_binomial_species&excluded=$excluded" target="_blank"};
				my $link_embl = qq{href="$pazar_cgi/gff_custom_track.cgi?resource=ensembl&chr=$rs_chromosome&start=$rs_start&end=$rs_break&species=$rs_binomial_species&excluded=$excluded" target="_blank"};
				my $rs_checkb = qq{<input type="checkbox" name="seq$seqcounter" value="$rs_site">};
				my $rs_bgco = qq{style="background-color:$colors{$bg_color};"};
				my $rs_set = substr($rs_site,0,10);
				my $rs_ses = substr($rs_site,0,10);
				my $rs_seqlen = length($rs_site);
				if ($rs_seqlen > 10) {
					$rs_seqlen = &pnum($rs_seqlen);
					$rs_set .= "... ($rs_seqlen&nbsp;bp)";
					$rs_ses .= "...";
				}
				my $seq_reg = qq{<div class=""><div onclick="popup(this,'$rs_seq','st');" class="popup">$rs_set</div></div>};
				my $seq_sml = qq{<div class=""><div onclick="popup(this,'$rs_seq','st');" class="popup">$rs_ses</div></div>};
				$bigrow .= qq{
					<tr class="genomic" $rs_bgco>
						<td class="btc"><div>$rs_checkb</div></td>
						<td class="btc"><div>Genomic</div></td>
						<td class="btc"><div><a href="$pazar_cgi/seq_search.cgi?regid=$rsid&excluded=$excluded" class="b">$id</a><br>$seqname</div></td>
						<td class="btc"><div>$asterisk<a href="$pazar_cgi/gene_search.cgi?geneID=$pazargeneid&excluded=$excluded" class="b">$pazargeneid</a> 
							<div class="b">$rs_gene</div>$species</div></td>
						<td class="btc">$seq_reg</td>
						<td class="btc"><div><div class="b">Coordinates:</div>$big_coord</div></td>
						<td class="btc"><div class="p5to"><a $link_ucsc ><img src="$pazar_html/images/ucsc_logo.png" alt="Go to UCSC Genome Browser"></a> 
							<a $link_embl ><img src="$pazar_html/images/ensembl_logo.gif" alt="Go to EnsEMBL Genome Browser"></a></div></td>
					</tr>};

				$smlrow .= qq{
					<tr class="genomic" $rs_bgco>
						<td class="btc"><div>$rs_checkb</div></td>
						<td class="btc"><div>Genomic</div></td>
						<td class="btc"><div><a href="$pazar_cgi/seq_search.cgi?regid=$rsid&excluded=$excluded" class="b">$id</a></div></td>
						<td class="btc"><div>$asterisk<a href="$pazar_cgi/gene_search.cgi?geneID=$pazargeneid&excluded=$excluded" class="b">$pazargeneid</a></div></td>
						<td class="btc">$seq_sml</td>
						<td class="btc"><div>$sml_coord</div></td>
						<td class="btc"><div><a $link_ucsc>UCSC</a> <a $link_embl >Ensembl</a></div></td>
					</tr>};
				
				$dh = 1;

			} elsif ($type eq "construct") {

				my $coid = $site->get_dbid;
				if (grep /^$coid$/, @coids) { next; }
				push @coids, $coid;
				my $id = write_pazarid($coid,"CO");
				my $seqname = $site->get_name == 0 ? "" : $site->get_name;
				my $desc = $site->get_desc || qq{(no description provided)};
				$seqcounter++;
				$count++;
				my $rs_site = $site->get_seq;
				my $rs_chps = chopstr($rs_site,20);
				my $rs_shrt = substr($rs_site,0,10);
				my $rs_shrs = substr($rs_site,0,10);
				my $rs_leng = length($rs_site);
				my $rs_bgco = qq{style="background-color:$colors{$bg_color};"};
				$seqname = substr($seqname,0,8) . "..." if length($seqname) > 10;
				my $rs_checkb = qq{<input type="checkbox" name="seq$seqcounter" value="$rs_site">};
				$fasta.=">$id\n$rs_site\n";
				
				if ($rs_leng > 10) {
					$rs_leng = &pnum($rs_leng);
					$rs_shrt .= "... ($rs_leng&nbsp;bp)";
					$rs_shrs .= "...";
				}
				
				my $seq_reg = qq{<div class=""><div onclick="popup(this,'$rs_chps','st');" class="popup">$rs_shrt</div></div>};
				my $seq_sml = qq{<div class=""><div onclick="popup(this,'$rs_chps','st');" class="popup">$rs_shrs</div></div>};

				if (length($desc) > 28) {
					$desc =~ s/\'/\&\#39\;/g;
					$desc = qq{<div onclick="popup(this,'$desc','rt');" class="popup">} . substr($desc,0,26) . "..." . qq{</div>};
				}

				$bigrow .= qq{
					<tr class="construct" $rs_bgco >
						<td class="btc"><div>$rs_checkb</div></td>
						<td class="btc"><div>Artificial</div></td>
						<td class="btc"><div><div><a href="$pazar_cgi/seq_search.cgi?regid=$id&excluded=$excluded" class="b">$id</a></div>$seqname</div></td>
						<td class="btc"><div>-</div></td>
						<td class="btc">$seq_reg</td>
						<td class="btc"><div><div class="b">Description:</div>$desc</div></td>
						<td class="btc"><div>&nbsp;</div></td>
					</tr>};

				$smlrow .= qq{
					<tr class="construct" $rs_bgco >
						<td class="btc"><div>$rs_checkb</div></td>
						<td class="btc"><div>Artificial</div></td>
						<td class="btc"><div><a href="$pazar_cgi/seq_search.cgi?regid=$id&excluded=$excluded" class="b">$id</a></div></td>
						<td class="btc"><div>-</div></td>
						<td class="btc">$seq_sml</td>
						<td class="btc"><div>$desc</div></td>
						<td class="btc"><div>&nbsp;</div></td></tr>};
				
				$dh = 1;

			    }

			my $construct_name = $pazartfid . "_site" . $count;
			print TMP ">" . $construct_name . "\n";
			my $construct_seq = $site->get_seq;
			$construct_seq =~ s/N//ig;
			print TMP $construct_seq . "\n";
			$bg_color = 1 - $bg_color;
		    } #while complex->next_target
		my $showhide_1 = "show";
		my $showhide_2 = "hide";
		if ($count > 40) {
			$showhide_1 = "hide";
			$showhide_2 = "show";
		}
		$dc .= qq{
			<div class="tr p5bo">
				<span class="b">View</span> <input type="button" href="#$pazartfid" onClick="toggleRows('list$pazartfid','1','2');" value="more detail"> 
				<input type="button" href="#$pazartfid" onClick="toggleRows('list$pazartfid','2','2');" value="less detail">
			</div>
			<div id="desc$pazartfid\_$tf_projid" name="desc$pazartfid\_$tf_projid" class="seqTableDiv">
				<div id="1_list$pazartfid" class="$showhide_1">
					<table id="$pazartfid\_$tf_projid" class="evidencetableborder tblw">
						<tbody><tr>
							<td class="tfdst w30">&nbsp;</td>
							<td class="tfdst w70">Seq type</td>
							<td class="tfdst w80">Seq ID</td>
							<td class="tfdst">Target gene</td>
							<td class="tfdst w110">Sequence</td>
							<td class="tfdst w210">Sequence info</td>
							<td class="tfdst w90">Links</td>
						</tr>
						$bigrow
						</tbody>
					</table>
				</div>
				<div id="2_list$pazartfid" class="$showhide_2">
					<table id="sml$pazartfid\_$tf_projid" class="evidencetableborder tblw">
						<tbody><tr>
							<td class="tfdst w30">&nbsp;</td>
							<td class="tfdst w70">Seq type</td>
							<td class="tfdst w80">Seq ID</td>
							<td class="tfdst">Target gene</td>
							<td class="tfdst w110">Sequence</td>
							<td class="tfdst w210">Sequence info</td>
							<td class="tfdst w90">Links</td>
						</tr>
						$smlrow
					</tbody></table>
				</div>
			</div>};

		close(TMP);
# By default, 200 targets are returned if numresults argument is not given to the page. numresults is passed to all get_tfcomplex_by... methods. It can be used to set desired number of results, or 'all'.


# use the result param, or use limit of 200 (hardcoded into tf.pm methods) if no results param. If limit=='all', then we are already showing all and don't need the button
my $resultlimit = $numresults;
if (!defined $numresults)
{
	$resultlimit = 200;
}
		if ($count == $resultlimit) {
			$dc .= qq{
				<div class="emp">Too many sequences are linked to this TF. Only the first $count are reported.</div>
				<div class="p10 bg-lg">};
				}
			$dc .= qq{
					<div class="b p5bo"><form name="fasta$pazartfid\_$tf_projid" method="POST" action="$pazar_cgi/fasta_call.pl"><input type="submit" value="Download above sequences"><input type="hidden" name="fasta" value="$fasta"><input type="hidden" name="TFID" value="$pazartfid"></form></div>};

#if number of results < limit, or all specified -> do nothing if number of results = specified limit, there are probably more - display show all button
if ($count == $resultlimit)
{
 $dc .= qq{<div class="b p5bo"><form name="showallseqs\_$tf_projid" method="POST" action="$pazar_cgi/tf_search.cgi"><input type="submit" value="Show all sequences"> (could take a long time if there are many sequences)<input type="hidden" name="ID_list" value="PAZAR_TF"><input type="hidden" name="excluded" value="none"><input type="hidden" name="results" value="all"><input type="hidden" name="geneID" value="$pazartfid"></form></div>};

$dc .= qq{<div class="b p5bo"><form name="downloadallseqs\_$tf_projid" method="POST" action="$pazar_cgi/fasta_all.pl"><input type="submit" value="Download complete sequence set"><input type="hidden" name="ID_list" value="PAZAR_TF"><input type="hidden" name="excluded" value="none"><input type="hidden" name="results" value="all"><input type="hidden" name="geneID" value="$pazartfid"></form></div>}
}

#function init () {
#        var divs = document.getElementsByTagName("div");
#        for (i = 0; i < divs.length; i++) {
#                if (divs[i].className == "seqTableDiv") {
#                        baseName = divs[i].id;
#                        baseName = baseName.replace(/^desc/,"");
#                        try {
#                                ajaxcall(baseName,"memediv"+baseName, 1);
#                        }
#                        catch (err) {
#                                alert(err);
#                        }
#                }
#        }
#}

#upper limit (number of regseqs) for generating a meme profile
my $memelimit = 40;

			$dc .= qq{
					<div class="b p5bo">Generate a custom PFM and logo with selected sequences from $tf_name ($pazartfid)</div>
					<div class="p5bo">
						<span class="b">Select</span> <input type="button" name="selectall" id="selectall" value="all" onclick="selectallseq('$pazartfid\_$tf_projid');"> <input type="button" name="selecttype1" id="selecttype1" value="genomic sequences" onclick="selectbytype('$pazartfid\_$tf_projid','genomic');"> <input type="button" name="selecttype2" id="selecttype2" value="artificial sequences" onclick="selectbytype('$pazartfid\_$tf_projid','construct');"> <input type="button" name="resetall" id="resetall" value="reset" onclick="resetallseq('$pazartfid\_$tf_projid');"> <span class="b">then click</span> <input type="button" name="Regenerate PFM" value="Generate PFM" onclick="ajaxcall('$pazartfid\_$tf_projid','memediv$pazartfid\_$tf_projid');">
					</div>
					<div id="memediv$pazartfid\_$tf_projid">Too many sequences: Profiles are automatically generated for $memelimit or fewer sequenecs only.</div>
					<div class="p5to small b">Note: to generate a profile with sequences from multiple projects, use the &quot;Custom matrix&quot; tool at the bottom of the page.</div>
				</div>};

#generate meme profile automatically and display if number of regseqs <= limit
if($count <= $memelimit)
{

	$dc .= qq{
	<script language='javascript'>
	ajaxcall("$pazartfid\_$tf_projid","memediv$pazartfid\_$tf_projid",1);
	</script>
	};

}

=unneeded
		 else {
#either all sequences (less than or greater than 200) or results limited to a number other than 200
#display the button to show all if 
			$dc .= qq{
				<div class="p10 bg-lg">
					<div class="b p5bo"><form name="fasta$pazartfid\_$tf_projid" method="POST" action="$pazar_cgi/fasta_call.pl"><input type="submit" value="Download all sequences"><input type="hidden" name="fasta" value="$fasta"><input type="hidden" name="TFID" value="$pazartfid"></form></div>
					<div class="b p5bo">Generate a custom PFM and logo with selected sequences from $tf_name ($pazartfid)</div>
					<div class="p5bo">
						<span class="b">Select</span> <input type="button" name="selectall" id="selectall" value="all" onclick="selectallseq('$pazartfid\_$tf_projid');"> <input type="button" name="selecttype1" id="selecttype1" value="genomic sequences" onclick="selectbytype('$pazartfid\_$tf_projid','genomic');"> <input type="button" name="selecttype2" id="selecttype2" value="artificial sequences" onclick="selectbytype('$pazartfid\_$tf_projid','construct');"> <input type="button" name="resetall" id="resetall" value="reset" onclick="resetallseq('$pazartfid\_$tf_projid');"> <span class="b">then click</span> <input type="button" name="Regenerate PFM" value="Generate PFM" onclick="ajaxcall('$pazartfid\_$tf_projid','memediv$pazartfid\_$tf_projid');">
					</div>
					<div id="memediv$pazartfid\_$tf_projid">Not generated</div>
					<div class="p5to small b">Note: to generate a profile with sequences from multiple projects, use the &quot;Custom matrix&quot; tool at the bottom of the page.</div>
				</div>};
		}
=cut
		if ($dh == 1) {
			print $dp . $dc;
		} else {
			print $dp . qq{<div class="hide">$dc</div><div class="p10to"><div class="emp">There is no sequence data for this TF in this project.</div></div>};
		}
		print qq{</div></div>};
	}
	if ($tfcount == 0) {
		print qq{
			<div class="p10bo"><span class="b">Projects excluded from the search:</span> $excluded</div>
			<div class="emp">No annotation could be found for the transcription factor $accn. 
			Please do not hesitate to create your own project and enter information about this TF or any other TF.</div>};
			&exitscr();
	}
	print qq{
		<h2>Custom matrix</h2>
		<div class="p20lo">
			<div class="p10 bg-lg">
				<div class="p10bo">You can recalculate matrix and logo based on select sequences on this page. You can also combine multiple TFs. First, select your sequences using the checkboxes that appear to the left of the sequences. Then, click on the <span class="b">Generate PFM</span> button. <input type="button" value="Generate PFM" onclick="multiTF('allSeqPFM');"></div>
				<div id="allSeqPFM" name="allSeqPFM"><div class="emp">No matrix built yet.</div></div>
			</div>
		</div>};
}
print qq{</div>};

sub exitscr {}

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

my $tail = HTML::Template->new(filename => "tail.tmpl");
print $tail->output;

exit;
