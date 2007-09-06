#!/usr/bin/perl

use DBI;
use CGI qw( :all);
use CGI::HTMLError trace => 1;

my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};

my $query=new CGI;
my %params = %{$query->Vars};

my $dbname = $ENV{PAZAR_name};
my $dbhost = $ENV{PAZAR_host};

my $DBUSER = $ENV{PAZAR_adminuser};
my $DBPASS = $ENV{PAZAR_adminpass};
my $DBDRV  = $ENV{PAZAR_drv};
my $DBPORT  = $ENV{PAZAR_port}||3306;
my $DBURL = "DBI:$DBDRV:dbname=$dbname;host=$dbhost;port=$DBPORT";


my $dbh = DBI->connect($DBURL,$DBUSER,$DBPASS)
    or die "Can't connect to pazar database";

sub select {
    my ($dbh, $sql) = @_;
    my $sth=$dbh->prepare($sql);
#    $sth->execute or die "$dbh->errstr\n";
    $sth->execute;
    return $sth;
}

print "Content-type: text/html \n\n";

my $sth = $dbh->prepare("select * from project");

$sth->execute;
print "<H2>PROJECT INFORMATION<H2>";
	print "<table width=1200 border=1>";
	print "<tr><td width=100><b>Project ID</b></td><td width=150><b>Project Name</b></td></td><td><b>Status</b></td><td width=200><b>Last Edit</b></td><td width=500><b>Statistics</b></td><td><b>Users</b></td><td><b>Description</b></td></tr>";
while(my $href=$sth->fetchrow_hashref)
{
	print "<tr><td>".$href->{"project_id"} ."</td><td>" . $href->{"project_name"} . "</td><td>" . $href->{"status"} . "</td><td>" . $href->{"edit_date"}  . "</td>";
#get statistics




my $gnb=&select($dbh, "SELECT count(distinct db_accn) FROM gene_source a, tsr b WHERE a.projec
t_id='".$href->{"project_id"}."' and a.gene_source_id=b.gene_source_id");
my $genenb=$gnb->fetchrow_array||'0';
my $rnb=&select($dbh, "SELECT count(reg_seq_id) FROM reg_seq WHERE project_id='".$href->{"project_id"}."'");
my $regseqnb=$rnb->fetchrow_array||'0';
my $cnb=&select($dbh, "SELECT count(construct_id) FROM construct WHERE project_id='".$href->{"project_id"}."'");
my $constrnb=$cnb->fetchrow_array||'0';
my $tnb=&select($dbh, "SELECT count(funct_tf_id) FROM funct_tf WHERE project_id='".$href->{"project_id"}."'");
my $tfnb=$tnb->fetchrow_array||'0';
my $mnb=&select($dbh, "SELECT count(matrix_id) FROM matrix WHERE project_id='".$href->{"project_id"}."'");
my $matrixnb=$mnb->fetchrow_array||'0';
my $refnb=&select($dbh, "SELECT count(ref_id) FROM ref WHERE project_id='".$href->{"project_id"}."'");
my $refsnb=$refnb->fetchrow_array||'0';


print "<td>";
print "Regulated Genes: ".$genenb."<br>";
print "Regulatory sequence (genomic): ".$regseqnb."<br>";
print "Regulatory sequence (artificial): ".$constrnb."<br>";
print "Transcription Factors: ".$tfnb."<br>";
print "Transcription Factor Profiles: ".$matrixnb."<br>";
print "Annotated Publications: ".$refsnb."<br>";
print "</td>";

print "<td>";
#print users for that project
my $refu=&select($dbh, "SELECT users.username FROM users,project,user_project WHERE users.user_id=user_project.user_id AND user_project.project_id=project.project_id AND project.project_id='".$href->{"project_id"}."'");
while(my $refuser=$refu->fetchrow_array)
{
	print $refuser."<br>";
}
print "</td>";

print "<td>" . $href->{"description"}  . "&nbsp;</td>";
print "</tr>";
}

print "</table>";

print "<H2>USER INFORMATION</H2>";

       print "<table border=1>";
        print "<tr><td width=100><b>User ID</b></td><td width=150><b>Username</b></td></td><td><b>First Name</b></td><td width=200><b>Last Name</b></td><td width=300><b>Creation Date</b></td><td><b>Affiliation</b></td><td><b>Stable ID</b></td></tr>";

my $usersth = $dbh->prepare("select * from users");
$usersth->execute;
while(my $userhref = $usersth->fetchrow_hashref)
{
	print "<tr><td width=100>".$userhref->{"user_id"}."</td><td width=150>".  $userhref->{"username"} ."</td><td>".$userhref->{"first_name"} ."&nbsp;</td><td width=200>".$userhref->{"last_name"}."&nbsp;</td><td width=300>". $userhref->{"edit_date"}."</td><td>". $userhref->{"aff"}."&nbsp;</td><td>". $userhref->{"stable_id"}."&nbsp;</td></tr>";
}

print "</table>";
