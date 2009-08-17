#!/usr/bin/perl

use pazar;
use pazar::gene;
use pazar::talk;

use HTML::Template;

use CGI qw(:standard);
use CGI::Carp qw(fatalsToBrowser);
###use CGI::Debug( report => 'everything', on => 'anything' );

#use Data::Dumper;

my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};

require "$pazarcgipath/getsession.pl";

# open the html header template
#my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");

#$template->param(TITLE => 'PAZAR sequence name update');
#$template->param(PAZAR_CGI => $pazar_cgi);
# send the obligatory Content-Type and print the template output
#print "Content-Type: text/html\n\n", $template->output;

print "Content-Type: text/html\n\n";
#get userinfo
my $get = new CGI;
my %params = %{$get->Vars};


if($loggedin eq 'true') {

	my $dbname = $ENV{PAZAR_name};
	my $dbhost = $ENV{PAZAR_host};
	
	my $DBUSER = $ENV{PAZAR_adminuser};
	my $DBPASS = $ENV{PAZAR_adminpass};
	my $DBDRV  = $ENV{PAZAR_drv};
	
	my $DBURL  = "DBI:$DBDRV:dbname=$dbname;host=$dbhost";
	
	my $dbh = DBI->connect($DBURL,$DBUSER,$DBPASS) or die "Can't connect to pazar database";
	
	#get analysis id and project id
    my $sequenceid = $params{sid};
    my $projectid = $params{pid};
    my $mode = $params{mode};
    my $seqname = $params{seqname};
	my $snameeditable = "false";

	foreach my $proj (@projids) {
	#see if $proj is the same as the analysis project or if my userid is same as analysis user_id
	    if($proj == $projectid) {
			#comments are editable
			$snameeditable = "true";
	    }
	}
#make sure user is a member of the project

	if($snameeditable eq "true") {
		#if yes, check mode
		if($mode eq "form") {
			print<<FORM_DONE;
			<form method="post" action="updatesequencename.pl">
			<input type="hidden" name="mode" value="update">
			<input type="hidden" name="sid" value="$sequenceid">
			<input type="hidden" name="pid" value="$projectid">
			<table><tr><td>Enter sequence name here: </td><td><input type=text name="seqname" size=30></td></tr></table>
			<input type="submit" value="submit">
			</form>
FORM_DONE
		} elsif ($mode eq "update") {
			if ($sequenceid =~ /^CO/) {
				$sequenceid =~ s/\D//g;
				$sequenceid =~ s/^0+//;
				$dbh->do("update construct set construct_name='$seqname' where construct_id=$sequenceid");
				#more HTML
				print "<script>window.opener.document.getElementById('ajaxseqname').innerHTML=\"$seqname\"</script>";
				print "Construct name updated<br><input type='button' value='Close window' onClick=javascript:window.close();>";
			} else {
				$dbh->do("update reg_seq set tfbs_name='$seqname' where reg_seq_id=$sequenceid");
				#more HTML
				print "<script>window.opener.document.getElementById('ajaxseqname').innerHTML=\"$seqname\"</script>";
				print "Sequence name updated<br><input type='button' value='Close window' onClick=javascript:window.close();>";
			}
		}
	} else {
	#if no, display error
		print "You are not authorized to update the name of this sequence";
	}
} else {
    print "You must be logged in to update sequence name";
}
