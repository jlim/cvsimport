#!/usr/bin/perl

use lib $ENV{ENS_API};

use HTML::Template;
#use CGI::Debug (report=>'everything', on=>'anything');
use CGI::Debug;

use CGI qw( :all);
use DBI;
use Bio::EnsEMBL::DBSQL::DBAdaptor;
use Bio::EnsEMBL::DBSQL::TranscriptAdaptor;
use Bio::EnsEMBL::DBSQL::SliceAdaptor;
use Bio::EnsEMBL::Transcript;
use Bio::EnsEMBL::Upstream;
use pazar::talk;

require '../getsession.pl';

# open the html header template
my $template = HTML::Template->new(filename => '../header.tmpl');

# fill in template parameters
$template->param(TITLE => 'Submission - method description');
$template->param(JAVASCRIPT_FUNCTION => q{
function ActivateCheckBox ()
{
document.form.pubmedid.disabled = false;
if ( document.form.published.value == 'Yes' )
{
document.form.pubmedid.disabled = false;
}
else
{
document.form.pubmedid.disabled = true;
}
}

function MM_openBrWindow(theURL,winName,features) { //v2.0
  window.open(theURL,winName,features);
}

function onoff(objref) {
	if (objref.disabled==true ) {
		objref.disabled=false;} 
		else {
		objref.disabled=true;}
	return;
}

function MM_findObj(n, d) { //v4.01
  var p,i,x;  if(!d) d=document; if((p=n.indexOf("?"))>0&&parent.frames.length) {
    d=parent.frames[n.substring(p+1)].document; n=n.substring(0,p);}
  if(!(x=d[n])&&d.all) x=d.all[n]; for (i=0;!x&&i<d.forms.length;i++) x=d.forms[i][n];
  for(i=0;!x&&d.layers&&i<d.layers.length;i++) x=MM_findObj(n,d.layers[i].document);
  if(!x && d.getElementById) x=d.getElementById(n); return x;
}

function MM_validateForm() { //v4.0
  var i,p,q,nm,test,num,min,max,errors='',args=MM_validateForm.arguments;
  for (i=0; i<(args.length-2); i+=3) { test=args[i+2]; val=MM_findObj(args[i]);
    if (val) { nm=val.name; if ((val=val.value)!="") {
      if (test.indexOf('isEmail')!=-1) { p=val.indexOf('@');
        if (p<1 || p==(val.length-1)) errors+='- '+nm+' must contain an e-mail address.\n';
      } else if (test!='R') { num = parseFloat(val);
        if (isNaN(val)) errors+='- '+nm+' must contain a number.\n';
        if (test.indexOf('inRange') != -1) { p=test.indexOf(':');
          min=test.substring(8,p); max=test.substring(p+1);
          if (num<min || max<num) errors+='- '+nm+' must contain a number between '+min+' and '+max+'.\n';
    } } } else if (test.charAt(0) == 'R') errors += '- '+nm+' is required.\n'; }
  } if (errors) alert('The following error(s) occurred:\n'+errors);
  document.MM_returnValue = (errors == '');
}

function NewOption(arg){
//alert('The pager number & (val)')
var args=arg.split(":");
st=document.getElementById('start');
st.value=args[1];
endel=document.getElementById('end');
endel.value=args[2];
chrel=document.getElementById('chromosome');
chrel.value=args[0];
orgrel=document.getElementById('organism');
orgrel.value=args[3];
buildrel=document.getElementById('build');
buildrel.value=args[4];
seqrel=document.getElementById('sequence');
seqrel.value=args[5];
trel=document.getElementById('tid');
trel.value=args[6];
fstrel=document.getElementById('fstart');
fstrel.value=args[7];
fendrel=document.getElementById('fend');
fendrel.value=args[8];
}

function PopUp(PopUpUrl){
var ScreenWidth=window.screen.width;
var ScreenHeight=window.screen.height;
var movefromedge=0;
placementx=(ScreenWidth/2)-((410)/500);
placementy=(ScreenHeight/2)-((440+10)/6);
WinPop=window.open(PopUpUrl,"","width=410,height=440,toolbar=1,location=1,directories=1,status=1,scrollbars=1,menubar=1,resizable=1,left="+placementx+",top="+placementy+",screenX="+placementx+",screenY="+placementy+",");
}
});

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

