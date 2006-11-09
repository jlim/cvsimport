#!/usr/bin/perl

use CGI qw( :all);
#use CGI::Debug(report => everything, on => anything);
use pazar::talk;
use pazar;
use pazar::reg_seq;
use pazar::tf;
use pazar::tf::tfcomplex;
use pazar::tf::subunit;

require '/usr/local/apache/pazar.info/cgi-bin/getsession.pl';

#SYNOPSYS: Addin TF that interact with the target sequence and each other to produce a certain effect
my $docroot=$ENV{PAZARHTDOCSPATH}.'/sWI';
my $cgiroot=$ENV{SERVER_NAME}.$ENV{PAZARCGI}.'/sWI';

my @voc=qw(TF TFDB family classe modifications);
my $query=new CGI;
my %params = %{$query->Vars};

my $selfpage;
unless ($params{'Interactadd'}) {
    $selfpage="$docroot/TF_complex.htm";
} else {
    $selfpage="$docroot/interactor.htm";
}

my (%tf,%tfdb,%class,%family,%modif,%seen,%interact);
my $input = $params{'submit'};
my $user=$info{user};
my $pass=$info{pass};
my $analysis=$params{'aname'};
my $an_desc=$params{'analysis_desc'};
my $auxDB=$params{'auxDB'};
my $proj=$params{'project'};

if ($params{'myclass'} eq 'Select from existing classes') {
    delete $params{'myclass'};
} elsif ($params{'myclass'}) {
    $params{'classe'} = $params{'myclass'};
    delete $params{'myclass'};
}
if ($params{'myfamily'} eq 'Select from existing families') {
    delete $params{'myfamily'};
} elsif ($params{'myfamily'}) {
    $params{'family'} = $params{'myfamily'};
    delete $params{'myfamily'};
}

print $query->header;

my $pazar=new 
pazar(-drv=>'mysql',-dbname=>$ENV{PAZAR_name},-user=>$ENV{PAZAR_pubuser},-pazar_user=>$user, -pazar_pass=>$pass,
                        -pass=>$ENV{PAZAR_pubpass}, -project=>$params{project}, -host=>$ENV{PAZAR_host});

my $ensdb = pazar::talk->new(DB=>'ensembl',USER=>$ENV{ENS_USER},PASS=>$ENV{ENS_PASS},HOST=>$ENV{ENS_HOST},DRV=>'mysql');

my $gkdb = pazar::talk->new(DB=>'genekeydb',USER=>$ENV{GKDB_USER},PASS=>$ENV{GKDB_PASS},HOST=>$ENV{GKDB_HOST},DRV=>'mysql');

SUBMIT: {
if ($input =~/cancel/i) {  exit();}
if ($params{'add'}) { last SUBMIT;} #Do what you normally do (add and write)
if ($input=~/submit/i||$params{'mycomplex'}) { &next_page($pazar,$ensdb,$gkdb,$user,$pass,\%params,$query); exit();}#JUst in case we decide we need more stuff to add
}

my @mytfs;
unless ($params{'add'}||$params{'Interactadd'}) {
    my @funct_tfs = $pazar->get_all_complex_ids($pazar->get_projectid);
    foreach my $funct_tf (@funct_tfs) {
	my $funct_name = $pazar->get_complex_name_by_id($funct_tf);
	my $tf = $pazar->create_tf;
	my $tfcomplex = $tf->get_tfcomplex_by_id($funct_tf,'notargets');
	my $su;
	while (my $subunit=$tfcomplex->next_subunit) {
	    if ($su) {
		$su = $su."-".$subunit->get_transcript_accession($pazar);
	    } else {
		$su = $subunit->get_transcript_accession($pazar);
	    }
	}
	push @mytfs, $funct_name." (".$su.")";
    }
}

my @classes= $pazar->get_all_classes();
my @families= $pazar->get_all_families();
my @cell_names=$pazar->get_all_cell_names;
my @tissue_names=$pazar->get_all_tissue_names;


#TODO: checks recognizing the genes
open (SELF,$selfpage)|| print $query->h3("Cannot open $selfpage");

