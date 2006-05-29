#!/usr/bin/perl

use HTML::Template;
use CGI qw( :all);
#use CGI::Debug(report => everything, on => anything);


require '../getsession.pl';

# open the html header template
my $template = HTML::Template->new(filename => '../header.tmpl');

# fill in template parameters
$template->param(TITLE => 'TF-centric Submission');
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

#SYNOPSYS: Addin TF that interact with the target sequence and each other to produce a certain effect
my $docroot=$ENV{PAZARHTDOCSPATH}.'/sWI';
my $cgiroot=$ENV{SERVER_NAME}.$cgiroot.'/sWI';

my $selfpage="$docroot/TFcentric.htm";
my $nextpage="$docroot/TFcentric_CRE.htm";

my @voc=qw(TF TFDB  family class);
my $query=new CGI;
my %params = %{$query->Vars};

my (%tf,%tfdb,%class,%family,%modif,%seen,%interact);
my $input = $params{'submit'};
my $user=$info{user};
my $pass=$info{pass};
my $analysis=$params{'aname'};
my $auxDB=$params{'auxDB'};

SUBMIT: {
if ($input eq 'cancel') {  exit();}
if ($params{'AddTF'}) { last SUBMIT;} #Do what you normally do (add and write)
if ($params{'addtocomplex'}) { &next_page; exit();}#JUst in case we decide we need more stuff to add
}

#TODO: checks recognizing the genes
open (SELF,$selfpage)||die "Cannot open $selfpage";

my $i=grep(/TFDB/,keys %params);
my $k=1;
my $next=$i;
#$next=$i+1 if ($i>0);


#print "Next is : $next i is $i";
foreach my $key (keys %params) {
            next if ($key eq 'aname')||($key eq 'file')||($key eq 'user')||($key=~/TFcomplex/)||($key=~/modification/);
            #print $key,"__";
            if ((($key=~/TF\d/i)||($key=~/TF$/i))&&($key!~/AddTF/)) { my $id=$key; $id=~s/\D//g; $id=$id=~/d/?$id:$next; $tf{$id}=$params{$key};}
            if ($key=~/TFDB/i) { my $id=$key; $id=~s/\D//g; $id=$id=~/d/?$id:$next; $tfdb{$id}=$params{$key}; }
            if ($key=~/class/i) { my $id=$key; $id=~s/\D//g; $id=$id=~/d/?$id:$next; $class{$id}=$params{$key}; }
            if ($key=~/family/i) { my $id=$key; $id=~s/\D//g; $id=$id=~/d/?$id:$next; $family{$id}=$params{$key}; }
            if ($key=~/interact/i) { my $id=$key; $id=~s/\D//g; $id=$id=~/d/?$id:$next; $interact{$id}=$params{$key}; }
 #           if ($key=~/modific/i) { my $id=$key; $id=~s/\D//g; $id=$id=~/\d/?$id:$next; $modif{$id}=$params{$key};  }
            
            print "\<input name=\"$key\" type=\"hidden\" value=\"$params{$key}\"\>"; 
}
my $started=1;
while (my $buf=<SELF>) {
    $buf=~s/serverpath/$cgiroot/;
    if ($buf=~/validateForm/) {
        print $buf;
        next;
    }
    if (($buf=~/modifications/i)&&($params{modifications})) {
        $buf=~s/name/value=\"$params{modifications}\" name/;
    }
       if (($buf=~/organism/i)&&($params{organism})) {
        $buf=~s/name/value=\"$params{organism}\" name/;
    }
       if (($buf=~/build/i)&&($params{build})) {
        $buf=~s/name/value=\"$params{build}\" name/;
    }
    if (($buf=~/TFcomplex/i)&&($params{TFcomplex})) {
        $buf=~s/name/value=\"$params{TFcomplex}\" name/;
    }
    print $buf;
	if ($buf=~/body/i) {$seen{body}++;}
	if ($buf=~/\<form/i) {$seen{form}++;} 
	if ($buf=~/modifications/i) {$seen{modif}++;} 
	if (($buf=~/\<hr\>/)&&($seen{modif})&&($started)) { 
        $started=0;
		print "\<input name=\"aname\" type=\"hidden\" value=\"$analysis\"\>";
		print "\<input name=\"auxDB\" type=\"hidden\" value=\"$auxDB\"\>";
#        for my $j (1..$i) {
#            my $k1='TF' . $j;
#	        my $k2='TFDB' . $j;
#	        my $sel=uc($params{$k2});
        print $query->br;
        
        foreach my $k (1..$i) {
            print "Added complex member $k",$query->br;
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
                    if ($key eq 'class') {$val=$class{$k}; last VAL;}
                    if ($key eq 'family') {$val=$family{$k}; last VAL;}
                    if ($key eq 'interact') {$val=$interact{$k}; last VAL;}
                   # if ($key eq 'modifications') {$val=$modif{$k}; next VAL;}
                }
                print $lkey,' ',$query->textfield (-label=>$lkey,-name=>$lkey,-size=>16, -value=>$val), $query->br; 
            }
            print $query->hr;
        }
	}
}
exit();

sub next_page {
unless ($params{userid}) {
    print $query->h3("An error occurred- not a valid user?\n If you believe this is an error, e-mail us and describe the problem");
# print out the html tail template
my $template_tail = HTML::Template->new(filename => '../tail.tmpl');
print $template_tail->output;
    exit();
}
my @numbered=qw(TF TFDB interact class family);
foreach my $mp(keys %params) {#Add 0 to the 0 key
my $key=$mp;
    if ((grep (/\b$mp\b/,@numbered))&&($mp!~/\d/)) {   
        $key .='0' ;
	    $params{$key}=$params{$mp};
        delete $params{$mp};
    }
}
print $query->start_form(-method=>'POST',-target=>'new',-width=>310,-height=>240,-toolbar=>0,-location=>0,-directories=>0,-status=>0,
                            -scrollbars=>0,-menubar=>0,-resizable=>0,
                            -action=>'TFcentric_CRE.cgi');
&forward_args($query,\%params);
print $query->h2('TF data accepted, please add CRE data now');
print $query->h2('We suggest you should not make more than 1 submission simultanuously');
print $query->h3('Do not close this window if you want to make more than one CRE submissions');
print $query->h3('Just click the appropriate button again once you have completed a submission');
print $query->submit(-name=>'submit',
                        -value=>'Add CRE to which the TF/TF complex binds');
print $query->h4(' or ');
print $query->submit(-name=>'submit',
                        -value=>'Add SELEX or similar artificial entry');
print $query->endform;
# print out the html tail template
my $template_tail = HTML::Template->new(filename => '../tail.tmpl');
print $template_tail->output;
exit();
}

sub forward_args {
my ($query,$params)=@_;
my %params=%$params;
foreach my $key (keys %params) {
    print $query->hidden($key,$params{$key});
}
}
exit;

