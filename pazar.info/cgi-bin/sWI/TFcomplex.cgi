#!/usr/bin/perl

use CGI qw( :all);
#use CGI::Debug(report => everything, on => anything);
use pazar::talk;
use pazar;
use pazar::reg_seq;
use pazar::tf;
use pazar::tf::tfcomplex;
use pazar::tf::subunit;

require '../getsession.pl';

#SYNOPSYS: Addin TF that interact with the target sequence and each other to produce a certain effect
my $docroot=$ENV{PAZARHTDOCSPATH}.'/sWI';
my $cgiroot=$ENV{SERVER_NAME}.$ENV{PAZARCGI}.'/sWI';

my $selfpage="$docroot/TF_complex.htm";

my @voc=qw(TF TFDB  family class modifications);
my $query=new CGI;
my %params = %{$query->Vars};

my (%tf,%tfdb,%class,%family,%modif,%seen,%interact);
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

SUBMIT: {
if ($input =~/cancel/i) {  exit();}
if ($params{'Add'}) { last SUBMIT;} #Do what you normally do (add and write)
if ($input=~/done/i) { &next_page($user,$pass,\%params,$query); exit();}#JUst in case we decide we need more stuff to add
}

#TODO: checks recognizing the genes
open (SELF,$selfpage)||die "Cannot open $selfpage";

my $i=grep(/TFDB/,keys %params);
my $k=1;
my $next=$i;
#$next=$i+1 if ($i>0);


