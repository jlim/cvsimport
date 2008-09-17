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
my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");

$template->param(TITLE => 'PAZAR Analysis Delete');
$template->param(PAZAR_CGI => $pazar_cgi);
# send the obligatory Content-Type and print the template output
print "Content-Type: text/html\n\n", $template->output;
#get userinfo
my $get = new CGI;
my %params = %{$get->Vars};


if($loggedin eq 'true')
{
    my $dbname = $ENV{PAZAR_name};
    my $dbhost = $ENV{PAZAR_host};

    my $DBUSER = $ENV{PAZAR_adminuser};
    my $DBPASS = $ENV{PAZAR_adminpass};
    my $DBDRV  = $ENV{PAZAR_drv};

    my $DBURL  = "DBI:$DBDRV:dbname=$dbname;host=$dbhost";

    my $dbh = DBI->connect($DBURL,$DBUSER,$DBPASS)
	or die "Can't connect to pazar database";

    #get analysis id and project id
    my $analysisid = $params{aid};
    my $projectid = $params{pid};
    my $mode = $params{mode};
    my $analysiseditable = "false"; #whether user is allowed to modify this analysis

    foreach my $proj (@projids) {
	#see if $proj is the same as the analysis project or if my userid is same as analysis user_id
	if($proj == $projectid)
	{
	    #comments are editable
	    $analysiseditable = "true";
	}
    }
    #make sure user is a member of the project

    if($analysiseditable eq "true")
    {
	$dbh->do("delete from analysis where analysis_id=".$analysisid);
##    print "delete from analysis where analysis_id=".$analysisid."<br>";
	print "Analysis with ID: ".$analysisid." deleted<br>";

	my $sth1 = $dbh->prepare("select analysis_input_id from analysis_input where analysis_id=$analysisid");
	$sth1->execute;
	while(my $href1 = $sth1->fetchrow_hashref)
	{
##	print "<font color='red'><b>Looping on analysis input id: ".$href1->{analysis_input_id}."</b></font><br>";
	    my $sth3 = $dbh->prepare("select analysis_i_link_id,analysis_o_link_id from analysis_i_link where analysis_input_id=".$href1->{analysis_input_id});
	    $sth3->execute;
	    #iterate through analysis_i_link records
	    while(my $href3 = $sth3->fetchrow_hashref)
	    {
##	    print "<b>looping on analysis_i_link records</b><br>";
		#delete the analysis output
		my $sth4 = $dbh->prepare("select analysis_output_id from analysis_o_link where analysis_i_link_id=".$href3->{analysis_i_link_id}." OR analysis_o_link_id=".$href3->{analysis_o_link_id}); # maybe too inclusive?
		$sth4->execute;
	
		#iterate over analysis output ids
		while(my $href4 = $sth4->fetchrow_hashref)
		{
		    #select io_type_id from analysis_output

		    #delete the io_type
		    #check if io_type only associated with analysis outputs being deleted
		    #if so
		    my $outputiosth = $dbh->prepare("select io_type_id from analysis_output where analysis_output_id=".$href4->{analysis_output_id});
		    $outputiosth->execute;
		    my $outputiohref = $outputiosth->fetchrow_hashref;
		    my $output_iotypeid = $outputiohref->{io_type_id};
		    
		    #figure out how many analysis outputs refer to the io_type record
		    my $outputs_sth = $dbh->prepare("select analysis_output_id from analysis_output where analysis_output_id!=".$href4->{analysis_output_id}." AND io_type_id=".$output_iotypeid);
		    $outputs_sth->execute;
		    my $numreferringoutputs = 0;
		    while(my $outputs_href = $outputs_sth->fetchrow_hashref)
		    {
			$numreferringoutputs++;
		    }
		    
		    if($numreferringoutputs == 0)
		    {
			$dbh->do("delete from io_type where io_type_id=".$output_iotypeid);
##		    print "output iotype: delete from io_type where io_type_id=".$output_iotypeid."<br>";
		    }
		    #should we only delete if not referenced by other inputs?
		    $dbh->do("delete from analysis_output where analysis_output_id=".$href4->{analysis_output_id});
##		print "delete from analysis_output where analysis_output_id=".$href4->{analysis_output_id}."<br>";
		    print "Deleted analysis output with ID: ".$href4->{analysis_output_id}."<br>";
		}
	    
		#delete analysis_o_link
		$dbh->do("delete from analysis_o_link where analysis_o_link_id=".$href3->{analysis_o_link_id});
##	    print "delete from analysis_o_link where analysis_o_link_id=".$href3->{analysis_o_link_id}."<br>";

		$dbh->do("delete from analysis_i_link where analysis_i_link_id=".$href3->{analysis_i_link_id});
##	    print "delete from analysis_i_link where analysis_i_link_id=".$href3->{analysis_i_link_id}."<br>";
	    }	       
    
	    my $sth2 = $dbh->prepare("select io_type_id from analysis_input where analysis_id=$analysisid");
	    $sth2->execute;
	    #check if io_type only associated with analysis inputs being deleted
	    #if so
	    
	    my $inputiosth = $dbh->prepare("select io_type_id from analysis_input where analysis_input_id=".$href1->{analysis_input_id});
	    $inputiosth->execute;
	    my $inputiohref = $inputiosth->fetchrow_hashref;
	    my $input_iotypeid = $inputiohref->{io_type_id};
	
	    #figure out how many analysis outputs refer to the io_type record
	    my $inputs_sth = $dbh->prepare("select analysis_input_id from analysis_input where analysis_input_id!=".$href1->{analysis_input_id}." AND io_type_id=".$input_iotypeid);
	    $inputs_sth->execute;
	    my $numreferringinputs = 0;
	    while(my $inputs_href = $inputs_sth->fetchrow_hashref)
	    {
		$numreferringinputs++;
	    }	

	    if($numreferringinputs == 0)
	    {
		#make sure these io records aren't linked to other analysis inputs (not being deleted)
		$dbh->do("delete from io_type where io_type_id=".$input_io_type_id);
##	    print "input iotype: delete from io_type where io_type_id=".$input_iotypeid."<br>";
	    }
	    $dbh->do("delete from analysis_input where analysis_input_id=".$href1->{analysis_input_id});
##	print "delete from analysis_input where analysis_input_id=".$href1->{analysis_input_id}."<br>";
	    print "Deleted analysis input with ID: ".$href1->{analysis_input_id}."<br>";
	}    
	print "Analysis was successfully deleted<br>";
    }
#if no, display error
    else
    {
	print "You are not authorized to delete this analysis";
    }
}
else
{
    print "You must be logged in to delete this analysis";
}
