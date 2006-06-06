#!/usr/bin/perl

use CGI qw( :all);
use CGI::Debug(report => everything, on => anything);
use pazar::talk;
use pazar;
use pazar::reg_seq;

require '../getsession.pl';

#SYNOPSYS: Addin TF that interact with the target sequence and each other to produce a certain effect
my $docroot=$ENV{PAZARHTDOCSPATH}.'/sWI';
my $cgiroot=$ENV{SERVER_NAME}.$ENV{PAZARCGI}.'/sWI';

my $sitepage="$docroot/creanalysis.htm";
my $evidpage="$docroot/condition1.htm";

my $query=new CGI;
my %params = %{$query->Vars};

my $input = $params{'submit'};
my $user=$info{user};
my $pass=$info{pass};
my $analysis=$params{'aname'};
my $an_desc=$params{'analysis_desc'};
my $auxDB=$params{'auxDB'};
my $proj=$params{'project'};

print $query->header;

my $pazar=new 
pazar(-drv=>'mysql',-dbname=>$ENV{PAZAR_name},-user=>$ENV{PAZAR_pubuser},-pazar_user=>$user, -pazar_pass=>$pass,
                        -pass=>$ENV{PAZAR_pubpass}, -project=>$params{project}, -host=>$ENV{PAZAR_host});

my $ensdb = pazar::talk->new(DB=>'ensembl',USER=>$ENV{ENS_USER},PASS=>$ENV{ENS_PASS},HOST=>$ENV{ENS_HOST},DRV=>'mysql');

my $gkdb = pazar::talk->new(DB=>'genekeydb',USER=>$ENV{GKDB_USER},PASS=>$ENV{GKDB_PASS},HOST=>$ENV{GKDB_HOST},DRV=>'mysql');


my ($regid,$type);
if (($params{reg_type})&&($params{reg_type}=~/construct/)) {
    $regid=store_artifical($pazar,$query,\%params);
    $type='construct';
} elsif (($params{reg_type})&&($params{reg_type}=~/reg_seq/)) {
    $regid=store_natural($pazar,$ensdb,$gkdb,$query,\%params);
    $type='reg_seq';
}
$pazar->add_input($type,$regid);
my ($cellid,$refid,$methid);
if (($params{newmethod})&&($params{newmethod}=~/[\w\d]/)) {
    $methid=$pazar->table_insert('method',$params{newmethod},$params{newmethoddesc});
}
else {
    my $meth=$params{methodname}||'NA';
    $methid=$pazar->get_method_id_by_name($meth);
}
if (($params{cell})&&($params{cell}=~/[\w\d]/)) {
    $cellid=$pazar->table_insert('cell',$params{cell},$params{tissue},$params{cellstat},'na',$params{organism});
}
if (($params{reference})&&($params{reference}=~/[\w\d]/)) {
    $refid=$pazar->table_insert('ref',$params{reference});
}
#Let's make sure initial manual submissions are categorized as curated, but provisional 
my $evidid=$pazar->table_insert('evidence','curated','provisional');

my $timeid;
if ($params{time_dev}!=0 || $params{range_start}!=0 || $params{range_end}!=0) {
    $timeid=$pazar->table_insert('time',$params{time_dev},$params{dev_desc},$params{dev_tscale},$params{range_start},$params{range_end});
}

$methid||=0;
$cellid||=0;
$refid||=0;
$evidid||=0;
$timeid||=0;
my $aid=&check_aname($pazar,$params{aname},$params{project},$info{userid},$evidid,$methid,$cellid,$timeid,$refid,$params{analysis_desc});

my @conds;
if ($params{env_comp} && $params{env_comp} ne '') {
    my $conc=$params{env_conc}||'na';
    my $molecule=$params{env_comp}||'na';
    my $scale=$params{env_scale}||'na';
    $condid=$pazar->table_insert('bio_condition','environmental',$molecule,'na',$conc,$scale);
    $pazar->add_input('bio_condition',$condid);
    push @conds,$condid;
}
if ($params{phys_cond} && $params{phys_cond} ne '') {
    my $conc=$params{phys_quant}||'na';
    my $scale=$params{phys_scale}||'na';
    my $physid=$pazar->table_insert('bio_condition','physical','na',$params{phys_cond},$conc,$scale);
    $pazar->add_input('bio_condition',$physid);
    push @conds,$condid;
}
my ($quant,$qual,$qscale);
if ($params{effect_grp} eq 'quan' && $params{effect0} && $params{effect0} ne ''){$quant=$params{effect0}; $qscale=$params{effectscale};}
else { $qual=$params{effectqual}||'NA'; }
my $expression=$pazar->table_insert('expression',$qual,$quant,$qscale,'');
$pazar->add_output('expression',$expression);

