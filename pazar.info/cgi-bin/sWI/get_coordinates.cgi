#!/usr/bin/perl

use Exporter;
use CGI qw( :all);
use CGI::Debug (report=>'everything', on=>'anything');
#use GKDB;
use DBI;
use Bio::EnsEMBL::DBSQL::DBAdaptor;
use Bio::EnsEMBL::DBSQL::TranscriptAdaptor;
use Bio::EnsEMBL::DBSQL::SliceAdaptor;
use Bio::EnsEMBL::Transcript;
use Bio::EnsEMBL::Upstream;
use Data::Dumper;
use pazar;
use pazar::talk;

require '../getsession.pl';

=Description
Get all transcripts and check the sequence and match the correct position
and the respective transcript id.
=cut

my $docroot=$ENV{PAZARHTDOCSPATH}.'/sWI';
my $cgiroot=$ENV{SERVER_NAME} . $ENV{PAZARCGI}.'/sWI';

undef $id;
my $query=new CGI;
my %params=%{$query->Vars};
my $selfpage="$docroot/chrcoordinates.htm";
print $query->header;

open (SELF, $selfpage) ||die;

my $auxdb=$params{auxDB};
if ($auxdb) {
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
		PASS=>$auxpass,HOST=>$auxh,DRV=>$auxdrv,organism=>$params{org});

my $geneid = $params{'geneid'};
my $genedb = $params{'genedb'};
my ($gene,$err,$ens);

if ($genedb eq 'locuslink') {
  $gene=$geneid;
 my @all=$talkdb->llid_to_ens($gene);
 $ens=$all[0];
 unless ($ens=~/\w{2,}/) { print "Conversion failed for $gene"; exit();}
 }
 elsif  ($genedb eq 'ens') {
  $ens=$geneid;
  $gene=$geneid;
}
else {
  ($gene,$ens,$err) =convert_id($talkdb,$genedb,$geneid);
 }
unless (($gene)&&($ens)) {print_self($query,"Gene $geneid not found $err",1); exit(0); } #Error message her - gene not in DB
#else {print "Gene symbol: ". $pazar->ll_to_sym($gene),$query->br;}
my $type = $params{'radiobutton'};

 next_page(\%params,$gene,$ens,$query,$pazar); 
my %input;
my $err;
#Check here if the start is correct and if alternative TSSs exist
my ($check,$corrected)=checkseq(\%params,$gene,$query);
display_check($check,$corrected);
}
exit();

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
return $ll,$ensembl[0];
}


sub print_self {
my ($q,$message,$state)=@_;
 while (my $buf=<SELF>) {
  print $buf;
  if ($buf=~/\<\/head\>/) {
    print $q->h2("An error occurred:") if ($state==1);
    print $q->h3($message);
  }
 }
}

sub checkseq {
my ($params,$gene,$html)=@_;
print "Checking sequence now..." . $html->br;
TYPE: {
	if ($params{'radiobutton'} eq 'region') { last TYPE;}
	if ($params{'radiobutton'} eq 'exact') { last TYPE;}
	if ($params{'radiobutton'} eq 'point mutation') {last TYPE;} #%params=read_pos(\%params); last TYPE;}
}
return 1,$corrected;
}



