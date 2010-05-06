#!/usr/local/bin/perl -l

use DBI;
use strict;
use HTTP::Lite;
use CGI qw(:standard);
use CGI::Carp qw(fatalsToBrowser);

my $q = new CGI;

my @dbanodb = ("vm2.cmmt.ubc.ca","ensembl_r","","","");
my @dbaendb = ("vm2.cmmt.ubc.ca","ensdbuser","ensdbuserpass","ensembl_databases");

sub rmtags() {
	my $input = shift;
	$input =~ s/\</\<\^\*/g;
	my @array = split(/\</, $input);
	my $r;
	foreach my $in (@array) {
		$in =~ s/\>/\*\^\>/g;
		my @tmp = split(/\>/, $in);
		my @out;
		foreach my $rest (@tmp) {
			@out = (@out,$rest) if ($rest !~ /^\^\*/) and ($rest !~ /\*\^$/);
		}
		$r = $r . join(" ",@out);
	}
	return $r;	
}

sub query() {
	my ($host,$user,$pass,$name,$s) = @_;
	my $dbh = DBI->connect("dbi:mysql:" . $name . ':' . $host, $user, $pass);
	my $input = $dbh->prepare($s);
	$input->execute;
	my @r;
	while (my @tmp = $input->fetchrow_array) {
		foreach my $row (@tmp) {
			@r = (@r,$row);
		}
	}
	return @r;
}

$dbanodb[4] = "SHOW DATABASES LIKE '%_core_%'";
my @dbs = &query(@dbanodb);