$pazar->store_analysis($aid);
$pazar->reset_inputs;
$pazar->reset_outputs;

print $query->h1("Submission successful!");
if ($type eq 'reg_seq') {
    print $query->h2("You can add Mutation information or close this window now");
    print $query->start_form(-method=>'POST',
			     -action=>"http://$cgiroot/addmutation.cgi", -name=>'mut');
    &forward_args($query,\%params);
    print $query->hidden(-name=>'tfid',-value=>$tfid);
    print $query->hidden(-name=>'aid',-value=>$aid);
    print $query->hidden(-name=>'regid',-value=>$regid);
    my $conds;
    if (@conds) {
	$conds=join(":",@conds);
	print $query->hidden(-name=>'conds',-value=>$conds);
    }
    print $query->hidden(-name=>'modeAdd',-value=>'Add');
    print $query->hidden(-name=>'effect',-value=>'expression');
    print $query->submit(-name=>'submit',
			 -value=>'Add Mutation Information',);
    print $query->br;
    print $query->br;
} else {
    print $query->h2("Please close this window now");
}
print $query->button(-name=>'close',
		     -value=>'Close window',
		     -onClick=>"window.close()");
print $query->br;
print $query->end_form;
exit;

sub check_TF {
    my ($db,$tf)=@_;

    my $ensdb = pazar::talk->new(DB=>'ensembl',USER=>$ENV{ENS_USER},PASS=>$ENV{ENS_PASS},HOST=>$ENV{ENS_HOST},DRV=>'mysql');

    my $gkdb = pazar::talk->new(DB=>'genekeydb',USER=>$ENV{GKDB_USER},PASS=>$ENV{GKDB_PASS},HOST=>$ENV{GKDB_HOST},DRV=>'mysql');

    my %factors;
    for (my $i=0;$i<@$db;$i++) {
	my $accn=@$tf[$i];
	my $dbaccn=@$db[$i];
	my @trans;
	if ($dbaccn eq 'EnsEMBL_gene') {
	    @trans = $gkdb->ens_transcripts_by_gene($accn);
	    unless ($trans[0]=~/\w{4,}\d{6,}/) {print "<p class=\"warning\">Conversion failed for $accn! Maybe it is not a $dbaccn ID!</p>"; exit;}
	} elsif ($dbaccn eq 'EnsEMBL_transcript') {
	    push @trans,$accn;
	    unless ($trans[0]=~/\w{4,}\d{6,}/) {print "<p class=\"warning\">Conversion failed for $accn! Maybe it is not a $dbaccn ID!</p>"; exit;}
	} elsif ($dbaccn eq 'EntrezGene') {
	    my @gene=$gkdb->llid_to_ens($accn);
	    unless ($gene[0]=~/\w{4,}\d{6,}/) {print "<p class=\"warning\">Conversion failed for $accn! Maybe it is not a $dbaccn ID!</p>"; exit;}
	    @trans = $gkdb->ens_transcripts_by_gene($gene[0]);
	} elsif ($dbaccn eq 'refseq') {
	    @trans=$gkdb->nm_to_enst($accn);
	    unless ($trans[0]=~/\w{4,}\d{6,}/) {print "<p class=\"warning\">Conversion failed for $accn! Maybe it is not a $dbaccn ID!</p>"; exit;}
	} elsif ($dbaccn eq 'swissprot') {
	    my $sp=$gkdb->{dbh}->prepare("select organism from ll_locus a, gk_ll2sprot b where a.ll_id=b.ll_id and sprot_id=?")||die;
	    $sp->execute($accn)||die;
	    my $species=$sp->fetchrow_array();
	    if (!$species) {print "<p class=\"warning\">Conversion failed for $accn! Maybe it is not a $dbaccn ID!</p>"; exit;}
	    $ensdb->change_mart_organism($species);
	    @trans =$ensdb->swissprot_to_enst($accn);
	    unless ($trans[0]=~/\w{4,}\d{6,}/) {print "<p class=\"warning\">Conversion failed for $accn! Maybe it is not a $dbaccn ID!</p>"; exit;}
	}
	$factors{$accn}=$trans[0];
    }
    return \%factors;
}

