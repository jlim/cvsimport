#!/usr/bin/perl

use CGI qw( :all);
#use CGI::Debug(report => everything, on => anything);
use pazar::talk;
use pazar;
use pazar::reg_seq;

my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazarcgipath = $ENV{PAZARCGIPATH};

require "$pazarcgipath/getsession.pl";

my $cgiroot=$pazar_cgi.'/sWI';

my $query=new CGI;
my %params = %{$query->Vars};

my $input = $params{'submit'};
my $user=$info{user};
my $pass=$info{pass};


my $pazar=new pazar(-drv=>$ENV{PAZAR_drv},-dbname=>$ENV{PAZAR_name},-user=>$ENV{PAZAR_pubuser},-pazar_user=>$user, -pazar_pass=>$pass, -pass=>$ENV{PAZAR_pubpass}, -project=>$params{project}, -host=>$ENV{PAZAR_host});

print $query->header;
my $pazaraid=write_pazarid($params{aid},'AN');

my $JSCRIPT=<<END;
// Add a javascript
var MyChildWin2=null;
function setCount_addCond(target){
    if (!MyChildWin2 || MyChildWin2.closed ) {
	if(target == 0) {
	    document.mut.action="$cgiroot/addmutation.cgi";
	    document.mut.target="MyChildWin2";
	    MyChildWin2=window.open('about:blank','MyChildWin2','height=800, width=800,toolbar=1,location=1,directories=1,status=1,scrollbars=1,menubar=1,resizable=1');
	}
    } else{
	alert('A child window is already open. Please finish your annotation before entering a new Mutation!');
	MyChildWin2.focus();
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

print $query->start_html(-title=>"Adding perturbation to experiment $pazaraid",
                         -script=>$JSCRIPT);

if ($params{modeCond}) {
    if ($params{condTF}==0 && $params{condPHYS}==0 && $params{condENV}==0) {
	print "<h3>An error occured! You haven't selected the type(s) of perturbation(s) you want to add.</h3>";
	exit();
    }

    print<<TOP_PAGE;
<form style="height: 546px;" action="$cgiroot/addcond.cgi" method="post" name="COND2">
  <h2>Add Perturbations to Experiment $pazaraid</h2>
  <hr color="black" style="width: 100%; height: 2px;">
  <hr color="black" style="width: 100%; height: 2px;">
TOP_PAGE

if ($params{condTF}>0) {
    my @mytfs;
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
    my @sorted_tfs = sort @mytfs;
    unshift @sorted_tfs, 'Select from existing TFs';

    my @classes= $pazar->get_all_classes();
    my @sorted_classes = sort @classes;
    unshift @sorted_classes, 'Select from existing classes';
    my @families= $pazar->get_all_families();
    my @sorted_families = sort @families;
    unshift @sorted_families, 'Select from existing families';

    for (my $i=0;$i<$params{condTF};$i++) {
	print<<TFCOND1;
<h4>Addition of a Transcription Factor</h4>

TFCOND1

        if (@mytfs) {
	    print "<input name=\"tftype$i\" type=\"radio\" value=\"mytftype$i\" onClick=\"COND2.mytfs$i.disabled=false;COND2.TFcomplex$i.disabled=true;COND2.pubmed$i.disabled=true;COND2.TF$i.disabled=true;COND2.TFDB$i.disabled=true;COND2.class$i.disabled=true;COND2.family$i.disabled=true;COND2.myclass$i.disabled=true;COND2.myfamily$i.disabled=true;COND2.modifications$i.disabled=true;COND2.mytfs$i.focus();\"><b>Select from my TFs:  </b>";
            my @sorted_tfs = sort @mytfs;
            unshift @sorted_tfs, 'Select from existing TFs';
            print $query->scrolling_list(-name=>"mytfs$i",
                                         -values=>\@sorted_tfs,
                                         -size=>1,
                                         -disabled=>true);
	    print "</p><p><input name=\"tftype$i\" type=\"radio\" value=\"newtftype$i\" checked=TRUE onClick=\"COND2.mytfs$i.disabled=true;COND2.TFcomplex$i.disabled=false;COND2.pubmed$i.disabled=false;COND2.TF$i.disabled=false;COND2.TFDB$i.disabled=false;COND2.class$i.disabled=false;COND2.family$i.disabled=false;COND2.myclass$i.disabled=false;COND2.myfamily$i.disabled=false;COND2.modifications$i.disabled=false;COND2.TFcomplex$i.focus();\">";
        } else {
	    print "<input name=\"tftype$i\" type=\"radio\" value=\"mytftype$i\" onClick=\"COND2.TFcomplex$i.disabled=true;COND2.pubmed$i.disabled=true;COND2.TF$i.disabled=true;COND2.TFDB$i.disabled=true;COND2.class$i.disabled=true;COND2.family$i.disabled=true;COND2.myclass$i.disabled=true;COND2.myfamily$i.disabled=true;COND2.modifications$i.disabled=true;\"><b>Select from my TFs:  </b>";
            print "<p style=\"color:red\"><b>You don't have any TFs in this project yet!</b></p>";
	    print "</p><p><input name=\"tftype$i\" type=\"radio\" value=\"newtftype$i\" checked=TRUE onClick=\"COND2.TFcomplex$i.disabled=false;COND2.pubmed$i.disabled=false;COND2.TF$i.disabled=false;COND2.TFDB$i.disabled=false;COND2.class$i.disabled=false;COND2.family$i.disabled=false;COND2.myclass$i.disabled=false;COND2.myfamily$i.disabled=false;COND2.modifications$i.disabled=false;COND2.TFcomplex$i.focus();\">";
        }

	print<<TFCOND2;
<b>Enter a new TF:</b></p>
  <p>TF complex name 
    <input name="TFcomplex$i" type="text" id="TFcomplex$i" maxlength=255></p>
  <p>Pubmed (if published) 
    <input name="pubmed$i" type="text" id="pubmed$i">
  </p>
  TF 
  <input name="TF$i" maxlength="25" type="text">
  TF Database 
  <select name="TFDB$i">
    <option value="EnsEMBL_gene">EnsEMBL
gene ID</option>
      <option value="EnsEMBL_transcript"> EnsEMBL
transcript
ID</option>
      <option value="EntrezGene"> Entrezgene ID</option>
       <option value="refseq"> RefSeq ID</option>
      <option value="swissprot"> Swissprot ID</option>
  </select>
  <p>class
    <input type="text" name="class$i" maxlength=100><b>  OR  </b>
TFCOND2

        print $query->scrolling_list(-name=>"myclass$i",
			             -values=>\@sorted_classes,
			             -size=>1);
	print<<TFCOND3;
  </p>
  <p>family 
    <input type="text" name="family$i" maxlength=100><b>  OR  </b>
TFCOND3

        print $query->scrolling_list(-name=>"myfamily$i",
			             -values=>\@sorted_families,
			             -size=>1);

	print<<TFCOND;
  </p>
  <p>modifications (Optional) 
    <input type="text" name="modifications$i" maxlength="45">
  </p>
<hr>
Concentration/Quantity <input name="tf_quant$i" maxlength="20"
 type="text"><br><br>
Scale <input name="tf_scale$i" type="text" maxlength="20"></p>

 <hr color="black" style="width: 100%; height: 2px;">
 
TFCOND
    }
}
if  ($params{condPHYS}>0) {
    for (my $i=0;$i<$params{condPHYS};$i++) {
	print<<PHYSCOND;
  <h4>Physiological Perturbation</h4>
  <p>Condition <input name="phys_cond$i" maxlength="45" type="text"><br>
Concentration/Quantity/Stage <input name="phys_quant$i" maxlength="20"
 type="text"><br>
Scale<input name="phys_scale$i" type="text" maxlength="20"></p>
<hr color="black" style="width: 100%; height: 2px;">

PHYSCOND
    }
}
if  ($params{condENV}>0) {
    for (my $i=0;$i<$params{condENV};$i++) {
	print<<ENVCOND;
   <h4>Environmental Perturbation</h4>
  <p>Chemical compound <input name="env_comp$i" maxlength="45"
 type="text"><br>
Concentration/Quantity <input name="env_conc$i" type="text" maxlength="20"><br>
 Scale<input name="env_scale$i" type="text" maxlength="20"></p>
  <hr color="black" style="width: 100%; height: 2px;">

ENVCOND
    }
}

    print<<BOTTOM_PAGE;
  <hr color="black" style="width: 100%; height: 2px;">
  <h3>Effect description</h3>
  <table width="200">
    <tr> 
      <td><label> 
        <input name="effect_grp" type="radio" value="qual" onClick="COND2.effect0.disabled=true;COND2.effectscale.disabled=true;COND2.effectqual.disabled=false;
		COND2.effectqual.focus();">
        qualitative</label></td>
    </tr>
    <tr> 
      <td><label> 
        <input name="effect_grp" type="radio" onClick="COND2.effect0.disabled=false;COND2.effectscale.disabled=false;COND2.effectqual.disabled=true;
		COND2.effectqual.focus();" value="quan" checked>
        quantitative</label></td>
    </tr>
  </table>
  <p>quantitative 
    <input name="effect0" type="text" id="effect0">
  </p>
  <p>scale 
    <select name="effectscale" id="effectscale">
      <option value="percent">percent</option>
      <option value="absolute">absolute</option>
      <option value="relative">relative</option>
      <option value="fold">fold</option>
    </select>
  </p>
  <p>qualitative 
    <select name="effectqual" id="effectqual" disabled="true">
      <option value="highly induced">highly induced</option>
      <option value="induced">induced</option>
      <option value="no change">no change</option>
      <option value="repressed">repressed</option>
      <option value="strongly repressed">strongly repressed</option>
      <option value="NA">NA</option>
    </select>
  </p>
<p><b>Comments on the expression level (if any) </b><textarea name="effectcomment" cols="100" rows="2" id="effectcomment"></textarea></p>
  <hr color="black" style="width: 100%; height: 2px;">
<input type="hidden" name="reg_type" value="$params{reg_type}">
<input type="hidden" name="aid" value="$params{aid}">
<input type="hidden" name="project" value="$params{project}">
<input type="hidden" name="regid" value="$params{regid}">
<input type="hidden" name="sequence" value="$params{sequence}">
<input type="hidden" name="condENV" value="$params{condENV}">
<input type="hidden" name="condPHYS" value="$params{condPHYS}">
<input type="hidden" name="condTF" value="$params{condTF}">
  <p><input name="submit" value="Submit Data" type="submit">
     <input name="cancel" value="cancel" type="reset"><br> </p><br>
</form>
</body></html>

BOTTOM_PAGE
} else {
my @conds;
eval {
    if  ($params{condENV}>0) {
	for (my $i=0;$i<$params{condENV};$i++) {
	    if ($params{"env_comp$i"} && $params{"env_comp$i"} ne '') {
		my $conc=$params{"env_conc$i"}||'na';
		my $molecule=$params{"env_comp$i"}||'na';
		my $scale=$params{"env_scale$i"}||'na';
		my $condid=$pazar->table_insert('bio_condition','environmental',$molecule,'na',$conc,$scale);
		$pazar->add_input('bio_condition',$condid);
		push @conds,$condid;
	    }
	}
    }
    if  ($params{condPHYS}>0) {
	for (my $i=0;$i<$params{condPHYS};$i++) {
	    if ($params{"phys_cond$i"} && $params{"phys_cond$i"} ne '') {
		my $conc=$params{"phys_quant$i"}||'na';
		my $scale=$params{"phys_scale$i"}||'na';
		my $physid=$pazar->table_insert('bio_condition','physical','na',$params{"phys_cond$i"},$conc,$scale);
		$pazar->add_input('bio_condition',$physid);
		push @conds,$physid;
	    }
	}
    }
    if ($params{condTF}>0) {
	for (my $i=0;$i<$params{condTF};$i++) {
	    if ($params{"myclass$i"} eq 'Select from existing classes') {
		delete $params{"myclass$i"};
	    } elsif ($params{"myclass$i"}) {
		$params{"class$i"} = $params{"myclass$i"};
		delete $params{"myclass$i"};
	    }
	    if ($params{"myfamily$i"} eq 'Select from existing families') {
		delete $params{"myfamily$i"};
	    } elsif ($params{"myfamily$i"}) {
		$params{"family$i"} = $params{"myfamily$i"};
		delete $params{"myfamily$i"};
	    }
	    my $tfid;
	    if ($params{"mytfs$i"} eq 'Select from existing TFs') {
		print $query->h3("An error occurred- You have to select a TF in the list!");
		exit();
	    } elsif ($params{"mytfs$i"}) {
		$tfid=get_TF_id($pazar,$params{"mytfs$i"});
	    } elsif ($params{"TFcomplex$i"}) {
		my $ens_tf=&check_TF($params{"TFDB$i"},$params{"TF$i"});
		$params{"ENS_TF$i"}=$ens_tf;
		$tfid=&store_TFs($pazar,$i,\%params);
		unless ($tfid > 0) {
		    print $query->h2("*** TF data NOT accepted - $params{TFcomplex$i} might already exist within your project with different subunits than the one you defined! ***");
		    exit();
		}
	    }
	    unless ($tfid > 0) {
		print $query->h2("An error occurred- No TF was selected!");
		exit();
	    }

	    my $conc=$params{"tf_quant$i"}||'na';
	    my $scale=$params{"tf_scale$i"}||'na';
	    my $tfcondid=$pazar->table_insert('bio_condition','co-expression','Transcription Factor',$tfid,$conc,$scale);
	    $pazar->add_input('bio_condition',$tfcondid);
	    push @conds,$tfcondid;
	}
    }
    my ($quant,$qual,$qscale);
    if ($params{effect_grp} eq 'quan' && $params{effect0} && $params{effect0} ne ''){$quant=$params{effect0}; $qscale=$params{effectscale}; $qual='NA'}
    else { $qual=$params{effectqual}||'NA'; }
    my $expression=$pazar->table_insert('expression',$qual,$quant,$qscale,$params{effectcomment});

    $pazar->add_input($params{reg_type},$params{regid});
    $pazar->add_output('expression',$expression);

    $pazar->store_analysis($params{aid});
    $pazar->reset_inputs;
    $pazar->reset_outputs;
};

if ($@) {
    print "<h3>An error occured! Please contact us to report the bug with the following error message:<br>$@</h3>";
    exit();
}

print $query->h1("The perturbation was successfully submitted to experiment $pazaraid!");
if ($params{reg_type} eq 'reg_seq') {
    print $query->h2("You can add Mutation information related to this perturbation");
    print $query->start_form(-method=>'POST',
			     -action=>'',
                              -name=>'mut');
#    &forward_args($query,\%params);
    print $query->hidden(-name=>'project',-value=>$params{'project'});
    print $query->hidden(-name=>'sequence',-value=>$params{'sequence'});
    print $query->hidden(-name=>'aid',-value=>$params{aid});
    print $query->hidden(-name=>'regid',-value=>$regid);
    my $conds;
    if (@conds) {
	$conds=join(":",@conds);
	print $query->hidden(-name=>'conds',-value=>$conds);
    }
    print $query->hidden(-name=>'modeAdd',-value=>'Add');
    print $query->hidden(-name=>'effect',-value=>'expression');
    print $query->submit(-name=>'submit',
			 -value=>'Add Mutation Information',
                         -onClick=>'return setCount_addCond(0);');
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
}

sub forward_args {
    my ($query,$params)=@_;
    my %params=%{$params};
foreach my $key (keys %params) {
    print $query->hidden($key,$params{$key});
}

}

sub write_pazarid {
    my $id=shift;
    my $type=shift;
    my $id7d = sprintf "%07d",$id;
    my $pazarid=$type.$id7d;
    return $pazarid;
}

sub check_TF {
    my ($db,$tf)=@_;

my $ensdb = pazar::talk->new(DB=>'ensembl',PORT => $ENV{ENS_PORT},ENSEMBL_DATABASES_HOST => $ENV{ENSEMBL_DATABASES_HOST},ENSEMBL_DATABASES_USER => $ENV{ENSEMBL_DATABASES_USER},ENSEMBL_DATABASES_PASS => $ENV{ENSEMBL_DATABASES_PASS},USER=>$ENV{ENS_USER},PASS=>$ENV{ENS_PASS},HOST=>$ENV{ENS_HOST},DRV=>'mysql');

my $gkdb = pazar::talk->new(DB=>'genekeydb',USER=>$ENV{GKDB_USER},PASS=>$ENV{GKDB_PASS},HOST=>$ENV{GKDB_HOST},DRV=>'mysql');

    my $accn=$tf;
    $accn=~s/[\s]//g;
    my $dbaccn=$db;
    my @trans;
	if ($dbaccn eq 'EnsEMBL_gene') {
	    @trans = $ensdb->ens_transcripts_by_gene($accn);
	    unless ($trans[0]=~/\w{2,}\d{4,}/) {print "<h3>An error occured! Check that the provided ID ($accn) is a $dbaccn ID!</h3>You will have the best results using an EnsEMBL transcript ID!"; exit;}
	} elsif ($dbaccn eq 'EnsEMBL_transcript') {
	    push @trans,$accn;
	    unless ($trans[0]=~/\w{2,}\d{4,}/) {print "<h3>An error occured! Check that the provided ID ($accn) is a $dbaccn ID!</h3>You will have the best results using an EnsEMBL transcript ID!"; exit;}
	} elsif ($dbaccn eq 'EntrezGene') {
	    my $species=$gkdb->llid_to_org($accn);
	    if (!$species) {print "<h3>An error occured! Check that the provided ID ($accn) is a $dbaccn ID!</h3>You will have the best results using an EnsEMBL transcript ID!"; exit;}
	    $ensdb->change_mart_organism($species);
	    my @gene=$ensdb->llid_to_ens($accn);
	    unless ($gene[0]=~/\w{2,}\d{4,}/) {print "<h3>An error occured! Check that the provided ID ($accn) is a $dbaccn ID!</h3>You will have the best results using an EnsEMBL transcript ID!"; exit;}
	    @trans = $ensdb->ens_transcripts_by_gene($gene[0]);
	} elsif ($dbaccn eq 'refseq') {
	    my $sp=$gkdb->{dbh}->prepare("select organism from ll_locus a, ll_refseq_nm b where a.ll_id=b.ll_id and b.nm_accn=?");
	    $sp->execute($accn);
	    my $species=$sp->fetchrow_array();
	    if (!$species) {print "<h3>An error occured! Check that the provided ID ($accn) is a $dbaccn ID!</h3>You will have the best results using an EnsEMBL transcript ID!"; exit;}
	    $ensdb->change_mart_organism($species);
	    @trans=$ensdb->nm_to_enst($accn);
	    unless ($trans[0]=~/\w{2,}\d{4,}/) {print "<h3>An error occured! Check that the provided ID ($accn) is a $dbaccn ID!</h3>You will have the best results using an EnsEMBL transcript ID!"; exit;}
	} elsif ($dbaccn eq 'swissprot') {
	    my $sp=$gkdb->{dbh}->prepare("select organism from ll_locus a, gk_ll2sprot b where a.ll_id=b.ll_id and sprot_id=?");
	    $sp->execute($accn);
	    my $species=$sp->fetchrow_array();
	    if (!$species) {print "<h3>An error occured! Check that the provided ID ($accn) is a $dbaccn ID!</h3>You will have the best results using an EnsEMBL transcript ID!"; exit;}
	    $ensdb->change_mart_organism($species);
	    @trans =$ensdb->swissprot_to_enst($accn);
	    unless ($trans[0]=~/\w{2,}\d{4,}/) {print "<h3>An error occured! Check that the provided ID ($accn) is a $dbaccn ID!</h3>You will have the best results using an EnsEMBL transcript ID!"; exit;}
	}
    return $trans[0];
}

sub store_TFs {
my ($pazar,$i,$params)=@_;

my $ensdb = pazar::talk->new(DB=>'ensembl',PORT => $ENV{ENS_PORT},ENSEMBL_DATABASES_HOST => $ENV{ENSEMBL_DATABASES_HOST},ENSEMBL_DATABASES_USER => $ENV{ENSEMBL_DATABASES_USER},ENSEMBL_DATABASES_PASS => $ENV{ENSEMBL_DATABASES_PASS},USER=>$ENV{ENS_USER},PASS=>$ENV{ENS_PASS},HOST=>$ENV{ENS_HOST},DRV=>'mysql');

%params=%{$params};
my $tf;
my @lookup=qw(TF TFDB ENS_TF family classe modifications); #Valid properties of a subunit

#$tf->{function}->{modifications}=$params{modifications};
my $tf=new pazar::tf::tfcomplex(name=>$params{"TFcomplex$i"},pmed=>$params{"pubmed$i"});

my $tid=$params{"ENS_TF$i"};
my $gid=$ensdb->ens_transcr_to_gene($tid);
my $build=$ensdb->current_release;
my $sunit=new pazar::tf::subunit(tid=>$tid,tdb=>'EnsEMBL',class=>$params{"class$i"},family=>$params{"family$i"},gdb=>'ensembl',id=>$gid,tdb_build=>$build,gdb_build=>$build,mod=>$params{"modifications$i"});

$tf->add_subunit($sunit);

return $pazar->store_TF_complex($tf);
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
