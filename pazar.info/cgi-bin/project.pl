#!/usr/bin/perl
use HTML::Template;
use pazar;
use pazar::talk;
use pazar::reg_seq;
use pazar::tf::subunit;
use pazar::tf::tfcomplex;
use CGI qw(:standard);
use CGI::Carp qw(fatalsToBrowser);
# use CGI::Debug(report => "everything", on => "anything");

my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};
require "$pazarcgipath/getsession.pl";

my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");
$template->param(TITLE => "Project view | PAZAR");
$template->param(PAZAR_HTML => $pazar_html);
$template->param(PAZAR_CGI => $pazar_cgi);
$template->param(JAVASCRIPT_FUNCTION => q{ });

if ($loggedin eq "true") {
	$template->param(LOGOUT => qq{<span class="b">You are signed in as $info{first} $info{last}.</span> 
	<a href="$pazar_cgi/logout.pl" class="b">Sign out</a>});
} else {
	$template->param(LOGOUT => qq{<a href="$pazar_cgi/login.pl"><span class="b">Sign in</span></a>});
}

print "Content-Type: text/html\n\n", $template->output;
my $get = new CGI;
my %param = %{$get->Vars};
my $proj = $param{project_name};
unless ($proj) {
	print qq{<div class="emp">A project name must be defined in order for this page to load correctly. Please define a project name and try again. If you believe you have encountered this message in error, please submit a bug report to the administrators of this site by sending an email to <a href="mailto:pazar@cmmt.ubc.ca?subject=Bug report on project.pl">pazar@cmmt.ubc.ca</a>.</div>};
}

my $dbh0 = pazar->new(
	-host         => $ENV{PAZAR_host},
	-user         => $ENV{PAZAR_pubuser},
	-pass         => $ENV{PAZAR_pubpass},
	-dbname       => $ENV{PAZAR_name},
	-drv          => $ENV{PAZAR_drv},
	-globalsearch => "yes"
);

my $stat = &select($dbh0, qq{SELECT status, description FROM project WHERE project_name="$proj"});
my ($status,$descrip) = $stat->fetchrow_array;