sub store_TFs {
my ($pazar,$ensdb,$params)=@_;
#Scanning
#print Dumper($params);
%params=%{$params};
my $tf;
my @lookup=qw(TF TFDB ENS_TF family class modifications); #Valid properties of a subunit
$tf->{function}->{modifications}=$params{modifications};
my $tf=new pazar::tf::tfcomplex(name=>$params{TFcomplex},pmed=>$params{pubmed});
my ($tfdat);
foreach my $key (keys %params) {
    my ($quant,$qual,$qscale);
    if ($key=~/inttype/i) {
	if ($params{inttype} eq 'quan' && $params{interact0} && $params{interact0} ne ''){$quant=$params{interact0}; $qscale=$params{interactscale};}
	else { $qual=$params{qual}||'NA'; }
	$pazar->store_interaction($qual,$quant,$qscale);
	next;
    }
    next unless ($key=~/\d/);
    my $ind=$key;
    $ind=~s/\D//g; #Index only
    my $nkey=$key;
    $nkey=~s/\d//; #Tag only
    next unless (grep(/\b$nkey\b/,@lookup));
    $tfdat->[$ind]->{$nkey}=$params{$key}; #Object created, pass it to regdb, should put here the TF_complex general data too!
}
foreach my $udef (@$tfdat) {
    my $tid=$udef->{ENS_TF};
    my $gid=$ensdb->ens_transcr_to_gene($tid);
    my $build=$ensdb->current_release;
    my $sunit=new pazar::tf::subunit(tid=>$tid,tdb=>'EnsEMBL',class=>$udef->{class},family=>$udef->{family},gdb=>'ensembl',id=>$gid,
                                tdb_build=>$build,gdb_build=>$build,mod=>$udef->{modifications});

    $tf->add_subunit($sunit);
}

return $pazar->store_TF_complex($tf);
}

sub store_natural {
my ($pazar,$ensdb,$gkdb,$query,$params)=@_;
my %params=%{$params};

my $accn = $params{'gid'};
my $dbaccn = $params{'genedb'};
my $taccn = $params{'tid'};
my $dbtrans = $params{'transdb'};

my ($ens,$err);
if ($dbaccn eq 'EnsEMBL_gene') {
    unless ($accn=~/\w{4,}\d{6,}/) {print "<p class=\"warning\">Conversion failed for $accn! Maybe it is not a $dbaccn ID!</p>"; exit;} else {
	$ens=$accn;
    }
} elsif ($dbaccn eq 'EnsEMBL_transcript') {
    my @gene = $ensdb->ens_transcr_to_gene($accn);
    $ens=$gene[0];
    unless ($ens=~/\w{4,}\d{6,}/) {print "<p class=\"warning\">Conversion failed for $accn! Maybe it is not a $dbaccn ID!</p>"; exit;}
} elsif ($dbaccn eq 'EntrezGene') {
    my @gene=$gkdb->llid_to_ens($accn);
    $ens=$gene[0];
    unless ($ens=~/\w{4,}\d{6,}/) {print "<p class=\"warning\">Conversion failed for $accn! Maybe it is not a $dbaccn ID!</p>"; exit;}
} else {
    ($ens,$err) =convert_id($gkdb,$dbaccn,$accn);
    if (!$ens) {print "<p class=\"warning\">Conversion failed for $accn! Maybe it is not a $dbaccn ID!</p>"; exit;}
}
unless ($ens) {print_self($query,"Gene $accn not found $err",1); exit(0); } #Error message her - gene not in DB
my $gene=$ens;

if ($taccn && $taccn ne '') {
    if ($dbtrans=~/ensembl/i) {
	my ($gene_chk)=$ensdb->ens_transcr_to_gene($taccn);
	die "your transcript ID doesn't match your gene ID!" unless ($gene_chk eq $ens);
    } elsif ($dbtrans=~/refseq/i) {
	my ($trans)=$ensdb->nm_to_enst($taccn);
	if ($trans=~/\w{2,}/) { $taccn=$trans; } else {die "Conversion failed for $taccn";}
	my ($gene_chk)=$ensdb->ens_transcr_to_gene($taccn);
	die "your transcript ID doesn't match your gene ID!" unless ($gene_chk eq $ens);
    } elsif ($dbtrans=~/swissprot/i) {
	my ($trans)=$ensdb->swissprot_to_enst($taccn);
	if ($trans=~/\w{2,}/) { $taccn=$trans; } else {die "Conversion failed for $taccn";}
	my ($gene_chk)=$ensdb->ens_transcr_to_gene($taccn);
	die "your transcript ID doesn't match your gene ID!" unless ($gene_chk eq $ens);
    }
    $gene=$taccn;
}

my ($chr,$build,$begin,$end,$orient)=$ensdb->get_ens_chr($gene);
my $tss;
if ($orient==1) {
    $tss=$begin;
} elsif ($orient==-1) {
    $tss=$end;
}
if ($params{chromosome} ne $chr) {
print $query->h3("Your gene $params{gid} is not on the selected chromosome $params{chromosome}!");
exit;
}
my $org=$ensdb->current_org();
if ($params{organism} ne $org) {
print $query->h3("Your gene $params{gid} is not from the selected organism $params{organism}!");
exit;
}
my $seq=&getseq($chr,$params{start},$params{end});
my $strand;
if ($params{sequence} && $params{sequence} ne '') {
    if (uc($seq) ne uc($params{sequence})) {
#reverse complement the seq
	my $rcseq = reverse ($seq);
	$rcseq =~ tr/ACTGactg/TGACtgac/;
	$seq=$rcseq;
	if (uc($seq) ne uc($params{sequence})) {
	    print $query->h3("The provided sequence $params{sequence} doesn't fit with the provided coordinates!<br>Please use the Get Chromosome Coordinates button to fetch the correct coordinates!");
	    exit;
	} else {
	    $strand='-';
	}
    } else {
	$strand='+';
    }
    if ($params{str} && $params{str} ne $strand) {
	print $query->h3("The provided strand $params{str} doesn't seem to be correct!<br>Please use the Get Chromosome Coordinates button to fetch the correct coordinates!");
	exit;
    }
} else {
    if ($params{str} eq '-') {
	my $rcseq = reverse ($seq);
	$rcseq =~ tr/ACTGactg/TGACtgac/;
	$seq=$rcseq;
	$strand='-';
    } else {
	$strand='+';
    }
}

die "Could not connect to pazar" unless ($pazar);

my $regseq=pazar::reg_seq->new(
                          -seq=>$seq,
                          -id=>$params{seqname},
                          -quality=>$params{quality},
                          -chromosome=>$chr, 
                          -start=>$params{start},
                          -end=>$params{end},
                          -strand=>$strand,
                          -binomial_species=>$org,
                          -seq_dbname=>'EnsEMBL',
                          -seq_dbassembly=>$build,
                          -gene_accession=>$ens,
                          -gene_description=>$params{giddesc},
                          -gene_dbname=>'EnsEMBL',
                          -gene_dbassembly=>$build,
                          -transcript_accession=>$taccn,
                          -transcript_dbname=>'EnsEMBL',
                          -transcript_dbassembly=>$build,
                          -transcript_fuzzy_start=>$params{fstart}||$tss,
                          -transcript_fuzzy_end=>$params{fend}||$tss);

my $rsid=$pazar->store_reg_seq($regseq);
return $rsid;
}