sub next_page {
my ($params,$gene,$ens,$html,$pazar)=@_;
my %params=%{$params};

my $region=$params{start};
my $element=$params{sequence};
#my ($trf_llid,$trfens,$trferr) =convert_id($params{TFDB},$params{TF});

my ($enstr,$sadapt,$proceed,%tr,%sites,%tss);
	my $precisetr;
   
     print ("Gene $gene (NCBI); $ens (Ensembl)" . $html->br);
      #Get the transcript ids and organism so we can look fot alt TSSs and upstream se
     
     #$org=$pazar->getorg($gene);
    my ($chr,$build,$begin,$end,$orient)=$talkdb->get_ens_chr($ens);
    $org=$talkdb->current_org($gene);
    unless ($chr) {print $query->h1("This gene is not mapped in the genome or was not found in the current ensembl release"); exit();}
    #We need now an ensembl adaptor to get the sequence
    my $sadapt=$talkdb->get_ens_adaptor;
    my $adapt=$sadapt->get_SliceAdaptor();
my $slice = $adapt->fetch_by_region('chromosome',$chr,$begin,$end,$orient); 
     print ("Specie: $org" . $html->br);
     #print ("Gene chromosome location: chrosomosome $chr, build $build, on $orient strand, begin $begin" . $html->br);
	$params{build}=$build;
	$params{strand}=$orient;
	$params{upstart}=$begin;
	$params{chromosome}=$chr;
	$params{llid}=$gene;
my $found;

print "
<script language=\"javascript\">
//by vwphillips - http://www.vicsjavascripts.org.uk
function SendInfo(){
var arg = document.chrcoord.start_end.options[document.chrcoord.start_end.selectedIndex].value;
var txt = document.chrcoord.start_end.options[document.chrcoord.start_end.selectedIndex].text; 
var sel = window.opener.NewOption(arg,txt);
window.close();
} 
</SCRIPT>
";
my $tr_adaptor  = $sadapt->get_TranscriptAdaptor();
my $enstr=$tr_adaptor->fetch_all_by_Slice($slice);
    my (@sites,%labels);
     foreach my $transcript (@$enstr) {
     #print "TR:",$row->[0];
     # my $transcript=$dbadapt->fetch_by_dbID($row->[0]);
      my $tr=$transcript->stable_id;
      #print $tr,$html->br;
      my ($tss,$seq)=getseq($transcript,$adapt,$chr,$begin,$end,$orient,$region);
       #print $tss,$seq,$html->br;
       #print join(':',$seq,$element,$region,$tss),$html->br;
	my ($nf,$site,$precise)=suggest_pos($seq,$element,$region,$tss);
    #print 'SITES',Dumper($site),$html->br;
    #print $nf,$site,$precise,$html->br;
    
	if ($nf>0) {
			print  $html->br;
			print "Found $nf possible sites", $html->br;
			foreach my $key (keys %{$site}) {
				my $rel=$site->{$key};
                my $label=$tr.' '.$rel.' '.$key;
                my $end=$key+length($element);
                my $uid=join(':',$chr,$key,$end,$org,$build,$element,$tr,$tss,$tss);#For now no fuzzy bussiness
                push @sites,$uid;
                $labels{$uid}=$label;
				#print ("Found at Abs $key, rel $rel, transcript $tr" . $html->br);#Just to debug
			}
	}
	
	$tr{$tr}=$seq;
	$sites{$tr}=$site;
	$tss{$tr}=$tss;	
#      print ("Transcript location: $tr: $tss" . $html->br);
#      print ("Target sequence: $region/$element/$seq" . $html->br);
      }
#	else {$found++;}		
#     }
#		unless ($found) {print_self ($html,'Element not found within 1 Kb', 1);}
print $html->h4("Please choose the appropriate combination (transcript, position, sequence) and click the submit button");
      #print "This gene has " . count_refseq_tr($gene) . " transcript(s) in RefSeq and $censtr in Ensembl" . $html->br;
    print " <FORM NAME=\"chrcoord\" onSubmit='javascript:SendInfo();'>";
    print $html->scrolling_list(-name=>'start_end',
                                '-values'=>\@sites,
                                #-default=>['eenie','moe'],
                                -size=>5,
                                #-multiple=>'true',
                                -labels=>\%labels
                                );
     print $html->submit(-name=>'Set coordinates',-value=>'submit',-onClick=>'SendInfo(); window.close;');
     print '    <input name="cancel" value="cancel" type="reset">';
     print '</form>';
exit();
}

sub getseq {
my ($id, $adapt, $chr,$begin,$end, $orient, $region)=@_;

my $l;
#Let's see how much we want
if ($region<0) {
	$l=1000-$region;
	$region=$l;
}
else {
	$region+=100;
	$l=$region;
}
#my $upstream =  Bio::EnsEMBL::Upstream->new(-transcript=>$id,-length=>$l);
if ($orient==1) {
	$start=$begin-$region;
	$end=$begin;
}
else {
   	$start=$end-1000;
        $end=$end+$region;
}
my $slice;
#print "$start $end $region $orient";
$slice = $adapt->fetch_by_region('chromosome',$chr,$start,$end,$orient);
unless ($orient==1) {
	my $rsl=$slice->invert;
	return $begin,$rsl->seq;
}
return $begin,$slice->seq;
}

