#!/usr/bin/perl

use HTML::Template;
use CGI qw( :all);
#use CGI::Debug(report => everything, on => anything);
use pazar;

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

my $query=new CGI;

my $docroot=$ENV{PAZARHTDOCSPATH}.'/sWI';
my $cgiroot=$ENV{SERVER_NAME} . $ENV{PAZARCGI}.'/sWI';
my $docpath=$ENV{SERVER_NAME}.'/sWI';

my %params = %{$query->Vars};
my $user=$info{user};
my $pass=$info{pass};
my $proj=$params{project};

die 'Not logged in' unless (($user)&&($pass));

my $auxdb=$params{auxDB};

my $pazar=new pazar(-drv=>'mysql',-dbname=>$ENV{PAZAR_name},-user=>$ENV{PAZAR_pubuser}, -pazar_user=>$user, -pazar_pass=>$pass,
                        -pass=>$ENV{PAZAR_pubpass}, -host=>$ENV{PAZAR_host}, -project=>$proj);

my @voc=qw(TF TFDB  family class);

my (%tf,%tfdb,%class,%family,%modif,%seen,%interact);
my $input = $params{'submit'};

my $analysis=$params{'aname'};
unless ($params{userid}) {
    print $query->h3("An error occurred- not a valid user? If you believe this is an error e-mail us and describe the problem");
# print out the html tail template
my $template_tail = HTML::Template->new(filename => '../tail.tmpl');
print $template_tail->output;
    exit();
}

my 
$alterpage=$input=~/CRE/?"$docroot/TFcentric_CRE.htm":"$docroot/SELEX.htm";
open (TFC,$alterpage)||die "Page $alterpage removed?";
my $done;
while (my $buf=<TFC>) {
    $buf=~s/serverpath/$cgiroot/;
    $buf=~s/htpath/$docpath/;
    if ($buf=~/\<body/) {
        print $query->start_form(-method=>'POST',
                           -action=>"http://$cgiroot/addcre.cgi", -name=>'CRE');
        &forward_args($query,\%params);
    }
    if (($buf=~/form/i)&&($buf=~/method/i)&&($buf=~/post/i)) {
        $done=1;
        
    }
    else {
        if (($buf=~/interact0/)&&($buf!~/validateForm/)) {
            my $val=$params{interact0};
            $buf=~s/>/value=\"$val\">/;
        }
        if (($buf=~/reference/)&&($buf!~/validateForm/)) {
            my $val=$params{reference};
            $buf=~s/>/value=\"$val\">/;
        }
        print $buf;
        if ($buf=~m/Method \(select from list/) {
	        my @methods;
    	    push @methods,('',$pazar->get_method_names);
	        print $query->scrolling_list('methodname',\@methods,1,'true');
        }
    }
}
close TSC;
# print out the html tail template
my $template_tail = HTML::Template->new(filename => '../tail.tmpl');
print $template_tail->output;

exit();

sub forward_args {
my ($query,$params)=@_;
my %params=%$params;
my @noforward=qw(interact0 qualitative reference inttype interactscale methodname newmethod newmethoddesc sequence constructname artificialcomment);
foreach my $key (keys %params) {
    next if (grep(/$key/,@noforward));
    print $query->hidden($key,$params{$key}) unless ($key=~/new/);
}
 print $query->hidden('CREtype',$params{submit});

}
