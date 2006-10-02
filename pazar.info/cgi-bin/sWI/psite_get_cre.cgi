#!/usr/bin/perl

#use CGI::Debug (report=>'everything', on=>'anything');

use CGI qw( :all);
use DBI;
use pazar::talk;
use pazar::reg_seq;
use pazar;

require '/usr/local/apache/pazar.info/cgi-bin/getsession.pl';

our $query=new CGI;
my %params = %{$query->Vars};

our $cgiroot=$ENV{SERVER_NAME}.$ENV{PAZARCGI}.'/sWI';
our $docroot=$ENV{PAZARHTDOCSPATH}.'/sWI';

my $user=$info{user};
my $pass=$info{pass};
my $proj=$params{project};

print $query->header;

unless (($user)&&($pass)) {
    &goback(2,$query);
}

my $pazar=new pazar(-drv=>'mysql',-dbname=>$ENV{PAZAR_name},-user=>$ENV{PAZAR_pubuser}, -pazar_user=>$user, -pazar_pass=>$pass,
                        -pass=>$ENV{PAZAR_pubpass}, -host=>$ENV{PAZAR_host}, -project=>$proj);

my $ensdb = pazar::talk->new(DB=>'ensembl',USER=>$ENV{ENS_USER},PASS=>$ENV{ENS_PASS},HOST=>$ENV{ENS_HOST},DRV=>'mysql');

my $gkdb = pazar::talk->new(DB=>'genekeydb',USER=>$ENV{GKDB_USER},PASS=>$ENV{GKDB_PASS},HOST=>$ENV{GKDB_HOST},DRV=>'mysql');

if ($params{reg_type} eq 'reg_seq') {
    $new_params=&check_seq($ensdb,$gkdb,$query,\%params);
    %params=%{$new_params};
}

my @cell_names=$pazar->get_all_cell_names;
my @tissue_names=$pazar->get_all_tissue_names;

my $selfpage="$docroot/condition1.htm";
open (SELF, $selfpage) ||die;
while (my $buf=<SELF>) {
    $buf=~s/serverpath/$cgiroot/i;
    print $buf;
    if (($buf=~/\<form/) && ($buf=~/action\=/)) {
	foreach my $key (keys %params) {
	    my $val=$params{$key};
	    print "\<input name=\"$key\" type=\"hidden\" value=\"$val\"\>";
	}

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
}

close SELF;

exit();

sub goback
 {
my $err=shift;
my $query=shift;
print $query->header;
my $message="under construction";
$message="Not authenticated and the interface is submission only" if ($err==2);
#$message="Mea culpa, I did something wrong, flame and burn my creator" if ($err==3);
print $query->h1("An error has occured because ");
print $query->h2($message);
#print a({href=>"http://watson.lsd.ornl.gov/genekeydb/psite/entryform1.htm"},"Go Back");
#print $query->redirect('http://somewhere.else/in/movie/land');
# print out the html tail template
my $template_tail = HTML::Template->new(filename => '/usr/local/apache/pazar.info/cgi-bin/tail.tmpl');
print $template_tail->output;
exit(0);
}


sub forward_args {
foreach my $key (keys %params) {
    print $query->hidden($key,$params{$key});
}
}

sub getseq {
my ($chr,$begin,$end)=@_;
my $sadapt=$ensdb->get_ens_adaptor;
my $adapt=$sadapt->get_SliceAdaptor();
my $slice = $adapt->fetch_by_region('chromosome',$chr,$begin,$end);
return $slice->seq;
}

sub check_seq {
    my ($ensdb,$gkdb,$query,$params)=@_;
    my %params=%{$params};

    my $accn = $params{'gid'};
    my $dbaccn = $params{'genedb'};
    my $taccn = $params{'tid'};
    my $dbtrans = $params{'transdb'};

    my ($ens,$err);
    if ($dbaccn eq 'EnsEMBL_gene') {
	unless ($accn=~/\w{4,}\d{6,}/) {print "<p class=\"warning\">An error occured! Check that the provided ID ($accn) is a $dbaccn ID!</p>"; exit;} else {
	    $ens=$accn;
	}
    } elsif ($dbaccn eq 'EnsEMBL_transcript') {
	my @gene = $ensdb->ens_transcr_to_gene($accn);
	$ens=$gene[0];
	unless ($ens=~/\w{4,}\d{6,}/) {print "<p class=\"warning\">An error occured! Check that the provided ID ($accn) is a $dbaccn ID!</p>"; exit;}
    } elsif ($dbaccn eq 'EntrezGene') {
	my @gene=$gkdb->llid_to_ens($accn);
	$ens=$gene[0];
	unless ($ens=~/\w{4,}\d{6,}/) {print "<p class=\"warning\">An error occured! Check that the provided ID ($accn) is a $dbaccn ID!</p>"; exit;}
    } else {
	($ens,$err) =convert_id($gkdb,$dbaccn,$accn);
	if (!$ens) {print "<p class=\"warning\">An error occured! Check that the provided ID ($accn) is a $dbaccn ID!</p>"; exit;}
    }
    unless ($ens) {print "<p class=\"warning\">An error occured! Check that the provided ID ($accn) is a $dbaccn ID!</p>"; exit;} #Error message her - gene not in DB
    my $gene=$ens;

    if ($taccn && $taccn ne '') {
	if ($dbtrans=~/ensembl/i) {
	    my ($gene_chk)=$ensdb->ens_transcr_to_gene($taccn);
	    unless ($gene_chk eq $ens) { print "<p class=\"warning\">An error occured! Check that the provided transcript ID matches the gene ID!</p>"; exit;}
	} elsif ($dbtrans=~/refseq/i) {
	    my ($trans)=$ensdb->nm_to_enst($taccn);
	    if ($trans=~/\w{2,}/) { $taccn=$trans; } else {print "<p class=\"warning\">An error occured! Check that the provided ID ($taccn) is a $dbtrans ID!</p>"; exit;}
	    my ($gene_chk)=$ensdb->ens_transcr_to_gene($taccn);
	    unless ($gene_chk eq $ens) { print "<p class=\"warning\">An error occured! Check that the provided transcript ID matches the gene ID!</p>"; exit;}
	} elsif ($dbtrans=~/swissprot/i) {
	    my ($trans)=$ensdb->swissprot_to_enst($taccn);
	    if ($trans=~/\w{2,}/) { $taccn=$trans; } else {print "<p class=\"warning\">An error occured! Check that the provided ID ($taccn) is a $dbtrans ID!</p>"; exit;}
	    my ($gene_chk)=$ensdb->ens_transcr_to_gene($taccn);
	    unless ($gene_chk eq $ens) { print "<p class=\"warning\">An error occured! Check that the provided transcript ID matches the gene ID!</p>"; exit;}
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
	    print "Unknown character used in the sequence<br>$element<br>";
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
	if (uc($params{str}) && uc($params{str}) ne uc($strand)) {
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

    $params{sequence}=$seq;
    $params{str}=$strand;
    $params{gid}=$ens;
    $params{build}=$build;
    $params{tid}=$taccn;
    $params{tss}=$tss;

    return \%params;
}
