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
function showHide(inputID) {
	theObj = document.getElementById(inputID)
	theDisp = theObj.style.display == "none" ? "block" : "none"
	theObj.style.display = theDisp
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
my $pid=$pazar->get_projectid;
unless ($pid) {
    print "<p class=\"warning\">You cannot submit to this project</p>";
    exit;
}

my $talkdb = pazar::talk->new(DB=>'ensembl',USER=>$ENV{ENS_USER},PASS=>$ENV{ENS_PASS},HOST=>$ENV{ENS_HOST},DRV=>'mysql');

print "<h1>Cis-Regulatory Sequence Submission</h1><hr>\n";
print "<form name=\"NewGene\" method=\"post\" action=\"http://www.pazar.info/cgi-bin/sWI/psite_get.cgi\" enctype=\"multipart/form-data\" target=\"_self\">\n";
&forward_args(\%params);
print "<input type=\"submit\" value=\"Annotate a New Gene\"></form>\n";

print "<span class='title3'>OR Add/Modify data in one of the following genes:</span><br>\n";

my @gene_project;
my $genes = &select($pazar, "SELECT * FROM gene_source WHERE project_id='$pid'");
if ($genes) {
    while (my $gene=$genes->fetchrow_hashref) {
	my $found=0;
	my $tsrs = &select($pazar, "SELECT * FROM tsr WHERE gene_source_id='$gene->{gene_source_id}'");
	if ($tsrs) {
	    while (my $tsr=$tsrs->fetchrow_hashref && $found==0) {
		my $reg_seqs = &select($pazar, "SELECT distinct reg_seq.* FROM reg_seq, anchor_reg_seq, tsr WHERE reg_seq.reg_seq_id=anchor_reg_seq.reg_seq_id AND anchor_reg_seq.tsr_id='$tsr->{tsr_id}'");
		if ($reg_seqs) {
		    my @coords = $talkdb->get_ens_chr($gene->{db_accn});
		    $coords[5]=~s/\[.*\]//g;
		    $coords[5]=~s/\(.*\)//g;
		    $coords[5]=~s/\.//g;
		    my $species = $talkdb->current_org();
		    $species = ucfirst($species)||'-';

		    my $pazargeneid = write_pazarid($gene->{gene_source_id},'GS');
		    my $gene_desc=$gene->{description};
		    if ($gene_desc eq '0'||$gene_desc eq '') {$gene_desc='-';}
		    push @gene_project, {
			ID => $pazargeneid,
			shortID => $gene->{gene_source_id},
			accn => $gene->{db_accn},
			desc => $gene_desc,
			ens_desc => $coords[5],
			species => $species};
		    $found++;
		}
	    }
	}
    }
}
unless ($gene_project[0]->{ID}) {print "<p class=\"warning\">No Genes have been annotated yet in this project!</p>"; exit;}

print "<table width='750' class='summarytable'><tr>\n";
print "<td class='genelisttabletitle' width='150'><form name=\"species_browse\" method=\"post\" action=\"http://www.pazar.info/cgi-bin/sWI/geneselect.cgi\" enctype=\"multipart/form-data\" target=\"_self\"><input type='hidden' name='BROWSE' value='species'>";
&forward_args(\%params);
print "<input type=\"submit\" class=\"submitLink2\" value=\"Species\"></form></td>\n";
print "<td class='genelisttabletitle' width='100'><form name=\"ID_browse\" method=\"post\" action=\"http://www.pazar.info/cgi-bin/sWI/geneselect.cgi\" enctype=\"multipart/form-data\" target=\"_self\"><input type='hidden' name='BROWSE' value='ID'>";
&forward_args(\%params);
print "<input type=\"submit\" class=\"submitLink2\" value=\"PAZAR Gene ID\"></form></td>\n";
print "<td class='genelisttabletitle' width='100'><form name=\"desc_browse\" method=\"post\" action=\"http://www.pazar.info/cgi-bin/sWI/geneselect.cgi\" enctype=\"multipart/form-data\" target=\"_self\"><input type='hidden' name='BROWSE' value='desc'>";
&forward_args(\%params);
print "<input type=\"submit\" class=\"submitLink2\" value=\"Gene name\"><small>(user defined)</small></form></td>\n";
print "<td class='genelisttabletitle' width='150'><form name=\"accn_browse\" method=\"post\" action=\"http://www.pazar.info/cgi-bin/sWI/geneselect.cgi\" enctype=\"multipart/form-data\" target=\"_self\"><input type='hidden' name='BROWSE' value='accn'>";
&forward_args(\%params);
print "<input type=\"submit\" class=\"submitLink2\" value=\"EnsEMBL Gene ID\"></form></td>\n";
print "<td class='genelisttabletitle' width='200'><form name=\"ens_desc_browse\" method=\"post\" action=\"http://www.pazar.info/cgi-bin/sWI/geneselect.cgi\" enctype=\"multipart/form-data\" target=\"_self\"><input type='hidden' name='BROWSE' value='ens_desc'>";
&forward_args(\%params);
print "<input type=\"submit\" class=\"submitLink2\" value=\"EnsEMBL Gene Description\"></form></td>\n";
print "<td class='genelisttabletitle'' width='50'></td>\n";
print "</tr>\n";

my @sorted;
if ($params{BROWSE} eq 'species') {
    @sorted=sort {lc($a->{species}) cmp lc($b->{species}) or lc($a->{desc}) cmp lc($b->{desc})} @gene_project;
} elsif ($params{BROWSE} eq 'ID') {
    @sorted=sort {$a->{ID} cmp $b->{ID}} @gene_project;
} elsif ($params{BROWSE} eq 'ens_desc') {
    @sorted=sort {lc($a->{ens_desc}) cmp lc($b->{ens_desc}) or lc($a->{species}) cmp lc($b->{species})} @gene_project;
} elsif ($params{BROWSE} eq 'accn') {
    @sorted=sort {$a->{accn} cmp $b->{accn}} @gene_project;
} else {
    @sorted=sort {lc($a->{desc}) cmp lc($b->{desc}) or lc($a->{species}) cmp lc($b->{species})} @gene_project;
}

my $bg_color = 0;
my %colors = (0 => "#fffff0",
	      1 => "#BDE0DC");

my $style='display:none';
foreach my $gene_data (@sorted) {
###print out gene data
print "<a name='$gene_data->{accn}'></a><tr id='$gene_data->{accn}'><td class='basictdnoborder' width='150' bgcolor=\"$colors{$bg_color}\">$gene_data->{species}</td>\n";
print "<td class='basictdnoborder' width='100' bgcolor=\"$colors{$bg_color}\">$gene_data->{ID}</td>\n";
print "<td class='basictdnoborder' width='100' bgcolor=\"$colors{$bg_color}\">$gene_data->{desc}</td>\n";
print "<td class='basictdnoborder' width='150' bgcolor=\"$colors{$bg_color}\">$gene_data->{accn}</td>\n";
print "<td class='basictdnoborder' width='200' bgcolor=\"$colors{$bg_color}\">$gene_data->{ens_desc}</td>\n";
print "<td class='basictdnoborder' width='50' bgcolor=\"$colors{$bg_color}\"><a href=\"#$gene_data->{accn}\"  onClick = \"showHide('$gene_data->{ID}');\">Annotate</a></td>\n";
print "</tr>\n";
print "<tr><td class='basictdnoborder' bgcolor=\"$colors{$bg_color}\" COLSPAN=6><table width=100% id=\"$gene_data->{ID}\" style=\"$style\">";
print "<tr><td bgcolor=\"$colors{$bg_color}\"><form name=\"NewSeq\" method=\"post\" action=\"http://www.pazar.info/cgi-bin/sWI/psite_get.cgi\" enctype=\"multipart/form-data\" target=\"_self\">&nbsp;<input type='hidden' name='geneID' value='$gene_data->{accn}'><input type='hidden' name='genedesc' value='$gene_data->{desc}'>";
&forward_args(\%params);
print "<input type='submit' name='submit' value='Add a regulatory Sequence'></form></td></tr><tr><td>\n";

###print out sequence data
my $bg_color2 = 0;
my %colors2 = (0 => "#fffff0",
	       1 => "#ffbd83"
	       );

print "<table class=\"summarytable\" width=100%><tr><td class=\"seqlisttabletitle\" width='100'><span class=\"bold\">RegSeq ID</span></td>";
print "<td width='110' class=\"seqlisttabletitle\"><span class=\"bold\">Sequence Name</span></td>";
print "<td width='240' class=\"seqlisttabletitle\"><span class=\"bold\">Sequence</span></td>";
print "<td width='180' class=\"seqlisttabletitle\"><span class=\"bold\">Coordinates</span></td>";
print "<td width='110' class=\"seqlisttabletitle\"></td>";
print "</tr>";
my @regseqs = $pazar->get_reg_seqs_by_accn($gene_data->{accn}); 
if (!$regseqs[0]) {
    print "<p class=\"warning\">No Regulatory Sequence has been annotated for this gene yet!</p>";
} else {
    foreach my $regseq (@regseqs) {
	my $regid=$regseq->accession_number;
	my $id=write_pazarid($regid,'RS');
	print "<tr><td width='100' class=\"basictdnoborder\" bgcolor=\"$colors2{$bg_color2}\"><div class='smoverflow'>$id</div></td>";

	my $seqname=$regseq->id||'-';
	print "<td width='110' class=\"basictdnoborder\" bgcolor=\"$colors2{$bg_color2}\"><div class='smoverflow'>".$seqname."&nbsp;</div></td>";	       

	my $seqstr=chopstr($regseq->seq,32);
	print "<td height=20 width=240 class=\"basictdnoborder\" bgcolor=\"$colors2{$bg_color2}\"><div style=\"font-family:monospace;height:40; width:240;overflow:auto;\">".$seqstr."</div></td>";

	print "<td width='180' class=\"basictdnoborder\" bgcolor=\"$colors2{$bg_color2}\"><div class='smoverflow'>chr".$regseq->chromosome.":".$regseq->start."-".$regseq->end."</div></td>";

	print "<td width='110' class=\"basictdnoborder\" bgcolor=\"$colors2{$bg_color2}\"><div class='smoverflow'><form name=\"addevid$id\" method=\"post\" action=\"http://www.pazar.info/cgi-bin/sWI/psite_get.cgi\" enctype=\"multipart/form-data\"><input type=hidden name='regid' value='$regid'><input type=hidden name='mode' value='addevid'>";
&forward_args(\%params);
	print "<input type='submit' name='submit' value='Add Evidence'></form></div></td>";
	print "</tr>";
	$bg_color2 =  1 - $bg_color2;
    }
}
print "</table></td></tr></table></td></tr>\n";
$bg_color =  1 - $bg_color;
}
print "</table><br>";

# print out the html tail template
my $template_tail = HTML::Template->new(filename => '/usr/local/apache/pazar.info/cgi-bin/tail.tmpl');
print $template_tail->output;


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

sub forward_args {
    my $params=shift;
    my %params=%{$params};
    foreach my $key (keys %params) {
	unless ($key eq 'BROWSE') {
	    print $query->hidden($key,$params{$key});
	}
    }
}

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

#split long lines into several smaller ones by inserting a line break at a specified character interval
#parameters: string to break up, interval
sub chopstr {

    my $longstr = $_[0];
    my $interval = $_[1];
    my $newstr = "";

    while(length($longstr) > $interval)
    {
#put line break at character+1 position
	$newstr = $newstr.substr($longstr,0,$interval)."<br>";
	$longstr = substr($longstr,$interval); #return everything starting at interval'th character	
    }
    $newstr = $newstr . $longstr;

    return $newstr;
}
