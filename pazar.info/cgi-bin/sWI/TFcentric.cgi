#!/usr/bin/perl

use HTML::Template;
use CGI qw( :all);
#use CGI::Debug(report => everything, on => anything);
use pazar::talk;

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

function setCount(target){
if(target == 0) 
{
document.SEQ.action="http://www.pazar.info/cgi-bin/sWI/TFcentric_CRE.cgi";
document.SEQ.target="Window3";
window.open('about:blank','Window3','height=800, width=800,toolbar=1,location=1,directories=1,status=1,scrollbars=1,menubar=1,resizable=1');
}
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
my $cgiroot=$ENV{SERVER_NAME}.$ENV{PAZARCGI}.'/sWI';

my $selfpage="$docroot/TFcentric.htm";
my $nextpage="$docroot/TFcentric_CRE.htm";

my @voc=qw(TF TFDB  family class modifications);
my $query=new CGI;
my %params = %{$query->Vars};

my (%tf,%tfdb,%class,%family,%modif,%seen,%interact);
my $input = $params{'submit'};
my $user=$info{user};
my $pass=$info{pass};
my $analysis=$params{'aname'};
my $an_desc=$params{'analysis_desc'};
my $auxDB=$params{'auxDB'};
my $proj=$params{'project'};

SUBMIT: {
if ($input eq 'cancel') {  exit();}
if ($params{'AddTF'}) { last SUBMIT;} #Do what you normally do (add and write)
if ($params{'addtocomplex'}) { &next_page($user,$pass,\%params,$query); exit();}#JUst in case we decide we need more stuff to add
}

#TODO: checks recognizing the genes
open (SELF,$selfpage)||die "Cannot open $selfpage";

my $i=grep(/TFDB/,keys %params);
my $k=1;
my $next=$i;
#$next=$i+1 if ($i>0);


#print "Next is : $next i is $i";
foreach my $key (keys %params) {
            next if ($key eq 'aname')||($key=~/TFcomplex/)||($key eq 'project')||($key eq 'analysis_desc');
            #print $key,"__";
            if ((($key=~/TF\d/i)||($key=~/TF$/i))&&($key!~/AddTF/)) { my $id=$key; $id=~s/\D//g; $id=$id=~/d/?$id:$next; $tf{$id}=$params{$key};}
            if ($key=~/TFDB/i) { my $id=$key; $id=~s/\D//g; $id=$id=~/d/?$id:$next; $tfdb{$id}=$params{$key}; }
            if ($key=~/class/i) { my $id=$key; $id=~s/\D//g; $id=$id=~/d/?$id:$next; $class{$id}=$params{$key}; }
            if ($key=~/family/i) { my $id=$key; $id=~s/\D//g; $id=$id=~/d/?$id:$next; $family{$id}=$params{$key}; }
            if ($key=~/interact/i) { my $id=$key; $id=~s/\D//g; $id=$id=~/d/?$id:$next; $interact{$id}=$params{$key}; }
            if ($key=~/modific/i) { my $id=$key; $id=~s/\D//g; $id=$id=~/\d/?$id:$next; $modif{$id}=$params{$key};  }
            
            print "\<input name=\"$key\" type=\"hidden\" value=\"$params{$key}\"\>"; 
}
my $started=1;
while (my $buf=<SELF>) {
    $buf=~s/serverpath/$cgiroot/;
    if ($buf=~/validateForm/) {
        print $buf;
        next;
    }
#    if (($buf=~/modifications/i)&&($params{modifications})) {
#        $buf=~s/name/value=\"$params{modifications}\" name/;
#    }
#       if (($buf=~/organism/i)&&($params{organism})) {
#        $buf=~s/name/value=\"$params{organism}\" name/;
#    }
       if (($buf=~/pubmed/i)&&($params{pubmed})) {
        $buf=~s/name/value=\"$params{pubmed}\" name/;
    }
    if (($buf=~/TFcomplex/i)&&($params{TFcomplex})) {
        $buf=~s/name/value=\"$params{TFcomplex}\" name/;
    }
    print $buf;
	if ($buf=~/body/i) {$seen{body}++;}
	if ($buf=~/\<form/i) {$seen{form}++;} 
	if ($buf=~/pubmed/i) {$seen{modif}++;} 
	if (($buf=~/\<hr\>/)&&($seen{modif})&&($started)) { 
        $started=0;
	print "\<input name=\"aname\" type=\"hidden\" value=\"$analysis\"\>";
	print "\<input name=\"analysis_desc\" type=\"hidden\" value=\"$an_desc\"\>";
	print "\<input name=\"auxDB\" type=\"hidden\" value=\"$auxDB\"\>";
	print "\<input name=\"project\" type=\"hidden\" value=\"$proj\"\>";
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
                    if ($key eq 'modifications') {$val=$modif{$k}; next VAL;}
                }
                print $lkey,' ',$query->textfield (-label=>$lkey,-name=>$lkey,-size=>16, -value=>$val), $query->br; 
            }
            print $query->hr;
        }
	}
}
exit();

sub next_page {
    my ($user,$pass,$params,$query)=@_;
    my %params=%{$params};
    unless ($user&&$pass) {
	print $query->h3("An error occurred- not a valid user?\n If you believe this is an error, e-mail us and describe the problem");
# print out the html tail template
	my $template_tail = HTML::Template->new(filename => '../tail.tmpl');
	print $template_tail->output;
	exit();
    }
    my @numbered=qw(TF TFDB interact class family modifications);
    my @db;
    foreach my $dbkey (grep(/TFDB/,keys %params)) {
	push @db, $params{$dbkey};
    }
    my @tf;
    foreach my $tfkey (grep(/^TF([0-9]*)$/,keys %params)) {
	push @tf, $params{$tfkey};
    }

    my $tfs=&check_TF(\@db,\@tf);
    my %tfs=%$tfs;
 #Add 0 to the 0 key
    foreach my $mp(keys %params) {
	my $key=$mp;
	if ((grep (/\b$mp\b/,@numbered))&&($mp!~/\d/)) {   
	    $key .='0' ;
	    $params{$key}=$params{$mp};
	    delete $params{$mp};
	}
	foreach my $trans (keys %tfs) {
	    if ($params{$key} eq $trans) {
		my $ens_key='ENS_'.$key;
		$params{$ens_key}=$tfs{$trans};
	    }
	}
    }

    print $query->start_form(-method=>'POST',-target=>'',
			     -action=>'',-name=>'SEQ');
    &forward_args($query,\%params);
    print $query->h2('TF data accepted:');
    foreach my $trans (keys %tfs) {
	print "The provided TF $trans has been successfully converted to the Ensembl transcript ID $tfs{$trans}.<br>";
    }
    print $query->h2('Please add CRE data now');
    print $query->h2('We suggest you should not make more than 1 submission simultanuously');
    print $query->h3('Do not close this window if you want to make more than one CRE submissions');
    print $query->h3('Just click the appropriate button again once you have completed a submission');
    print $query->submit(-name=>'submit',
			 -value=>'Add CRE to which the TF/TF complex binds',
                         -onClick=>"setCount(0)");
    print $query->h4(' or ');
    print $query->submit(-name=>'submit',
			 -value=>'Add SELEX or similar artificial entry',
                         -onClick=>"setCount(0)");
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

sub check_TF {
    my ($db,$tf)=@_;

    my $ensdb = pazar::talk->new(DB=>'ensembl',USER=>$ENV{ENS_USER},PASS=>$ENV{ENS_PASS},HOST=>$ENV{ENS_HOST},DRV=>'mysql');

    my $gkdb = pazar::talk->new(DB=>'genekeydb',USER=>$ENV{GKDB_USER},PASS=>$ENV{GKDB_PASS},HOST=>$ENV{GKDB_HOST},DRV=>'mysql');

    my %factors;
    for (my $i=0;$i<@$db;$i++) {
	my $accn=@$tf[$i];
	my $dbaccn=@$db[$i];
	my @trans;
	if ($dbaccn eq 'EnsEMBL_gene') {
	    @trans = $gkdb->ens_transcripts_by_gene($accn);
	    unless ($trans[0]=~/\w{4,}\d{6,}/) {print "<p class=\"warning\">Conversion failed for $accn! Maybe it is not a $dbaccn ID!</p>"; exit;}
	} elsif ($dbaccn eq 'EnsEMBL_transcript') {
	    push @trans,$accn;
	    unless ($trans[0]=~/\w{4,}\d{6,}/) {print "<p class=\"warning\">Conversion failed for $accn! Maybe it is not a $dbaccn ID!</p>"; exit;}
	} elsif ($dbaccn eq 'EntrezGene') {
	    my @gene=$gkdb->llid_to_ens($accn);
	    unless ($gene[0]=~/\w{4,}\d{6,}/) {print "<p class=\"warning\">Conversion failed for $accn! Maybe it is not a $dbaccn ID!</p>"; exit;}
	    @trans = $gkdb->ens_transcripts_by_gene($gene[0]);
	} elsif ($dbaccn eq 'refseq') {
	    @trans=$gkdb->nm_to_enst($accn);
	    unless ($trans[0]=~/\w{4,}\d{6,}/) {print "<p class=\"warning\">Conversion failed for $accn! Maybe it is not a $dbaccn ID!</p>"; exit;}
	} elsif ($dbaccn eq 'swissprot') {
	    my $sp=$gkdb->{dbh}->prepare("select organism from ll_locus a, gk_ll2sprot b where a.ll_id=b.ll_id and sprot_id=?")||die;
	    $sp->execute($accn)||die;
	    my $species=$sp->fetchrow_array();
	    if (!$species) {print "<p class=\"warning\">Conversion failed for $accn! Maybe it is not a $dbaccn ID!</p>"; exit;}
	    $ensdb->change_mart_organism($species);
	    @trans =$ensdb->swissprot_to_enst($accn);
	    unless ($trans[0]=~/\w{4,}\d{6,}/) {print "<p class=\"warning\">Conversion failed for $accn! Maybe it is not a $dbaccn ID!</p>"; exit;}
	}
	$factors{$accn}=$trans[0];
    }
    return \%factors;
}
