#!/usr/bin/perl

use pazar;
use pazar::talk;
use pazar::reg_seq;
use HTML::Template;
use TFBS::Matrix::PFM;
use pazar::tf::subunit;
use pazar::tf::tfcomplex;
use TFBS::PatternGen::MEME;
use CGI qw(:standard);
use CGI::Carp qw(fatalsToBrowser);

# use CGI::Debug(report => "everything", on => "anything");

my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};
my $pazarhtdocspath = $ENV{PAZARHTDOCSPATH};

require "$pazarcgipath/getsession.pl";
my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");
$template->param(TITLE => "Project view | PAZAR");
$template->param(ONLOAD_FUNCTION => "init();");
$template->param(JAVASCRIPT_FUNCTION => q{ });
$template->param(PAZAR_HTML => $pazar_html);
$template->param(PAZAR_CGI => $pazar_cgi);

if ($loggedin eq "true") {
	$template->param(LOGOUT => qq{<span class="b">You are signed in as $info{first} $info{last}.</span> <a href="$pazar_cgi/logout.pl" class="b">Sign out</a>});
} else {
	$template->param(LOGOUT => qq{<a href="$pazar_cgi/login.pl"><span class="b">Sign in</span></a>});
}

print qq{Content-Type: text/html\n\n}, $template->output;

my $get = new CGI;
my %param = %{$get->Vars};
foreach my $item (keys %param) {
	my @vals;
	foreach my $val ($get->param($item)) {
		push @vals, $val;
	}
	$param{$item}=join(";",@vals);
}

my $proj = $param{project_name};

my $dbh0 = pazar->new( 
	-host         => $ENV{PAZAR_host},
	-user         => $ENV{PAZAR_pubuser},
	-pass         => $ENV{PAZAR_pubpass},
	-dbname       => $ENV{PAZAR_name},
	-drv          => $ENV{PAZAR_drv},
	-globalsearch => "yes");

my $stat = &select($dbh0, qq{SELECT status FROM project WHERE project_name="$proj"});
my $status = $stat->fetchrow_array;

my $dbh;
if ($status =~ /open/i || $status =~ /published/i) {
	$dbh = pazar->new( 
		-host    => $ENV{PAZAR_host},
		-user    => $ENV{PAZAR_pubuser},
		-pass    => $ENV{PAZAR_pubpass},
		-dbname  => $ENV{PAZAR_name},
		-drv     => $ENV{PAZAR_drv},
		-project => $proj);
} elsif ($status=~/restricted/i) {
	$dbh = pazar->new( 
		-host       => $ENV{PAZAR_host},
		-user       => $ENV{PAZAR_pubuser},
		-pass       => $ENV{PAZAR_pubpass},
		-pazar_user => $info{user},
		-pazar_pass => $info{pass},
		-dbname     => $ENV{PAZAR_name},
		-drv        => $ENV{PAZAR_drv},
		-project    => $proj);
}

our $ensdb = pazar::talk->new(
	DB => "ensembl",
	USER => $ENV{ENS_USER},
	PASS => $ENV{ENS_PASS},
	HOST => $ENV{ENS_HOST},
	DRV => "mysql");

my $projid = $dbh->get_projectid();
my $qytype = $param{submit};
print qq{<h1><a href="$pazar_cgi/project.pl?project_name=$proj">$proj</a> project in $qytype</h1>};
my $modfil = qq{
		<div class="float-r">
			<form name="modify_filters" method="post" action="$pazar_cgi/project.pl" enctype="multipart/form-data" target="_self"><input type="hidden" name="project_name" value="$proj"><input type="submit" name="submit" value="Modify filters"></form>
		</div>};