sub display_check {
my ($html,$tr,$sites,$tss,$params,$org,$ens,$gene)=@_;
my %params=%{$params};
#my ($trf_llid,$trfens,$trferr) =convert_id($params{TFDB},$params{TF});
print $html->h2("Your site was not confirmed, choose one of the following sites (if any):");
print ("Format is: transcript id followed by absolute position and relative to TSS position"),$html->br;
my $c=keys %{$tr};
print $html->start_form(-method=>'POST',-action=>'http://$cgiroot/accept_cre.cgi');
 #   unless (($trf_llid) || ($params{TF} eq '')|| !defined($params{TF})) {
#	print $html->h3("Transcription factor gene $params{TF} not recognized, will be ignored, go back if you want to try again");
 #    }
  #     else { print "Transcription factor ". GKDB::ll_to_sym($trf_llid),$query->br;}
my @ns;
foreach my $key (keys %{$sites}) {
my @val;
	foreach my $v (keys %{$sites->{$key}}) {
		push @val,$v." ".$sites->{$key}->{$v};
	}
	foreach my $val (@val) {
		push @ns,$key." ".$val;
	}
}	

	print $html->scrolling_list('corrected_site',\@ns,1,'true');
    foreach my $key (keys %params) {
      my $val=$params{$key};
      print "\<input name=\"$key\" type=\"hidden\" value=\"$val\"\>\n" unless ($key eq 'submit');
    }
    my $i;
    foreach my $tr (@ns) {
      $i++;
      my ($transcript,@junk)=split(/ /,$tr);
      print "\<input name=\"transcript$i\" type=\"hidden\" value=\"$transcript\"\>\n";
    }
    print "\<input name=\"specie\" type=\"hidden\" value=\"$org\"\>";
    print "\<input name=\"llid\" type=\"hidden\" value=\"$gene\"\>";
    print "\<input name=\"ensgene\" type=\"hidden\" value=\"$ens\"\>";
    print "\<input name=\"trf_llid\" type=\"hidden\" value=\"$trf_llid\"\>";
print $html->submit(-name=>'SUBMIT',-value=>'submit');
print $html->endform;
print $html->end_html;
exit;
}

#Get all transcripts upstream regions (if alternative) and see if anyone matches

#What if pos is not ok- suggest some positions (both chromosome and relative)
sub suggest_pos {
my ($region,$seq,$pos,$upstart)=@_;
my $l=length($region);
my $t=substr($region, $l+$pos, length($seq));
return 1,0,1 if ($t eq $seq);
my %site;
my $i=0;
my $precise;
while ($region=~m/$seq/ig) {
	$precise=1 if (($-[0]-$l) == $pos);
	$site{$-[0]+$upstart}=$-[0]-$l;	
	$i++;
}
return $i,\%site,$precise;
}
	
sub read_pos {
	my $params=shift;
	my $user=$params->{userid};
	my $analysis=$params->{aname};
	my $file=$user ."\_".$analysis . ".pos.tmp";
	open (POS,$file)||die;
	while (my $buf=<POS>) {
		chomp $buf;
		my ($t1,$v1,$t2,$v2)=split(/\t/,$buf);
		$params->{$t1}=$v1;
		$params->{$t2}=$v2;
	}
	close POS;
	unlink($file);
	return %{$params};
}


sub filename {
 my $fn;
 my $_rand;

 my $fnl = $_[0];
 if (!$fnl) {
  $fnl = 10;
 }

 my @chars = split(" ",
 "a b c d e f g h i j k l m n o p q r s t u v w x y z 
  - _ % # |
  0 1 2 3 4 5 6 7 8 9");

 srand;

 for (my $i=0; $i <= $fnl ;$i++) {
  $_rand = int(rand 41);
  $fn .= $chars[$_rand];
 }
 return $fn;
}
