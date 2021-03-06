#!/usr/bin/perl

use HTML::Template;
use Exporter;
use CGI qw(  :all);
use pazar;

#use CGI::Debug(report => everything, on => anything);

my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};
my $pazarhtdocspath = $ENV{PAZARHTDOCSPATH};

my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");
my $temptail = HTML::Template->new(filename => "$pazarcgipath/tail.tmpl");
$template->param(TITLE => "Submit data | PAZAR");
$template->param(PAZAR_HTML => $pazar_html);
$template->param(PAZAR_CGI => $pazar_cgi);
$template->param(ONLOAD_FUNCTION => "resetMenu();");
$template->param(JAVASCRIPT_FUNCTION => q{
	function PopUp(PopUpUrl){
		var ScreenWidth=window.screen.width;
		var ScreenHeight=window.screen.height;
		var movefromedge=0;
		placementx=(ScreenWidth/2)-((580)/500);
		placementy=(ScreenHeight/2)-((380+10)/6);
		WinPop=window.open(PopUpUrl,"","width=580,height=380,toolbar=1,location=1,directories=1,status=1,scrollbars=1,menubar=1,resizable=1,left="+placementx+",top="+placementy+",screenX="+placementx+",screenY="+placementy+",");
	}}.qq{
	var ChildWin=null;
	function setCount_submit(target){
		if (document.MM_returnValue) {
		if (!ChildWin || ChildWin.closed ) {
			if(target == 0) {
				document.CRE.action="$pazar_cgi/sWI/TFcomplex.cgi";
				document.CRE.target="ChildWin";
				ChildWin=window.open('about:blank','ChildWin','height=800, width=800,toolbar=1,location=1,directories=1,status=1,scrollbars=1,menubar=1,resizable=1');
			}
			if(target == 1) {
				document.CRE.action="$pazar_cgi/sWI/psite_get_cre.cgi";
				document.CRE.target="ChildWin";
				ChildWin=window.open('about:blank','ChildWin','height=800, width=800,toolbar=1,location=1,directories=1,status=1,scrollbars=1,menubar=1,resizable=1');
			}
			if(target == 2) {
				document.CRE.action="$pazar_cgi/sWI/accept_cre.cgi";
				document.CRE.target="_self";
			}
			if(target == 3) {
				document.CRE.action="$pazar_cgi/sWI/geneselect.cgi";
				document.CRE.target="_self";
			}
		} else{
			alert('A child window is open. Please finish your annotation before entering a new Experiment!');
			ChildWin.focus();
			return correctSubmitHandler();
		}
	}
}});


require "$pazarcgipath/getsession.pl";
if ($loggedin eq "true") {
	$template->param(LOGOUT => qq{<span class="b">You are signed in as $info{first} $info{last}.</span> <a href="$pazar_cgi/logout.pl" class="b">Sign out</a>});
} else {
	$template->param(LOGOUT => qq{<a href="$pazar_cgi/login.pl"><span class="b">Sign in</span></a>});
}

print "Content-Type: text/html\n\n", $template->output;

my $docroot=$pazarhtdocspath.'/sWI';
my $cgiroot=$pazar_cgi.'/sWI';
my $docpath=$pazar_html.'/sWI';

our $query=new CGI;

my %params=%{$query->Vars};
my $userid=$info{userid};

unless ($userid) {&goback(2,$query);}

my $proj = $params{'project'};

my $nextpage = "$docroot/creanalysis.htm";
my $alterpage = "$docroot/TFcentric.htm";
my $pazar;
eval {$pazar = pazar->new( 
			   -host          =>    $ENV{PAZAR_host},
			   -user          =>    $ENV{PAZAR_pubuser},
			   -pass          =>    $ENV{PAZAR_pubpass},
			   -pazar_user    =>    $info{user},
			   -pazar_pass    =>    $info{pass},
			   -dbname        =>    $ENV{PAZAR_name},
			   -drv           =>    $ENV{PAZAR_drv},
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
	$buf=~s/pazar_cgi/$pazar_cgi/g;
	$buf=~s/pazar_html/$pazar_html/g;
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
my $template_tail = HTML::Template->new(filename => "$pazarcgipath/tail.tmpl");
print $template_tail->output;
exit();
}

if ($params{mode} eq 'addevid') {

	my $regid=$params{regid};
	my $id=write_pazarid($regid,'RS');
	print<<ALTERNATE;
<h2>Annotate your Cis Regulatory Element: $id</h2>
<form style="height: 546px;" action="" method="post" name="CRE" target="">
<input type='hidden' name='project' value='$proj'>
<input type='hidden' name='aname' value='$aid'>
<input type='hidden' name='regid' value='$regid'>
  <hr style="width: 100%; height: 2px;">
  <h3>Transcription factor/complex binding to this CRE (if known)</h3>
  <p>
	<input value="Add TF Interaction Evidence" name="TFcomplexadd" type="submit" onClick="MM_validateForm();return setCount_submit(0);return document.MM_returnValue;">
  </p>
  <hr style="width: 100%; height: 2px;">
  <h3>Interaction Evidence with an unknown factor (e.g. nuclear extract)</h3>
  <p>
	<input value="Add Interaction Evidence" name="Interactadd" type="submit" onClick="MM_validateForm();return setCount_submit(0);return document.MM_returnValue;">
  </p>
  <hr style="width: 100%; height: 2px;">
  <h3>Other Experimental Evidence for a Role of this CRE in Regulating Gene Expression</h3>
  <p>
	<input value="Add Experimental Evidence" name="Evidadd" type="submit" onClick="MM_validateForm();return setCount_submit(1);return document.MM_returnValue;">
  </p>
  <hr>
  <p> 
	<input name="done" id="done" value="Done" type="submit" onClick="MM_validateForm();return setCount_submit(3);return document.MM_returnValue;">
  </p><br>  </form>

ALTERNATE

} else {
	my $geneID='?&gid='.$params{geneID};

	open (NEXT, $nextpage);
	while (my $buf=<NEXT>) {
	$buf=~s/htpath/$docpath/;
	$buf=~s/serverpath/$cgiroot/i;
	$buf=~s/genepath/$geneID/i;
	if ($params{geneID}) {
		if ($buf=~/<input id=\"gid\" name=\"gid\" maxlength=\"25\" type=\"text\">/i) {
		print "<input id='gid' name='gid' value='$params{geneID}' maxlength='25' type='text' disabled><input id='hidgid' name='hidgid' value='$params{geneID}' type='hidden'>";
		next;
		}
		if ($buf=~/<input name=\"giddesc\" type=\"text\" id=\"giddesc\" maxlength=255>/i) {
		print "<input id='giddesc' name='giddesc' value='$params{genedesc}' maxlength='255' type='text' disabled><input id='hidgiddesc' name='hidgiddesc' value='$params{genedesc}' type='hidden'>";
		next;
		}
	}
	print $buf;
	if (($buf=~/form/i)&&($buf=~/method/i)&&($buf=~/post/i)) {
		print $query->hidden('project', $proj);
		print $query->hidden('aname', $aid);
		next;
	}
	}
	close NEXT;
}

# print out the html tail template
print $temptail->output;
exit();



sub goback {
	my $err=shift;
	my $query=shift;
	print $query->header;
	my $message="under construction";
	$message="Not authenticated and the interface is submission only" if ($err==2);
	print $query->h1("An error has occured because ");
	print $query->h2($message);
	exit(0);
}

sub write_pazarid {
	my $id=shift;
	my $type=shift;
	my $id7d = sprintf "%07d",$id;
	my $pazarid=$type.$id7d;
	return $pazarid;
}