my $i=grep(/TFDB/,keys %params);
my $k=1;
my $next=$i;
#$next=$i+1 if ($i>0);


#print "Next is : $next i is $i";
foreach my $key (keys %params) {
            next if ($key eq 'add')||($key eq 'aname')||($key=~/TFcomplex/)||($key eq 'project')||($key eq 'analysis_desc');
            #print $key,"__";
            if ((($key=~/TF\d/i)||($key=~/TF$/i))&&($key!~/AddTF/)) { my $id=$key; $id=~s/\D//g; $id=$id=~/d/?$id:$next; $tf{$id}=$params{$key};}
            if ($key=~/TFDB/i) { my $id=$key; $id=~s/\D//g; $id=$id=~/\d/?$id:$next; $tfdb{$id}=$params{$key}; }
            if ($key=~/classe/i) { my $id=$key; $id=~s/\D//g; $id=$id=~/\d/?$id:$next; $class{$id}=$params{$key}; }
            if ($key=~/family/i) { my $id=$key; $id=~s/\D//g; $id=$id=~/\d/?$id:$next; $family{$id}=$params{$key}; }
            if ($key=~/interact/i) { my $id=$key; $id=~s/\D//g; $id=$id=~/\d/?$id:$next; $interact{$id}=$params{$key}; }
            if ($key=~/modific/i) { my $id=$key; $id=~s/\D//g; $id=$id=~/\d/?$id:$next; $modif{$id}=$params{$key};  }
            
#            print "\<input name=\"$key\" type=\"hidden\" value=\"$params{$key}\"\>"; 
}
my $started=1;
while (my $buf=<SELF>) {
    $buf=~s/serverpath/$cgiroot/;
    unless (@mytfs) {
	$buf=~s/MUT\.mytfs\.disabled\=true\;//;
	$buf=~s/MUT\.mytfs\.disabled\=false\;//;
	$buf=~s/MUT\.mytfs\.focus()\;//;
    }
    if ($params{'add'}) {
	$buf=~s/disabled=true//;
	if ($buf=~/<hr color/i || $buf=~/mytf/i || $buf=~/my tf/i) {
	    next;
	}
    } 
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
    unless ($params{'add'}||$params{'Interactadd'}) {
	if ($buf=~/Select from my TFs:/i) {
	    if (@mytfs) {
		my @sorted_tfs = sort @mytfs;
		unshift @sorted_tfs, 'Select from existing TFs';
		print $query->scrolling_list('mytfs',\@sorted_tfs,1,'true');
	    } else {
		print "<p style=\"color:red\"><b>You don't have any TFs in this project yet!</b></p>";
	    }
	}
    }
    if ($buf=~/<input type=\"text\" name=\"classe\"/i && @classes) {
	my @sorted_classes = sort @classes;
	unshift @sorted_classes, 'Select from existing classes';
	print "<b>  OR  </b>";
	if ($params{'add'}) {
	    print $query->scrolling_list(-name=>'myclass',
					 -values=>\@sorted_classes,
					 -size=>1);
	} else {
	    print $query->scrolling_list(-name=>'myclass',
					 -values=>\@sorted_classes,
					 -size=>1,
					 -disabled=>true);
	}
    }
    if ($buf=~/<input type=\"text\" name=\"family\"/i && @families) {
	my @sorted_families = sort @families;
	unshift @sorted_families, 'Select from existing families';
	print "<b>  OR  </b>";
	if ($params{'add'}) {
	    print $query->scrolling_list(-name=>'myfamily',
					 -values=>\@sorted_families,
					 -size=>1);
	} else {
	    print $query->scrolling_list(-name=>'myfamily',
					 -values=>\@sorted_families,
					 -size=>1,
					 -disabled=>true);
	}
    }
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
        
        foreach my $k (1..$i) {
            print "<b>Added complex member $k</b>",$query->br,$query->br;
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
		  if ($key eq 'classe') {$val=$class{$k}; last VAL;}
		  if ($key eq 'family') {$val=$family{$k}; last VAL;}
		  if ($key eq 'interact') {$val=$interact{$k}; last VAL;}
		  if ($key eq 'modifications') {$val=$modif{$k}; next VAL;}
	      }
                print $lkey,' ',$query->textfield (-label=>$lkey,-name=>$lkey,-size=>16, -value=>$val), $query->br; 
            }
            print $query->br,$query->hr;
        }
	print $query->br;
    }
    if ($buf=~/<p>Method Name/) {
	my @methods=$pazar->get_method_names;
	my @sorted_methods = sort @methods;
	unshift @sorted_methods, 'Select from existing methods';
	print $query->scrolling_list('methodname',\@sorted_methods,1,'true');
    }
    if ($buf=~/<input name=\"cell\" type=\"text\" id=\"cell\"/i && @cell_names) {
	my @sorted_cells = sort @cell_names;
	unshift @sorted_cells, 'Select from existing cell names';
	print "<b>  OR  </b>";
	print $query->scrolling_list('mycell',\@sorted_cells,1,'true');
    }
    if ($buf=~/<input name=\"tissue\" type=\"text\" id=\"tissue\"/i && @tissue_names) {
	my @sorted_tissues = sort @tissue_names;
	unshift @sorted_tissues, 'Select from existing tissue names';
	print "<b>  OR  </b>";
	print $query->scrolling_list('mytissue',\@sorted_tissues,1,'true');
    }
    if ($buf=~/<input name=\"samplecell\" type=\"text\" id=\"samplecell\"/i && @cell_names) {
	my @sorted_cells = sort @cell_names;
	unshift @sorted_cells, 'Select from existing cell names';
	print "<b>  OR  </b>";
	print $query->scrolling_list('mysamplecell',\@sorted_cells,1,'true');
    }
    if ($buf=~/<input name=\"sampletissue\" type=\"text\" id=\"sampletissue\"/i && @tissue_names) {
	my @sorted_tissues = sort @tissue_names;
	unshift @sorted_tissues, 'Select from existing tissue names';
	print "<b>  OR  </b>";
	print $query->scrolling_list('mysampletissue',\@sorted_tissues,1,'true');
    }
}
exit();

# sub forward_args {
#     my $params=shift;
#     my %params = %{$params};
#     my @voc=qw(add TF TFDB family classe modifications TFcomplex cell cellstat interact0 interactscale inttype qual methodname newmethod newmethoddesc pubmed reference tissue cellspecies analysis_desc);
# foreach my $key (keys %params) {
#     unless (grep(/^$key$/,@voc)) {
# 	print $query->hidden($key,$params{$key});
#     }
# }
# }

# sub recopy_args {
#     my $params=shift;
#     my $buf=shift;
#     my %params = %{$params};
#     my @voc=qw(TFcomplex cell interact0 newmethod newmethoddesc pubmed reference tissue cellspecies analysis_desc);
#     my @list=qw(cellstat methodname qual interactscale);

#     foreach my $key (@evoc) {
# 	if (($buf=~/name=\"$key\"/i)&&($params{$key})) {
# 	    $buf=~s/name/value=\"$params{$key}\" name/;
# 	}
#     }
#     my @options;
# foreach my $key (@list) {
#     if (($buf=~/name=\"$key\"/i)&&($params{$key})) {
#         $buf=~s/option value=\"$params{$key}\"/option value=\"$params{$key}\";
#     }
# }

# }
sub forward_args {
my @voc=qw(add TF TFDB family classe myclass myfamily modifications TFcomplex cell cellstat mycell mytissue cellspecies interact0 interactscale intercomment inttype methodname newmethod newmethoddesc pubmed reference tissue);
foreach my $key (keys %params) {
    unless (grep(/^$key$/,@voc)) {
	print $query->hidden($key,$params{$key});
    }
}
}

sub next_page {
    my ($pazar,$ensdb,$gkdb,$user,$pass,$params,$query)=@_;
    my %params=%{$params};

    unless ($user&&$pass) {
	print $query->h3("An error occurred- not a valid user?\n If you believe this is an error, e-mail us and describe the problem");
	exit();
    }
    my $tfid;
    if ($params{'mytfs'} eq 'Select from existing TFs') {
	print $query->h3("An error occurred- You have to select a TF in the list!");
	exit();
    } elsif ($params{'mytfs'}) {
	$tfid=get_TF_id($pazar,$params{'mytfs'});
    } elsif ($params{'TFcomplex'}) {
	my @numbered=qw(TF TFDB interact classe family modifications);
	my @db;
	foreach my $dbkey (grep(/TFDB/,keys %params)) {
	    push @db, $params{$dbkey};
	}
	my @tf;
	foreach my $tfkey (grep(/^TF([0-9]*)$/,keys %params)) {
	    push @tf, $params{$tfkey};
	}

	my $tfs=&check_TF($ensdb,$gkdb,\@db,\@tf);
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
	$tfid=store_TFs($pazar,$ensdb,\%params);
	unless ($tfid > 0) {
	    print $query->h2("*** TF data NOT accepted - $params{'TFcomplex'} might already exist within your project with different subunits than the one you defined! ***");
	    exit();
	}
    } elsif ($params{'sampletype'}) {

	if ($params{'mysamplecell'} eq 'Select from existing cell names') {
	    delete $params{'mysamplecell'};
	} elsif ($params{'mysamplecell'}) {
	    $params{'samplecell'} = $params{'mysamplecell'};
	    delete $params{'mysamplecell'};
	}
	if ($params{'mysampletissue'} eq 'Select from existing tissue names') {
	    delete $params{'mysampletissue'};
	} elsif ($params{'mysampletissue'}) {
	    $params{'sampletissue'} = $params{'mysampletissue'};
	    delete $params{'mysampletissue'};
	}

	unless ($params{'samplecell'} || $params{'sampletissue'}) {
	    print $query->h2("*** You must select either a cell or a tissue name for your biological sample! ***");
    exit();
	}

	my $samplecellspecies=$params{samplecellspecies}||'NA';
	my $samplecellid;
	if (($params{samplecell})&&($params{samplecell}=~/[\w\d]/)) {
	    $samplecellid=$pazar->table_insert('cell',$params{samplecell},$params{sampletissue},$params{samplecellstat},'na',$samplecellspecies);
	} elsif ($params{sampletissue}&&($params{sampletissue}=~/[\w\d]/)) {
	    $samplecellid=$pazar->table_insert('cell','na',$params{sampletissue},'na','na',$samplecellspecies);
	}
	my $sampletimeid;
	if ($params{sampletime}!=0 || $params{samplerange_start}!=0 || $params{samplerange_end}!=0) {
	    $sampletimeid=$pazar->table_insert('time',$params{sampletime},$params{sampledesc},$params{samplescale},$params{samplerange_start},$params{samplerange_end});
	}
	$sampletimeid||=0;
	$tfid=$pazar->table_insert('sample',$params{'sampletype'},$samplecellid,$sampletimeid);
    }

    if ($params{'mycell'} eq 'Select from existing cell names') {
	delete $params{'mycell'};
    } elsif ($params{'mycell'}) {
	$params{'cell'} = $params{'mycell'};
	delete $params{'mycell'};
    }
    if ($params{'mytissue'} eq 'Select from existing tissue names') {
	delete $params{'mytissue'};
    } elsif ($params{'mytissue'}) {
	$params{'tissue'} = $params{'mytissue'};
	delete $params{'mytissue'};
    }

    my ($regid,$type,$aid);
    eval {
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
    my $cellspecies=$params{cellspecies}||'NA';
    if (($params{cell})&&($params{cell}=~/[\w\d]/)) {
	$cellid=$pazar->table_insert('cell',$params{cell},$params{tissue},$params{cellstat},'na',$cellspecies);
    } elsif ($params{tissue}&&($params{tissue}=~/[\w\d]/)) {
	$cellid=$pazar->table_insert('cell','na',$params{tissue},'na','na',$cellspecies);
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
    $aid=&check_aname($pazar,$params{aname},$params{project},$info{userid},$evidid,$methid,$cellid,$refid,$params{analysis_desc});

    my ($quant,$qual,$qscale);
    if ($params{inttype} eq 'quan' && $params{interact0} && $params{interact0} ne ''){$quant=$params{interact0}; $qscale=$params{interactscale}; $qual='NA';}
    else { $qual=$params{qual}||'NA'; }
    $pazar->store_interaction($qual,$quant,$qscale,$params{intercomment});
    unless ($params{'sampletype'}) {
	$pazar->add_input('funct_tf',$tfid);
    } else {
	$pazar->add_input('sample',$tfid);
    }
    $pazar->store_analysis($aid);
    $pazar->reset_inputs;
    $pazar->reset_outputs;
};
    my $pazaraid=write_pazarid($aid,'AN');

my $JSCRIPT=<<END;
// Add a javascript
var MyChildWin=null;
function setCount(target){
    if (!MyChildWin || MyChildWin.closed ) {
	if(target == 0) {
	    document.mut.action="http://$cgiroot/addmutation.cgi";
	    document.mut.target="MyChildWin";
	    MyChildWin=window.open('about:blank','MyChildWin','height=800, width=800,toolbar=1,location=1,directories=1,status=1,scrollbars=1,menubar=1,resizable=1');
	}
    } else{
	alert('A child window is already open. Please finish your annotation before entering a new Mutation!');
	MyChildWin.focus();
	return correctSubmitHandler();
    }
}
function correctSubmitHandler(e)
{
	if (e && e.preventDefault)
		e.preventDefault();
	return false;
}
END

print $query->start_html(-title=>"Annotating experiment $pazaraid",
                         -script=>$JSCRIPT);

    if ($@) {
	print "<h3>An error occured! Please contact us to report the bug with the following error message:<br>$@</h3>";
	exit();
    }

    print $query->h1("Submission successful for experiment $pazaraid!");
    if ($type eq 'reg_seq') {
	print $query->h2("You can add Mutation information or close this window now");
	print $query->start_form(-method=>'POST',
				 -action=>'',
                                 -name=>'mut');
#	&forward_args($query,\%params);
	if ($params{'sampletype'}) {
	    print $query->hidden(-name=>'sample',-value=>'yes');
	}
	print $query->hidden(-name=>'tfid',-value=>$tfid);
	print $query->hidden(-name=>'aid',-value=>$aid);
	print $query->hidden(-name=>'regid',-value=>$regid);
	print $query->hidden(-name=>'project',-value=>$params{'project'});
	print $query->hidden(-name=>'sequence',-value=>$params{'sequence'});
	print $query->hidden(-name=>'modeAdd',-value=>'Add');
	print $query->hidden(-name=>'effect',-value=>'interaction');
	print $query->submit(-name=>'submit',
			     -value=>'Add Mutation Information',
                             -onClick=>'return setCount(0);');
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
    my ($ensdb,$gkdb,$db,$tf)=@_;

    my %factors;
    for (my $i=0;$i<@$db;$i++) {
	my $accn=@$tf[$i];
	my $dbaccn=@$db[$i];
	my @trans;
	if ($dbaccn eq 'EnsEMBL_gene') {
	    @trans = $gkdb->ens_transcripts_by_gene($accn);
	    unless ($trans[0]=~/\w{4,}\d{6,}/) {print "<h3>An error occured! Check that the provided ID ($accn) is a $dbaccn ID!</h3>You will have the best results using an EnsEMBL gene ID!"; exit;}
	} elsif ($dbaccn eq 'EnsEMBL_transcript') {
	    push @trans,$accn;
	    unless ($trans[0]=~/\w{4,}\d{6,}/) {print "<h3>An error occured! Check that the provided ID ($accn) is a $dbaccn ID!</h3>You will have the best results using an EnsEMBL gene ID!"; exit;}
	} elsif ($dbaccn eq 'EntrezGene') {
	    my @gene=$gkdb->llid_to_ens($accn);
	    unless ($gene[0]=~/\w{4,}\d{6,}/) {print "<h3>An error occured! Check that the provided ID ($accn) is a $dbaccn ID!</h3>You will have the best results using an EnsEMBL gene ID!"; exit;}
	    @trans = $gkdb->ens_transcripts_by_gene($gene[0]);
	} elsif ($dbaccn eq 'refseq') {
	    @trans=$gkdb->nm_to_enst($accn);
	    unless ($trans[0]=~/\w{4,}\d{6,}/) {print "<h3>An error occured! Check that the provided ID ($accn) is a $dbaccn ID!</h3>You will have the best results using an EnsEMBL gene ID!"; exit;}
	} elsif ($dbaccn eq 'swissprot') {
	    my $sp=$gkdb->{dbh}->prepare("select organism from ll_locus a, gk_ll2sprot b where a.ll_id=b.ll_id and sprot_id=?");
	    $sp->execute($accn);
	    my $species=$sp->fetchrow_array();
	    if (!$species) {print "<h3>An error occured! Check that the provided ID ($accn) is a $dbaccn ID!</h3>You will have the best results using an EnsEMBL gene ID!"; exit;}
	    $ensdb->change_mart_organism($species);
	    @trans =$ensdb->swissprot_to_enst($accn);
	    unless ($trans[0]=~/\w{4,}\d{6,}/) {print "<h3>An error occured! Check that the provided ID ($accn) is a $dbaccn ID!</h3>You will have the best results using an EnsEMBL gene ID!"; exit;}
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
my @lookup=qw(TF TFDB ENS_TF family classe modifications); #Valid properties of a subunit
#$tf->{function}->{modifications}=$params{modifications};
my $tf=new pazar::tf::tfcomplex(name=>$params{TFcomplex},pmed=>$params{pubmed});
my ($tfdat);
foreach my $key (keys %params) {
    if ($key=~/inttype/i) {
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
    my $sunit=new pazar::tf::subunit(tid=>$tid,tdb=>'EnsEMBL',class=>$udef->{classe},family=>$udef->{family},gdb=>'ensembl',id=>$gid,
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
    unless ($accn=~/\w{4,}\d{6,}/) {print "<h3>An error occured! Check that the provided ID ($accn) is a $dbaccn ID!</h3>You will have the best results using an EnsEMBL gene ID!"; exit;} else {
	$ens=$accn;
    }
} elsif ($dbaccn eq 'EnsEMBL_transcript') {
    my @gene = $ensdb->ens_transcr_to_gene($accn);
    $ens=$gene[0];
    unless ($ens=~/\w{4,}\d{6,}/) {print "<h3>An error occured! Check that the provided ID ($accn) is a $dbaccn ID!</h3>You will have the best results using an EnsEMBL gene ID!"; exit;}
} elsif ($dbaccn eq 'EntrezGene') {
    my @gene=$gkdb->llid_to_ens($accn);
    $ens=$gene[0];
    unless ($ens=~/\w{4,}\d{6,}/) {print "<h3>An error occured! Check that the provided ID ($accn) is a $dbaccn ID!</h3>You will have the best results using an EnsEMBL gene ID!"; exit;}
} else {
    ($ens,$err) =convert_id($gkdb,$dbaccn,$accn);
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

unless ($pazar) {
    print $query->h3("Could not connect to pazar");
    exit;
}

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
    my $element=$params{csequence};
    $element=~s/\s*//g;
    if ($element=~/[^agctnAGCTN]/) {
	print $query->h3("Unknown character used in the sequence<br>$element<br>");
	exit();
    }
    return $pazar->table_insert('construct',$params{constructname},$params{artificialcomment},$element);
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
    my $dh=$pazar->prepare("select count(*) from analysis where project_id='$projid' and name=?");
    my $unique=0;
    my $i=1;
    my $aid;
    while ($unique==0) {
	$aid=$pazar->get_primary_key('analysis',$userid,$evidid,$aname,$methid,$cellid,0,$refid,$desc);
	if ($aid) {
	    return $aid;
	} else {
	    $dh->execute($aname);
	    my $exist=$dh->fetchrow_array;
	    if ($exist) {
		if ($i>1) {
		    my $last;
		    while ($last ne '_') {
			$last=chop($aname);
		    }
		}
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

sub get_TF_id {
    my ($pazar,$tfname)=@_;

    my @tfnames = split(/ \(/,$tfname);
    my @ids=$pazar->get_complex_id_by_name($tfnames[0]);
    return $ids[0];
}

sub write_pazarid {
    my $id=shift;
    my $type=shift;
    my $id7d = sprintf "%07d",$id;
    my $pazarid=$type.$id7d;
    return $pazarid;
}
