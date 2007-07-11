#!/usr/bin/perl -w

use DBI;
use pazar;
use pazar::reg_seq;

use CGI qw(:standard);
use CGI::Carp qw(fatalsToBrowser);
#use CGI::Debug( report => 'everything', on => 'anything' );

my $pazar_html = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};
my $pazarhtdocspath = $ENV{PAZARHTDOCSPATH};

require "$pazarcgipath/getsession.pl";

my $get = new CGI;
my %params = %{$get->Vars};
my $resource = $params{resource};
my $ensembl_sync = "false";
my $ucsc_sync = "false";
my $pazar_version = "";
my $ucscdb = "";

#number of base pairs around start and end coordinates in browser display
my $flanking_bp = 50;

print "Content-Type: text/html\n\n";
print "<html><head><title>GFF custom track</title></head><body>";


###database connection
my $dbh= pazar->new( 
		     -host          =>    $ENV{PAZAR_host},
		     -user          =>    $ENV{PAZAR_adminuser},
		     -pass          =>    $ENV{PAZAR_adminpass},
		     -dbname        =>    $ENV{PAZAR_name},
		     -drv           =>    $ENV{PAZAR_drv});

my $ens_dbname = $ENV{TALKDB_ENSEMBL_NAME};
my $ens_dbhost = $ENV{ENS_HOST};
my $ens_DBUSER = $ENV{ENS_USER};
my $ens_DBPASS = $ENV{ENS_PASS};
my $ens_DBURL = "DBI:mysql:dbname=$ens_dbname;host=$ens_dbhost";

my $ens_dbh = DBI->connect($ens_DBURL,$ens_DBUSER,$ens_DBPASS)
    or die "Can't connect to ensembl database";

#use species to check whether ensembl and ucsc links are displayable using db_sync table in ensembl_databases
#print "species: ".lc($params{species});
my $ens_sth = $ens_dbh->prepare("select * from db_sync where organism='".lc($params{species})."'");
    $ens_sth->execute();
if (@row = $ens_sth->fetchrow_hashref)
{
    $pazar_version = $row[0]->{pazar_version};
#    print "pazar version: ".$pazar_version."<br>";

    $ensembl_sync = $row[0]->{ensembl};
#    print "ensembl_sync: ".$ensembl_sync."<br>";

    $ucscdb = $row[0]->{ucsc};

    if($ucscdb eq '')
    {
	$ucsc_sync="false";
    }
    else
    {
	$ucsc_sync="true";
    }
#    print "ucsc db: ".$ucscdb."<br>";
#    print "ucsc_sync: ".$ucsc_sync."<br>";

}

$ens_sth->finish();
$ens_dbh->disconnect();


