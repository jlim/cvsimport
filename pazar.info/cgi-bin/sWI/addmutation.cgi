#!/usr/bin/perl

use CGI qw( :all);
#use CGI::Debug(report => everything, on => anything);

use pazar;

 require '../getsession.pl';

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
        if ($buf=~m/Method used to make the mutation/) {
	        my @methods;
    	    push @methods,('',$pazar->get_method_names);
	        print $query->scrolling_list('mutmethodname',\@methods,1,'true');
        }
    }
    exit();
} elsif ($params{modeDone})  {
    if ($params{effect}=~/interaction/i) {
	eval {
	    &store_mut_inter($pazar,$query,\%params);
	    
	    $pazar->add_input('funct_tf',$params{tfid});
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
    if (length($params{sequence})!=length($params{mutseq})) {
	print "<h3>The length of the mutant sequence should be the same that the original sequence. If the mutation involves deletion replace original nucleotides with 'N' in the mutant sequence!</h3>";
	exit;
    }
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
    my $mutsetid = $pazar->table_insert('mutation_set',$params{regid},$mutname,$methid,$refid,$params{mutseq},undef);
    $pazar->add_input('mutation_set',$mutsetid);
    my %mutants;
    my $mutations = 0;
    for (my $pos=0;$pos<length($params{mutseq});$pos++) {
	my $base = substr($params{mutseq}, $pos, 1);
	if ($base =~ /[ACGT]/) {
	    $mutants{$pos}=lc($base);
	    $mutations++;
	}
	if ($base =~ /N/) {
	    $mutants{$pos}='';
	    $mutations++;
	}
    }
    if ($mutations == 0) {
	print "<h3>The format of the mutant sequence should be lowercase where the nucleotide are unchaged and UPPERCASE for the mutated nucleotides!</h3>";
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
    if (length($params{sequence})!=length($params{mutseq})) {
	print "<h3>The length of the mutant sequence should be the same that the original sequence. If the mutation involves deletion replace original nucleotides with 'N' in the mutant sequence!</h3>";
	exit;
    }
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
    my $mutsetid = $pazar->table_insert('mutation_set',$params{regid},$mutname,$methid,$refid,$params{mutseq},undef);
    $pazar->add_input('mutation_set',$mutsetid);
    my %mutants;
    my $mutations = 0;
    for (my $pos=0;$pos<length($params{mutseq});$pos++) {
	my $base = substr($params{mutseq}, $pos, 1);
	if ($base =~ /[ACGT]/) {
	    $mutants{$pos}=lc($base);
	    $mutations++;
	}
	if ($base =~ /N/) {
	    $mutants{$pos}='';
	    $mutations++;
	}
    }
    if ($mutations == 0) {
	print "<h3>The format of the mutant sequence should be lowercase where the nucleotide are unchaged and UPPERCASE for the mutated nucleotides!</h3>";
    }

    foreach (keys %mutants) {
	my $pos = $_+1;
	my $mutantid = $pazar->table_insert('mutation',$mutsetid,$pos,$mutants{$_});
    }

    my ($quant,$qual,$qscale);
    if ($params{muteffecttype} eq 'mutquan' && $params{muteffect0} && $params{effect0} ne ''){$quant=$params{muteffect0}; $qscale=$params{muteffectscale}; $qual='NA';}
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
