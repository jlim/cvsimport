#!/usr/bin/perl

use pazar;
use pazar::talk;
use HTML::Template;

use CGI qw(:standard);
use CGI::Carp qw(fatalsToBrowser);

# use CGI::Debug(report => "everything", on => "anything");

my $pazar_cgi       = $ENV{PAZAR_CGI};
my $pazar_html      = $ENV{PAZAR_HTML};
my $pazarcgipath    = $ENV{PAZARCGIPATH};
my $pazarhtdocspath = $ENV{PAZARHTDOCSPATH};

use constant DB_DRV  => $ENV{PAZAR_drv};
use constant DB_NAME => $ENV{PAZAR_name};
use constant DB_USER => $ENV{PAZAR_pubuser};
use constant DB_PASS => $ENV{PAZAR_pubpass};
use constant DB_HOST => $ENV{PAZAR_host};

my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");
my $temptail = HTML::Template->new(filename => "tail.tmpl");
$template->param(TITLE => "List of transcription factors (TFs) | PAZAR");
$template->param(ONLOAD_FUNCTION => "init(); coll_all(); self.focus();");
$template->param(JAVASCRIPT_FUNCTION => qq{ });
$template->param(PAZAR_HTML => $pazar_html);
$template->param(PAZAR_CGI => $pazar_cgi);

my $pazarcgipath = $ENV{PAZARCGIPATH};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazar_cgi = $ENV{PAZAR_CGI};

my $get = new CGI;
my %param = %{$get->Vars};

my $dbh = pazar->new( 
	-host         => DB_HOST,
	-user         => DB_USER,
	-pass         => DB_PASS,
	-dbname       => DB_NAME,
	-drv          => DB_DRV,
	-globalsearch => "yes");

my $talkdb = pazar::talk->new(
	DB => "ensembl",
	USER => $ENV{ENS_USER},
	PASS => $ENV{ENS_PASS},
	HOST => $ENV{ENS_HOST},
        PORT => $ENV{ENS_PORT},
        ENSEMBL_DATABASES_HOST => $ENV{ENSEMBL_DATABASES_HOST},
        ENSEMBL_DATABASES_USER => $ENV{ENSEMBL_DATABASES_USER},
        ENSEMBL_DATABASES_PASS => $ENV{ENSEMBL_DATABASES_PASS},
	DRV => "mysql");

my $bg_color = 0;
my %colors = (
	0 => "#fffff0",
	1 => "#FFB5AF");

my $projects = &select($dbh,
	qq{SELECT * FROM project 
	WHERE upper(status)="OPEN" 
	OR upper(status)="PUBLISHED"});

require "$pazarcgipath/getsession.pl";
if ($loggedin eq "true") {
	$template->param(LOGOUT => qq{<span class="b">You are signed in as $info{first} $info{last}.</span> <a href="$pazar_cgi/logout.pl" class="b">Sign out</a>});
} else {
	$template->param(LOGOUT => qq{<a href="$pazar_cgi/login.pl"><span class="b">Sign in</span></a>});
}
print "Content-Type: text/html\n\n", $template->output;
my @desc;
while (my $project = $projects->fetchrow_hashref) {
	push @desc, $project;
}

if ($loggedin eq "true") {
	foreach my $proj (@projids) {
		my $restricted = &select($dbh, qq{SELECT * FROM project WHERE project_id="$proj" and upper(status)="RESTRICTED"});
		while (my $restr = $restricted->fetchrow_hashref) {
			push @desc, $restr;
		}
	}
}

my %tf_project;
foreach my $project (@desc) {
	my @funct_tfs = $dbh->get_all_complex_ids($project->{project_id});
	foreach my $funct_tf (@funct_tfs) {
	my $funct_name = $dbh->get_complex_name_by_id($funct_tf);
	my $tf = $dbh->create_tf;
	my $tfcomplex = $tf->get_tfcomplex_by_id($funct_tf,"notargets");
	my $pazartfid = write_pazarid($funct_tf,"TF");
	my @accns;
	my @classes;
	my @species;
	while (my $subunit = $tfcomplex->next_subunit) {
		my $fam =! $subunit->get_fam?"":"/".$subunit->get_fam;
		my $class =! $subunit->get_class?"":$subunit->get_class.$fam;
		push @classes, $class;
		my $sub_accn = $subunit->get_transcript_accession($dbh);
		push @accns, $sub_accn;
		my @coords = $talkdb->get_ens_chr($sub_accn);
		my $species = $talkdb->current_org();
		$species = ucfirst($species) || "-";
		push @species, $species;
	}
	push (@{$tf_project{$project->{project_name}}}, {
		tfname => $funct_name,
		accn => \@accns,
		class => \@classes,
		species => \@species,
		ID => $pazartfid});
	}
}
print qq{
	<div class="docp">
		<div class="float-r b txt-grey">PAZAR Database</div>
		<a href="$pazar_cgi/tf_search.cgi" class="b">&laquo; Return to TF search</a>
		<div class="clear-r"></div>
	</div>
	<h1>List of transcription factors</h1>};

