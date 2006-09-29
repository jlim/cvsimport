#!/usr/bin/perl

use CGI qw( :all);
#use CGI::Debug(report => everything, on => anything);

use pazar;

 require '/usr/local/apache/pazar.info/cgi-bin/getsession.pl';

our $query=new CGI;
my %params = %{$query->Vars};

my $cgiroot=$ENV{SERVER_NAME}.$ENV{PAZARCGI}.'/sWI';
my $docroot=$ENV{PAZARHTDOCSPATH}.'/sWI';

my $selfpage;
if ($params{effect}=~/interaction/i) {
    $selfpage="$docroot/mutation.htm";
} elsif ($params{effect}=~/expression/i) {
    $selfpage="$docroot/mutation2.htm";
}

my $user=$info{user};
my $pass=$info{pass};

print $query->header;

unless (($user)&&($pass)) {
    print $query->h3("An error occurred- not a valid user? If you believe this is an error e-mail us and describe the problem");
}

my $pazar=new 
pazar(-drv=>'mysql',-dbname=>$ENV{PAZAR_name},-user=>$ENV{PAZAR_pubuser},-pazar_user=>$user, -pazar_pass=>$pass,
                        -pass=>$ENV{PAZAR_pubpass}, -project=>$params{project}, -host=>$ENV{PAZAR_host});

if ($params{modeAdd})  {
    open (SELF,$selfpage)||print "Cannot Open Page $selfpage";

    while (my $buf=<SELF>) {
	$buf=~s/serverpath/$cgiroot/;
	print $buf;
	if (($buf=~/form/i)&&($buf=~/method/i)&&($buf=~/post/i)) {
	    &forward_args($query,\%params);        
	}
        if ($buf=~/<p>Method Name/) {
	    my @methods=$pazar->get_method_names;
    	    my @sorted_methods = sort @methods;
	    unshift @sorted_methods, 'Select from existing methods';
	    print $query->scrolling_list('mutmethodname',\@sorted_methods,1,'true');
        }
	if ($buf=~/<h3>Original Sequence/i) {
	    &print_seq($params{sequence});
	}
    }
    exit();
} elsif ($params{modeDone})  {
    if ($params{effect}=~/interaction/i) {
	eval {
	    &store_mut_inter($pazar,$query,\%params);
	    if ($params{'sample'}) {	    
		$pazar->add_input('sample',$params{'tfid'});
	    } else {
		$pazar->add_input('funct_tf',$params{'tfid'});
	    }
	    $pazar->store_analysis($params{aid});
	    $pazar->reset_inputs;
	    $pazar->reset_outputs;
	};
    }  elsif ($params{effect}=~/expression/i) {
	eval {
	    &store_mut_expr($pazar,$query,\%params);
	    
	    $pazar->store_analysis($params{aid});
	    $pazar->reset_inputs;
	    $pazar->reset_outputs;
	};
    }

if ($@) {
    print "<span class=\"warning\">An error occured! Please contact us to report the bug with the following error message:<br>$@";
    exit();
}

print $query->h1("Submission successful!");
print $query->h2("You can add Mutation information or close this window now");
print $query->start_form(-method=>'POST',
			 -action=>"http://$cgiroot/addmutation.cgi", -name=>'mut');
&forward_some_args($query,\%params);
    print $query->hidden(-name=>'modeAdd',-value=>'Add');
print $query->submit(-name=>'Add Mutation Information',
		     -value=>'Add Mutation Information',);
print $query->br;
print $query->br;
print $query->button(-name=>'close',
		     -value=>'Close window',
		     -onClick=>"window.close()");
print $query->br;
print $query->end_form;
    exit();
}

sub forward_args {
    my ($query,$params)=@_;
    my %params=%{$params};
foreach my $key (keys %params) {
    unless ($key=~/mode/i) {
    print $query->hidden($key,$params{$key});
}
}
}

sub forward_some_args {
    my ($query,$params)=@_;
    my %params=%{$params};
foreach my $key (keys %params) {
    unless ($key=~/mut/i || $key=~/mode/i) {
	print $query->hidden($key,$params{$key});
    }
}
}

