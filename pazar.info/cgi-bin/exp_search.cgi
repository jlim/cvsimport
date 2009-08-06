#!/usr/bin/perl
use pazar;
use pazar::gene;
use pazar::talk;
use pazar::reg_seq;
use HTML::Template;
use CGI qw(:standard);
use CGI::Carp qw(fatalsToBrowser);
# use CGI::Debug(report => 'everything', on => 'anything');
my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};
require "$pazarcgipath/getsession.pl";
require "$pazarcgipath/searchbox.pl";
my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");
$template->param(TITLE => "Analysis view | PAZAR");
$template->param(PAZAR_HTML => $pazar_html);
$template->param(PAZAR_CGI => $pazar_cgi);
$template->param(JAVASCRIPT_FUNCTION => qq{ });
if ($loggedin eq "true") {$template->param(LOGOUT => qq{<span class="b">You are signed in as $info{first} $info{last}.</span> <a href="$pazar_cgi/logout.pl" class="b">Sign out</a>});} else {$template->param(LOGOUT => qq{<a href="$pazar_cgi/login.pl"><span class="b">Sign in</span></a>});}
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
	DRV  => "mysql"
);
print "Content-Type: text/html\n\n", $template->output;
my @pubprojects = $dbh->public_projects;
print $bowz;
my $bg_color = 0;
my %colors = (
	0 => "#fffff0",
	1 => "#B7DDA6");
my $get = new CGI;
my %params = %{$get->Vars};
my $aid = $params{aid};
my $xc = $params{excluded} || "none";
my $projstat = &select($dbh,qq{
	SELECT b.project_name,b.status 
	FROM analysis a,project b 
	WHERE a.analysis_id="$aid" 
	AND a.project_id=b.project_id});
my @res = $projstat->fetchrow_array;
undef $dbh;
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
		-globalsearch  => "no",			  
		-host          => $ENV{PAZAR_host},
		-user          => $ENV{PAZAR_pubuser},
		-pass          => $ENV{PAZAR_pubpass},
		-dbname        => $ENV{PAZAR_name},
		-drv           => $ENV{PAZAR_drv},
		-project       => $res[0]);
}   
my $cellinfo;
my $anid = &wpid($aid,"AN");
my @an = $dbh->get_data_by_primary_key("analysis",$aid);
my @cell = $dbh->get_data_by_primary_key("cell",$an[4]);
my @met = $dbh->get_data_by_primary_key("method",$an[3]);
my @ceco = ("Cell","Tissue","Status","Description","Species");
for (my $i=0; $i<5; $i++) {
	if (($cell[$i] && $cell[$i] ne "") and ($cell[$i] ne "0") and ($cell[$i] ne "NA")) {
		if ($ceco[$i] eq "Species") {
			$cell[$i] = lc($cell[$i]);
			$cell[$i] = ucfirst($cell[$i]);
		}
		if ($ceco[$i] eq "Status") {
			$cell[$i] = lc($cell[$i]);
		}
		my $temp = qq{<div class="">} . $ceco[$i] . ": " . $cell[$i] . qq{</div>};
		$cellinfo .= $temp;
	}
}
$cellinfo = "(not provided)" unless ($cellinfo);
my $timeinfo;
my @time = $dbh->get_data_by_primary_key("time",$an[5]);
my @time_cols = ("Name","Description","Scale","Range Start","Range End");
for (my $i=0; $i<5; $i++) {
	if ($time[$i] and ($time[$i] ne "") and ($time[$i] ne "0") and ($time[$i] ne "NA")) {
		if ($timeinfo) {
			$timeinfo .= "<br>";
		}
		$timeinfo .= $time_cols[$i] . ": " . $time[$i];
	}
}
my @ref = $dbh->get_data_by_primary_key("ref",$an[6]);
my $comments = $an[7];
my $commentseditable = "false";
my $analysis_projid = "";
my $edito;
if ($loggedin eq "true") {	
	$analysis_projid = $an[9];
	foreach my $proj (@projids) {
		if ($proj == $analysis_projid) {
			$commentseditable = "true";
		}
	}
	if ($commentseditable eq "true") {
		$edito .= qq{<div class="p5to"><span class="txt-ora b">Editing options:</span> <input type="button" name="commentupdatebutton" value="Update comments" onclick="javascript:window.open('updateanalysiscomments.pl?mode=form&pid=$analysis_projid&aid=$aid');"> <input type="button" value="Delete this analysis" onclick="confirm_entry_exp_search('$aid','$analysis_projid');"></div>};
	}
}
my @ev = $dbh->get_data_by_primary_key("evidence",$an[1]);
my $evinfo = qq{
	<div>Evidence type: <span class="b">$ev[0]</span></div>
	<div>Evidence status: <span class="b">$ev[1]</span></div>};
