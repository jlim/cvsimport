#!/usr/bin/perl

use  lib $ENV{BPLIVE};

use HTML::Template;
use Exporter;
use CGI qw(  :all);
use pazar;
use CGI::Debug;

require '../getsession.pl';

# open the html header template
my $template = HTML::Template->new(filename => '../header.tmpl');

# fill in template parameters
$template->param(TITLE => 'Submission entry form');
$template->param(JAVASCRIPT_FUNCTION => q{
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
placementx=(ScreenWidth/2)-((580)/500);
placementy=(ScreenHeight/2)-((380+10)/6);
WinPop=window.open(PopUpUrl,"","width=580,height=380,toolbar=1,location=1,directories=1,status=1,scrollbars=1,menubar=1,resizable=1,left="+placementx+",top="+placementy+",screenX="+placementx+",screenY="+placementy+",");
}

function MM_callJS(jsStr) { //v2.0
  return eval(jsStr)
}

function MM_popupMsg(msg) { //v1.0
  alert(msg);
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

my $docroot=$ENV{PAZARHTDOCSPATH}.'/sWI';
my $cgiroot=$ENV{SERVER_NAME} . $ENV{PAZARCGI}.'/sWI';

our $query=new CGI;

my %params=%{$query->Vars};
my $userid=$info{userid};
my $talkdb=$params{auxDB};
unless ($userid) {&goback(2,$query);}

my $aid = $params{'aname'};
my $pubmedid = $params{'pubmedid'};
my $desc1 = $params{'textarea2'};
my $proj = $params{'project'};

my $pazar = pazar->new( 
		       -host          =>    $ENV{PAZAR_host},
		       -user          =>    $ENV{PAZAR_pubuser},
		       -pass          =>    $ENV{PAZAR_pubpass},
		       -pazar_user    =>    $info{user},
		       -pazar_pass    =>    $info{pass},
		       -dbname        =>    $ENV{PAZAR_name},
		       -drv           =>    'mysql',
		       -project       =>    $proj);

die "You cannot submit to this project" unless ($pazar->{projectid});
my $err=check_input_and_write($pazar,$aid,$proj);
if ($params{TFcentric}) {
&tfcentric;
exit();
}
my $nextpage="$docroot/creanalysis.htm";
my $selfpage="$docroot/entryform1.htm";
my $tmpdir="$cgiroot/tmp";
chdir($tmpdir);

open (NEXT, $nextpage) ||die;

#print $query->h3("Analysis $aid");
#print $query->h3("Submission authorized");
mkdir($userid) unless (-e $userid);
chdir $userid;
system ("rm -fr *");
$file=filename(length(10));

while (my $buf=<NEXT>) {
  if (($buf=~/TFcomplexadd/)||($buf=~/Add to set of mutations/)) {
    $buf=~s/file/'$file'/;
     print $buf;
     next;
  }
  if (($buf=~/form/i)&&($buf=~/method/i)&&($buf=~/post/i)) {
	    $buf=~s/serverpath/$cgiroot/i;
      print $buf;
#  unless ($buf=~/method/&&/name/&&/action/) {my $buf=<NEXT>; print $buf;}
      foreach my $key (keys %params) {
	  my $val=$params{$key};
	  #     print "$key $val",$html->br;
	  print "\<input name=\"$key\" type=\"hidden\" value=\"$val\"\>";
      }
      print "\<input name=\"userid\" type=\"hidden\" value=\"$userid\"\>";
      print "\<input name=\"filebase\" type=\"hidden\" value=\"$file\"\>";
      print "\<input name=\"auxDB\" type=\"hidden\" value=\"$talkdb\"\>";
      next;
  }
  print $buf;
}
close NEXT;

# print out the html tail template
my $template_tail = HTML::Template->new(filename => '../tail.tmpl');
print $template_tail->output;
exit();


sub check_input_and_write {
my ($pazar,$aid,$proj)=@_;
return "Need analysis name" unless ($aid);
$aid=uc($aid);
my $projid=$pazar->get_projectid;
my $dh=$pazar->prepare("select count(*) from analysis where project_id='$projid' and name='$aid'")||die;
$dh->execute||die;
my $exist=$dh->fetchrow_array;
if ($exist) { print "<p class=\"warning\">Analysis $aid for project $proj already exists. Modifying analysis is disabled at the moment.</p>";
# print out the html tail template
my $template_tail = HTML::Template->new(filename => '../tail.tmpl');
print $template_tail->output;
exit();
	  }
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


sub tfcentric {
my $alterpage="$docroot/TFcentric.htm";
open (TFC,$alterpage)||die;
while (my $buf=<TFC>) {
	if ($buf=~/action/i) {
		$buf=~s/serverpath/$cgiroot/i;
	}
    print $buf;
    if (($buf=~/form/i)&&($buf=~/method/i)&&($buf=~/post/i)) {
        &forward_args;
    }
}
close TFC;
# print out the html tail template
my $template_tail = HTML::Template->new(filename => '../tail.tmpl');
print $template_tail->output;
}

sub forward_args {
foreach my $key (keys %params) {
    print $query->hidden($key,$params{$key});
}
}
