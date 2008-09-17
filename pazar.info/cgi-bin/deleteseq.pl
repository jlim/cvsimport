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

$template->param(TITLE => 'PAZAR sequence name update');
$template->param(PAZAR_CGI => $pazar_cgi);
# send the obligatory Content-Type and print the template output
print "Content-Type: text/html\n\n", $template->output;

#get userinfo
my $get = new CGI;
my %params = %{$get->Vars};


#checke if logged in

if($loggedin eq "true")
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
    my $sequenceid = $params{sid};
    my $projectid = $params{pid};
    my $mode = $params{mode};

    my $seqeditable = "false"; #whether user is allowed to modify the sequence

    foreach my $proj (@projids) {
	#see if $proj is the same as the analysis project
	if($proj == $projectid)
	{
	    #comments are editable
	    $seqeditable = "true";
	}
    }
    #make sure user is a member of the project
    if($seqeditable eq "true")
    {
	$dbh->do("delete from reg_seq where reg_seq_id=".$sequenceid);
##	print "delete from reg_seq where reg_seq_id=".$sequenceid."<br>";
	print "Sequence with ID ".$sequenceid." has been deleted<br>";

	$dbh->do("delete from dataset where reg_seq_id=".$sequenceid." AND project_id=".$projectid);
##	print "delete from dataset where reg_seq_id=".$sequenceid."<br>";
	print "Associated datasets have been deleted<br>";

	$dbh->do("delete from conserved_el where reg_seq_id=".$sequenceid." AND project_id=".$projectid);
##	print "delete from conserved_el where reg_seq_id=".$sequenceid."<br>";
	print "Associated conserved elements have been deleted<br>";

	$dbh->do("delete from reg_seq_construct where reg_seq_id=".$sequenceid." AND project_id=".$projectid);
##	print "delete from reg_seq_construct where reg_seq_id=".$sequenceid."<br>";
	print "Associated constructs have been deleted<br>";

	$dbh->do("delete from anchor_reg_seq where reg_seq_id=".$sequenceid);
##	print "delete from anchor_reg_seq where reg_seq_id=".$sequenceid."<br>";

        #get matrix_id referenced with the reg_seq_id (may return >1)
	my $matrixsth = $dbh->prepare("select matrix_id from reg_seq_set where reg_seq_id=".$sequenceid);
	$matrixsth->execute;
	if(my $matrixhref = $matrixsth->fetchrow_hashref)
	{
	    #find out how many other reg_seq_set records refer to this matrix
	    my $matrixsth2 = $dbh->prepare("select * from reg_seq_set where reg_seq_id!=".$sequenceid."AND matrix_id=".$matrixhref->{matrix_id});
##	    print "select * from reg_seq_set where reg_seq_id!=".$sequenceid."AND matrix_id=".$matrixhref->{matrix_id}."<br>";
	    
	    $matrixsth2->execute;

	    my $matrixcounter = 0;
	    while(my $matrixhref2 = $matrixsth2->fetchrow_hashref)
	    {
		$matrixcounter++;
	    }

	    #delete matrix and matrix info if reg_seq being deleted is the only one referencing this matrix
	    if($matrixcounter == 0)
	    {
	
	    $dbh->do("delete from matrix where matrix_id=".$matrixhref->{matrix_id}." AND project_id=".$projectid);
##		print "delete from matrix where matrix_id=".$matrixhref->{matrix_id}."<br>";
		
	    $dbh->do("delete from matrix_info where matrix_id=".$matrixhref->{matrix_id});
##		print "delete from matrix_info where matrix_id=".$matrixhref->{matrix_id}."<br>";
	    print "Associated matrix info with ID ".$matrixhref->{matrix_id} . " has been deleted<br>";
	    }
	
	    $dbh->do("delete from reg_seq_set where reg_seq_id=".$sequenceid);
##	    print "delete from reg_seq_set where reg_seq_id=".$sequenceid."<br>";
	}
	print "Sequence was successfully deleted<br>";
    }
    #if no, display error
    else
    {
	print "You are not authorized to delete this sequence";
    }
}
else
{
    print "You must be logged in to delete this sequence";
}