sub store_artifical {
    my ($pazar,$query,$params)=@_;
    my %params=%{$params};
    return $pazar->table_insert('construct',$params{constructname},$params{artificialcomment},$params{sequence});
}

sub getseq {
my ($chr,$begin,$end)=@_;
my $sadapt=$ensdb->get_ens_adaptor;
my $adapt=$sadapt->get_SliceAdaptor();
my $slice = $adapt->fetch_by_region('chromosome',$chr,$begin,$end);
return $slice->seq;
}

sub convert_id {
 my ($auxdb,$genedb,$geneid,$ens)=@_;
undef my @id;
 my $add=$genedb . "_to_llid";
# print "Working on $geneid in $genedb; $add";
 @id=$auxdb->$add($geneid);
 my $ll=$id[0];
 my @ensembl;
if ($ll) { 
  @ensembl=$ens?$ens:$auxdb->llid_to_ens($ll) ;
}
return $ensembl[0];
}

sub check_aname {
    my ($pazar,$aname,$proj,$userid,$evidid,$methid,$cellid,$timeid,$refid,$desc)=@_;
    $aname=uc($aname);
    my $projid=$pazar->get_projectid;
    my $dh=$pazar->prepare("select count(*) from analysis where project_id='$projid' and name=?")||die;
    my $unique=0;
    my $i=1;
    my $aid;
    while ($unique==0) {
	$aid=$pazar->get_primary_key('analysis',$userid,$evidid,$aname,$methid,$cellid,$timeid,$refid,$desc);
	if ($aid) {
	    return $aid;
	} else {
	    $dh->execute($aname)||die;
	    my $exist=$dh->fetchrow_array;
	    if ($exist) {
		$aname=$aname.'_'.$i;
		$i++;
	    } else {
		$unique=1;
	    }
	}
    }
    $aid=$pazar->table_insert('analysis',$userid,$evidid,$aname,$methid,$cellid,$timeid,$refid,$desc);
    return $aid;
}

sub forward_args {
    my ($query,$params)=@_;
    my %params=%{$params};
foreach my $key (keys %params) {
    print $query->hidden($key,$params{$key});
}

}