my @user = $dbh->get_data_by_primary_key("users",$an[0]);
my $userinfo;
unless ($user[0] or $user[1]) {
	$userinfo = $user[4];
} else {
	$userinfo = qq{$user[0] $user[1]};
}
my $timeinfodisplay = "";
my $commentsinfodisplay = "";
if ($timeinfo) {
	$timeinfodisplay = qq{<div>Time: <span class="b">$timeinfo</span></div>};
}
if ($comments) {
	$commentsinfodisplay = qq{<div>Comments: <div id="ajaxcomment" class="inline"><span class="b">$comments</span></div></div>};
}
print qq{
	<h2>Analysis <a class="b" href="$pazar_cgi/exp_search.cgi?aid=$params{aid}&amp;excluded=$xc">$anid</a> in the <a class="b" href="$pazar_cgi/project.pl?project_name=$res[0]">$res[0]</a> project <a href="$pazar_cgi/help_FAQ.pl#2.5%20Analysis%20View" target="helpwin" onclick="window.open('about:blank','helpwin');"><img src="$pazar_html/images/help.gif" alt="Help" align="bottom" width="10"></a></h2>
	<div class="p10lo p10bo">
		<div>Analysis method: <span class="b">$met[0]</span></div>
		<div><div class="float-l">Cell&nbsp;type:&nbsp;</div><div class="float-l b w600">$cellinfo</div><div class="clear-l"></div></div>
		$timeinfodisplay
		<div>Pubmed: <a href="http://www.ncbi.nlm.nih.gov/pubmed/$ref[0]" class="b" target="_blank">$ref[0]</a></div>
		$commentsinfodisplay
		$evinfo
		<div>Annotator: <span class="b">$userinfo</span></div>
		$edito
	</div>};