sub store_mut_inter() {
    my ($pazar,$query,$params)=@_;
    my %params=%{$params};
    unless ($params{aid}&&$params{regid}&&$params{tfid}) {
	print "<h3>An error occured!</h3>";
	exit;
    }
    my $element=$params{sequence};
    $element=~s/\s*//g;
    if ($element=~/[^agctnAGCTN]/) {
	print "Unknown character used in the sequence<br>$element<br>";
	exit();
    }
    my $mutelement=&get_mutseq(\%params);
    my ($methid,$refid);
    if (($params{mutnewmethod})&&($params{mutnewmethod}=~/[\w\d]/)) {
	$methid=$pazar->table_insert('method',$params{mutnewmethod},$params{mutnewmethoddesc});
    }
    else {
	my $meth=$params{mutmethodname}||'NA';
	$methid=$pazar->get_method_id_by_name($meth);
    }
    if (($params{mutref})&&($params{mutref}=~/[\w\d]/)) {
	$refid=$pazar->table_insert('ref',$params{mutref});
    }
    $methid||=0;
    $refid||=0;
    my $mutname = $params{mutseqname}||'NA';
    my $mutsetid = $pazar->table_insert('mutation_set',$params{regid},$mutname,$methid,$refid,$mutelement,$params{mutcomment});
    $pazar->add_input('mutation_set',$mutsetid);
    my %mutants;
    my $mutations = 0;
    for (my $pos=0;$pos<length($mutelement);$pos++) {
	my $base = substr($mutelement, $pos, 1);
	if ($base =~ /[ACGT]/) {
	    $mutants{$pos}=lc($base);
	    $mutations++;
	}
	if ($base =~ /[XN]/) {
	    $mutants{$pos}='';
	    $mutations++;
	}
    }
    if ($mutations == 0) {
	print "<h3>An error occured! No mutation was found in your mutant sequence!</h3>";
	exit();
    }

    foreach (keys %mutants) {
	my $pos = $_+1;
	my $mutantid = $pazar->table_insert('mutation',$mutsetid,$pos,$mutants{$_});
    }
    my ($quant,$qual,$qscale);

    if ($params{mutinttype} eq 'mutquan' && $params{mutinteract0} && $params{mutinteract0} ne ''){$quant=$params{mutinteract0}; $qscale=$params{mutinteractscale}; $qual='NA';} else { $qual=$params{mutqual}||'NA'; }
    $pazar->store_interaction($qual,$quant,$qscale);

}

sub store_mut_expr() {
    my ($pazar,$query,$params)=@_;
    my %params=%{$params};
    unless ($params{aid}&&$params{regid}) {
	print "<h3>An error occured!</h3>";
	exit;
    }
    my $element=$params{sequence};
    $element=~s/\s*//g;
    if ($element=~/[^agctnAGCTN]/) {
	print "Unknown character used in the sequence<br>$element<br>";
	exit();
    }
    my $mutelement=&get_mutseq(\%params);
    my ($methid,$refid);
    if (($params{mutnewmethod})&&($params{mutnewmethod}=~/[\w\d]/)) {
	$methid=$pazar->table_insert('method',$params{mutnewmethod},$params{mutnewmethoddesc});
    }
    else {
	my $meth=$params{mutmethodname}||'NA';
	$methid=$pazar->get_method_id_by_name($meth);
    }
    if (($params{mutref})&&($params{mutref}=~/[\w\d]/)) {
	$refid=$pazar->table_insert('ref',$params{mutref});
    }
    $methid||=0;
    $refid||=0;
    my $mutname = $params{mutseqname}||'NA';
    my $mutsetid = $pazar->table_insert('mutation_set',$params{regid},$mutname,$methid,$refid,$mutelement,$params{mutcomment});
    $pazar->add_input('mutation_set',$mutsetid);
    my %mutants;
    my $mutations = 0;
    for (my $pos=0;$pos<length($mutelement);$pos++) {
	my $base = substr($mutelement, $pos, 1);
	if ($base =~ /[ACGT]/) {
	    $mutants{$pos}=lc($base);
	    $mutations++;
	}
	if ($base =~ /[XN]/) {
	    $mutants{$pos}='';
	    $mutations++;
	}
    }
    if ($mutations == 0) {
	print "<h3>An error occured! No mutation was found in your mutant sequence!</h3>";
	exit();
    }

    foreach (keys %mutants) {
	my $pos = $_+1;
	my $mutantid = $pazar->table_insert('mutation',$mutsetid,$pos,$mutants{$_});
    }

    my ($quant,$qual,$qscale);
    if ($params{muteffecttype} eq 'mutquan' && $params{muteffect0} && $params{muteffect0} ne ''){$quant=$params{muteffect0}; $qscale=$params{muteffectscale}; $qual='NA';}
    else { $qual=$params{mutqual}||'NA'; }
    my $expression=$pazar->table_insert('expression',$qual,$quant,$qscale,'');
    $pazar->add_output('expression',$expression);

    if ($params{conds} && $params{conds} ne '') {
	my @conds = split(/:/,$params{conds});
	foreach my $condid (@conds) {
	    $pazar->add_input('bio_condition',$condid);
	}
    }
}

