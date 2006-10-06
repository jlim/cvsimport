#!/usr/bin/perl

use HTML::Template;
use Exporter;
use CGI qw(  :all);
use pazar;
#use CGI::Debug(report => everything, on => anything);

require '/usr/local/apache/pazar.info/cgi-bin/getsession.pl';

# open the html header template
my $template = HTML::Template->new(filename => '/usr/local/apache/pazar.info/cgi-bin/header.tmpl');

# fill in template parameters
$template->param(TITLE => 'PAZAR submission interface');
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
    if (val && val.disabled==false) { nm=val.name; if ((val=val.value)!="") {
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

resetMenu = function() {
   var ddm=document.getElementsByTagName("select");
   for (var n=0; n<ddm.length; n++) {
      ddm[n].selectedIndex=0;
   }
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
st.value=args[2];
endel=document.getElementById('end');
endel.value=args[3];
chrel=document.getElementById('chromosome');
chrel.value=args[0];
orgrel=document.getElementById('organism');
orgrel.value=args[4];
buildrel=document.getElementById('build');
buildrel.value=args[5];
seqrel=document.getElementById('sequence');
seqrel.value=args[6];
trel=document.getElementById('tid');
trel.value=args[8];
fstrel=document.getElementById('fstart');
fstrel.value=args[9];
fendrel=document.getElementById('fend');
fendrel.value=args[10];
gidrel=document.getElementById('gid');
gidrel.value=args[7];
strrel=document.getElementById('str');
strrel.value=args[1];
giddesc=document.getElementById('giddesc');
giddesc.value=args[11];
}

function PopUp(PopUpUrl){
var ScreenWidth=window.screen.width;
var ScreenHeight=window.screen.height;
var movefromedge=0;
placementx=(ScreenWidth/2)-((580)/500);
placementy=(ScreenHeight/2)-((380+10)/6);
WinPop=window.open(PopUpUrl,"","width=580,height=380,toolbar=1,location=1,directories=1,status=1,scrollbars=1,menubar=1,resizable=1,left="+placementx+",top="+placementy+",screenX="+placementx+",screenY="+placementy+",");
}

function setCount(target){
    if (document.MM_returnValue) {
if(target == 0) 
{
document.CRE.action="http://www.pazar.info/cgi-bin/sWI/TFcomplex.cgi";
document.CRE.target="Window1";
window.open('about:blank','Window1','height=800, width=800,toolbar=1,location=1,directories=1,status=1,scrollbars=1,menubar=1,resizable=1');
}
if(target == 1) 
{
document.CRE.action="http://www.pazar.info/cgi-bin/sWI/psite_get_cre.cgi";
document.CRE.target="Window2";
window.open('about:blank','Window2','height=800, width=800,toolbar=1,location=1,directories=1,status=1,scrollbars=1,menubar=1,resizable=1');
}
if(target == 2) 
{
document.CRE.action="http://www.pazar.info/cgi-bin/sWI/accept_cre.cgi";
document.CRE.target="_self";
}
}
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
    $template->param(LOGOUT => "$info{first} $info{last} logged in. ".'<a href=\'http://www.pazar.info/cgi-bin/logout.pl\'>Log Out</a>');
}
else
{
    #log in link
    $template->param(LOGOUT => '<a href=\'http://www.pazar.info/cgi-bin/login.pl\'>Log In</a>');
}

# send the obligatory Content-Type and print the template output
print "Content-Type: text/html\n\n", $template->output;

my $docroot=$ENV{PAZARHTDOCSPATH}.'/sWI';
my $cgiroot=$ENV{SERVER_NAME} . $ENV{PAZARCGI}.'/sWI';
my $docpath=$ENV{SERVER_NAME}.'/sWI';
my $cgipath=$ENV{PAZARCGIPATH}.'/sWI';

our $query=new CGI;

my %params=%{$query->Vars};
my $userid=$info{userid};

unless ($userid) {&goback(2,$query);}

my $proj = $params{'project'};

my $nextpage="$docroot/creanalysis.htm";
my $alterpage="$docroot/TFcentric.htm";
my $pazar;
eval {$pazar = pazar->new( 
		       -host          =>    $ENV{PAZAR_host},
		       -user          =>    $ENV{PAZAR_pubuser},
		       -pass          =>    $ENV{PAZAR_pubpass},
		       -pazar_user    =>    $info{user},
		       -pazar_pass    =>    $info{pass},
		       -dbname        =>    $ENV{PAZAR_name},
		       -drv           =>    'mysql',
		       -project       =>    $proj);};

if ($@) {
    print "<p class=\"warning\">You cannot submit to this project</p>";
#    print "error $@";
    exit;
}
unless ($pazar->get_projectid) {
    print "<p class=\"warning\">You cannot submit to this project</p>";
    exit;
}

#create a unique analysis name by adding random number with current time as seed
srand(time() ^ ($$ + ($$ << 15) ) );
my $randnum = substr(rand() * 100,3);
my $aid = 'analysis_'.$randnum;

if ($params{TFcentric}) {
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
    my @classes= $pazar->get_all_classes();
    my @families= $pazar->get_all_families();

open (TFC,$alterpage);
while (my $buf=<TFC>) {
	if ($buf=~/action/i) {
		$buf=~s/serverpath/$cgiroot/i;
	}
	print $buf;
	if (($buf=~/form/i)&&($buf=~/method/i)&&($buf=~/post/i)) {
	    print $query->hidden('project', $proj);
	    print $query->hidden('aname', $aid);
	}
	if ($buf=~/<h3>Select from my TFs:/i) {
	    if (@mytfs) {
		print $query->scrolling_list('mytfs',\@mytfs,1,'true');
		print "<br><br><input name=\"mycomplex\" type=\"submit\" id=\"mycomplex\" value=\"Proceed to CRE section\">";
	    } else {
		print "<p class=\"warning\">You don't have any TFs in this project yet!</p>";
	    }
	}
	if ($buf=~/<input type=\"text\" name=\"class\"/i && @classes) {
	    my @sorted_classes = sort @classes;
	    unshift @sorted_classes, 'Select from existing classes';
	    my $hidclass;
	    foreach my $class (@sorted_classes) {
		if ($hidclass) {
		    $hidclass=$hidclass."::".$class;
		} else {
		    $hidclass=$class;
		}
	    }
	    print "<b>  OR  </b>";
	    print $query->scrolling_list('myclass',\@sorted_classes,1,'true');
	    print $query->hidden('hidcla', $hidclass);
	}
	if ($buf=~/<input type=\"text\" name=\"family\"/i && @families) {
	    my @sorted_families = sort @families;
	    unshift @sorted_families, 'Select from existing families';
	    my $hidfam;
	    foreach my $fam (@sorted_families) {
		if ($hidfam) {
		    $hidfam=$hidfam."::".$fam;
		} else {
		    $hidfam=$fam;
		}
	    }

	    print "<b>  OR  </b>";
	    print $query->scrolling_list('myfamily',\@sorted_families,1,'true');
	    print $query->hidden('hidfam', $hidfam);
	}

}
close TFC;
# print out the html tail template
my $template_tail = HTML::Template->new(filename => '/usr/local/apache/pazar.info/cgi-bin/tail.tmpl');
print $template_tail->output;
exit();
}

open (NEXT, $nextpage);
while (my $buf=<NEXT>) {
    $buf=~s/htpath/$docpath/;
    $buf=~s/serverpath/$cgiroot/i;
    print $buf;
    if (($buf=~/form/i)&&($buf=~/method/i)&&($buf=~/post/i)) {
	print $query->hidden('project', $proj);
	print $query->hidden('aname', $aid);
	next;
    }
}
close NEXT;

# print out the html tail template
my $template_tail = HTML::Template->new(filename => '/usr/local/apache/pazar.info/cgi-bin/tail.tmpl');
print $template_tail->output;
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

exit(0);
}