my $dbh;
if ($status =~ /open/i || $status =~ /published/i) {
	$dbh = pazar->new(
		-host    => $ENV{PAZAR_host},
		-user    => $ENV{PAZAR_pubuser},
		-pass    => $ENV{PAZAR_pubpass},
		-dbname  => $ENV{PAZAR_name},
		-drv     => $ENV{PAZAR_drv},
		-project => $proj);
} elsif ($status =~ /restricted/i) {
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
my $talkdb = pazar::talk->new(
	DB   => "ensembl",
	USER => $ENV{ENS_USER},
	PASS => $ENV{ENS_PASS},
	HOST => $ENV{ENS_HOST},
	DRV  => "mysql");

my $projid = $dbh->get_projectid();

my $mnb = &select($dbh,qq{SELECT count(distinct db_accn) FROM marker WHERE project_id="$projid"});
my $markernb = $mnb->fetchrow_array || "0";
my $gnb = &select($dbh,qq{SELECT count(distinct db_accn) FROM gene_source a, tsr b 
	WHERE a.project_id="$projid" and a.gene_source_id=b.gene_source_id});
my $genenb = $gnb->fetchrow_array || "0";
my $totmrk = $genenb + $markernb;

my $rnb = &select($dbh,qq{SELECT count(reg_seq_id) FROM reg_seq WHERE project_id="$projid"});
my $regseqnb = $rnb->fetchrow_array || "0";
my $cnb = &select($dbh,qq{SELECT count(construct_id) FROM construct WHERE project_id="$projid"});
my $constrnb = $cnb->fetchrow_array || "0";
my $tnb = &select($dbh,qq{SELECT count(funct_tf_id) FROM funct_tf WHERE project_id="$projid"});
my $tfnb = $tnb->fetchrow_array || "0";
my $mnb = &select($dbh,qq{SELECT count(matrix_id) FROM matrix WHERE project_id="$projid"});
my $matrixnb = $mnb->fetchrow_array || "0";
my $refnb = &select($dbh,qq{SELECT count(ref_id) FROM ref WHERE project_id="$projid"});
my $refsnb = $refnb->fetchrow_array || "0";

print qq{
	<h1><div class="float-r ns"><a href="$pazar_cgi/projects.pl">see other projects &raquo;</a></div>
	The <span class="txt-ora">$proj</span> project in PAZAR 
	<a href="$pazar_cgi/help_FAQ.pl#5.%20Search%20within%20a%20specific%20Boutique%20Project" 
	target="helpwin" onClick="window.open('about:blank','helpwin');"
	><img src="$pazar_html/images/help.gif" alt="Help" align="bottom" width="12"></a></h1>
	<div class="float-l w60p block">
		<div class="p20ro">
			<h3>Description</h3>
			<div class="p10bo">
				<div class="p10 bg-lg">$descrip</div>
			</div>
		</div>
	</div>
	<div class="float-l w40p block">
		<h3>Statistics</h3>
		<div class="p10bo">
			Regulated genes (or markers): <span class="b">$totmrk</span><br>
			Regulatory sequences (genomic): <span class="b">$regseqnb</span><br>
			Regulatory sequences (artificial): <span class="b">$constrnb</span><br>
			Transcription factors: <span class="b">$tfnb</span><br>
			Transcription factor profiles: <span class="b">$matrixnb</span><br>
			Annotated publications: <span class="b">$refsnb</span><br>
		</div>
	</div>
	<div class="clear-l"></div>};

if ($genenb == 0
	&& $regseqnb == 0
	&& $constrnb == 0
	&& $tfnb == 0
	&& $matrixnb != 0) {
	print qq{<div class="emp">This project only holds pre-computed profiles. Please use the &quot;Pre-computed TF profiles&quot; page to look at the profiles in this project.</div>};
} else {
	print qq{
		<h3>Access project data</h3>
		<div class="p20bo">
			<form name="filtersnownownow" METHOD="post" ACTION="$pazar_cgi/proj_res.cgi" enctype="multipart/form-data" target="_self">
				<input type="hidden" name="project_name" value="$proj">
				<span class="b">View all data now in</span> <input type="submit" name="submit" VALUE="gene view"> <span class="b">or</span> <input type="submit" name="submit" VALUE="TF view"> (not recommended&mdash;please use a filter to reduce output size and load time)
			</form>
		</div>
		<div class="p10bo">
			<form name="filters" METHOD="post" ACTION="$pazar_cgi/proj_res.cgi" enctype="multipart/form-data" target="_self">
			<input type="hidden" name="project_name" value="$proj">};

	my @species;
	my $species = &select($dbh,qq{SELECT species FROM location WHERE project_id="$projid"});
	if ($species) {
		while (my $sp = $species->fetchrow_array) {
			if (!grep(/$sp/i, @species)) {
				push(@species, $sp);
			}
		}
	}
	my @functs = $dbh->get_all_complex_ids($projid);
	foreach my $funct_tf (@functs) {
		my $tf = $dbh->create_tf;
		my $tfcomplex = $tf->get_tfcomplex_by_id($funct_tf,"notargets");
		while (my $subunit = $tfcomplex->next_subunit) {
			my $trans = $subunit->get_transcript_accession($dbh);
			my $gene = $talkdb->ens_transcr_to_gene($trans);
			my $sp = $talkdb->current_org();
			if (!grep(/$sp/i, @species)) {
				push(@species, $sp);
			}
		}
	}
	if (@species) {
		my @sp = sort(@species);
		print qq{
			<div class="b p5bo"><input type="checkbox" name="species_filter" onclick="toche(this,'species_filter');"> 
			Restrict to species &raquo;</div>
			<div class="hide" id="species_filter"><div class="p30lo p10bo">};
		foreach my $sp (@sp) {
			my $nsp = uc(substr($sp,0,1)) . lc(substr($sp,1));
			print qq{
				<div class="p5bo"><input type="checkbox" name="species" value="$sp"> $nsp</div>};
		}
		print qq{</div></div>};
	}

	my $chr = &select($dbh,qq{SELECT chr FROM location WHERE project_id="$projid"});
	if ($chr) {
		print qq{
			<div class="b p5bo"><input type="checkbox" name="region_filter" onclick="toche(this,'region_filter'); CheckBox();"> 
			Restrict to genomic region &raquo;</div>
			<div class="hide" id="region_filter"><div class="p30lo p10bo">
				<div class="p5bo"><input type="checkbox" name="chr_filter"> chromosome <select name="chromosome">};
		my @chr;
		while (my $ch = $chr->fetchrow_array) {
			if (!grep(/$ch/i, @chr)) {
				push(@chr, $ch);
			}
		}
		my @schr = sort(@chr);
		foreach (@schr) {print qq{<option value="$_">$_</option>};}
		print qq{
				</select></div>
				<div class="p5bo"><input type="checkbox" name="bp_filter"> 
					<span class="b">also restrict by base pair</span> &nbsp; 
					start <input name="bp_start" value="" type="text"> &nbsp; 
					end <input name="bp_end" value="" type="text">
				</div>
			</div></div>};
	}
	my $markercount = $dbh->prepare(qq{SELECT count(*) FROM marker WHERE project_id="$projid"}) || die DBI::errstr;
	$markercount->execute || die;
	my $mc = $markercount->fetchrow_array;
	my $checkcount = $dbh->prepare(qq{SELECT count(*) FROM gene_source a, tsr b 
		WHERE a.project_id="$projid" and a.gene_source_id=b.gene_source_id}) || die DBI::errstr;
	$checkcount->execute || die;
	my $gc = $checkcount->fetchrow_array;
	my $mimo;
	unless (($gc + $mc) > 1000) {
		# Display both genes and markers...
		my $mh = $dbh->prepare(qq{SELECT * FROM marker WHERE project_id=?}) || die DBI::errstr;
		$mh->execute($projid) || die DBI::errstr;
		my $gh = $dbh->prepare(qq{SELECT * FROM gene_source a, tsr b WHERE a.project_id=? and a.gene_source_id=b.gene_source_id}) || die DBI::errstr;
		$gh->execute($projid) || die DBI::errstr;
		while (my $gene = $gh->fetchrow_hashref) {
			my @coords = $talkdb->get_ens_chr($gene->{db_accn});
			$coords[5] =~ s/\[.*\]//g;
			$coords[5] =~ s/\(.*\)//g;
			$coords[5] =~ s/\.//g;
			$gene{ $gene->{db_accn} } = $coords[5];
		}
		# Now add markers tp $gene hashtable...
		while (my $marker = $mh->fetchrow_hashref) {
			my @coords = $talkdb->get_ens_chr($marker->{db_accn});
			$coords[5] =~ s/\[.*\]//g;
			$coords[5] =~ s/\(.*\)//g;
			$coords[5] =~ s/\.//g;
			$gene{ $marker->{db_accn} } = $coords[5];
		}
		if (%gene) {
			my @sortedaccn = sort { lc($gene{$a}) cmp lc($gene{$b}) } (keys %gene);
			foreach my $accn (@sortedaccn) {
				$mimo .= qq{<div class="p5bo"><input type="checkbox" name="gene" value="$accn"> $gene{$accn} 
				<a href="http://www.ensembl.org/Homo_sapiens/psychic?species=all&amp;q=$accn">$accn</a></div>};
			}
		}
	} else {
		$mimo .= qq{<div class="emp">This feature has been disabled because there are over 1,000 genes in this project.</div>};
	}

	print qq{
		<div class="b p5bo"><input type="checkbox" name="gene_filter" onclick="toche(this,'gene_filter');"> 
		Restrict to one or more regulated genes or markers &raquo;</div>
		<div class="hide" id="gene_filter"><div class="p30lo p10bo"><div class="boxit">$mimo</div></div></div>};

	print qq{
		<div class="b p5bo"><input type="checkbox" name="length_filter" onclick="toche(this,'length_filter');"> 
		Restrict to sequence length &raquo;</div>
		<div class="hide" id="length_filter"><div class="p30lo p10bo">
			Only show results with a sequence length that is <select name="shorter_larger">
				<option value="greater_than" selected="selected">greater than</option>
				<option value="less_than">less than</option>
				<option value="equal_to">equal to</option>
			</select> <input type="text" name="length"> bases
		</div></div>};

	my @funct_tfs = $dbh->get_all_complex_ids($projid);
	my %tf_subunit;
	my $ftf = 0;
	foreach my $funct_tf (@funct_tfs) {
		$ftf = 1;
		my $funct_name = $dbh->get_complex_name_by_id($funct_tf);
		my $tf = $dbh->create_tf;
		my $tfcomplex = $tf->get_tfcomplex_by_id($funct_tf, "notargets");
		while (my $subunit = $tfcomplex->next_subunit) {
			push(
				@{ $tf_subunit{$funct_name} },
				$subunit->get_transcript_accession($dbh)
			);
		}
	}
	if ($ftf == 1) {
		print qq{
			<div class="b p5bo"><input type="checkbox" name="tf_filter" onclick="toche(this,'tf_filter');"> 
			Restrict to one or more regulating factors &raquo;</div>
			<div class="hide" id="tf_filter"><div class="p30lo p10bo"><div class="boxit">};
		my @tfnames = keys %tf_subunit;
		my @sortedtfname = sort(@tfnames);
		foreach my $name (@sortedtfname) {
			print qq{<div class="p5bo"><input type="checkbox" name="tf" value="$name"> $name };
			foreach my $su (@{ $tf_subunit{$name} }) {
				print qq{<a href="http://www.ensembl.org/Homo_sapiens/psychic?species=all&amp;q=$su">$su</a> };
			}
			print qq{</div>};
		}
		print qq{</div></div></div>};
	}

	my $classes = &select($dbh,qq{SELECT class, family FROM tf WHERE project_id="$projid"});
	if ($classes) {
		my @classes;
		my $miko;
		while (my ($class, $fam) = $classes->fetchrow_array) {
			my $fam2 = !$fam ? "" : "/" . $fam;
			my $cf = !$class ? "" : $class . $fam2;
			unless (grep(/$cf/i, @classes) || !$cf) {
				push @classes, $cf;
			}
		}
		@classes = sort(@classes);
		foreach (@classes) {$miko .= qq{<div class="float-l w25p block p5bo"><input type="checkbox" name="classes" value="$_"> $_</div>};}
		unless (length($miko) > 10) {
			$miko = qq{<div class="emp">There are no class or family annotations to filter in this project.</div>};
		}
		print qq{
			<div class="b p5bo"><input type="checkbox" name="class_filter" onclick="toche(this,'class_filter');"> 
			Restrict to a specific TF classification class or family &raquo;</div>
			<div class="hide" id="class_filter"><div class="p30lo p10bo">
			$miko
			<div class="clear-l"></div>
			</div></div>};
	}

	print qq{
		<div class="b p5bo"><input type="checkbox" name="interaction_filter" onclick="toche(this,'interaction_filter');"> 
		Restrict to protein-DNA interaction quality &raquo;</div>
		<div class="hide" id="interaction_filter"><div class="p30lo p10bo">
			Restrict to sequences where interaction is <select name="interaction">
				<option value="not_null" selected="selected">not null</option>
				<option value="none">null</option>
				<option value="poor">poor</option>
				<option value="marginal">marginal</option>
				<option value="good">good</option>
				<option value="saturation">saturation</option>
			</select>
		</div></div>
		<div class="b p5bo"><input type="checkbox" name="expression_filter" onclick="toche(this,'expression_filter');"> 
		Restrict to expression outcome &raquo;</div>
		<div class="hide" id="expression_filter"><div class="p30lo p10bo">
			Restrict to sequences where expression is <select name="expression">
				<option value="change" selected="selected">changed</option>
				<option value="no change">not changed</option>
				<option value="highly induced">highly induced</option>
				<option value="induced">induced</option>
				<option value="repressed">repressed</option>
				<option value="strongly repressed">strongly repressed</option>
			</select>
		</div></div>
		<div class="b p5bo"><input type="checkbox" name="evidence_filter" onclick="toche(this,'evidence_filter');"> 
		Restrict to one or more evidence types &raquo;</div>
		<div class="hide" id="evidence_filter"><div class="p30lo p10bo">
			<div class="p5bo"><input type="checkbox" name="evidence" value="ADMC">ADMC</div>
			<div class="p5bo"><input type="checkbox" name="evidence" value="curated">curated</div>
			<div class="p5bo"><input type="checkbox" name="evidence" value="predicted">predicted</div>
		</div></div>
		<div class="b p5bo"><input type="checkbox" name="method_filter" onclick="toche(this,'method_filter');"> 
		Restrict to one or more experimental methods &raquo;</div>
		<div class="hide" id="method_filter"><div class="p30lo p10bo"><div class="boxit">};
	my @m = $dbh->get_method_names();
	@m = sort(@m);
	foreach (@m) {print qq{<div class="p5bo"><input type="checkbox" name="method" value="$_">$_</div>};}
	print qq{</div>
		</div></div>
		<div class="p15to p5bo b">
			View filtered data in 
			<input type="submit" name="submit" VALUE="gene view"> or 
			<input type="submit" name="submit" VALUE="TF view">
	  	</div>
	</form></div>};
}
sub select {
	my ($dbh, $sql) = @_;
	my $sth = $dbh->prepare($sql);
	$sth->execute or die qq{$dbh->errstr\n};
	return $sth;
}
my $tail = HTML::Template->new(filename => "$pazarcgipath/tail.tmpl");
print $tail->output;