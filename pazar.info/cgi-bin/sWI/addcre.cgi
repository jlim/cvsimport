#!/usr/bin/perl
use  lib $ENV{BPLIVE};

use HTML::Template;
use CGI qw( :all);
use CGI::Debug;#(report => everything, on => anything);
use strict;
use pazar;
use pazar::talk;
use pazar::tf;
use pazar::tf::tfcomplex;
use pazar::tf::subunit;
use Crypt::Imail;
 
use Bio::Matrix::PSM::InstanceSite;
use Bio::LiveSeq::Mutation;
use Bio::Annotation::DBLink;
use Bio::Annotation::Collection;
use Bio::Annotation::SimpleValue;
use Bio::Species;
#use Data::Dumper;

require '../getsession.pl';

# open the html header template
my $template = HTML::Template->new(filename => '../header.tmpl');

# fill in template parameters
$template->param(TITLE => 'Submission Confirmation');

if($loggedin eq 'true')
{
    #log out link
    $template->param(LOGOUT => "$info{first} $info{last} logged in. ".'<a href=\'../logout.pl\'>Log Out</a>');
}
else
{
    #log in link
    $template->param(LOGOUT => '<a href=\'../login.pl\'>Log In</a>');
}

# send the obligatory Content-Type and print the template output
print "Content-Type: text/html\n\n", $template->output;


my @voc=qw(TF TFDB  family class);
our $query=new CGI;
my %params = %{$query->Vars};

my $cgiroot=$ENV{SERVER_NAME}.$ENV{PAZARCGI}.'/sWI';
my $docroot=$ENV{PAZARHTDOCSPATH}.'/sWI';

our @tdbs=qw(refseq ensembl_transcript accn);

my $user=$info{user};
my $pass=$info{pass};

unless (($user)&&($pass)) {
    print $query->h3("An error occurred- not a valid user? If you believe this is an error e-mail us and describe the problem");
# print out the html tail template
my $template_tail = HTML::Template->new(filename => '../tail.tmpl');
print $template_tail->output;
    exit();
}

my $pazar=new 
pazar(-drv=>'mysql',-dbname=>$ENV{PAZAR_name},-user=>$ENV{PAZAR_pubuser},-pazar_user=>$user, -pazar_pass=>$pass,
                        -pass=>$ENV{PAZAR_pubpass}, -project=>$params{project}, -host=>$ENV{PAZAR_host});#Should pass project as well, not analysis name
my ($auxh,$auxname,$auxpass,$auxuser,$auxdrv);
if ($params{auxDB} =~/ensembl/i) {
    $auxh=$ENV{ENS_HOST};
    $auxuser=$ENV{ENS_USER};
    $auxpass=$ENV{ENS_PASS};
    $auxdrv=$ENV{ENS_DRV}||'mysql';
}
if ($params{auxDB} =~/genekeydb/i) {
    $auxh=$ENV{GKDB_HOST};
    $auxuser=$ENV{GKDB_USER};
    $auxpass=$ENV{GKDB_PASS};
      $auxdrv=$ENV{GKDB_DRV}||'mysql';
}

our $talkdb=pazar::talk->new(DB=>lc($params{auxDB}),USER=>$auxuser,
		PASS=>$auxpass,HOST=>$auxh,DRV=>$auxdrv,organism=>$params{organism});
my ($regid,$type);
if (($params{CREtype})&&($params{CREtype}=~/[\w\d]/)) {
    $regid=store_artifical($pazar,$query,%params);
     $type='construct';
}
else {
    $regid=store_natural($pazar,$query,%params);
    $type='reg_seq';
}
$pazar->add_input($type,$regid);


