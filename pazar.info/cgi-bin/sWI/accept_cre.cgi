#!/usr/bin/perl

use CGI qw( :all);
#use CGI::Debug(report => everything, on => anything);
use pazar::talk;
use pazar;
use pazar::reg_seq;

my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazarcgipath = $ENV{PAZARCGIPATH};

require "$pazarcgipath/getsession.pl";

#SYNOPSYS: Addin TF that interact with the target sequence and each other to produce a certain effect

my $query=new CGI;
my %params = %{$query->Vars};

my $user=$info{user};
my $pass=$info{pass};
my $analysis=$params{'aname'};
#my $an_desc=$params{'analysis_desc'};
my $auxDB=$params{'auxDB'};
my $proj=$params{'project'};

print $query->header;

my $pazar=new 
    pazar(-drv=>$ENV{PAZAR_drv},-dbname=>$ENV{PAZAR_name},-user=>$ENV{PAZAR_pubuser},-pazar_user=>$user, -pazar_pass=>$pass,
	  -pass=>$ENV{PAZAR_pubpass}, -project=>$params{project}, -host=>$ENV{PAZAR_host});

my $ensdb = pazar::talk->new(DB=>'ensembl',PORT => $ENV{ENS_PORT},ENSEMBL_DATABASES_HOST => $ENV{ENSEMBL_DATABASES_HOST},ENSEMBL_DATABASES_USER => $ENV{ENSEMBL_DATABASES_USER},ENSEMBL_DATABASES_PASS => $ENV{ENSEMBL_DATABASES_PASS},USER=>$ENV{ENS_USER},PASS=>$ENV{ENS_PASS},HOST=>$ENV{ENS_HOST},DRV=>'mysql');

my $gkdb = pazar::talk->new(DB=>'genekeydb',USER=>$ENV{GKDB_USER},PASS=>$ENV{GKDB_PASS},HOST=>$ENV{GKDB_HOST},DRV=>'mysql');

my ($regid,$type);
if (($params{reg_type})&&($params{reg_type}=~/construct/)) {
    eval {$regid=store_artifical($pazar,$query,\%params);};
    $type='construct';
} elsif (($params{reg_type})&&($params{reg_type}=~/reg_seq/)) {
    eval {$regid=store_natural($pazar,$ensdb,$gkdb,$query,\%params);};
    $type='reg_seq';
}
if ($@) {
    print "<h3>An error occured! Please contact us to report the bug with the following error message:<br>$@</h3>";
    exit();
}
print "<body onload='document.F1.submit();'><form action='$pazar_cgi/sWI/geneselect.cgi' method='post' name='F1'><input type='hidden' name='project' value='$proj'></form></body></html>";