our $query=new CGI;
my %params = %{$query->Vars};

our $cgiroot=$ENV{SERVER_NAME}.$ENV{PAZARCGI}.'/sWI';
our $docroot=$ENV{PAZARHTDOCSPATH}.'/sWI';

my $user=$info{user};
my $pass=$info{pass};

unless (($user)&&($pass)) {
    &goback(2,$query);
}

my $aid=$params{aname};
my $region=$params{start};
my $element=$params{sequence};
#my ($trf_llid,$trfens,$trferr) =convert_id($params{TFDB},$params{TF});
my $selfpage="$docroot/condition1.htm";
open (SELF, $selfpage) ||die;
while (my $buf=<SELF>) {
    if (($buf=~/\<form/) && ($buf=~/action\=/)) {
	$buf=~s/serverpath/$cgiroot/i;
    }
    print $buf;
    if (($buf=~/\<form/) && ($buf=~/action\=/)) {
	foreach my $key (keys %params) {
	    my $val=$params{$key};
	    print "\<input name=\"$key\" type=\"hidden\" value=\"$val\"\>";
	}
    }
    if ($buf=~/Method name/) {
	my @methods;
	push @methods,('',$regdb->known_methods);
	print $query->scrolling_list('methodname',\@methods,1,'true');
    }
}
}
close SELF;
# print out the html tail template
my $template_tail = HTML::Template->new(filename => '../tail.tmpl');
print $template_tail->output;

exit();
}

# sub getseq {
# my ($id, $slice_adaptor, $chr,$begin,$end, $orient, $region)=@_;
# =SECURUTY RISK
# my $env=$ENV{PERL5LIB};
# @env=split(/:/,$env);
# my $sysarg="ssh -v -i /home/sao/.ssh/identity.pub watson.lsd.ornl.gov perl ";
# foreach my $dir (@env) {
#    $sysarg.="-I$dir ";
# }
# $sysarg.="  /home/sao/BSA/bsa/get_upstream_by_transcr.pl |";
# open (SEQ, $sysarg)||die ;
# while (my $buf=<SEQ>) {
#   print $buf;
#   print "n line";
# }
# close SEQ;
# =cut
# my $l;
# #Let's see how much we want
# if ($region<0) {
# 	$l=1000-$region;
# 	$region=$l;
# }
# else {
# 	$region+=100;
# 	$l=$region;
# }
# #my $upstream =  Bio::EnsEMBL::Upstream->new(-transcript=>$id,-length=>$l);
# if ($orient==1) {
# 	$start=$begin-$region;
# 	$end=$begin;
# }
# else {
#    	$start=$end-1000;
#         $end=$end+$region;
# }
# my $slice;
# print "$start $end $region $orient";
# $slice = $slice_adaptor->fetch_by_region('chromosome',$chr,$start,$end,$orient);
# unless ($orient==1) {
# 	my $rsl=$slice->invert;
# 	return $begin,$rsl->seq;
# }
# return $begin,$slice->seq;
# }

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
# print out the html tail template
my $template_tail = HTML::Template->new(filename => '../tail.tmpl');
print $template_tail->output;

exit;
}


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
	
# sub read_pos {
# 	my $params=shift;
# 	my $user=$params->{userid};
# 	my $analysis=$params->{aname};
# 	my $file=$user ."\_".$analysis . ".pos.tmp";
# 	open (POS,$file)||die;
# 	while (my $buf=<POS>) {
# 		chomp $buf;
# 		my ($t1,$v1,$t2,$v2)=split(/\t/,$buf);
# 		$params->{$t1}=$v1;
# 		$params->{$t2}=$v2;
# 	}
# 	close POS;
# 	unlink($file);
# 	return %{$params};
# }


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
my $template_tail = HTML::Template->new(filename => '../tail.tmpl');
print $template_tail->output;
exit(0);
}


# sub tfcentric {
# my $alterpage="$docroot/TFcentric.htm";
# open (TFC,$alterpage)||die;
# my $done;
# while (my $buf=<TFC>) {
#     if (($buf=~/form/i)&&($buf=~/method/i)&&($buf=~/post/i)) {
#         $done=1;
#         &forward_args;
#     }
# }
# }

sub forward_args {
foreach my $key (keys %params) {
    print $query->hidden($key,$params{$key});
}
}