my @proj_names = sort(keys %tf_project);
foreach my $proj_name (@proj_names) {
	my $div_id = $proj_name;
	$div_id =~ s/ /_/g;
	my $style = "hide";
	if ($param{opentable} eq $proj_name) {
		$style = "show";
	}
	my %anti = (
		"show" => "hide",
		"hide" => "show"
	);
	$bg_color = 0;
	print qq{
		<div id="1_$div_id" class="$anti{$style}">
			<div onclick="toggleRows('$div_id','2','2');" class="blklk">+ $proj_name</div>
		</div>
		<div id="2_$div_id" class="$style">
			<div onclick="toggleRows('$div_id','1','2');" class="blklk-a">&ndash; $proj_name</div>
			<div class="p20lo p20bo"><table class="summarytable w100p">
				<tr>
					<td class="tftt b w160">Species <a href="$pazar_cgi/tf_list.cgi?BROWSE=species&amp;opentable=$proj_name"><img src="$pazar_html/images/arrow-none.gif" alt="Sort" height="10" border="0"></a></td>
					<td class="tftt b w100">PAZAR TF ID <a href="$pazar_cgi/tf_list.cgi?BROWSE=ID&amp;opentable=$proj_name"><img src="$pazar_html/images/arrow-none.gif" alt="Sort" height="10" border="0"></a></td>
					<td class="tftt b w20p">TF name <a href="$pazar_cgi/tf_list.cgi?BROWSE=desc&amp;opentable=$proj_name"><img src="$pazar_html/images/arrow-none.gif" alt="Sort" height="10" border="0"></a></td>
					<td class="tftt b w20p">Ensembl transcript ID <a href="$pazar_cgi/tf_list.cgi?BROWSE=accn&amp;opentable=$proj_name"><img src="$pazar_html/images/arrow-none.gif" alt="Sort" height="10" border="0"></a></td>
					<td class="tftt b">TF class and family <a href="$pazar_cgi/tf_list.cgi?BROWSE=class&amp;opentable=$proj_name"><img src="$pazar_html/images/arrow-none.gif" alt="Sort" height="10" border="0"></a></td>
				</tr>};

	my @sorted;
	if ($param{BROWSE} eq "species") {
		@sorted = sort {$a->{species}->[0] cmp $b->{species}->[0] or $a->{tfname} cmp $b->{tfname}} @{$tf_project{$proj_name}};
	} elsif ($param{BROWSE} eq "ID") {
		@sorted = sort {$a->{ID} cmp $b->{ID}} @{$tf_project{$proj_name}};
	} elsif ($param{BROWSE} eq "class") {
		@sorted = sort {$a->{class}->[0] cmp $b->{class}->[0] or $a->{species}->[0] cmp $b->{species}->[0]} @{$tf_project{$proj_name}};
	} elsif ($param{BROWSE} eq "accn") {
		@sorted = sort {$a->{accn}->[0] cmp $b->{accn}->[0]} @{$tf_project{$proj_name}};
	} else {
		@sorted = sort {$a->{tfname} cmp $b->{tfname} or $a->{species}->[0] cmp $b->{species}->[0]} @{$tf_project{$proj_name}};
	}

	foreach my $tf_data (@sorted) {
		my $classes = ucfirst(lc(join(", ",@{$tf_data->{class}})));
		my $accns = join(", ",@{$tf_data->{accn}});
		my $spec = ucfirst(lc(join(", ",@{$tf_data->{species}})));
		my $actfn = $tf_data->{tfname};
		my $tfgid = $tf_data->{ID};
		$actfn =~ s/ZEBRAFISH_/zebrafish /g;
		$actfn =~ s/XENOPUS_/xenopus /g;
		$actfn =~ s/CHICKEN_/chicken /g;
		$actfn =~ s/HUMAN_/human /g;
		$actfn =~ s/MOUSE_/mouse /g;
		$actfn =~ s/WORM_/worm /g;
		$actfn =~ s/RAT_/rat /g;
		$actfn =~ s/FLY_/fly /g;
		
		if (length($spec) > 24) {
			$spec =~ s/\'/\&\#39\;/g;
			$spec = qq{<div onclick="popup(this,'$spec','rt');" class="popup">} . substr($spec,0,22) . "..." . qq{</div>};
		}
		if (length($actfn) > 18) {
			$actfn =~ s/\'/\&\#39\;/g;
			$actfn = qq{<div onclick="popup(this,'$actfn','rt');" class="popup">} . substr($actfn,0,16) . "..." . qq{</div>};
		}
		if (length($accns) > 18) {
			$accns =~ s/\'/\&\#39\;/g;
			$accns = qq{<div onclick="popup(this,'$accns','rt');" class="popup">} . substr($accns,0,16) . "..." . qq{</div>};
		}
		if (length($classes) > 30) {
			$classes =~ s/\'/\&\#39\;/g;
			$classes = qq{<div onclick="popup(this,'$classes','rt');" class="popup">} . substr($classes,0,28) . "..." . qq{</div>};
		}
		print qq{
			<tr style="background-color: $colors{$bg_color};">
				<td class="btd">$spec</td>
				<td class="btd"><a href="$pazar_cgi/tf_search.cgi?searchtab=tfs&amp;ID_list=PAZAR_TF&amp;geneID=$tfgid">$tfgid</a></td>
				<td class="btd">$actfn</td>
				<td class="btd">$accns</td>
				<td class="btd">$classes</td>
			</tr>};
		$bg_color =  1 - $bg_color;
	}
	print qq{</table></div></div>};
}
print $temptail->output;

sub select {
	my ($dbh,$sql) = @_;
	my $sth = $dbh->prepare($sql);
	$sth->execute or die qq{$dbh->errstr\n};
	return $sth;
}
sub write_pazarid {
	my $id = shift;
	my $type = shift;
	my $id7d = sprintf "%07d",$id;
	my $pazarid = $type.$id7d;
	return $pazarid;
}