my @analysis = $dbh->get_analysis_structure_by_id($aid);
my %results;
my @idlist;
my $mode;
my %sort;
foreach my $link (@analysis) {
    my @out_types = $link->get_output_types;
    $mode = $out_types[0];
    my ($type,$id,@ins) = $link->next_relationship;
    while ($type) {
		unless (grep(/^$id$/,@idlist)) {
			push @idlist, $id;
			my @condid;
			my @seq;
			my @tf;
			foreach my $in (@ins) {
				my ($intable,$inid,@indata) = $dbh->links_to_data($in,"input");
				if (($intable eq "reg_seq") or ($intable eq "construct") or ($intable eq "mutation_set")) {
					push @seq, [$intable,$inid];
					push @{$sort{$intable}}, $id;
				} elsif (($intable eq "funct_tf") or ($intable eq "sample")) {
					push @tf, [$intable,$inid];
				} elsif ($intable eq "bio_condition") {
					push @condid, $inid;
				}
			}
			$results{$id}{"condid"} = \@condid;
			$results{$id}{"seq"} = \@seq;
			$results{$id}{"tf"} = \@tf;
		}
		($type,$id,@ins) = $link->next_relationship;
    }
}
my @sorted_keys = @{$sort{"reg_seq"}};
push @sorted_keys, @{$sort{"mutation_set"}};
push @sorted_keys, @{$sort{"construct"}};
my $count = 0;
print qq{<div class="p10lo">};
if ($mode eq "expression") {
	print qq{
		<table class="evidencedetailstableborder tblw">
			<tr>
				<td class="adtt w100">Seq ID and info</td>
				<td class="adtt w120">Target gene</td>
				<td class="adtt w100">Sequence</td>
				<td class="adtt">Sequence or method info</td>
				<td class="adtt w200">Expression level and condition(s)</td>
			</tr>};
} elsif ($mode eq "interaction") {
	print qq{
		<table class="evidencedetailstableborder tblw">
			<tr>
				<td class="adtt w100">Seq ID and info</td>
				<td class="adtt w120">Target gene</td>
				<td class="adtt w100">Sequence</td>
				<td class="adtt">Sequence or method info</td>
				<td class="adtt w200">Interaction level and interactor</td>
			</tr>};
}
foreach my $key (@sorted_keys) {
	print qq{<tr style="background-color: $colors{$bg_color};">};
	my $seqtable = $results{$key}{"seq"}->[0]->[0];
	my $seqid = $results{$key}{"seq"}->[0]->[1];
	my $tftable = $results{$key}{"tf"}->[0]->[0];
	my $tfid = $results{$key}{"tf"}->[0]->[1];
	$count++;
	if ($seqtable eq "reg_seq") {
		my $rsq = pazar::reg_seq::get_reg_seq_by_regseq_id($dbh,$seqid);
		my $rgid = $rsq->accession_number;
		my $prs = &wpid($rgid,"RS");
		my $gid = $rsq->PAZAR_gene_ID;
		my $sqna = $rsq->id;
		my $gpf = "GS";
		my $stk = "";
		if ($rsq->gene_type eq "marker") {
			$stk = qq{<span class="warning">*</span>};
			$gpf = "MK";
		}
		my $pgid = &wpid($gid,$gpf);
		my $gnac = $rsq->gene_accession;
		my @ec = $ensdb->get_ens_chr($gnac);
		$ec[5] =~ s/\[.*\]//g;
		$ec[5] =~ s/\(.*\)//g;
		$ec[5] =~ s/\.//g;
		my $spc = $ensdb->current_org();
		$spc = ucfirst($spc) || "(none provided)";
		my $chrst = $rsq->strand; $chrst = "&ndash;" if $chrst eq "-";
		my $seqstr = $rsq->seq;
		my $coord = 
			"chr" . $rsq->chromosome . ":"
			. &pnum($rsq->start) . "-"
			. &pnum($rsq->end)
			. qq{ ($chrst)}
			. qq{<div class="small">[}
			. $rsq->seq_dbname . " " . $rsq->seq_dbassembly . qq{]</div>};
		my $rs_gene = $ec[5];
		if (length($rs_gene) > 16) {
			$rs_gene = qq{<div onclick="popup(this,'$rs_gene','rt');" class="popup">} . substr($rs_gene,0,14) . "..." . qq{</div>};
		}
		my $rs_chp = chopstr($seqstr,20);
		my $rs_set = substr($seqstr,0,10);
		my $rs_len = length($seqstr);
		my $rs_sql = &pnum($rs_len);
		if ($rs_len > 10) {$rs_set .= "...";}
		my $fi_seq = qq{<div class=""><div onclick="popup(this,'$rs_chp','st');" class="popup">$rs_set<br>($rs_sql&nbsp;bp)</div></div>};
		print qq{
			<td class="btc"><div>Genomic</div>
			<a class="b" href="$pazar_cgi/seq_search.cgi?regid=$rgid&amp;excluded=$xc">$prs</a></td>
			<td class="btc">
				<a class="b" href="$pazar_cgi/gene_search.cgi?geneID=$pgid&amp;ID_list=PAZAR_gene&amp;excluded=$xc">$pgid</a>
				$stk
				<div class="b">$rs_gene</div>
				<div>$spc</div>
			</td>
			<td class="btc">$fi_seq</td>
			<td class="btc"><div class="b">Coordinates:</div>$coord</td>};
	} elsif ($seqtable eq "mutation_set") {
		my @mut = $dbh->get_data_by_primary_key("mutation_set",$seqid);
		my $sqna = $mut[1];
		my $rgid = $mut[0];
		my $muid = &wpid($seqid,"MS");
		my $prs = &wpid($rgid,"RS");
		my $rsq = pazar::reg_seq::get_reg_seq_by_regseq_id($dbh,$rgid);
		my $gid = $rsq->PAZAR_gene_ID;
		my $gpf = "GS";
		my $stk = "";
		if ($rsq->gene_type eq "marker") {
			$stk = qq{<span class="warning">*</span>};
			$gpf = "MK";
		}
		my $pgid = &wpid($gid,$gpf);
		my $gnac = $rsq->gene_accession;
		my @ec = $ensdb->get_ens_chr($gnac);
		my $spc = $ensdb->current_org();
		$spc = ucfirst($spc) || "(none provided)";
		$ec[5] =~ s/\[.*\]//g;
		$ec[5] =~ s/\(.*\)//g;
		$ec[5] =~ s/\.//g;
		my $seqstr = $mut[4];
		my $mutp;
		if ($mut[2] > 0) {
			my @mm = $dbh->get_data_by_primary_key("method",$mut[2]);
			my @mc = split(/::/,$mm[0]);
			my $mf;
			foreach my $m (@mc) {
				if (length($m) > 20) {
					$m = qq{<div onclick="popup(this,'$m','rt');" class="popup">} . substr($m,0,18) . "..." . qq{</div>};
				}
				$mf .= $m;
			}
			$mutp .= qq{<div class="b">Method(s):</div>$mf};
		}
		if ($mut[3] > 0) {
			my @mutref = $dbh->get_data_by_primary_key("ref",$mut[3]);
			$mutp .= qq{<div><span class="b">Pubmed:</span> <a class="b" href="http://www.ncbi.nlm.nih.gov/pubmed/$mutref[0]" target="_blank">$mutref[0]</a></div>};
		}
		if ($mut[5] and ($mut[5] ne "0")) {
			if (length($mut[5]) > 18) {
				$mut[5] = qq{<div onclick="popup(this,'$mut[5]','rt');" class="popup">} . substr($mut[5],0,16) . "..." . qq{</div>};
			}
			$mutp .= qq{<div><span class="b">Comments:</span> $mut[5]</div>};
		}
		my $rs_chp = chopstr($seqstr,20);
		my $rs_set = substr($seqstr,0,10);
		my $rs_len = length($seqstr);
		my $rs_sql = &pnum($rs_len);
		if ($rs_len > 10) {$rs_set .= "...";}
		my $fi_seq = qq{<div class=""><div onclick="popup(this,'$rs_chp','st');" class="popup">$rs_set<br>($rs_sql&nbsp;bp)</div></div>};
		my $rs_gene = $ec[5];
		if (length($rs_gene) > 16) {
			$rs_gene = qq{<div onclick="popup(this,'$rs_gene','rt');" class="popup">} . substr($rs_gene,0,14) . "..." . qq{</div>};
		}
		if (length($sqna) > 12) {
			$sqna = qq{<div onclick="popup(this,'$sqna','rt');" class="popup">} . substr($sqna,0,10) . "..." . qq{</div>};
		}
		print qq{
			<td class="btc"><div class="b">$muid</div>$sqna<div class="p5to">Mutant of sequence <a class="b" href="$pazar_cgi/seq_search.cgi?regid=$rgid&amp;excluded=$xc">$prs</a></div></td>
			<td class="btc">
				<a class="b" href="$pazar_cgi/gene_search.cgi?geneID=$pgid&amp;ID_list=PAZAR_gene&amp;excluded=$xc">$pgid</a>$stk
				<div class="b">$rs_gene</div>
				$spc</td>
			<td class="btc">$fi_seq</td>
			<td class="btc">$mutp</td>};
	} elsif ($seqtable eq "construct") {
		my @construct = $dbh->get_data_by_primary_key("construct",$seqid);
		my $desc = $construct[1] || "(no description)";
		my $pazarcoid = &wpid($seqid,"CO");
		my $seqstr = $construct[2];
		my $sqna = $construct[0];
		my $rs_chp = chopstr($seqstr,20);
		my $rs_set = substr($seqstr,0,10);
		my $rs_sql = &pnum(length($seqstr));
		if ($rs_sql > 10) {$rs_set .= "...";}
		my $fi_seq = qq{<div class=""><div onclick="popup(this,'$rs_chp','st');" class="popup">$rs_set<br>($rs_sql&nbsp;bp)</div></div>};
		print qq{
			<td class="btc">Artificial<div class="b">$pazarcoid</div>$sqna</td>
			<td class="btc">(not applicable)</td>
			<td class="btc">$fi_seq</td>
			<td class="btc"><div class="b">Description:</div>$desc</td>};
	}
	if ($mode eq "expression") {
		my ($outtable,$outid,@outdat) = $dbh->links_to_data($key,"output");
		my @outdata;
		my $tda;
		for (my $i=0; $i<(@outdat-3); $i++) {
			if ($outdat[$i] and ($outdat[$i] ne "0")) {
				$tda .= $outdat[$i] . " ";
			}
		}
		my @condids = @{$results{$key}{"condid"}};
		if (length($tda) > 28) {
			$tda = qq{<div onclick="popup(this,'$tda','rt');" class="popup">} . substr($tda,0,26) . "..." . qq{</div>};
		}
		print qq{<td class="btc"><div class="p5bo"><div class="br-b b">$tda</div></div>};
		my $nocond = 0;
		for (my $i=0; $i<@condids; $i++) {
			if ($i>0) {print qq{<div class="p5to p5bo"><div class="br-b"></div></div>};}
			$nocond = 1;
			my @dat = $dbh->get_data_by_primary_key("bio_condition",$condids[$i]);
			my $condinfo;
			my @cond_cols = ("Type","Molecule","Description","Concentration","Scale");
			for (my $j=0; $j<5; $j++) {
				if (lc($dat[0]) eq "co-expression" && $j==2) {
					next;
				}
				if ($dat[$j] and ($dat[$j] ne "") and ($dat[$j] ne "NA")) {
					$condinfo .= qq{<div><span class="b">} . $cond_cols[$j] . qq{:</span> } . $dat[$j] . qq{</div>};
				}
			}
			print $condinfo;
			if (lc($dat[0]) eq "co-expression") {
				my $tfid = $dat[2];
				my $tf = $dbh->create_tf;
				my $ptfd = &wpid($tfid,"TF");
				my $cp = $tf->get_tfcomplex_by_id($tfid,"notargets");
				my $cn = $cp->name;
				if (length($cn) > 10) {
					$cn = qq{<div onclick="popup(this,'$cn','rt');" class="popup">} . substr($cn,0,8) . "..." . qq{</div>};
				}
				print qq{<a href="$pazar_cgi/tf_search.cgi?ID_list=PAZAR_TF&amp;geneID=$ptfd&amp;excluded=$xc" class="b">$ptfd</a><div class="b">$cn</div>};
			}
		}
		if ($nocond == 0) {
			print "(no condition)";
		}
		print qq{</td>};
	} elsif ($mode eq "interaction") {
		print qq{<td class="btc">};
		my ($outtable,$outid,@outdat) = $dbh->links_to_data($key,"output");
		my $tda;
		for (my $i=0; $i<(@outdat-3); $i++) {
			if ($outdat[$i] and ($outdat[$i] ne "0")) {
				$tda .= $outdat[$i] . " ";
			}
		}
		print qq{<div class="p5bo"><div class="br-b b">$tda</div></div>};
		if ($tftable eq "funct_tf") {
			my $tf = $dbh->create_tf;
			my $complex = $tf->get_tfcomplex_by_id($tfid,"notargets");
			my $ptfd = &wpid($tfid,"TF");
			my $cn = $complex->name;
			if (length($cn) > 28) {
				$cn = qq{<div onclick="popup(this,'$cn','rt');" class="popup">} . substr($cn,0,26) . "..." . qq{</div>};
			}
			print qq{<div><a class="b" href="$pazar_cgi/tf_search.cgi?ID_list=PAZAR_TF&amp;geneID=$ptfd&amp;excluded=$xc">$ptfd</a></div><div class="b">$cn</div>};
		} elsif ($tftable eq "sample") {
			my @sa = $dbh->get_data_by_primary_key("sample",$tfid);
			my @sc = $dbh->get_data_by_primary_key("cell",$sa[1]);
			print qq{$sa[0] $sc[0]};
		} else {
			print qq{(unknown)};
		}
		print qq{</td>};
	}
	print qq{</tr>};
	$bg_color = 1 - $bg_color;
}
print "</table></div>";
my $temptail = HTML::Template->new(filename => "$pazarcgipath/tail.tmpl");
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
sub select {
	my ($dbh,$sql) = @_;
	my $sth = $dbh->prepare($sql);
	$sth->execute or die "$dbh->errstr\n";
	return $sth;
}
sub wpid {
	my ($id,$type) = @_;
	my $id7d = sprintf "%07d", $id;
	my $pzid = $type . $id7d;
	return $pzid;
}
sub convert_id {
	my ($auxdb,$genedb,$geneid,$ens) = @_;
	undef my @id;
	my $add = $genedb . "_to_llid";
	@id = $auxdb->$add($geneid);
	my $ll = $id[0];
	my @ensembl;
	if ($ll) { 
		@ensembl = $ens?$ens:$auxdb->llid_to_ens($ll) ;
	}
	return $ensembl[0];
}