#my $timeid;
#if ($params{time_dev}!=0) {
#    $timeid=$pazar->table_insert('time',$params{time_dev},undef,$params{dev_tscale});
#    my $sampleid=$pazar->table_insert('sample','',$cellid,$timeid);
#    $pazar->add_input('sample',$sampleid);
#}
my ($cellid,$refid,$methid);
if (($params{newmethod})&&($params{newmethod}=~/[\w\d]/)) {
    $methid=$pazar->table_insert('method',$params{newmethod},$params{newmethoddesc});
}
else {
    $methid=$pazar->get_method_id_by_name($params{methodname});
}
if (($params{cell})&&($params{cell}=~/[\w\d]/)) {
    $cellid=$pazar->table_insert('cell',$params{cell},$params{tissue},$params{status},'na',$params{organism});
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
my $aid=$pazar->get_primary_key('analysis',$params{userid},$evidid,$params{aname},$methid,$cellid,0,$refid,0);
print 'Adding to analysis ',$aid;
unless ($aid) {
	$aid=$pazar->table_insert('analysis',$params{userid},$evidid,$params{aname},$methid,$cellid,'',$refid,'');
}

my $tfid=store_TFs($pazar,\%params); 
$pazar->add_input('funct_tf',$tfid);
    
$pazar->store_analysis($aid,'add');
print $query->h1("Submission successful!");
print $query->h2("Please close this window now");
print $query->button(-name=>'close',
                          -value=>'Close window',
                          -onClick=>"window.close()");
if ($type eq 'construct') {
    print $query->start_form(-method=>'POST',
                           -action=>"http://$cgiroot/TFcentric_CRE.cgi", -name=>'chr');
    &forward_args;
    print $query->submit(-name=>'Add more similar',
                          -value=>'Add more similar',);
    print $query->end_form;
}

# print out the html tail template
my $template_tail = HTML::Template->new(filename => '../tail.tmpl');
print $template_tail->output;
    exit();

sub store_TFs {
my ($pazar,$params)=@_;
#Scanning
#print Dumper($params);
%params=%$params;
my $tf;
my @lookup=qw(TF TFDB family class build); #Valid properties of a subunit
$tf->{function}->{modifications}=$params{modifications};
my $tf=new pazar::tf::tfcomplex(name=>$params{TFcomplex},pubmed=>$params{pubmed});
my ($tfdat);
foreach my $key (keys %params) {
my ($quant,$qual,$qscale);
if ($key eq 'inttype') {
     if ($params{inttype} eq 'quan'){$quant=$params{interact0}; $qscale=$params{interactscale};}
     else { $qual=$params{qualitative}; }
    $pazar->store_interaction($qual,$quant,$qscale);
    next;
}
next unless ($key=~/\d/);
my $ind=$key;
$ind=~s/\D//g;#Index only
my $nkey=$key;
$nkey=~s/\d//;#Tag only
next unless (grep(/\b$nkey\b/,@lookup));
$tfdat->[$ind]->{$nkey}=$params{$key};#Object created, pass it to regdb, should put here the TF_complex general data too!
}
foreach my $udef (@$tfdat) {
$udef->{TFDB}=~s/nm/refseq/; #old HTML page templates... 
my $db=$udef->{TFDB};

my ($tid,$gid);
unless (grep(/\b$db\b/,@tdbs)) {
    my @tfs=$talkdb->convert_to_transcripts($db,'ensembl',$udef->{TF});
    $tid=$tfs[0];
    $gid=$udef->{TF};
    print $query->h2("Multiple transcripts exist, choosing $tid, use a transcript id for genes with many isoforms");
}
else {
    if ($db eq 'ensembl_transcript') {
        $tid=$udef->{TF};
    }
    else {
        my @ids=$talkdb->convert_to_transcripts($db,'ensembl',$udef->{TF});
        $tid=$ids[0];
    }
    $gid=$talkdb->convert_to_gene('ensembl','ensembl',$tid);

}

my $sunit=new pazar::tf::subunit(tid=>$tid,tdb=>$udef->{TFDB},'class'=>$udef->{class},family=>$udef->{family},gdb=>'ensembl',gid=>$gid,
                                tdb_build=>$params{build},gdb_build=>$params{build});

$tf->add_subunit($sunit);
}

return $pazar->store_TF_complex($tf);
}

sub store_natural {
my ($pazar,$query,%params)=@_;


my $geneid=$pazar->ens_transcr_to_gene($params{tid});

print ($geneid);

die "Could not connect to pazar" unless ($pazar);

my ($gen,$spec)=split(/\s/,$params{organism});

my $specie=new Bio::Species(-classification => [$spec,$gen]);
my $inst=new Bio::Matrix::PSM::InstanceSite(-seq=> $params{sequence}, -id=>$params{tid}, #This is how
				-accession_number=>$params{tid},
                                 -desc=>'',  -anchor=>$params{chromosome}, -start=>$params{start}, -end=>$params{end},
				 -strand=>$params{strand});
                 
my $dblink=new Bio::Annotation::DBLink(-primary_id=>$geneid, -database=>'ensembl');
my $ulink=new Bio::Annotation::DBLink(-primary_id=>$params{tid}, -database=>'ensembl');

my $ann=new Bio::Annotation::Collection;
$ann->add_Annotation('DBLink',$dblink);
$ann->add_Annotation('DBLink',$ulink);
my $build=new Bio::Annotation::SimpleValue($params{build});
$ann->add_Annotation('Build',$build);
$inst->species($specie);
$inst->annotation($ann);
my ($condid,$expression);
my $rec=$pazar->store_element_location($inst);
return $rec->get_current_id('reg_seq');
}

sub store_artifical {
    my ($pazar,$query,%params)=@_;
    return $pazar->table_insert('construct',$params{constructname},$params{artificialcomment},$params{sequence});
}

sub forward_args {
foreach my $key (keys %params) {
    print $query->hidden($key,$params{$key});
}
 print $query->hidden('remember','yes');

}