sub store_natural {
my ($pazar,$ensdb,$gkdb,$query,$params)=@_;
my %params=%{$params};

my $accn = $params{'gid'}||$params{'hidgid'};
$accn=~s/\s//g;
my $dbaccn = $params{'genedb'};
my $taccn = $params{'tid'};
$taccn=~s/\s//g;
my $dbtrans = $params{'transdb'};

my ($ens,$err);
if ($dbaccn eq 'EnsEMBL_gene') {
    unless ($accn=~/\w{4,}\d{6,}/) {print "<h3>An error occured! Check that the provided ID ($accn) is a $dbaccn ID!</h3>You will have the best results using an EnsEMBL gene ID!"; exit;} else {
	$ens=$accn;
    }
} elsif ($dbaccn eq 'EnsEMBL_transcript') {
    my @gene = $ensdb->ens_transcr_to_gene($accn);
    $ens=$gene[0];
    unless ($ens=~/\w{4,}\d{6,}/) {print "<h3>An error occured! Check that the provided ID ($accn) is a $dbaccn ID!</h3>You will have the best results using an EnsEMBL gene ID!"; exit;}
} elsif ($dbaccn eq 'EntrezGene') {
    my $species=$gkdb->llid_to_org($accn);
    if (!$species) {print "<h3>An error occured! Check that the provided ID ($accn) is a $dbaccn ID!</h3>You will have the best results using an EnsEMBL gene ID!"; exit;}
    $ensdb->change_mart_organism($species);
    my @gene=$ensdb->llid_to_ens($accn);
    $ens=$gene[0];
    unless ($ens=~/\w{4,}\d{6,}/) {print "<h3>An error occured! Check that the provided ID ($accn) is a $dbaccn ID!</h3>You will have the best results using an EnsEMBL gene ID!"; exit;}
} else {
    $ens = convert_id($ensdb,$gkdb,$dbaccn,$accn);
    if (!$ens) {print "<h3>An error occured! Check that the provided ID ($accn) is a $dbaccn ID!</h3>You will have the best results using an EnsEMBL gene ID!"; exit;}
}
unless ($ens) {print "<h3>An error occured! Check that the provided ID ($accn) is a $dbaccn ID!</h3>You will have the best results using an EnsEMBL gene ID!"; exit; } #Error message her - gene not in DB
my $gene=$ens;

if ($taccn && $taccn ne '') {
    if ($dbtrans=~/ensembl/i) {
	my ($gene_chk)=$ensdb->ens_transcr_to_gene($taccn);
	unless ($gene_chk eq $ens) { print "<h3>An error occured! Check that the provided transcript ID matches the gene ID!</h3>You will have the best results using EnsEMBL IDs!"; exit;}
    } elsif ($dbtrans=~/refseq/i) {
	my ($trans)=$ensdb->nm_to_enst($taccn);
	if ($trans=~/\w{2,}/) { $taccn=$trans; } else {print "<h3>An error occured! Check that the provided ID ($taccn) is a $dbtrans ID!</h3>You will have the best results using an EnsEMBL ID!"; exit;}
	my ($gene_chk)=$ensdb->ens_transcr_to_gene($taccn);
	unless ($gene_chk eq $ens) { print "<h3>An error occured! Check that the provided transcript ID matches the gene ID!</h3>You will have the best results using EnsEMBL IDs!"; exit;}
    } elsif ($dbtrans=~/swissprot/i) {
	my ($trans)=$ensdb->swissprot_to_enst($taccn);
	if ($trans=~/\w{2,}/) { $taccn=$trans; } else {print "<h3>An error occured! Check that the provided ID ($taccn) is a $dbtrans ID!</h3>You will have the best results using an EnsEMBL ID!"; exit;}
	my ($gene_chk)=$ensdb->ens_transcr_to_gene($taccn);
	unless ($gene_chk eq $ens) { print "<h3>An error occured! Check that the provided transcript ID matches the gene ID!</h3>You will have the best results using EnsEMBL IDs!"; exit;}
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
if (uc($params{chromosome}) ne uc($chr)) {
print $query->h3("Your gene $accn is not on the selected chromosome $params{chromosome}!");
exit;
}
my $org=$ensdb->current_org();
if (uc($params{organism}) ne uc($org)) {
print $query->h3("Your gene $accn is not from the selected organism $params{organism}!");
exit;
}
my $seq=&getseq($ensdb,$chr,$params{start},$params{end});
my $strand;
if ($params{sequence} && $params{sequence} ne '') {
    my $element=$params{sequence};
    $element=~s/\s*//g;
    if ($element=~/[^agctnAGCTN]/) {
	print $query->h3("Unknown character used in the sequence<br>$element<br>");
	exit();
    }
    if (uc($seq) ne uc($element)) {
#reverse complement the seq
	my $rcseq = reverse ($seq);
	$rcseq =~ tr/ACTGactg/TGACtgac/;
	$seq=$rcseq;
	if (uc($seq) ne uc($element)) {
	    print $query->h3("The provided sequence $element doesn't fit with the provided coordinates!<br>Please use the Get Chromosome Coordinates button to fetch the correct coordinates!");
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

unless ($pazar) {
    print $query->h3("Could not connect to pazar");
    exit;
}
my $giddesc=$params{giddesc}||$params{hidgiddesc};

my $regseq=pazar::reg_seq->new(
			  -pazar=>$pazar,
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
                          -gene_description=>$giddesc,
                          -gene_dbname=>'EnsEMBL',
                          -gene_dbassembly=>$build,
                          -transcript_accession=>$taccn,
                          -transcript_dbname=>'EnsEMBL',
                          -transcript_dbassembly=>$build,
                          -transcript_fuzzy_start=>$params{fstart}||$tss,
                          -transcript_fuzzy_end=>$params{fend}||$tss);

my $rsid=pazar::reg_seq->store_reg_seq($pazar,$regseq);
return $rsid;
}

sub store_artifical {
    my ($pazar,$query,$params)=@_;
    my %params=%{$params};
    my $element=$params{csequence};
    $element=~s/\s*//g;
    if ($element=~/[^agctnAGCTN]/) {
	print $query->h3("Unknown character used in the sequence<br>$element<br>");
	exit();
    }
    return $pazar->table_insert('construct',$params{constructname},$params{artificialcomment},$element);
}

sub getseq {
my ($ensdb,$chr,$begin,$end)=@_;
my $sadapt=$ensdb->get_ens_adaptor;
my $adapt=$sadapt->get_SliceAdaptor();
my $slice = $adapt->fetch_by_region('chromosome',$chr,$begin,$end);
return $slice->seq;
}

sub convert_id {
 my ($ensdb,$gkdb,$genedb,$geneid)=@_;
undef my @id;
 my $add=$genedb . "_to_llid";
# print "Working on $geneid in $genedb; $add";
 @id=$gkdb->$add($geneid);
 my $ll=$id[0];
 my @gene;
 if ($ll) {
   my $species=$gkdb->llid_to_org($ll);
   if (!$species) {print "<h3>An error occured! Check that the provided ID ($geneid) is a $genedb ID!</h3>You will have the best results using an EnsEMBL gene ID!"; exit;}
   $ensdb->change_mart_organism($species);
   @gene=$ensdb->llid_to_ens($ll);
 }
 return $gene[0];
}