#check whether or not to proceed with gff construction and track display
# check if resource is ucsc and organism is unavailable
# ucsc_sync false if database field empty
if(($resource eq "ucsc") && ($ucsc_sync eq "false"))
{
#print error message
    print "The track for this sequence feature could not be displayed";
}
else
{
    print "Loading genome browser...";
#continue with the rest of the file********************************************

    my @projects;
    
    my $projects=&select($dbh, "SELECT project_id, project_name FROM project WHERE upper(status)='OPEN' OR upper(status)='PUBLISHED'");
    while (my ($pid,$proj)=$projects->fetchrow_array) {
	push @projects, {name => $proj,
			 id   => $pid};
    }


    if ($loggedin eq 'true') {
	foreach my $proj (@projids) {
	    my $restricted=&select($dbh, "SELECT project_name FROM project WHERE project_id='$proj' and upper(status)='RESTRICTED'");
	    my @restr_proj=$restricted->fetchrow_array();
	    if (@restr_proj) {
		push @projects,  {name => $restr_proj[0],
				  id   => $proj}};
	}
    }


#print out projects
#foreach my $hashref (@projects)
#{
#    print "hash loop".$hashref->{name}."<br>";
#}


#need to make file name unique
#alter file name by adding random number with current time as seed
    srand(time() ^ ($$ + ($$ << 15) ) );
    my $randnum = substr(rand() * 100,3);
    my $filename  = 'pazarchr'.$params{chr}."_".$randnum.'.gff';
    my $file = $pazarhtdocspath.'/mapping/'.$filename;
    open (GFF,">$file")||die;

    my $chr = $params{chr};
    $chr=~s/\s//g;
    my $start = $params{start};
    $start=~s/\s//g;
    my $end = $params{end};
    $end=~s/\s//g;

#print "resource: ".$resource;

    my $header = "";
#print the header
    if($resource eq 'ucsc')
    {
	$header = "browser position chr".$chr.":".($start-$flanking_bp)."-".($end+$flanking_bp)."\n";
	$header = $header . "track name=PAZAR description='PAZAR-curated regulatory elements' color=160,1,1 url=\"$pazar_html/mapping/\"";
    }
    elsif($resource eq 'ensembl')
    {
	$header = "browser position chr".$chr.":".($start-$flanking_bp)."-".($end+$flanking_bp)."\n";
	$header = $header . "track name=PAZAR description='PAZAR-curated regulatory elements' color=160,1,1 url=\"$pazar_html/mapping/\"";
    }

#browser position chr5:142638872-142638896
#track name=ORegAnno description='ORegAnno-curated regulatory elements' color=160,1,1 url="http://www.bcgsc.ca:8080/oregano/recordview.action?recid=$$"
    print GFF $header."\n";
#    print $header."\n";

    foreach my $project (@projects) {
	my $proj=$project->{name};
	my $pid=$project->{id};
	my $sp=uc($params{species});
	my $rsh = &select($dbh, "SELECT reg_seq_id, begin, end, strand  FROM reg_seq a, coordinate b, location c WHERE a.project_id='$pid' AND c.location_id=b.location_id AND b.coordinate_id=a.coordinate_id AND chr='$chr' AND species='$sp'");
	while (my ($regid,$rsstart,$rsend,$rsstrand)=$rsh->fetchrow_array) {

	    my $id=write_pazarid($regid,'RS');
	    my $gff='chr'.$chr."\t".join("\t",$proj,$id,$rsstart,$rsend,'.',$rsstrand,'.',$proj."_".$id);
	    print GFF $gff."\n";
#	    print $gff."\n";
	}
    }
    close(GFF);

    if($resource eq 'ucsc')
    {

#assemble the ucsc web link
	print "<script>document.location.href='http://genome.ucsc.edu/cgi-bin/hgTracks?db=$ucscdb&hgt.customText=$pazar_html/mapping/$filename'</script>";
    }
    else
    {
	my $ensembl_url = "www.ensembl.org";
#assemble the ensembl web link
#if ensembl is sync, use current one, else use specified ensembl version
	unless ($ensembl_sync eq "sync")
	{
#take latter part of ensembl_sync and create url from it
	    my @ens_ver_date = split('_',$ensembl_sync);

	    $ensembl_url=$ens_ver_date[1].".archive.ensembl.org";
	}

#convert pazar species to ensembl species (capitalize first letter of species and replace any spaces with underscore)
	my $ensemblorg = lc($params{species});
	$ensemblorg=ucfirst($ensemblorg);
	$ensemblorg=~s/ /_/;

	print "<script>document.location.href='http://$ensembl_url/$ensemblorg/contigview?data_URL=$pazar_html/mapping/$filename'</script>";
    }
    
} # else continue with the rest of the file
print "</body></html>";

sub select {

    my ($dbh, $sql) = @_;
    my $sth=$dbh->prepare($sql);
    $sth->execute or die "$dbh->errstr\n";
    return $sth;
}

sub write_pazarid {
    my $id=shift;
    my $type=shift;
    my $id7d = sprintf "%07d",$id;
    my $pazarid=$type.$id7d;
    return $pazarid;
}