print $q->header("text/html");
print qq {
<html>
<head>
	<title>Parser</title>
	<style>
		td.cr {background-color: #ffffcc;}
		td.rr {background-color: #FFFF00;}
	</style>
</head>
<body>
};

@dbaendb = (@dbaendb,"SELECT DISTINCT organism FROM db_sync");
my @organisms = &query(@dbaendb);
pop(@dbaendb);
@dbaendb = (@dbaendb,"SELECT DISTINCT ucsc FROM db_sync");
my @cur_ucsc = &query(@dbaendb);

# #<table border="2">
# #<tbody>
# #<tr><td>organism</td><td>pazar version</td><td>ensembl</td><td>ucsc</td></tr>};
# #foreach my $organism (@organisms) {
# #	pop(@dbaendb);
# #	@dbaendb = (@dbaendb,"SELECT * FROM db_sync WHERE organism='$organism'");
# #	my @at = &query(@dbaendb);
# #	print qq {<tr><td>$at[0]</td><td>$at[1]</td><td>$at[2]</td><td>$at[3]</td></tr>};
# }
# #print qq {
# #</tbody>
# #</table>
print qq {
<p>Getting Ensembl homepages for each species...</p>
<table border="2" cellpadding="2"><tbody>
<tr>
	<td colspan="3"><h2>Ensembl</h2></td>
	<td colspan="3"><h2>UCSC</h2></td>
	<td></td>
</tr><tr>
	<td><h3>Ensembl species</h3></td>
	<td><h3>Ensembl assembly</h3></td>
	<td><h3>Ensembl date</h3></td>
	<td><h3>UCSC species</h3></td>
	<td><h3>UCSC assembly</h3></td>
	<td><h3>UCSC date</h3></td>
	<td><h3>Match</h3></td>
</tr>};

my $husc = new HTTP::Lite;
$husc->request("http://genome.ucsc.edu/FAQ/FAQreleases");
my $ucsc = $husc->body();
my @ucsc = split(/\n/,$ucsc);

my %interface = (
	"Aedes_aegypti" => "",
	"Anolis_carolinensis" => "anoCar",
	"Anopheles_gambiae" => "anoGam",
	"Apis_mellifera" => "apiMel",
	"Bos_taurus" => "bosTau",
	"Caenorhabditis_elegans" => "ce",
	"Canis_familiaris" => "canFam",
	"Cavia_porcellus" => "cavPor",
	"Choloepus _hoffmanni" => "",
	"Ciona_intestinalis" => "ci",
	"Ciona_savignyi" => "",
	"Danio_rerio" => "danRer",
	"Dasypus novemcinctus" => "",
	"Dipodomys_ordii" => "",
	"Drosophila_melanogaster" => "dm",
	"Echinops_telfairi" => "",
	"Equus_caballus" => "equCab",
	"Erinaceus_europaeus" => "",
	"Felis_catus" => "felCat",
	"Gallus_gallus" => "galGal",
	"Gasterosteus_aculeatus" => "gasAcu",
	"Gorilla_gorilla" => "",
	"Homo_sapiens" => "hg",
	"Loxodonta_africana" =>	"",
	"Macaca_mulatta" => "rheMac",
	"Microcebus_murinus" => "",
	"Monodelphis_domestica" => "monDom",
	"Mus_musculus" => "mm",
	"Myotis_lucifugus" => "",
	"Ochotona_princeps" => "",
	"Ornithorhynchus_anatinus" => "ornAna",
	"Oryctolagus_cuniculus" => "",
	"Oryzias_latipes" => "oryLat",
	"Otolemur_garnettii" => "",
	"Pan_troglodytes" => "panTro",
	"Pongo_pygmaeus" => "",
	"Procavia_capensis" => "",
	"Pteropus_vampyrus" => "",
	"Rattus_norvegicus" => "rn",
	"Saccharomyces_cerevisiae" => "sacCer",
	"Sorex_araneus" => "",
	"Spermophilus_tridecemlineatus" => "",
	"Taeniopygia_guttata" => "taeGut",
	"Takifugu_rubripes" => "fr",
	"Tarsius_syrichta" => "",
	"Tetraodon_nigroviridis" => "tetNig",
	"Tupaia_belangeri" => "",
	"Tursiops_truncatus" => "",
	"Vicugna_pacos" => "",
	"Xenopus_tropicalis" => "xenTro"
);

my $prev;
my $rows = 0;
foreach my $db (keys %interface) {
	my @x = split(/_/,$db);
	my $spc = ucfirst(lc($x[0] . "_" . $x[1]));
	my $spc_ucsc_print;
	my $spc_form_print;
	my $style = qq { class="cr"};
	if ($spc ne $prev) {
		$prev = $spc;
		my ($ens_assembl,$ens_species);
		my $y = qq {http://uswest.ensembl.org/} . $spc . qq{/Info/StatsTable};

#eg http://uswest.ensembl.org/Homo_sapiens/Info/StatsTable
#if ensembl ever changes website structure, we can get assemblies through API
#The following code is an example of how to get assembly information
###########################################
#use Bio::EnsEMBL::Registry;

#my $registry = 'Bio::EnsEMBL::Registry';

#$registry->load_registry_from_db(
#    -host => 'ensembldb.ensembl.org',
#    -user => 'anonymous'
#);

#my @db_adaptors = @{ $registry->get_all_DBAdaptors() };

#foreach my $db_adaptor (@db_adaptors) {
    
#        if ($db_adaptor->group() eq 'core')
#        {
#                my $db_connection = $db_adaptor->dbc();

#            printf(
#                "species/group\t%s/%s\ndatabase\t%s\nhost:port\t%s:%s\nassembly\t%s\n\n",
#                $db_adaptor->species(),   $db_adaptor->group(),
#                $db_connection->dbname(), $db_connection->host(),
#                $db_connection->port(), getassemblytype($db_adaptor)
#                );
#        }
#}


#note that DBAdaptor->assembly_type() is deprecated so use CoordSystemAdaptor now
#parameters: DBAdaptor object
#sub getassemblytype
#{
#my $csa = $_[0]->get_CoordSystemAdaptor();
#return $csa->fetch_all->[0]->version;
#}
################################


		my $http = new HTTP::Lite;
		$http->request($y);
		my $page = $http->body();
		$http = "";
		my @p = split(/Assembly:/,$page);
		if ($p[1]) {
			my @e = split(/\>/,$p[1]);
			my $m = $e[2];
			($ens_assembl,$ens_species) = split(/, /,$m);
		}
		foreach my $line (@ucsc) {
			my $spc_ucsc = $interface{$spc} if $interface{$spc};
			if ($spc_ucsc) {
				if ($line =~ /<TD>$spc_ucsc/) {
					my @data = split(/<\/TD><TD>/, $line);
					my $species = &rmtags($data[0]);
					my $ucscnom = &rmtags($data[1]);
					my $assembl = &rmtags($data[3]);
					my $asmdate = &rmtags($data[2]);
					if (grep(/^$ucscnom$/,@cur_ucsc)) { $style = qq { class="rr"}; }
					$species =~ s/&nbsp;//g;
					$spc_ucsc_print = $species if ($species =~ /\w/);
					$spc_ucsc_print =~ s/^\s+//g;
					$spc_ucsc_print =~ s/\s+$//g;
					$spc_form_print = $spc;
					$spc_form_print =~ s/_/ /g;
					$spc_form_print = lc $spc_form_print;
					$assembl =~ s/^\s+//g;
					$assembl =~ s/\s+$//g;
					print qq {
						<tr>
							<td$style>$spc</td>
							<td$style>$ens_assembl</td>
							<td$style>$ens_species</td>
							<td$style>$spc_ucsc_print</td>
							<td$style>$assembl - $ucscnom</td>
							<td$style>$asmdate</td>
							<td$style><form name="row$rows" action="UCSC_version_store.pl" target="_blank" method="POST">
								<input type="hidden" name="organism" value="$spc_form_print">
								<input type="hidden" name="ucsc" value="$ucscnom">
								<div id="div$rows"><input type="submit" name="button$rows" value="add">	</div><div id="divis$rows"><input type="submit" name="cancel$rows" value="remove"></div>
							</form></td>
						</tr>};
					$rows++;
					$style = "";
				}
			}
		}
	}
}
print qq {</tbody></table>};
#<iframe name="gw" width="1" height="1" src="UCSC_version_store.pl" frameborder="0"></iframe>};
print $q->end_html();