sub print_seq {
    print "<p style=\"font-family: monospace;\">";
    my $seq=shift;
    $seq=~s/\s*//g;
#    print $seq;
    my $c = 10;
    my $nc = 5;
    my $space='&nbsp';
    my $l = length($seq);
    my $col1 = length($l);
    my @letters = split(//, $seq);
    if ($l>=1) {
	my $first="1";
	print &add_spaces(\$first, \$col1);
    }
    for (my $i=0; $i<=$#letters; $i++) {
	if ( (($i+1)/($c*$nc)) == int(($i+1)/($c*$nc)) ) {
	    print $letters[$i]."<br>";
	    unless ($i == $#letters) { my $s = $i+2; print &add_spaces(\$s, \$col1); } 
	} elsif ( (($i+1)/($c)) == int(($i+1)/($c)) ) {
	    print $letters[$i]." ";
	} else {
	    print $letters[$i];
	}
    }
    unless ( (($#letters+1)/($c*$nc)) == int(($#letters+1)/($c*$nc)) ) { print "<br>"; }
print "</p>";
}

sub add_spaces {
  my ($str, $l) = @_;
  my $long = ($$l - (length($$str)));
  my $final=$$str;
  for (my $i=0; $i<=$long; $i++) {
    $final.="&nbsp;";
  }
  return($final);
}

sub get_mutseq {
    my ($params)=@_;
    my %params=%{$params};
    my $seq=lc($params{sequence});
    $params{mutdel}=~s/\s*//g;
    $params{pointmutation}=~s/\s*//g;
    if ($params{mutdel}=~/[^\d;-]/) {&print_deletion_error;}
    if ($params{pointmutation}=~/[^\d;-acgtACGT]/) {&print_pointmutation_error;}
###Handle Deletions
    my @deletions=split(/;/,$params{mutdel});
    my @delstart;
    my @delend;
    foreach my $del (@deletions) {
	my @dels=split(/-/,$del);
        if ($dels[0]=~/[^\d]/) {&print_deletion_error;}
        if ($dels[1]=~/[^\d]/) {&print_deletion_error;}
        unless ($dels[1]>$dels[0]) {&print_deletion_error;}
	push @delstart,$dels[0];
	push @delend,$dels[1];
    }
    unless (@delstart==@delend) {&print_deletion_error;}
    for ($i=0; $i<@delstart;$i++) {
	my $start=$delstart[$i]-1;
	my $length=$delend[$i]-$delstart[$i]+1;
	my $substr='X'x$length;
	substr($seq,$start,$length)=$substr;
    }
 
###Handle Point Mutations
    my @mutations=split(/;/,$params{pointmutation});
    my @nt;
    my @pos;
    foreach my $mut (@mutations) {
	my $nt=uc($mut);
	$nt=~s/\d//g;
	my $pos=$mut;
	$pos=~s/[a-zA-Z]//g;
        if ($nt=~/[^ACGT]/ || length($nt)!=1) {&print_pointmutation_error;}
        if ($pos=~/[^\d]/) {&print_pointmutation_error;}
	push @nt,$nt;
	push @pos,$pos;
    }
    unless (@nt==@pos) {&print_pointmutation_error;}
    for ($j=0; $j<@nt;$j++) {
	my $base=$pos[$j]-1;
	substr($seq,$base,1)=$nt[$j];
    }
    return $seq;
}

sub print_deletion_error {
    print "The format of your deletion description is not correct.\n";
    print "It should be [start nt]-[end nt] separated by semi-colons if there are more than one (e.g. 100-200;300-400). You also have to use the numbering scheme provided on the webpage besides the original sequence.\n";
    exit();
}

sub print_pointmutation_error {
    print "The format of your point mutation description is not correct.\n";
    print "It should be [position][mutant nt] separated by semi-colons if there are more than one (e.g. 5A;7T). You also have to use the numbering scheme provided on the webpage besides the original sequence.\n";
    exit();
}