#print "Next is : $next i is $i";
foreach my $key (keys %params) {
            next if ($key eq 'aname')||($key=~/TFcomplex/)||($key eq 'project')||($key eq 'analysis_desc');
            #print $key,"__";
            if ((($key=~/TF\d/i)||($key=~/TF$/i))&&($key!~/AddTF/)) { my $id=$key; $id=~s/\D//g; $id=$id=~/d/?$id:$next; $tf{$id}=$params{$key};}
            if ($key=~/TFDB/i) { my $id=$key; $id=~s/\D//g; $id=$id=~/d/?$id:$next; $tfdb{$id}=$params{$key}; }
            if ($key=~/class/i) { my $id=$key; $id=~s/\D//g; $id=$id=~/d/?$id:$next; $class{$id}=$params{$key}; }
            if ($key=~/family/i) { my $id=$key; $id=~s/\D//g; $id=$id=~/d/?$id:$next; $family{$id}=$params{$key}; }
            if ($key=~/interact/i) { my $id=$key; $id=~s/\D//g; $id=$id=~/d/?$id:$next; $interact{$id}=$params{$key}; }
            if ($key=~/modific/i) { my $id=$key; $id=~s/\D//g; $id=$id=~/\d/?$id:$next; $modif{$id}=$params{$key};  }
            
            print "\<input name=\"$key\" type=\"hidden\" value=\"$params{$key}\"\>"; 
}
my $started=1;
while (my $buf=<SELF>) {
    $buf=~s/serverpath/$cgiroot/;
    if ($buf=~/validateForm/) {
        print $buf;
        next;
    }
#    if (($buf=~/modifications/i)&&($params{modifications})) {
#        $buf=~s/name/value=\"$params{modifications}\" name/;
#    }
#       if (($buf=~/organism/i)&&($params{organism})) {
#        $buf=~s/name/value=\"$params{organism}\" name/;
#    }
    if (($buf=~/pubmed/i)&&($params{pubmed})) {
        $buf=~s/name/value=\"$params{pubmed}\" name/;
    }
    if (($buf=~/TFcomplex/i)&&($params{TFcomplex})) {
        $buf=~s/name/value=\"$params{TFcomplex}\" name/;
    }
    print $buf;
    if ($buf=~/body/i) {$seen{body}++;}
    if ($buf=~/\<form/i) {$seen{form}++;} 
    if ($buf=~/pubmed/i) {$seen{modif}++;} 
    if (($buf=~/\<hr\>/)&&($seen{modif})&&($started)) { 
        $started=0;
	&forward_args();
#        for my $j (1..$i) {
#            my $k1='TF' . $j;
#	        my $k2='TFDB' . $j;
#	        my $sel=uc($params{$k2});
        print $query->br;
        
        foreach my $k (1..$i) {
            print "Added complex member $k",$query->br;
            foreach my $key (@voc) {
                my $addon;
                $addon=$k-1 if ($i>0);
                my $ukey=$key . ($addon?$addon:'');
                my $lkey=$key . $k;
                #print "UKEY $ukey:";
                my $val;
                #print "k is $k";
	      VAL: {
		  if ($key eq 'TF') {$val=$tf{$k}; last VAL;}
		  if ($key eq 'TFDB') {$val=$tfdb{$k}; last VAL;}
		  if ($key eq 'class') {$val=$class{$k}; last VAL;}
		  if ($key eq 'family') {$val=$family{$k}; last VAL;}
		  if ($key eq 'interact') {$val=$interact{$k}; last VAL;}
		  if ($key eq 'modifications') {$val=$modif{$k}; next VAL;}
	      }
                print $lkey,' ',$query->textfield (-label=>$lkey,-name=>$lkey,-size=>16, -value=>$val), $query->br; 
            }
            print $query->hr;
        }
    }
    if ($buf=~m/Method \(select from list/) {
	my @methods;
	push @methods,('',$pazar->get_method_names);
	print $query->scrolling_list('methodname',\@methods,1,'true');
    }
}
exit();

sub forward_args {
my @voc=qw(TF TFDB family class modifications TFcomplex cell cellstat interact0 interactscale inttype methodname newmethod newmethoddesc pubmed reference tissue);
foreach my $key (keys %params) {
    unless (grep(/^$key$/,@voc)) {
	print $query->hidden($key,$params{$key});
    }
}
}

sub next_page {
    my ($user,$pass,$params,$query)=@_;
    my %params=%{$params};
    unless ($user&&$pass) {
	print $query->h3("An error occurred- not a valid user?\n If you believe this is an error, e-mail us and describe the problem");
	exit();
    }
    my @numbered=qw(TF TFDB interact class family modifications);
    my @db;
    foreach my $dbkey (grep(/TFDB/,keys %params)) {
	push @db, $params{$dbkey};
    }
    my @tf;
    foreach my $tfkey (grep(/^TF([0-9]*)$/,keys %params)) {
	push @tf, $params{$tfkey};
    }

    my $tfs=&check_TF(\@db,\@tf);
    my %tfs=%$tfs;
 #Add 0 to the 0 key
    foreach my $mp(keys %params) {
	my $key=$mp;
	if ((grep (/\b$mp\b/,@numbered))&&($mp!~/\d/)) {   
	    $key .='0' ;
	    $params{$key}=$params{$mp};
	    delete $params{$mp};
	}
	foreach my $trans (keys %tfs) {
	    if ($params{$key} eq $trans) {
		my $ens_key='ENS_'.$key;
		$params{$ens_key}=$tfs{$trans};
	    }
	}
    }
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

    $methid||=0;
    $cellid||=0;
    $refid||=0;
    $evidid||=0;
    my $aid=&check_aname($pazar,$params{aname},$params{project},$info{userid},$evidid,$methid,$cellid,$refid,$params{analysis_desc});

    my $tfid=store_TFs($pazar,$ensdb,\%params); 
    $pazar->add_input('funct_tf',$tfid);
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
	print $query->hidden(-name=>'modeAdd',-value=>'Add');
	print $query->submit(-name=>'submit',
			     -value=>'Add Mutation Information',);
	print $query->br;
	print $query->br;
    } else {
	print $query->h2("Please close this window now!");
    }
    print $query->button(-name=>'close',
			 -value=>'Close window',
			 -onClick=>"window.close()");
    print $query->br;
    print $query->end_form;
    exit;
}

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
if (uc($params{chromosome}) ne uc($chr)) {
print $query->h3("Your gene $params{gid} is not on the selected chromosome $params{chromosome}!");
exit;
}
my $org=$ensdb->current_org();
if (uc($params{organism}) ne uc($org)) {
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
    if ($params{str} && uc($params{str}) ne uc($strand)) {
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
    my ($pazar,$aname,$proj,$userid,$evidid,$methid,$cellid,$refid,$desc)=@_;
    $aname=uc($aname);
    my $projid=$pazar->get_projectid;
    my $dh=$pazar->prepare("select count(*) from analysis where project_id='$projid' and name=?")||die;
    my $unique=0;
    my $i=1;
    my $aid;
    while ($unique==0) {
	$aid=$pazar->get_primary_key('analysis',$userid,$evidid,$aname,$methid,$cellid,0,$refid,$desc);
	if ($aid) {
	    return $aid;
	    exit();
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
    $aid=$pazar->table_insert('analysis',$userid,$evidid,$aname,$methid,$cellid,'',$refid,$desc);
    return $aid;
}