if ($param{submit} =~ /gene/i) {
	my @reg_seqs;
	undef(my @filters);
	if ($param{species_filter} eq "on") {
		if (!$param{species}) {
			print qq{<div class="emp">You need to select one or more species when using the species filter.</div>};
		}
		my @species = split(/;/,$param{species});
		if (!grep(/Species\:/, @filters)) {
			my $filter = qq{Species: <span class="b">} . join(", ", @species) . qq{</span>};
			push @filters, $filter;
		}
		unless ($param{region_filter} eq "on") {
			foreach my $sp (@species) {
				my @seqs = pazar::reg_seq::get_reg_seq_by_species($dbh,$sp);
				foreach my $regseq (@seqs) {
					push @reg_seqs, $regseq;
				}
			}
			if (!$reg_seqs[0]) {
				print qq{<div class="emp">No regulatory sequence was found for species: } . join(", ", @species) . qq{</div>};
			}
		} else {
			if (scalar(@species)>1) {
				print qq{<div class="emp">You have to choose a unique species when using the region filter.</div>};
			}
			if ($param{chr_filter} eq "on") {
				unless ($param{bp_filter} eq "on") {
					@reg_seqs = pazar::reg_seq::get_reg_seq_by_chromosome($dbh,$param{chromosome},$param{species});
					if (!grep(/Chromosome\:/, @filters)) {
						my $filter = qq{Chromosome: <span class="b">} . $param{chromosome} . qq{</span>};
						push @filters, $filter;
					}
					if (!$reg_seqs[0]) {
						print qq{<div class="emp">There are no regulatory sequence was found on chromosome $param{chromosome} in species $param{species}.</div>};
					}
				} else {
					if (!$param{bp_start} || !$param{bp_end}) {
						print qq{<div class="emp">You need to specify the start and end of the region you're interested in when using the base pair filter.</div>};
					}
					if ($param{bp_start} >= $param{bp_end}) {
						print qq{<div class="emp">The start coordinate needs to be lower that the end.</div>};
					}
					if (!grep(/region filter/, @filters)) {
						my $filter = "region filter: " . $param{chromosome} . ":" . $param{bp_start} ."-" . $param{bp_end};
						push @filters, $filter;
					}
					@reg_seqs = pazar::reg_seq::get_reg_seq_by_region($dbh,$param{bp_start},$param{bp_end},$param{chromosome},$param{species});
					if (!$reg_seqs[0]) {
						print qq{<div class="emp">No regulatory sequence was found between bp $param{bp_start} and $param{bp_end} on chromosome $param{chromosome} in species $param{species}.</div>};
					}
				}
			}
		}
	} else {
		if ($param{region_filter} eq "on") {
			print qq{<div class="emp">You have to select a species if you want to use the region filter.</div>};
		}
	}
	if ($param{gene_filter} eq "on") {
		if ($reg_seqs[0]) {
			print qq{<div class="emp">You cannot use species and region filters when using the gene filter.</div>};
		}
		if (!$param{gene}) {
			print qq{<div class="emp">You need to select one or more gene when using the gene filter.</div>};
		}
		my @genes = split(/;/,$param{gene});
		if (!grep(/Gene\:/, @filters)) {
			my $filter = qq{Gene: <span class="b">} . join(", ", @genes) . qq{</span>};
			push @filters, $filter;
		}
		foreach my $accn (@genes) {
			my @seqs = pazar::reg_seq::get_reg_seqs_by_accn($dbh,$accn);
			foreach my $regseq (@seqs) {
				push @reg_seqs, $regseq;
			}
		}
		if (!$reg_seqs[0]) {
			print qq{<div class="emp">No regulatory sequence was found for the genes } . join(", ", @genes) . qq{.</div>};
		}
	}
	if (!$reg_seqs[0]) {
		my @rsid = $dbh->get_all_regseq_ids();
		foreach my $id (@rsid) {
			my @seqs = pazar::reg_seq::get_reg_seq_by_regseq_id($dbh,$id);
			foreach my $regseq (@seqs) {
				push @reg_seqs, $regseq;
			}
		}
	}
	if (!$reg_seqs[0]) {
		print qq{<div class="emp">No regulatory sequence was found in this project.</div>};
	}
	my $res = 0;
	my $filt = 0;
	my @sorted_regseqs = sort {$a->gene_accession cmp $b->gene_accession} @reg_seqs;
	my $prev_gene_accn;
	my $display_counter = 0;
	my $bg_color = 0;
	my %colors = (
		0 => "#fffff0",
		1 => "#BDE0DC"
	);
	foreach my $regseq (@sorted_regseqs) {
		if (($param{length_filter} eq "on") and ($param{length} ne "0")) {
			if (!$param{length} || $param{length} <= 0) {
				print qq{<div class="emp">You need to specify a length greater than 0 when using the length filter.</div>};
			}
			if (!grep(/Length\:/, @filters)) {
				my $filter = qq{Length: <span class="b">} . $param{shorter_larger} . " " . $param{length} . qq{ bases</span>};
				push @filters, $filter;
			}
			my $length = $regseq->end - $regseq->start +1;
			if ($param{shorter_larger} eq "equal_to") {
				unless ($length == $param{length}) {
					my $filter = next;
				}
			}
			if ($param{shorter_larger} eq "greater_than") {
				unless ($length >= $param{length}) {
					next;
				}
			}
			if ($param{shorter_larger} eq "less_than") {
				unless ($length <= $param{length}) {
					next;
				}
			}
		}
		my @inters;
		my @interactors = $dbh->get_interacting_factor_by_regseq_id($regseq->accession_number);
		my $datalinks = 0;
		if (!@interactors) {
			unless (
				($param{tf_filter} eq "on") || 
				($param{class_filter} eq "on") || 
				($param{interaction_filter} eq "on") || 
				($param{evidence_filter} eq "on") || 
				($param{method_filter} eq "on")) {
				$datalinks++;
			}
		}
		foreach my $inter (@interactors) {
			if ($param{tf_filter} eq "on") {
				if (!$param{tf}) {
					print qq{<div class="emp">You need to select one or more TF when using the TF filter.</div>};
				}
				my @tfs = split(/;/,$param{tf});
				if (!grep(/TF filter/, @filters)) {
					my $filter = "TF filter: " . join(", ", @tfs);
					push @filters, $filter;
				}
				my $tf_name = $dbh->get_complex_name_by_id($inter->{tfcomplex});
				unless (grep(/^$tf_name$/,@tfs)) {
					next;
				}
			}
			if ($param{class_filter} eq "on") {
				my $tf = $dbh->create_tf;
				my $complex = $tf->get_tfcomplex_by_id($inter->{tfcomplex}, "notargets");
				my $found = 0;
				my $cf;
				if (!grep(/TF class filter/, @filters)) {
					my $filter = "TF class filter: " . $param{class};
					push @filters, $filter;
				}
				while (my $subunit = $complex->next_subunit) {
					if (($subunit->get_class) and ($subunit->get_fam)) {
						$cf = $subunit->get_class . "/" . $subunit->get_fam;
					} elsif ($subunit->get_class && !$subunit->get_fam) {
						$cf = $subunit->get_class;
					}
					if ($param{class} == $cf) {
						$found = 1;
					}
				}
				if ($found == 0) {
					next;
				}
			}
			if ($param{interaction_filter} eq "on") {
				my ($table,$pazarid,@dat) = $dbh->links_to_data($inter->{olink}, "output");
				my $qual = lc($dat[0]);
				my $match = 0;
				if (!grep(/interaction filter/, @filters)) {
					my $filter;
					if ($param{interaction} eq "none") {
						$filter = "interaction filter: null";
					} else {
						$filter = "interaction filter: " . $param{interaction};
					}
					push @filters, $filter;
				}
				my @notnull = ("good","poor","marginal","saturation");
				if ($qual eq $param{interaction}) {
					$match = 1;
				} elsif (($param{interaction} eq "not_null") and (grep(/$qual/,@notnull))) {
					$match = 1;
				} elsif (($param{interaction} ne "none") and ($dat[1]>0)) {
					$match = 1;
				} elsif (($param{interaction} eq "none") and (!grep(/$qual/,@notnull) && $dat[1]==0)) {
					$match = 1;
				}
				if ($match == 0) {
					next;
				}
			}
			if ($param{evidence_filter} eq "on") {
				if (!$param{evidence}) {
					print qq{<div class="emp">You need to select one or more evidence type when using the evidence filter.</div>};
				}
				my $evidu = uc($param{evidence});
				my @evids = split(/;/,$evidu);
				if (!grep(/Evidence\:/, @filters)) {
					my $filter = qq{Evidence: <span class="b">} . join(", ", @evids) . qq{</span>};
					push @filters, $filter;
				}
				my ($evid,@res) = $dbh->get_evidence_by_analysis_id($inter->{aid});
				$evid = uc($evid);
				unless (grep(/^$evid$/,@evids)) {
					next;
				}
			}
			if ($param{method_filter} eq "on") {
				if (!$param{method}) {
					print qq{<div class="emp">You need to select one or more method type when using the method filter.</div>};
				}
				my @mets = split(/;/,$param{method});
				if (!grep(/method filter/, @filters)) {
					my $filter = "method filter: " . join(", ", @mets);
					push @filters, $filter;
				}
				my ($met,@res) = $dbh->get_method_by_analysis_id($inter->{aid});
				unless (grep(/^$met$/,@mets)) {
					next;
				}
			}
			push @inters, $inter;
		}
		my @exprs;
		my @expressors = $dbh->get_expression_by_regseq_id($regseq->accession_number);
		if (!@expressors) {
			unless (($param{expression_filter} eq "on") or ($param{evidence_filter} eq "on") or ($param{method_filter} eq "on")) {
				$datalinks++;
			}
		}
		foreach my $expr (@expressors) {
			if ($param{expression_filter} eq "on") {
				my ($table,$pazarid,@dat) = $dbh->links_to_data($expr->{olink},"output");
				my $qual = lc($dat[0]);
				my $match = 0;
				if (!grep(/Expression\:/, @filters)) {
					my $filter = qq{Expression: <span class="b">} . $param{expression} . qq{</span>};
					push @filters, $filter;
				}
				my @change = ("highly induced","induced","repressed","strongly repressed");
				my @induce = ("highly induced","induced","change");
				my @repress = ("repressed","strongly repressed","change");
				if ($qual eq $param{expression}) {
					$match = 1;
				} elsif ($param{expression} eq "change" && grep(/$qual/,@change)) {
					$match = 1;
				} elsif (grep(/^$param{expression}$/,@induce) && $dat[1]>0) {
					$match = 1;
				} elsif (grep(/^$param{expression}$/,@repress) && $dat[1]<0) {
					$match = 1;
				}
				if ($match == 0) {
					next;
				}
			}
			if ($param{evidence_filter} eq "on") {
				if (!$param{evidence}) {
					print qq{<div class="emp">You need to select one or more evidence type when using the evidence filter.</div>};
				}
				my $evidu = uc($param{evidence});
				my @evids = split(/;/,$evidu);
				if (!grep(/Evidence\:/, @filters)) {
					my $filter = qq{Evidence: <span class="b">} . join(", ", @evids) . qq{</span>};
					push @filters, $filter;
				}
				my ($evid,@res) = $dbh->get_evidence_by_analysis_id($expr->{aid});
				$evid = uc($evid);
				unless (grep(/^$evid$/,@evids)) {
					next;
				}
			}
			if ($param{method_filter} eq "on") {
				if (!$param{method}) {
					print qq{<div class="emp">You need to select one or more method type when using the method filter.</div>};
				}
				my @mets = split(/;/, $param{method});
				if (!grep(/method filter/, @filters)) {
					my $filter = "method filter: " . join(", ", @mets);
					push @filters, $filter;
				}
				my ($met,@res) = $dbh->get_method_by_analysis_id($expr->{aid});
				unless (grep(/^$met$/,@mets)) {
					next;
				}
			}
			push @exprs, $expr;
		}
		if (!@filters) {
			push @filters, "none";
		}
		if ($res == 0) {
			$res = 1;
			print qq{<div class="p10 bg-lg">$modfil<div class="b">Selected filters</div>} . join("<br>", @filters) . qq{</div>};
			print qq{
				<h2>Gene-by-gene details</h2>
				<div class="small b">Note: a red asterisk <span class="warning">*</span> indicates that the gene is a marker located in the vicinity of the regulatory region. It has not been shown to be regulated by the described sequence.</div>};
		}
		if (($exprs[0]) or ($inters[0]) or ($datalinks == 2)) {
			$filt = 1;
			my $gene_accn = $regseq->gene_accession;
			my $gene_desc = $regseq->gene_description || "";
			my $lcsp = lc($regseq->binomial_species);
			my $gene_sp = ucfirst($lcsp);
			my $ensspecies = $gene_sp;
			$ensspecies =~ s/ /_/g;
			my $gidprefix = "GS";
			my $asterisk = "";
			my $genetype = $regseq->gene_type;
			if ($genetype eq "marker") {
				$gidprefix = "MK";
				$asterisk = qq{<span class="warning">*</span>};
			}
			my $pazargeneid = write_pazarid($regseq->PAZAR_gene_ID,$gidprefix);
			if ($gene_accn ne $prev_gene_accn) {
				if ($prev_gene_accn) {
					print "</table></div>";
				}
				$bg_color = 0;
				my @ens_coords = $ensdb->get_ens_chr($gene_accn);
				$ens_coords[5] =~ s/\[.*\]//g;
				$ens_coords[5] =~ s/\(.*\)//g;
				$ens_coords[5] =~ s/\.//g;
				my $geneDescription = $ens_coords[5] || "-";
				print qq{
					<h3><div class="float-r"><a href="#top" class="ns">back to top</a></div><a href="$pazar_cgi/gene_search.cgi?geneID=$pazargeneid&amp;ID_list=PAZAR_gene">$gene_desc</a>$asterisk in the <a href="$pazar_cgi/project.pl?project_name=$proj">$proj</a> project<div class="clear-l"></div></h3>
					<div class="p20lo p40bo">
						<div class="p5bo">
							<div>Species: <span class="b">$gene_sp</span></div>
							<div>PAZAR gene ID: <a class="b" href="$pazar_cgi/gene_search.cgi?geneID=$pazargeneid&amp;ID_list=PAZAR_gene">$pazargeneid</a></div>
							<div>Ensembl gene ID: <a class="b" href="http://www.ensembl.org/$ensspecies/geneview?gene=$gene_accn">$gene_accn</a></div>
							<div>Ensembl gene description: <span class="b">$geneDescription</span></div>
						</div>
						<table class="searchtable tblw"><tbody>
							<tr>
								<td class="gdtc w80">Regseq ID</td>
								<td class="gdtc w110">Seq name</td>
								<td class="gdtc">Sequence</td>
								<td class="gdtc w200">Coordinates</td>
								<td class="gdtc w90">Links</td>
							</tr>};
				$prev_gene_accn = $gene_accn;
			}
			&print_gene_attr($regseq,\%colors,$bg_color,$display_counter);
			$display_counter++;
			$bg_color = 1 - $bg_color;
		}
	}
	if (!@filters) {
		push @filters, "none";
	}
	if ($filt == 1) {
		print qq{</tbody></table>};
	}
	if (($res == 1) and ($filt == 0)) {
		print qq{<div class="emp">No regulatory sequence was found using this set of filters.</div>};
	}
	if ($res == 0) {
		print qq{<div class="p10 bg-lg">$modfil<div class="b">Selected filters</div>} . join("<br>", @filters) . qq{</div>};
		print qq{<div class="emp">No regulatory sequence was found using this set of filters.</div>};
	}
} elsif ($param{submit} =~ /tf/i) {
	my @complexes;
	undef(my @filters);
	if ($param{tf_filter} eq "on") {
		if (!$param{tf}) {
			print qq{<div class="emp">You need to select one or more TF when using the TF filter.</div>};
		}
		my @tfs = split(/;/,$param{tf});
		if (!grep(/TF filter/, @filters)) {
			my $filter = "TF filter: " . join(", ", @tfs);
			push @filters, $filter;
		}
		foreach my $tf (@tfs) {
			my $complex = $dbh->create_tf;
			my @tfcomplex = $complex->get_tfcomplex_by_name($tf);
			foreach my $tfcomplex (@tfcomplex) {
				push @complexes, $tfcomplex;
			}
		}
		if (!$complexes[0]) {
			print qq{<div class="emp">No TF was found with the following names: } . join(", ", @tfs) . qq{.</div>};
		}
	}
	if ($param{class_filter} eq "on") {
		if ($complexes[0]) {
			print qq{<div class="emp">You cannot use the TF filter and TF class filter at the same time.</div>};
		}
		my @cf = split(/\//,$param{classes});
		my $tf = $dbh->create_tf;
		my @tfcomplex = $tf->get_tfcomplex_by_class($cf[0]);
		foreach my $tfcomplex (@tfcomplex) {
			push @complexes, $tfcomplex;
		}
		if (!grep(/TF class filter/, @filters)) {
			my $filter = "TF class filter: " . $param{classes};
			push @filters, $filter;
		}
		if (!$complexes[0]) {
			print qq{<div class="emp">No TF was found within the following class: $cf[0].</div>};
		}
	}
	if ($param{species_filter} eq "on") {
		if (!$param{species}) {
			print qq{<div class="emp">You need to select one or more species when using the species filter.</div>};
		}
		my @species = split(/;/,$param{species});
		if (!grep(/Species\:/, @filters)) {
			my $filter = qq{Species: <span class="b">} . join(", ", @species) . qq{</span>};
			push @filters, $filter;
		}
		my @funct_tfs = $dbh->get_all_complex_ids($projid);
		my @tfs;
		foreach my $funct_tf (@funct_tfs) {
			my $funct_name = $dbh->get_complex_name_by_id($funct_tf);
			my $tf = $dbh->create_tf;
			my $tfcomplex = $tf->get_tfcomplex_by_id($funct_tf,"notargets");
			while (my $subunit = $tfcomplex->next_subunit) {
				my $trans = $subunit->get_transcript_accession($dbh);
				my $gene = $ensdb->ens_transcr_to_gene($trans);
				my $species = $ensdb->current_org();
				if (!grep(/^$species$/i,@species)) {
					next;
				} else {
					if (!grep(/^$funct_name$/,@tfs)) {
						push @tfs,$funct_name;
					}
				}
			}
		}
		if (!$complexes[0]) {
			foreach my $tf (@tfs) {
				my $complex = $dbh->create_tf;
				my @tfcomplex = $complex->get_tfcomplex_by_name($tf);
				foreach my $tfcomplex (@tfcomplex) {
					push @complexes, $tfcomplex;
				}
			}
			if (!$complexes[0]) {
				print qq{<div class="emp">No TF was found from the following species: } . join(", ", @species) . qq{</div>};
			}
		} else {
			my @comp = @complexes;
			undef (@complexes);
			foreach my $tf (@comp) {
				my $name=$tf->name;
				if (grep(/^$name$/,@tfs)) {
					push @complexes, $tf;
				}
			}
			if (!$complexes[0]) {
				print qq{<div class="p10 bg-lg">$modfil<div class="b">Selected filters</div>} . join("<br>", @filters) . qq{</div>};
				print qq{<div class="emp">No TF was found in this project using this set of filters.</div>};
			}
		}
	}
	if (!$complexes[0]) {
		my @funct_tfs = $dbh->get_all_complex_ids($projid);
		my @tfs;
		foreach my $funct_tf (@funct_tfs) {
			my $tf = $dbh->create_tf;
			my $tfcomplex = $tf->get_tfcomplex_by_id($funct_tf);
			push @complexes, $tfcomplex;
		}
	}
	if (!$complexes[0]) {
		print qq{<div class="emp">No TF was found in this project.</div>};
	}
	my @reg_seqs;
	if ($param{species_filter} eq "on") {
		my @species = split(/;/,$param{species});
		if (!grep(/Species\:/, @filters)) {
			my $filter = qq{Species: <span class="b">} . join(", ", @species) . qq{</span>};
			push @filters, $filter;
		}
		unless ($param{region_filter} eq "on") {
			foreach my $sp (@species) {
				my @seqs = pazar::reg_seq::get_reg_seq_by_species($dbh,$sp);
				foreach my $regseq (@seqs) {
					push @reg_seqs, $regseq->accession_number;
				}
			}
		} else {
			if (scalar(@species)>1) {
				print qq{<div class="emp">You have to choose a unique species when using the region filter.</div>};
			}
			if ($param{chr_filter} eq "on") {
				unless ($param{bp_filter} eq "on") {
					my @seqs = pazar::reg_seq::get_reg_seq_by_chromosome($dbh,$param{chromosome},$param{species});
					foreach my $regseq (@seqs) {
						push @reg_seqs, $regseq->accession_number;
					}
					if (!grep(/Chromosome\:/, @filters)) {
						my $filter = qq{Chromosome: <span class="b">} . $param{chromosome} . qq{</span>};
						push @filters, $filter;
					}
					if (!$reg_seqs[0]) {
						print qq{<div class="emp">No regulatory sequence was found on chromosome $param{chromosome} in species $param{species}.</div>};
					}
				} else {
					if (!$param{bp_start} || !$param{bp_end}) {
						print qq{<div class="emp">You need to specify the start and end of the region you're interested in when using the base pair filter.</div>};
					}
					if ($param{bp_start} >= $param{bp_end}) {
						print qq{<div class="emp">The start coordinate needs to be lower that the end.</div>};
					}
					if (!grep(/region filter/, @filters)) {
						my $filter = "region filter: " . $param{chromosome} . ":" . $param{bp_start} . "-" . $param{bp_end};
						push @filters, $filter;
					}
					my @seqs = pazar::reg_seq::get_reg_seq_by_region($dbh,$param{bp_start},$param{bp_end},$param{chromosome},$param{species});
					foreach my $regseq (@seqs) {
						push @reg_seqs, $regseq->accession_number;
					}
					if (!$reg_seqs[0]) {
						print qq{<div class="emp">No regulatory sequence was found between bp $param{bp_start} and $param{bp_end} on chromosome $param{chromosome} in species $param{species}.</div>};
					}
				}
			}
		}
	} else {
		if ($param{region_filter} eq "on") {
			print qq{<div class="emp">You have to select a species if you want to use the region filter.</div>};
		}
	}
	if ($param{gene_filter} eq "on") {
		if ($param{species_filter} eq "on") {
			print qq{<div class="emp">You cannot use species and region filters when using the gene filter.</div>};
		}
		if (!$param{gene}) {
			print qq{<div class="emp">You need to select one or more gene when using the gene filter.</div>};
		}
		my @genes = split(/;/,$param{gene});
		if (!grep(/Gene\:/, @filters)) {
			my $filter = qq{Gene: <span class="b">} . join(", ", @genes) . qq{</span>};
			push @filters, $filter;
		}
		foreach my $accn (@genes) {
			my @seqs = pazar::reg_seq::get_reg_seqs_by_accn($dbh,$accn);
			foreach my $regseq (@seqs) {
				push @reg_seqs, $regseq->accession_number;
			}
		}
		if (!$reg_seqs[0]) {
			print qq{<div class="emp">No regulatory sequence was found for the genes } . join(", ", @genes) . qq{.</div>};
		}
	}
	my $res = 0;
	my %inters;
	foreach my $tf (@complexes) {
		my $tfname = $tf->name;
		while (my $site = $tf->next_target) {
			my $type = $site->get_type;
			if ($type eq "matrix") {
				next;
			}
			if ($type eq "reg_seq") {
				my @regseq = pazar::reg_seq::get_reg_seq_by_regseq_id($dbh,$site->get_dbid);
				my $rsid = $regseq[0]->accession_number;
				if ($reg_seqs[0]) {
					unless (grep(/^$rsid$/,@reg_seqs)) {
						next;
					}
				}
				if (($param{length_filter} eq "on") and ($param{length} ne "0")) {
					if ((!$param{length}) or ($param{length} <= 0)) {
						print qq{<div class="emp">You need to specify a length greater than 0 when using the length filter.</div>};
					}
					if (!grep(/Length\:/, @filters)) {
						my $filter = qq{Length: <span class="b">} . $param{shorter_larger} . " " . $param{length} . qq{ bases</span>};
						push @filters, $filter;
					}
					my $length = $regseq[0]->end - $regseq[0]->start +1;
					if ($param{shorter_larger} eq "equal_to") {
						unless ($length == $param{length}) {
							my $filter = next;
						}
					}
					if ($param{shorter_larger} eq "greater_than") {
						unless ($length >= $param{length}) {
							next;
						}
					}
					if ($param{shorter_larger} eq "less_than") {
						unless ($length <= $param{length}) {
							next;
						}
					}
				}
			}
			if ($type eq "construct" || $type eq "reg_seq") {
				if ($param{interaction_filter} eq "on") {
					my ($table,$pazarid,@dat) = $dbh->links_to_data($site->get_olink,"output");
					unless ($table eq "interaction") {
						next;
					}
					my $qual = lc($dat[0]);
					my $match = 0;
					if (!grep(/interaction filter/, @filters)) {
						my $filter;
						if ($param{interaction} eq "none") {
							$filter = "interaction filter: null";
						} else {
							$filter = "interaction filter: " . $param{interaction};
						}
						push @filters, $filter;
					}
					my @notnull = ("good","poor","marginal","saturation");
					if ($qual eq $param{interaction}) {
						$match = 1;
					} elsif (($param{interaction} eq "not_null") and (grep(/$qual/,@notnull))) {
						$match = 1;
					} elsif ($param{interaction} ne "none" && $dat[1]>0) {
						$match = 1;
					} elsif ($param{interaction} eq "none" && !grep(/$qual/,@notnull) && $dat[1]==0) {
						$match = 1;
					}
					if ($match == 0) {
						next;
					}
				}
				if ($param{evidence_filter} eq "on") {
					if (!$param{evidence}) {
						print qq{<div class="emp">You need to select one or more evidence type when using the evidence filter.</div>};
					}
					my $evidu = uc($param{evidence});
					my @evids = split(/;/, $evidu);
					if (!grep(/Evidence\:/, @filters)) {
						my $filter = qq{Evidence: <span class="b">} . join(", ", @evids) . qq{</span>};
						push @filters, $filter;
					}
					my ($evid,@res) = $dbh->get_evidence_by_analysis_id($site->get_analysis);
					$evid = uc($evid);
					unless (grep(/^$evid$/,@evids)) {
						next;
					}
				}
				if ($param{method_filter} eq "on") {
					if (!$param{method}) {
						print qq{<div class="emp">You need to select one or more method type when using the method filter.</div>};
					}
					my @mets = split(/;/,$param{method});
					if (!grep(/method filter/, @filters)) {
						my $filter = "method filter: " . join(", ", @mets);
						push @filters, $filter;
					}
					my ($met,@res) = $dbh->get_method_by_analysis_id($site->get_analysis);
					unless (grep(/^$met$/,@mets)) {
						next;
					}
				}
			}
			push (@{$inters{$tfname}},{
				dbid => $site->get_dbid,
				ilink => $site->get_ilink,
				olink => $site->get_olink,
				aid => $site->get_analysis});
			$res = 1;
		}
	}
	if (!@filters) {
		push @filters, "none";
	}
	if ($res == 0) {
		print qq{<div class="p10 bg-lg">$modfil<div class="b">Selected filters</div>} . join("<br>", @filters) . qq{</div>};
		print qq{<div class="emp">No regulatory sequence and (or) TF was found using this set of filters.</div>};
	} else {
		print qq{<div class="p10 bg-lg">$modfil<div class="b">Selected filters</div>} . join("<br>", @filters) . qq{</div>};
		print qq{
			<h2>TF-by-TF details</h2>
			<div class="small b">A red asterisk <span class='warning'>*</span> indicates that the gene is a marker located in the vicinity of the regulatory region. It has not been shown to be regulated by the described sequence.</div>};
		my $seqcounter = 0;
		foreach my $tf (keys %inters) {
			$seqcounter = &print_tf_attr($dbh,$tf,\@{$inters{$tf}},$seqcounter);
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
}

my $temptail = HTML::Template->new(filename => "$pazarcgipath/tail.tmpl");
print $temptail->output;

sub print_gene_attr {
	my ($regseq,$colors,$bg_color,$regseq_counter) = @_;
	my $rs_accnum = $regseq->accession_number;
	my $rs_binosp = $regseq->binomial_species;
	my $rs_dbasse = $regseq->seq_dbassembly;
	my $rs_dbname = $regseq->seq_dbname;
	my $rs_chromo = $regseq->chromosome;
	my $rs_strand = $regseq->strand;
	my $rs_startp = $regseq->start;
	my $rs_breakp = $regseq->end;
	my $id = write_pazarid($rs_accnum,"RS");
	my $seqname = $regseq->id || "-";
	my %colors = %{$colors};
	
	my $rs_fstart = &pnum($rs_startp);
	my $rs_fbreak = &pnum($rs_breakp);
	my $rs_fstran = $rs_strand;
	$rs_fstran = "&ndash;" if $rs_fstran eq "-";
	
	my $seqseq = $regseq->seq;
	my $seqlen = length($seqseq);
	my $seqstr = chopstr($seqseq, 20);
	my $rs_set = substr($seqstr,0,10);
	$rs_chstrnd = "&ndash;" if $rs_chstrnd eq "-";
	if ($seqlen > 10) {
		$seqlen = &pnum($seqlen);
		$rs_set .= "... ($seqlen&nbsp;bp)";
	}
	$seqstr = qq{<div class=""><div onclick="popup(this,'$seqstr','st');" class="popup">$rs_set</div></div>};

	print qq{
		<tr style="background-color: $colors{$bg_color};">
			<td class="btc"><a href="$pazar_cgi/seq_search.cgi?regid=$rs_accnum" class="b">$id</a></td>
			<td class="btc">$seqname</td>
			<td class="btc"><div>$seqstr</div></td>
			<td class="btc">
				chr$rs_chromo:$rs_fstart-$rs_fbreak ($rs_fstran)
				<div class="small">[$rs_dbname $rs_dbasse]</div>
			</td>
			<td class="btc">
				<div class="p2to">
					<form name="display$regseq_counter" method="post" action="$pazar_cgi/gff_custom_track.cgi" enctype="multipart/form-data" target="_blank">
						<input type="hidden" name="chr" value="$rs_chromo">
						<input type="hidden" name="start" value="$rs_startp">
						<input type="hidden" name="end" value="$rs_breakp">
						<input type="hidden" name="species" value="$rs_binosp">
						<input type="hidden" name="resource" value="ucsc">
						<a href='#' onClick="javascript:document.display$regseq_counter.resource.value='ucsc'; document.display$regseq_counter.submit();"><img src="$pazar_html/images/ucsc_logo.png" alt="Go to UCSC Genome Browser"></a> <a href='#' onClick="javascript:document.display$regseq_counter.resource.value='ensembl'; document.display$regseq_counter.submit();"><img src="$pazar_html/images/ensembl_logo.gif" alt="Go to Ensembl Genome Browser"></a>
					</form>
				</div>
			</td>
		</tr>};
}

sub print_tf_attr {
	my ($dbh,$tfname,$target,$seqcounter) = @_;
	my $tf = $dbh->create_tf;
	my @tfcomplexes = $tf->get_tfcomplex_by_name($tfname);
	foreach my $complex (@tfcomplexes) {
		my $bg_color = 0;
		my %colors = (0 => "#fffff0",
		              1 => "#FFB5AF");
		my $count = 0;
		my $pazartfid = write_pazarid($complex->dbid,"TF");
		my $file = "$pazarhtdocspath/tmp/$pazartfid.fa";
		open (TMP, ">$file");
		my @classes = ();
		my @families = ();
		my @transcript_accessions = ();
		my $species;
		while (my $subunit = $complex->next_subunit) {
			my $class = !$subunit->get_class?'-':$subunit->get_class;
			my $fam = !$subunit->get_fam?'-':$subunit->get_fam;
			push(@classes,$class);
			push(@families,$fam);
			my $tr_accn = $subunit->get_transcript_accession($dbh);
			unless ($species) {
				my @ens_coords = $ensdb->get_ens_chr($tr_accn);
				$ens_coords[5] =~ s/\[.*\]//g;
				$ens_coords[5] =~ s/\(.*\)//g;
				$ens_coords[5] =~ s/\.//g;
				$species = $ensdb->current_org();
				$species = ucfirst($species);
			}
			my $ensspecies = $species;
			$ensspecies =~ s/ /_/g;
			my $link_tr_accn = qq{<a href="http://www.ensembl.org/$ensspecies/geneview?gene=$tr_accn" target="_blank">$tr_accn</a>};
			push(@transcript_accessions,$link_tr_accn);
	
		}
		unless ($species) {
			$species = "-";
		}
		my $traccns = join("<br>",@transcript_accessions);
		my $trclasses = join("<br>",@classes);
		my $trfams = join("<br>",@families);
		print qq{
			<h3><div class="float-r"><a href="#top" class="ns">back to top</a></div><a href="$pazar_cgi/tf_search.cgi?geneID=$pazartfid">$tfname</a> in the <a href="$pazar_cgi/project.pl?project_name=$proj">$proj</a> project<div class="clear-l"></div></h3>
			<div class="p20lo p40bo">
				<div class="p5bo">
					<div>Species: <span class="b">$species</span></div>
					<div>PAZAR TF ID: <a href="$pazar_cgi/tf_search.cgi?geneID=$pazartfid" class="b">$pazartfid</a></div>
					<div>Transcript accession: <span class="b">$traccns</span></div>
					<div>Class and family: <span class="b">$trclasses $trfams</span></div>
					<div id="Hidden$pazartfid" class="hide">$tfname</div>
				</div>
				<div class="hide">
					<table id="sml$pazartfid" class="">
						<tbody>
							<tr><td></td></tr>
							<tr><td><div><checkbox name="sml$pazartfid\_checkbox" value=""></div></td></tr>
						</tbody>
					</table>
				</div>
				<div id="desc$pazartfid" name="desc$pazartfid" class="seqTableDiv">
					<table id="$pazartfid" class="evidencetableborder w100p"><tbody>
						<tr>
							<td class="tfdst w20">&nbsp;</td>
							<td class="tfdst w70">Seq type</td>
							<td class="tfdst w90">Seq ID</td>
							<td class="tfdst">Target gene</td>
							<td class="tfdst w110">Sequence</td>
							<td class="tfdst w210">Sequence info</td>
							<td class="tfdst w90">Links</td>
						</tr>};
	
		if (!$complex->{targets}) {
			print qq{<div class="emp">No target could be found for this TF.</div>};
			next;
		}
	
		my @rsids;
		my @coids;
		while (my $site = $complex->next_target) {
			$seqcounter++;
			my $type = $site->get_type;
			if ($type eq "matrix") {
				next;
			}
			if ($type eq "reg_seq") {
				my $found = 0;
				foreach my $targ (@$target) {
					if (($targ->{dbid} eq $site->get_dbid) and
						($targ->{aid} eq $site->get_analysis) and 
						($targ->{ilink} eq $site->get_ilink) and
						($targ->{olink} eq $site->get_olink)) {
						$found=1;
					}
				}
				unless ($found == 1) {
					next;
				}
				my $rsid = $site->get_dbid;
				if (grep/^$rsid$/,@rsids) {
					next;
				}
				push @rsids, $rsid;
				my $id = write_pazarid($rsid,"RS");
				my $seqname =! $site->get_name?"":$site->get_name;
				my $reg_seq = pazar::reg_seq::get_reg_seq_by_regseq_id($dbh,$site->get_dbid);
					my $gidprefix = "GS";
					my $asterisk = "";
					my $genetype = $reg_seq->gene_type;
					if ($genetype eq "marker") {
							$gidprefix = "MK";
							$asterisk = qq{<span class="warning">*</span>};
					}
		
				my $pazargeneid = write_pazarid($reg_seq->PAZAR_gene_ID,$gidprefix);
				my $gene_accession = $reg_seq->gene_accession;
				my @ens_coords = $ensdb->get_ens_chr($reg_seq->gene_accession);
				$ens_coords[5] =~ s/\[.*\]//g;
				$ens_coords[5] =~ s/\(.*\)//g;
				$ens_coords[5] =~ s/\.//g;
				my $species = $ensdb->current_org();
				$species = ucfirst($species) || "-";
				my $rs_binosp = $reg_seq->binomial_species;
				my $rs_chromo = $reg_seq->chromosome;
				my $rs_sstart = $reg_seq->start;
				my $rs_sbreak = $reg_seq->end;
				my $rs_strand = $reg_seq->strand;
				my $rs_dbname = $reg_seq->seq_dbname;
				my $rs_dbasse = $reg_seq->seq_dbassembly;
				my $rs_rawseq = $site->get_seq;
				my $rs_fstart = &pnum($rs_sstart);
				my $rs_fbreak = &pnum($rs_sbreak);
				my $rs_fstran = $rs_strand;
				$rs_fstran = "&ndash;" if $rs_fstran eq "-";
				
				my $seqseq = $rs_rawseq;
				my $seqlen = length($seqseq);
				my $seqstr = chopstr($seqseq, 20);
				my $rs_set = substr($seqstr,0,10);
				$rs_chstrnd = "&ndash;" if $rs_chstrnd eq "-";
				if ($seqlen > 10) {
					$seqlen = &pnum($seqlen);
					$rs_set .= "... ($seqlen&nbsp;bp)";
				}
				$seqstr = qq{<div class=""><div onclick="popup(this,'$seqstr','st');" class="popup">$rs_set</div></div>};

				my $coord = qq{chr$rs_chromo:$rs_fstart-$rs_fbreak ($rs_fstran)<div class="small">[$rs_dbname $rs_dbasse]</div>};

				my $rs_gene = $ens_coords[5];
				if (length($rs_gene) > 16) {
					$rs_gene =~ s/\'/\&\#39\;/g;
					$rs_gene = qq{<div onclick="popup(this,'$rs_gene','rt');" class="popup b">} . substr($rs_gene,0,14) . "..." . qq{</div>};
				}

				print qq{
				<tr class="genomic" style="background-color: $colors{$bg_color};">
					<td class="btc"><div><input type="checkbox" name="seq$seqcounter" value="$rs_rawseq"></div></td>
					<td class="btc">Genomic</td>
					<td class="btc">
						<a class="b" href="$pazar_cgi/seq_search.cgi?regid=$rsid">$id</a>
						<div>$seqname</div>
					</td>
					<td class="btc">
						<a class="b" href="$pazar_cgi/gene_search.cgi?geneID=$pazargeneid">$pazargeneid</a>$asterisk
						<div>$rs_gene</div>
						<div>$species</div>
					</td>
					<td class="btc">$seqstr</td>
					<td class="btc"><div class="b">Coordinates:</div>$coord</td>
					<td class="btc">
						<a href="$pazar_cgi/gff_custom_track.cgi?resource=ucsc&chr=$rs_chromo&start=$rs_sstart&end=$rs_sbreak&species=$rs_binosp" target="_blank"><img src="$pazar_html/images/ucsc_logo.png"></a> <a href="$pazar_cgi/gff_custom_track.cgi?resource=ensembl&chr=$rs_chromo&start=$rs_sstart&end=$rs_sbreak&species=$rs_binosp" target="_blank"><img src="$pazar_html/images/ensembl_logo.gif"></a>
					</td>
				</tr>};
			} elsif ($type eq "construct") {
				my $found = 0;
				foreach my $targ (@$target) {
					if (($targ->{dbid} eq $site->get_dbid) and
						($targ->{aid} eq $site->get_analysis) and
						($targ->{ilink} eq $site->get_ilink) and 
						($targ->{olink} eq $site->get_olink)) {
						$found = 1;
					}
				}
				unless ($found == 1) {
					next;
				}
				my $coid = $site->get_dbid;
				if (grep/^$coid$/,@coids) {
					next;
				}
				push @coids, $coid;
				my $id = write_pazarid($coid,"CO");
				my $seqname = $site->get_name == 0 ? "" : $site->get_name;
				my $desc = $site->get_desc || "-";
				
				my $rs_rawseq = $site->get_seq;
				
				my $seqseq = $rs_rawseq;
				my $seqlen = length($seqseq);
				my $seqstr = chopstr($seqseq, 20);
				my $rs_set = substr($seqstr,0,10);
				$rs_chstrnd = "&ndash;" if $rs_chstrnd eq "-";
				if ($seqlen > 10) {
					$seqlen = &pnum($seqlen);
					$rs_set .= "... ($seqlen&nbsp;bp)";
				}
				$seqstr = qq{<div class=""><div onclick="popup(this,'$seqstr','st');" class="popup">$rs_set</div></div>};
				
				print qq{
					<tr class="construct" style="background-color: $colors{$bg_color};">
						<td class="btc"><div><input type="checkbox" name="seq$seqcounter" value="$rs_rawseq"></div></td>
						<td class="btc">Artificial</td>
						<td class="btc"><div><div><a href="$pazar_cgi/seq_search.cgi?regid=$id" class="b">$id</a></div>$seqname</div></td>
						<td class="btc">-</td>
						<td class="btc">$seqstr</td>
						<td class="btc">
							<div class="b">Description:</div> 
							$desc
						</td>
						<td class="btc"> </td>
					</tr>};
			}
			$count++;
			my $construct_name = $pazartfid . "_site" . $count;
			print TMP ">" . $construct_name . "\n";
			my $construct_seq = $site->get_seq;
			$construct_seq =~ s/N//ig;
			print TMP $construct_seq . "\n";
			$bg_color = 1 - $bg_color;
		}
		close (TMP);
		if ($count == 200) {
			print qq{
				</tbody></table></div>
				<div class="emp">Too many sequences are linked to this TF. Only the first 200 are reported.</div>
				<div class="p10 bg-lg">
					<div class="b p5bo"><form name="fasta$pazartfid" method="POST" action="$pazar_cgi/fasta_call.pl"><input type="submit" value="Download all sequences"><input type="hidden" name="fasta" value="$fasta"><input type="hidden" name="TFID" value="$pazartfid"></form></div>
					<div class="b p5bo">Generate a custom PFM and logo with selected sequences from $tf_name ($pazartfid)</div>
					<div class="p5bo">
						<span class="b">Select</span> <input type="button" name="selectall" id="selectall" value="all" onclick="selectallseq('$pazartfid');"> <input type="button" name="selecttype1" id="selecttype1" value="genomic sequences" onclick="selectbytype('$pazartfid','genomic');"> <input type="button" name="selecttype2" id="selecttype2" value="artificial sequences" onclick="selectbytype('$pazartfid','construct');"> <input type="button" name="resetall" id="resetall" value="reset" onclick="resetallseq('$pazartfid');"> <span class="b">then click</span> <input type="button" name="Regenerate PFM" value="Generate PFM" onclick="ajaxcall('$pazartfid','memediv$pazartfid');">
					</div>
					<div id="memediv$pazartfid">Not generated</div>
					<div class="p5to small b">Note: to generate a profile with sequences from multiple projects, use the &quot;Custom matrix&quot; tool at the bottom of the page.</div>
				</div>};
		} else {
			print qq{
				</tbody></table></div>
				<div class="p10 bg-lg">
					<div class="b p5bo"><form name="fasta$pazartfid" method="POST" action="$pazar_cgi/fasta_call.pl"><input type="submit" value="Download all sequences"><input type="hidden" name="fasta" value="$fasta"><input type="hidden" name="TFID" value="$pazartfid"></form></div>
					<div class="b p5bo">Generate a custom PFM and logo with selected sequences from $tf_name ($pazartfid)</div>
					<div class="p5bo">
						<span class="b">Select</span> <input type="button" name="selectall" id="selectall" value="all" onclick="selectallseq('$pazartfid');"> <input type="button" name="selecttype1" id="selecttype1" value="genomic sequences" onclick="selectbytype('$pazartfid','genomic');"> <input type="button" name="selecttype2" id="selecttype2" value="artificial sequences" onclick="selectbytype('$pazartfid','construct');"> <input type="button" name="resetall" id="resetall" value="reset" onclick="resetallseq('$pazartfid');"> <span class="b">then click</span> <input type="button" name="Regenerate PFM" value="Generate PFM" onclick="ajaxcall('$pazartfid','memediv$pazartfid');">
					</div>
					<div id="memediv$pazartfid">Not generated</div>
					<div class="p5to small b">Note: to generate a profile with sequences from multiple projects, use the &quot;Custom matrix&quot; tool at the bottom of the page.</div>
				</div>};
		}
	}
	print qq{</div>};
	return $seqcounter;
}
sub select {
	my ($dbh, $sql) = @_;
	my $sth=$dbh->prepare($sql);
	$sth->execute or die "$dbh->errstr\n";
	return $sth;
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
sub write_pazarid {
	my $id=shift;
	my $type=shift;
	my $id7d = sprintf "%07d",$id;
	my $pazarid=$type.$id7d;
	return $pazarid;
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