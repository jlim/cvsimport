#!/usr/bin/perl

use HTML::Template;
use Data::Dumper;
use pazar;
use pazar::reg_seq;
use pazar::talk;
use pazar::tf::tfcomplex;
use pazar::tf::subunit;
use CGI qw(:standard);
use CGI::Carp qw(fatalsToBrowser);
#use CGI::Debug( report => 'everything', on => 'anything' );
use TFBS::PatternGen::MEME;
use TFBS::Matrix::PFM;

require 'getsession.pl';

 
# open the html header template
my $template = HTML::Template->new(filename => 'header.tmpl');

# fill in template parameters
$template->param(TITLE => "PAZAR - Project Search Results");
$template->param(JAVASCRIPT_FUNCTION => q{function verifyCheckedBoxes() {            
    var numChecked = 0;
    var counter;
    
    // iterate through sequenceform elements


    for(counter=0;counter<document.sequenceform.length;counter++)
    {
	if (document.sequenceform.elements[counter].checked)
	{
	    numChecked++;
	}
    }
    if (numChecked < 2)
    {
	alert('You must select at least 2 sequences\nNumber of sequences selected: ' + numChecked);
    }
    else
    {
	document.sequenceform.submit();
    }

        }});

if($loggedin eq 'true')
{
    #log out link
    $template->param(LOGOUT => "$info{first} $info{last} logged in. ".'<a href=\'logout.pl\'>Log Out</a>');
}
else
{
    #log in link
    $template->param(LOGOUT => '<a href=\'login.pl\'>Log In</a>');
}

# send the obligatory Content-Type and print the template output
print "Content-Type: text/html\n\n", $template->output;

my $get = new CGI;
my %param = %{$get->Vars};

###getting the project_name
my $proj=$param{project_name};

###database connection
my $dbh0= pazar->new( 
		       -host          =>    $ENV{PAZAR_host},
		       -user          =>    $ENV{PAZAR_pubuser},
		       -pass          =>    $ENV{PAZAR_pubpass},
		       -dbname        =>    $ENV{PAZAR_name},
		       -drv           =>    'mysql',
		       -globalsearch  =>    'yes');

my $stat = &select($dbh0, "SELECT status FROM project WHERE project_name='$proj'");
my $status=$stat->fetchrow_array;

my $dbh;
if ($status=~/open/i || $status=~/published/i) {
### global database connection
$dbh= pazar->new( 
		       -host          =>    $ENV{PAZAR_host},
		       -user          =>    $ENV{PAZAR_pubuser},
		       -pass          =>    $ENV{PAZAR_pubpass},
		       -dbname        =>    $ENV{PAZAR_name},
		       -drv           =>    'mysql',
		       -project       =>    $proj);
} elsif ($status=~/restricted/i) {
### user specific database connection
$dbh= pazar->new( 
		       -host          =>    $ENV{PAZAR_host},
		       -user          =>    $ENV{PAZAR_pubuser},
		       -pass          =>    $ENV{PAZAR_pubpass},
		       -pazar_user    =>    $info{user},
		       -pazar_pass    =>    $info{pass},
		       -dbname        =>    $ENV{PAZAR_name},
		       -drv           =>    'mysql',
		       -project       =>    $proj);
}

my $ensdb = pazar::talk->new(DB=>'ensembl',USER=>$ENV{ENS_USER},PASS=>$ENV{ENS_PASS},HOST=>$ENV{ENS_HOST},DRV=>'mysql');

my $projid = $dbh->get_projectid();

print "<p class=\"title1\">PAZAR - $proj Search Results</p>";

###
### gene-centric view
###

if ($param{view} eq 'gene-centric') {
    my @reg_seqs;
    undef(my @filters);
### species filter
    if ($param{species_filter} eq 'on') {
	if (!$param{species}) {print "<p class=\"warning\">You need to select one or more species when using the species filter!<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"http://www.pazar.info/cgi-bin/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
	my @species=split(/;/,$param{species});
	if (!grep(/species filter/, @filters)) {
	    my $filter='species filter: '.join(',',@species);
	    push @filters, $filter;
	}
	unless ($param{region_filter} eq 'on') {
	    foreach my $sp (@species) {
		my @seqs=$dbh->get_reg_seq_by_species($sp);
		foreach my $regseq (@seqs) {
		    push @reg_seqs, $regseq;
		}
	    }
            if (!$reg_seqs[0]) {print "<p class=\"warning\">No regulatory sequence was found for species: ".join(',',@species)."<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"http://www.pazar.info/cgi-bin/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
	} else {

### region filter
	    if (scalar(@species)>1) {print "<p class=\"warning\">You have to choose a unique species when using the region filter!<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"http://www.pazar.info/cgi-bin/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
	    if ($param{chr_filter} eq 'on') {
		unless ($param{bp_filter} eq 'on') {
		    @reg_seqs=$dbh->get_reg_seq_by_chromosome($param{chromosome},$param{species});
	if (!grep(/chromosome filter/, @filters)) {
		    my $filter='chromosome filter: '.$param{chromosome};
		    push @filters, $filter;
		}
                    if (!$reg_seqs[0]) {print "<p class=\"warning\">No regulatory sequence was found on chromosome $param{chromosome} in species $param{species}<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"http://www.pazar.info/cgi-bin/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
		} else {
                    if (!$param{bp_start} || !$param{bp_end}) {print "<p class=\"warning\">You need to specify the start and end of the region you're interested in when using the base pair filter!<br><form><input type=\"button\" name=\"change_filters\" value=\"Modify Filters\" onclick=\"parent.location.href='http://www.pazar.info/cgi-bin/project.pl&project_name=\"$proj\"'\"></form></p>\n"; exit;}
		    if ($param{bp_start}>=$param{bp_end}) {print "<p class=\"warning\">The start coordinate needs to be lower that the end!<br><form><input type=\"button\" name=\"change_filters\" value=\"Modify Filters\" onclick=\"parent.location.href='http://www.pazar.info/cgi-bin/project.pl&project_name=\"$proj\"'\"></form></p>\n"; exit;}
	if (!grep(/region filter/, @filters)) {
		    my $filter='region filter: '.$param{chromosome}.':'.$param{bp_start}.'-'.$param{bp_end};
		    push @filters, $filter;
		}
		    @reg_seqs=$dbh->get_reg_seq_by_region($param{bp_start},$param{bp_end},$param{chromosome},$param{species});
                    if (!$reg_seqs[0]) {print "<p class=\"warning\">No regulatory sequence was found between bp $param{bp_start} and $param{bp_end} on chromosome $param{chromosome} in species $param{species}<br><form><input type=\"button\" name=\"change_filters\" value=\"Modify Filters\" onclick=\"parent.location.href='http://www.pazar.info/cgi-bin/project.pl&project_name=\"$proj\"'\"></form></p>\n"; exit;}
		}
	    }
	}
    } else {
	if ($param{region_filter} eq 'on') {print "<p class=\"warning\">You have to select a species if you want to use the region filter!<br><form><input type=\"button\" name=\"change_filters\" value=\"Modify Filters\" onclick=\"parent.location.href='http://www.pazar.info/cgi-bin/project.pl&project_name=\"$proj\"'\"></form></p>\n"; exit;}
    }

### gene filter
    if ($param{gene_filter} eq 'on') {
	if ($reg_seqs[0]) {print "<p class=\"warning\">You cannot use species and region filters when using the gene filter!<br><form><input type=\"button\" name=\"change_filters\" value=\"Modify Filters\" onclick=\"parent.location.href='http://www.pazar.info/cgi-bin/project.pl&project_name=\"$proj\"'\"></form></p>\n"; exit;}
	if (!$param{gene}) {print "<p class=\"warning\">You need to select one or more gene when using the gene filter!<br><form><input type=\"button\" name=\"change_filters\" value=\"Modify Filters\" onclick=\"parent.location.href='http://www.pazar.info/cgi-bin/project.pl&project_name=\"$proj\"'\"></form></p>\n"; exit;}
	my @genes=split(/;/,$param{gene});
	if (!grep(/gene filter/, @filters)) {
	my $filter='gene filter: '.join(',',@genes);
	push @filters, $filter;
    }
        foreach my $accn (@genes) {
	    my @seqs=$dbh->get_reg_seqs_by_accn($accn);
	    foreach my $regseq (@seqs) {
		push @reg_seqs, $regseq;
	    }
	}
	if (!$reg_seqs[0]) {print "<p class=\"warning\">No regulatory sequence was found for the genes ".join(',',@genes)."!<br><form><input type=\"button\" name=\"change_filters\" value=\"Modify Filters\" onclick=\"parent.location.href='http://www.pazar.info/cgi-bin/project.pl&project_name=\"$proj\"'\"></form></p>\n"; exit;}

    }
    if (!$reg_seqs[0]) {
	my @rsid = $dbh->get_all_regseq_ids();
	foreach my $id (@rsid) {
	    my @seqs=$dbh->get_reg_seq_by_regseq_id($id);
	    foreach my $regseq (@seqs) {
		push @reg_seqs, $regseq;
	    }
	}
    }
    if (!$reg_seqs[0]) {print "<p class=\"warning\">No regulatory sequence was found in this project!<br></p>\n"; exit;}
    my $res=0;
    my $filt=0;
    my @sorted_regseqs = sort {$a->gene_accession cmp $b->gene_accession} @reg_seqs;
    my $prev_gene_accn;
    foreach my $regseq (@sorted_regseqs) {

### length filter
	if ($param{length_filter} eq 'on' && $param{length} ne '0') {
	    if (!$param{length} || $param{length}<=0) {print "<p class=\"warning\">You need to specify a length greater than 0 when using the length filter!<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"http://www.pazar.info/cgi-bin/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
	if (!grep(/length filter/, @filters)) {
		my $filter='length filter: '.$param{shorter_larger}.' '.$param{length}.' bases';
		push @filters, $filter;
	    }
	    my $length = $regseq->end - $regseq->start +1;
	    if ($param{shorter_larger} eq 'equal_to') {
		unless ($length == $param{length}) {
my $filter = 
		    next;
		}
	    }
	    if ($param{shorter_larger} eq 'greater_than') {
		unless ($length >= $param{length}) {
		    next;
		}
	    }
	    if ($param{shorter_larger} eq 'less_than') {
		unless ($length <= $param{length}) {
		    next;
		}
	    }
	}
	my @inters;
	my @interactors=$dbh->get_interacting_factor_by_regseq_id($regseq->accession_number);
	my $datalinks=0;
	if (!@interactors) {
	    unless ($param{tf_filter} eq 'on' || $param{class_filter} eq 'on' || $param{interaction_filter} eq 'on' || $param{evidence_filter} eq 'on' || $param{method_filter} eq 'on') {
		$datalinks++;
	    }
	}
       	foreach my $inter (@interactors) {

### TF filter
	    if ($param{tf_filter} eq 'on') {
	        if (!$param{tf}) {print "<p class=\"warning\">You need to select one or more TF when using the TF filter!<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"http://www.pazar.info/cgi-bin/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
		my @tfs=split(/;/,$param{tf});
	if (!grep(/TF filter/, @filters)) {
		    my $filter='TF filter: '.join(',',@tfs);
		    push @filters, $filter;
		}
		my $tf_name = $dbh->get_complex_name_by_id($inter->{tfcomplex});
		unless (grep(/^$tf_name$/,@tfs)) {
		    next;
		}
	    }

### TF class filter
	    if ($param{class_filter} eq 'on') {
		my $tf = $dbh->create_tf;
		my $complex = $tf->get_tfcomplex_by_id($inter->{tfcomplex},'notargets');
		my $found = 0;
		my $cf;
		if (!grep(/TF class filter/, @filters)) {
		    my $filter='TF class filter: '.$param{class};
		    push @filters, $filter;
		}
		while (my $subunit=$complex->next_subunit) {
		    if ($subunit->get_class && $subunit->get_fam) {
			$cf = $subunit->get_class."/".$subunit->get_fam;
		    } elsif ($subunit->get_class && !$subunit->get_fam) {
			$cf = $subunit->get_class;
		    }
		    if ($param{class} == $cf) {
			$found = 1;
		    }
		}
		if ($found == 0) {
		    next;
		}
	    }

### interaction filter
	    if ($param{interaction_filter} eq 'on') {
		my ($table,$pazarid,@dat)=$dbh->links_to_data($inter->{olink},'output');
		my $qual=lc($dat[0]);
		my $match=0;
		if (!grep(/interaction filter/, @filters)) {
		    my $filter;
		    if ($param{interaction} eq 'none') {
			$filter='interaction filter: null';
		    } else {
			$filter='interaction filter: '.$param{interaction};
		    }
		    push @filters, $filter;
		}
		my @notnull=('good','poor','marginal','saturation');
		if ($qual eq $param{interaction}) {
		    $match = 1;
		} elsif ($param{interaction} eq 'not_null' && grep(/$qual/,@notnull)) {
		    $match = 1;
		} elsif ($param{interaction} ne 'none' && $dat[1]>0) {
		    $match = 1;
		} elsif ($param{interaction} eq 'none' && !grep(/$qual/,@notnull) && $dat[1]==0) {
		    $match = 1;
		}
#		print $match.$param{interaction}.$qual.$dat[1].'<br>';
		if ($match == 0) {
		    next;
		}
	    }

### evidence filter
	    if ($param{evidence_filter} eq 'on') {
	        if (!$param{evidence}) {print "<p class=\"warning\">You need to select one or more evidence type when using the evidence filter!<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"http://www.pazar.info/cgi-bin/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
		my @evids=split(/;/,$param{evidence});
		if (!grep(/evidence filter/, @filters)) {
		    my $filter='evidence filter: '.join(',',@evids);
		    push @filters, $filter;
		}
		my ($evid,@res)=$dbh->get_evidence_by_analysis_id($inter->{aid});
		unless (grep(/^$evid$/,@evids)) {
		    next;
		}
	    }

### method filter
	    if ($param{method_filter} eq 'on') {
	        if (!$param{method}) {print "<p class=\"warning\">You need to select one or more method type when using the method filter!<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"http://www.pazar.info/cgi-bin/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
		my @mets=split(/;/,$param{method});
		if (!grep(/method filter/, @filters)) {
		    my $filter='method filter: '.join(',',@mets);
		    push @filters, $filter;
		}
		my ($met,@res)=$dbh->get_method_by_analysis_id($inter->{aid});
		unless (grep(/^$met$/,@mets)) {
		    next;
		}
	    }
	    push @inters, $inter;
	}
	my @exprs;
	my @expressors=$dbh->get_expression_by_regseq_id($regseq->accession_number);
	if (!@expressors) {
	    unless ($param{expression_filter} eq 'on' || $param{evidence_filter} eq 'on' || $param{method_filter} eq 'on') {
		$datalinks++;
	    }
	}
       	foreach my $expr (@expressors) {

### expression filter
	    if ($param{expression_filter} eq 'on') {
		my ($table,$pazarid,@dat)=$dbh->links_to_data($expr->{olink},'output');
		my $qual=lc($dat[0]);
		my $match=0;
		if (!grep(/expression filter/, @filters)) {
		    my $filter='expression filter: '.$param{expression};
		    push @filters, $filter;
		}
		my @change=('highly induced','induced','repressed','strongly repressed');
		my @induce=('highly induced','induced','change');
		my @repress=('repressed','strongly repressed','change');
		if ($qual eq $param{expression}) {
		    $match = 1;
		} elsif ($param{expression} eq 'change' && grep(/$qual/,@change)) {
		    $match = 1;
		} elsif (grep(/^$param{expression}$/,@induce) && $dat[1]>0) {
		    $match = 1;
		} elsif (grep(/^$param{expression}$/,@repress) && $dat[1]<0) {
		    $match = 1;
		}
#		print $match.$param{expression}.$qual.$dat[1].'<br>';
		if ($match == 0) {
		    next;
		}
	    }

### evidence filter
	    if ($param{evidence_filter} eq 'on') {
	        if (!$param{evidence}) {print "<p class=\"warning\">You need to select one or more evidence type when using the evidence filter!<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"http://www.pazar.info/cgi-bin/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
		my @evids=split(/;/,$param{evidence});
		if (!grep(/evidence filter/, @filters)) {
		    my $filter='evidence filter: '.join(',',@evids);
		    push @filters, $filter;
		}
		my ($evid,@res)=$dbh->get_evidence_by_analysis_id($expr->{aid});
		unless (grep(/^$evid$/,@evids)) {
		    next;
		}
	    }

### method filter
	    if ($param{method_filter} eq 'on') {
	        if (!$param{method}) {print "<p class=\"warning\">You need to select one or more method type when using the method filter!<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"http://www.pazar.info/cgi-bin/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
		my @mets=split(/;/,$param{method});
		if (!grep(/method filter/, @filters)) {
		    my $filter='method filter: '.join(',',@mets);
		    push @filters, $filter;
		}
		my ($met,@res)=$dbh->get_method_by_analysis_id($expr->{aid});
		unless (grep(/^$met$/,@mets)) {
		    next;
		}
	    }
	    push @exprs, $expr;
	}
	if (!@filters) {push @filters, 'none';}
	if ($res==0) {
	    $res=1;
	    print "<p><span class=\"title3\">Selected filters: </span><br>".join('; ',@filters)."<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"http://www.pazar.info/cgi-bin/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>";
	    print "<p class=\"title3\">Results: </p>";
	}
	if ($exprs[0] || $inters[0] || $datalinks==2) {
	    $filt=1;
	    my $gene_accn = $regseq->gene_accession;
	    my $gene_desc = $regseq->gene_description || '';
	    my $gene_sp = $regseq->binomial_species;
	    if ($gene_accn ne $prev_gene_accn) {
		my @ens_coords = $ensdb->get_ens_chr($gene_accn);
		my @des = split('\(',$ens_coords[5]);
		my @desc = split('\[',$des[0]);    
		my $geneDescription = $desc[0];
#print header

print<<HEADER_TABLE;

<table width='1150' border=1 cellspacing=0>
<tr><td align="center" valign="top" bgcolor="#39aecb"><span class="title4">Gene Name</span></td><td align='left'>&nbsp;&nbsp;&nbsp;&nbsp;$gene_desc</td></tr>
<tr><td align="center" valign="top" bgcolor="#39aecb"><span class="title4">Accession</span></td><td align='left'>&nbsp;&nbsp;&nbsp;&nbsp;$gene_accn</td></tr>
<tr><td align="center" valign="top" bgcolor="#39aecb"><span class="title4">Description</span></td><td align='left'>&nbsp;&nbsp;&nbsp;&nbsp;$geneDescription</td></tr>
<tr><td align="center" valign="top" bgcolor="#39aecb"><span class="title4">Species</span></td><td align='left'>&nbsp;&nbsp;&nbsp;&nbsp;$gene_sp</td></tr>
</table>
HEADER_TABLE
                $prev_gene_accn = $gene_accn;
	    }
	    &print_gene_attr($dbh, $ensdb, $regseq, \@inters, \@exprs, %param);
	}
    }
    if (!@filters) {push @filters, 'none';}
    if ($res==1 && $filt==0) {
	print "<p class=\"warning\">No regulatory sequence was found using this set of filters!<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"http://www.pazar.info/cgi-bin/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>";
    }
    if ($res==0) {
	print "<p><span class=\"title3\">Selected filters: </span><br>".join('; ',@filters)."<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"http://www.pazar.info/cgi-bin/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>";
	print "<p class=\"title3\">Results: </p>";
	print "<p class=\"warning\">No regulatory sequence was found using this set of filters!</p>";
    }

###
### TF-centric view
###

} elsif ($param{view} eq 'tf-centric') {

### TF filter
    my @complexes;
    undef(my @filters);
    if ($param{tf_filter} eq 'on') {
	if (!$param{tf}) {print "<p class=\"warning\">You need to select one or more TF when using the TF filter!<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"http://www.pazar.info/cgi-bin/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
	my @tfs=split(/;/,$param{tf});
	if (!grep(/TF filter/, @filters)) {
	    my $filter='TF filter: '.join(',',@tfs);
	    push @filters, $filter;
	}
	foreach my $tf (@tfs) {
            my $complex = $dbh->create_tf;
	    my @tfcomplex = $complex->get_tfcomplex_by_name($tf);
	    foreach my $tfcomplex (@tfcomplex) {
		push @complexes, $tfcomplex;
	    }
	}
        if (!$complexes[0]) {print "<p class=\"warning\">No TF was found with the following names: ".join(',',@tfs)."<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"http://www.pazar.info/cgi-bin/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
    }

### TF class filter
    if ($param{class_filter} eq 'on') {
	if ($complexes[0]) {print "<p class=\"warning\">You cannot use the TF filter and TF class filter at the same time!<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"http://www.pazar.info/cgi-bin/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
	my @cf = split(/\//,$param{classes});
	my $tf = $dbh->create_tf;
	my @tfcomplex = $tf->get_tfcomplex_by_class($cf[0]);
	foreach my $tfcomplex (@tfcomplex) {
	    push @complexes, $tfcomplex;
	}
	if (!grep(/TF class filter/, @filters)) {
	    my $filter='TF class filter: '.$param{classes};
	    push @filters, $filter;
	}
        if (!$complexes[0]) {print "<p class=\"warning\">No TF was found within the following class: ".$cf[0]."<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"http://www.pazar.info/cgi-bin/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
    }

### species filter
    if ($param{species_filter} eq 'on') {
	if (!$param{species}) {print "<p class=\"warning\">You need to select one or more species when using the species filter!<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"http://www.pazar.info/cgi-bin/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
	my @species=split(/;/,$param{species});
	if (!grep(/species filter/, @filters)) {
	    my $filter='species filter: '.join(',',@species);
	    push @filters, $filter;
	}
	my @funct_tfs = $dbh->get_all_complex_ids($projid);
	my @tfs;
	foreach my $funct_tf (@funct_tfs) {
	    my $funct_name = $dbh->get_complex_name_by_id($funct_tf);
	    my $tf = $dbh->create_tf;
	    my $tfcomplex = $tf->get_tfcomplex_by_id($funct_tf,'notargets');
	    while (my $subunit=$tfcomplex->next_subunit) {
		my $trans=$subunit->get_transcript_accession($dbh);
		my $gene=$ensdb->ens_transcr_to_gene($trans);
		my $species=$ensdb->current_org();
		if (!grep(/^$species$/,@species)) {
		    next;
		} else {
		    if (!grep(/^$funct_name$/,@tfs)) {
			push @tfs,$funct_name;
		    }
		}
	    }
	}
	if (!$complexes[0]) {
	    foreach my $tf (@tfs) {
		my $complex = $dbh->create_tf;
		my @tfcomplex = $complex->get_tfcomplex_by_name($tf);
		foreach my $tfcomplex (@tfcomplex) {
		    push @complexes, $tfcomplex;
		}
	    }
	    if (!$complexes[0]) {print "<p class=\"warning\">No TF was found from the following species: ".join(',',@species)."<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"http://www.pazar.info/cgi-bin/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
	} else {
	    my @comp = @complexes;
	    undef (@complexes);
	    foreach my $tf (@comp) {
		my $name=$tf->name;
		if (grep(/^$name$/,@tfs)) {
		    push @complexes, $tf;
		}
	    }
	    if (!$complexes[0]) {
		print "<p><span class=\"title3\">Selected filters: </span><br>".join('; ',@filters)."<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"http://www.pazar.info/cgi-bin/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>";
		print "<p class=\"title3\">Results: </p>";
		print "<p class=\"warning\">No TF was found in this project using this set of filters!<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"http://www.pazar.info/cgi-bin/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n";
		exit;
	    }
	}
    }
    if (!$complexes[0]) {
	my @funct_tfs = $dbh->get_all_complex_ids($projid);
	my @tfs;
	foreach my $funct_tf (@funct_tfs) {
	    my $tf = $dbh->create_tf;
	    my $tfcomplex = $tf->get_tfcomplex_by_id($funct_tf);
	    push @complexes, $tfcomplex;
	}
    }
    if (!$complexes[0]) {print "<p class=\"warning\">No TF was found in this project!<br></p>\n"; exit;}

###
### regulated gene filters
###
### species filter
    my @reg_seqs;
    if ($param{species_filter} eq 'on') {
	my @species=split(/;/,$param{species});
	if (!grep(/species filter/, @filters)) {
	    my $filter='species filter: '.join(',',@species);
	    push @filters, $filter;
	}
	unless ($param{region_filter} eq 'on') {
	    foreach my $sp (@species) {
		my @seqs=$dbh->get_reg_seq_by_species($sp);
		foreach my $regseq (@seqs) {
		    push @reg_seqs, $regseq->accession_number;
		}
	    }
	} else {

### region filter
	    if (scalar(@species)>1) {print "<p class=\"warning\">You have to choose a unique species when using the region filter!<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"http://www.pazar.info/cgi-bin/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
	    if ($param{chr_filter} eq 'on') {
		unless ($param{bp_filter} eq 'on') {
		    my @seqs=$dbh->get_reg_seq_by_chromosome($param{chromosome},$param{species});
		    foreach my $regseq (@seqs) {
			push @reg_seqs, $regseq->accession_number;
		    }
		    if (!grep(/chromosome filter/, @filters)) {
			my $filter='chromosome filter: '.$param{chromosome};
			push @filters, $filter;
		    }
                    if (!$reg_seqs[0]) {print "<p class=\"warning\">No regulatory sequence was found on chromosome $param{chromosome} in species $param{species}<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"http://www.pazar.info/cgi-bin/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
		} else {
                    if (!$param{bp_start} || !$param{bp_end}) {print "<p class=\"warning\">You need to specify the start and end of the region you're interested in when using the base pair filter!<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"http://www.pazar.info/cgi-bin/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
		    if ($param{bp_start}>=$param{bp_end}) {print "<p class=\"warning\">The start coordinate needs to be lower that the end!<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"http://www.pazar.info/cgi-bin/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
		    if (!grep(/region filter/, @filters)) {
			my $filter='region filter: '.$param{chromosome}.':'.$param{bp_start}.'-'.$param{bp_end};
			push @filters, $filter;
		    }
		    my @seqs=$dbh->get_reg_seq_by_region($param{bp_start},$param{bp_end},$param{chromosome},$param{species});
		    foreach my $regseq (@seqs) {
			push @reg_seqs, $regseq->accession_number;
		    }

                    if (!$reg_seqs[0]) {print "<p class=\"warning\">No regulatory sequence was found between bp $param{bp_start} and $param{bp_end} on chromosome $param{chromosome} in species $param{species}<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"http://www.pazar.info/cgi-bin/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
		}
	    }
	}
    } else {
	if ($param{region_filter} eq 'on') {print "<p class=\"warning\">You have to select a species if you want to use the region filter!<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"http://www.pazar.info/cgi-bin/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
    }

### gene filter
    if ($param{gene_filter} eq 'on') {
	if ($param{species_filter} eq 'on') {print "<p class=\"warning\">You cannot use species and region filters when using the gene filter!<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"http://www.pazar.info/cgi-bin/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
	if (!$param{gene}) {print "<p class=\"warning\">You need to select one or more gene when using the gene filter!<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"http://www.pazar.info/cgi-bin/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
	my @genes=split(/;/,$param{gene});
	if (!grep(/gene filter/, @filters)) {
	    my $filter='gene filter: '.join(',',@genes);
	    push @filters, $filter;
	}
        foreach my $accn (@genes) {
	    my @seqs=$dbh->get_reg_seqs_by_accn($accn);
	    foreach my $regseq (@seqs) {
		push @reg_seqs, $regseq->accession_number;
	    }
	}
	if (!$reg_seqs[0]) {print "<p class=\"warning\">No regulatory sequence was found for the genes ".join(',',@genes)."!<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"http://www.pazar.info/cgi-bin/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
    }
    my $res=0;
    my %inters;
    foreach my $tf (@complexes) {
	my $tfname=$tf->name;
	while (my $site=$tf->next_target) {
	    my $type=$site->get_type;
#	    print "<span>$type</span>";
	    if ($type eq 'matrix') {next;}
	    if ($type eq 'reg_seq') {
		my @regseq = $dbh->get_reg_seq_by_regseq_id($site->get_dbid);
		my $rsid=$regseq[0]->accession_number;
		if ($reg_seqs[0]) {
		    unless (grep(/^$rsid$/,@reg_seqs)) {next;}
		}

### length filter
		if ($param{length_filter} eq 'on' && $param{length} ne '0') {
		    if (!$param{length} || $param{length}<=0) {print "<p class=\"warning\">You need to specify a length greater than 0 when using the length filter!<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"http://www.pazar.info/cgi-bin/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
		    if (!grep(/length filter/, @filters)) {
			my $filter='length filter: '.$param{shorter_larger}.' '.$param{length}.' bases';
			push @filters, $filter;
		    }
		    my $length = $regseq[0]->end - $regseq[0]->start +1;
		    if ($param{shorter_larger} eq 'equal_to') {
			unless ($length == $param{length}) {
			    my $filter = 
				next;
			}
		    }
		    if ($param{shorter_larger} eq 'greater_than') {
			unless ($length >= $param{length}) {
			    next;
			}
		    }
		    if ($param{shorter_larger} eq 'less_than') {
			unless ($length <= $param{length}) {
			    next;
			}
		    }
		}
	    }
	    if ($type eq 'construct' || $type eq 'reg_seq') {

### interaction filter
		if ($param{interaction_filter} eq 'on') {
		    my ($table,$pazarid,@dat)=$dbh->links_to_data($site->get_olink,'output');
		    unless ($table eq 'interaction') {next;}
		    my $qual=lc($dat[0]);
		    my $match=0;
		    if (!grep(/interaction filter/, @filters)) {
			my $filter;
			if ($param{interaction} eq 'none') {
			    $filter='interaction filter: null';
			} else {
			    $filter='interaction filter: '.$param{interaction};
			}
			push @filters, $filter;
		    }
		    my @notnull=('good','poor','marginal','saturation');
		    if ($qual eq $param{interaction}) {
			$match = 1;
		    } elsif ($param{interaction} eq 'not_null' && grep(/$qual/,@notnull)) {
			$match = 1;
		    } elsif ($param{interaction} ne 'none' && $dat[1]>0) {
			$match = 1;
		    } elsif ($param{interaction} eq 'none' && !grep(/$qual/,@notnull) && $dat[1]==0) {
			$match = 1;
		    }
#		print $match.$param{interaction}.$qual.$dat[1].'<br>';
		    if ($match == 0) {
			next;
		    }
		}

### evidence filter
		if ($param{evidence_filter} eq 'on') {
		    if (!$param{evidence}) {print "<p class=\"warning\">You need to select one or more evidence type when using the evidence filter!<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"http://www.pazar.info/cgi-bin/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
		    my @evids=split(/;/,$param{evidence});
		    if (!grep(/evidence filter/, @filters)) {
			my $filter='evidence filter: '.join(',',@evids);
			push @filters, $filter;
		    }
		    my ($evid,@res)=$dbh->get_evidence_by_analysis_id($site->get_analysis);
		    unless (grep(/^$evid$/,@evids)) {
			next;
		    }
		}

### method filter
		if ($param{method_filter} eq 'on') {
		    if (!$param{method}) {print "<p class=\"warning\">You need to select one or more method type when using the method filter!<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"http://www.pazar.info/cgi-bin/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
		    my @mets=split(/;/,$param{method});
		    if (!grep(/method filter/, @filters)) {
			my $filter='method filter: '.join(',',@mets);
			push @filters, $filter;
		    }
		    my ($met,@res)=$dbh->get_method_by_analysis_id($site->get_analysis);
		    unless (grep(/^$met$/,@mets)) {
			next;
		    }
		}
	    }
	    push (@{$inters{$tfname}},{
                        dbid => $site->get_dbid,
                        ilink => $site->get_ilink,
                        olink => $site->get_olink,
			aid => $site->get_analysis});
	    $res=1;
	}
    }
    if (!@filters) {push @filters, 'none';}
    if ($res==0) {
	print "<p><span class=\"title3\">Selected filters: </span><br>".join('; ',@filters)."<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"http://www.pazar.info/cgi-bin/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>";
	print "<p class=\"title3\">Results: </p>";
	print "<p class=\"warning\">No regulatory sequence and/or TF was found using this set of filters!<br></p>";
    } else{
	print "<p><span class=\"title3\">Selected filters: </span><br>".join('; ',@filters)."<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"http://www.pazar.info/cgi-bin/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>";
	print "<p class=\"title3\">Results: </p>\n";
####start of form
	print "<form name='sequenceform' method='post' target='logowin' action='tf_logo.pl' onsubmit='window.open('','foo','resizable=1,scrollbars=1,width=400,height=300')'>\n";
	foreach my $tf (keys %inters) {
	    &print_tf_attr($dbh,$tf,$projid,\@{$inters{$tf}},%param);
	}
####hidden form inputs
print "<br><table bordercolor='white' bgcolor='white'><tr><td class=\"title2\">Click Go to recalculate matrix and logo based on selected sequences</td>";
print "<td><input type='button' value='Go' onClick=\"verifyCheckedBoxes();\"></td></tr>
<tr><td>(you can combine sequences from multiple TFs)</td></tr></table>";
print "</form>";
####end of form
    }
}

###  print out the html tail template
my $template_tail = HTML::Template->new(filename => 'tail.tmpl');
print $template_tail->output;

sub select {
    my ($dbh, $sql) = @_;
    my $sth=$dbh->prepare($sql);
    $sth->execute or die "$dbh->errstr\n";
    return $sth;
}

sub print_gene_attr {
    my ($dbh, $ensdb, $regseq, $inters, $exprs, %params) = @_;
    my @interactors = @$inters;
    my @expressors = @$exprs;

#start table
print<<COLNAMES;	    
		<table width='1150' border=1 cellspacing=0><tr><td>
		    <table width='100%' border="1" cellspacing="0" cellpadding="3">
		    <tr>
		    <td width="100" align="center" valign="top" bgcolor="#61b9cf"><span class="title4">Project</span></td>
		    
COLNAMES

print "<td width='150' align='center' valign='top' bgcolor='#61b9cf'><span class=\"title4\">Gene/Transcript ID</span></td>";

    if ($params{at_tss} eq 'on')
    {
	print "<td width='100' align='center' valign='top' bgcolor='#61b9cf'><span class=\"title4\">Transcription Start Site</span></td>";
    }
    print "<td width='150' align='center' valign='top' bgcolor='#61b9cf'><span class=\"title4\">Sequence Name</span></td>";
    print "<td align='center' valign='top' bgcolor='#61b9cf'><span class=\"title4\">Sequence</span></td>";
    print "<td width='100' align='center' valign='top' bgcolor='#61b9cf'><span class=\"title4\">RegSeq ID</span></td>";
    print "<td width='150' align='center' valign='top' bgcolor='#61b9cf'><span class=\"title4\">Coordinates</span></td>";

    if ($params{at_quality} eq 'on') {
	print "<td width='100' align='center' valign='top' bgcolor='#61b9cf'><span class=\"title4\">Quality</span></td>";
    }
    print "<td width='80' align='center' valign='top' bgcolor='#61b9cf'><span class=\"title4\">Display</span></td>";

    print "</tr>";
    
#print out default information
    print "<form name='display$regseq_counter' method='post' action='http://www.pazar.info/cgi-bin/gff_custom_track.cgi' enctype='multipart/form-data' target='_blank'>";
    print "<tr>";
    print "<td width='100' align='center' bgcolor=\"$colors{$bg_color}\">$proj</td>";
    
    my $transcript=$regseq->transcript_accession || 'Transcript Not Specified';
    print "<td width='150' align='center' bgcolor=\"$colors{$bg_color}\">".$transcript."</td>";

    if ($params{at_tss} eq 'on') {
	if ($regseq->transcript_fuzzy_start == $regseq->transcript_fuzzy_end) { print "<td width='100' align='center' bgcolor=\"$colors{$bg_color}\">".$regseq->transcript_fuzzy_start."</td>";} else {
	    print "<td width='100' align='center' bgcolor=\"$colors{$bg_color}\">".$regseq->transcript_fuzzy_start."-".$regseq->transcript_fuzzy_end."</td>";
	}
    }

    print "<td width='150' align='center' bgcolor=\"$colors{$bg_color}\">".$regseq->id."&nbsp;</td>";	       
    print "<td align='left' bgcolor=\"$colors{$bg_color}\">".chopstr($regseq->seq,40)."&nbsp;</td>";

    my $rsid = $regseq->accession_number;
    my $rsid7d = sprintf "%07d",$rsid;
    my $id="RS".$rsid7d;
    print "<td width='100' align='center' bgcolor=\"$colors{$bg_color}\">".$id."&nbsp;</td>";
    print "<td width='150' align='center' bgcolor=\"$colors{$bg_color}\">".$regseq->chromosome." (".$regseq->strand.") ".$regseq->start."-".$regseq->end."</td>";

    if ($params{at_quality} eq 'on') {
	print "<td width='100' align='center' bgcolor=\"$colors{$bg_color}\">".$regseq->quality."&nbsp;</td>";
    }
    print "<td width='80' align='center' bgcolor=\"$colors{$bg_color}\"><input type='hidden' name='chr' value='".$regseq->chromosome."'><input type='hidden' name='start' value='".$regseq->start."'><input type='hidden' name='end' value='".$regseq->end."'><input type='hidden' name='species' value='".$regseq->binomial_species."'><input type='hidden' name='resource' value='ucsc'><a href='#' onClick=\"javascript:document.display$regseq_counter.resource.value='ucsc';document.display$regseq_counter.submit();\"><img src='http://www.pazar.info/images/ucsc_logo.png'></a><!--<input type='submit' name='ucsc' value='ucsc' onClick=\"javascript:document.display$regseq_counter.resource.value='ucsc';\">--><br><a href='#' onClick=\"javascript:document.display$regseq_counter.resource.value='ensembl';document.display$regseq_counter.submit();\"><img src='http://www.pazar.info/images/ensembl_logo.gif'></a><!--<input type='submit' name='ensembl' value='ensembl' onClick=\"javascript:document.display$regseq_counter.resource.value='ensembl';\">--></td>";

    print "</tr></form></table>";
    print "<p></td></tr>";

#make sure that if there is at least one interactor or expressor and that there is at least 1 field being displayed 	 if(scalar(@interactors)>0 || scalar(@expressors)>0)
    if((scalar(@interactors)>0 && ($params{at_tf} eq 'on' || $params{at_tf_analysis} eq 'on' || $params{at_tf_reference} eq 'on' || $params{at_tf_interaction} eq 'on' || $params{at_tf_evidence} eq 'on')) || (scalar(@expressors)>0 && ($params{at_other_analysis} eq 'on' || $params{at_other_reference} eq 'on' || $params{at_other_effect} eq 'on' || $params{at_other_evidence} eq 'on'))) {
        print "<tr><td align='center' bgcolor='#ff9a40'><center><span class=\"title4\">Lines of Evidence</span></center></td></tr><tr><td>";
    }
################### BEGIN INTERACTING EVIDENCE SECTION #####################
#reset row color
    $bg_color = 0;
    my $count=1;

    if ($params{at_tf} eq 'on' || $params{at_tf_analysis} eq 'on' || $params{at_tf_reference} eq 'on' || $params{at_tf_interaction} eq 'on' || $params{at_tf_evidence} eq 'on') {
	
#    print "<td align='center' bgcolor=\"$colors{$bg_color}\">";

#only print table if there is at least one result

	if(scalar(@interactors)>0)
	{
	    print "<table width='100%' cellspacing=0 border=1><tr><td width='150' align='center' valign='top' bgcolor='#ff9a40'><span class=\"title4\">&nbsp;</span></td>";
	    
	    if ($params{at_tf} eq 'on') {
		print "<td width='200' align='center' valign='top' bgcolor='#ff9a40'><span class=\"title4\">Transcription Factor</span></td>";
	    }
	    if ($params{at_tf_analysis} eq 'on' || $params{at_other_analysis} eq 'on')
	    {
		print "<td align='center' valign='top' bgcolor='#ff9a40'><span class=\"title4\">Analysis Details</span></td>";
	    }
	    if ($params{at_tf_reference} eq 'on' || $params{at_other_reference} eq 'on')
	    {
		print "<td width='150' align='center' valign='top' bgcolor='#ff9a40'><span class=\"title4\">Reference (PMID)</span></td>";
	    }
	    if ($params{at_tf_interaction} eq 'on')
	    {
		print "<td width='100' align='center' valign='top' bgcolor='#ff9a40'><span class=\"title4\">Interaction Description</span></td>";
	    }
	    if ($params{at_other_effect} eq 'on')
	    {
		print "<td width='150' align='center' valign='top' bgcolor='#ff9a40'><span class=\"title4\">Effects</span></td>";
	    }
	    if ($params{at_tf_evidence} eq 'on' || $params{at_other_evidence} eq 'on')
	    {
		print "<td width='150' align='center' valign='top' bgcolor='#ff9a40'><span class=\"title4\">Evidence</span></td>";
	    }
	    print "</tr>";
	}
    }
    foreach my $inter (@interactors) {
	if ($params{at_tf} eq 'on' || $params{at_tf_analysis} eq 'on' || $params{at_tf_reference} eq 'on' || $params{at_tf_interaction} eq 'on' || $params{at_tf_evidence} eq 'on') {
	    print "<tr><td width='150' align='center' bgcolor=\"$colors{$bg_color}\">Line of evidence $count</td>";
	    if ($params{at_tf} eq 'on') {
		my $tf = $dbh->create_tf;
		my $complex = $tf->get_tfcomplex_by_id($inter->{tfcomplex}, 'notargets');
		print "<td width='200' align='center' bgcolor=\"$colors{$bg_color}\">".$complex->name;
		while (my $subunit=$complex->next_subunit) {
		    my $db = $subunit->get_tdb;
		    my $tid = $subunit->get_transcript_accession($dbh);
		    my $cl = $subunit->get_class ||'unknown'; 
		    my $fam = $subunit->get_fam ||'unknown';
		    print $tid."&nbsp;(".$cl.")&nbsp; - Family: ".$fam."<br>";
		}
		print "</td>";
	    }
	    my @an=$dbh->get_data_by_primary_key('analysis',$inter->{aid});
	    if ($params{at_tf_analysis} eq 'on') {
		my $aname=$an[2];
		my @anal;
		push @anal,$aname;
		if ($an[3]) {
		    my @met=$dbh->get_data_by_primary_key('method',$an[3]);
		    push @anal,$met[0];
		}
		if ($an[4]) {
		    my @cell=$dbh->get_data_by_primary_key('cell',$an[4]);
		    push @anal,$cell[0];
		}
		if ($an[5]) {
		    my @time=$dbh->get_data_by_primary_key('time',$an[5]);
		    push @anal,$time[0];
		}
		print "<td align='center' bgcolor=\"$colors{$bg_color}\">";
		print join(':',@anal)."</td>";
	    }
	    if ($params{at_tf_reference} eq 'on' && $an[6]) {
		my @ref=$dbh->get_data_by_primary_key('ref',$an[6]);
		print "<td width='150' align='center' bgcolor=\"$colors{$bg_color}\">".$ref[0]."</td>";
	    }
	    if ($params{at_tf_interaction} eq 'on') {
		my ($table,$pazarid,@dat)=$dbh->links_to_data($inter->{olink},'output');
		if ($table eq 'interaction') {
		    print "<td width='100' align='center' bgcolor=\"$colors{$bg_color}\">";
		    my @data;
		    for (my $i=0;$i<(@dat-3);$i++) {
			if ($dat[$i] && $dat[$i] ne '0') {
			    push @data,$dat[$i];
			}
		    }
		    print join(":",@data)."</td>";
		}
	    }
	    if ($params{at_other_effect} eq 'on')
	    {
		print "<td width='150' align='center' valign='top' bgcolor=\"$colors{$bg_color}\">&nbsp;</td>";
	    }

	    if ($params{at_tf_evidence} eq 'on' && $an[1]) {
		my @ev=$dbh->get_data_by_primary_key('evidence',$an[1]);
		print "<td width='150' align='center' bgcolor=\"$colors{$bg_color}\">".$ev[0]."_".$ev[1]."</td>";
	    }
	    $count++;
	    print "</tr>";
	    $bg_color = 1 - $bg_color;
	}}

    if ($params{at_tf} eq 'on' || $params{at_tf_analysis} eq 'on' || $params{at_tf_reference} eq 'on' || $params{at_tf_interaction} eq 'on' || $params{at_tf_evidence} eq 'on') {
	
#end table that was created if there were results
	if(scalar(@interactors)>0)
	{
	    print "</table>";
	}		    
    }

################### BEGIN OTHER EVIDENCE SECTION #####################
#reset row color
    $bg_color = 0;



    if ($params{at_other_analysis} eq 'on' || $params{at_other_reference} eq 'on' || $params{at_other_effect} eq 'on' || $params{at_other_evidence} eq 'on') {
	
	
#print table only if results exist
	if (scalar(@expressors) > 0)
	{
	    print "<table width='100%' border=1 cellspacing=0><tr><td width='150' align='center' valign='top' bgcolor='#ff9a40'><span class=\"title4\">&nbsp;</span></td>";

# 			if ($params{at_tf} eq 'on') {
# 			    print "<td width='200' align='center' valign='top' bgcolor='#ff9a40'><span class=\"title4\">Transcription Factor</span></td>";
# 			}
	    if ($params{at_other_analysis} eq 'on' || $params{at_tf_analysis} eq 'on')
	    {
		print "<td align='center' valign='top' bgcolor='#ff9a40'><span class=\"title4\">Analysis Details</span></td>";
	    }
	    if ($params{at_other_reference} eq 'on' || $params{at_tf_reference} eq 'on')
	    {
		print "<td width='150' align='center' valign='top' bgcolor='#ff9a40'><span class=\"title4\">Reference (PMID)</span></td>";
	    }
# 			if ($params{at_tf_interaction} eq 'on')
# 			{
# 			    print "<td width='100' align='center' valign='top' bgcolor='#ff9a40'><span class=\"title4\">Interaction Description</span></td>";
# 			}
	    if ($params{at_other_effect} eq 'on')
	    {
		print "<td width='150' align='center' valign='top' bgcolor='#ff9a40'><span class=\"title4\">Effects</span></td>";
	    }
	    if ($params{at_other_evidence} eq 'on' || $params{at_tf_evidence} eq 'on')
	    {
		print "<td width='150' align='center' valign='top' bgcolor='#ff9a40'><span class=\"title4\">Evidence</span></td>";
	    }
	    
	    print "</tr>";
	}
    }
    foreach my $exp (@expressors) {
	if ($params{at_other_analysis} eq 'on' || $params{at_other_reference} eq 'on' || $params{at_other_effect} eq 'on' || $params{at_other_evidence} eq 'on') {
	    print "<tr><td width='150' align='center' bgcolor=\"$colors{$bg_color}\">Line of evidence $count</td>";

# 			if ($params{at_tf} eq 'on') {
# 			    print "<td width='200' align='center' valign='top' bgcolor=\"$colors{$bg_color}\">&nbsp;</td>";
# 			}

	    my @an=$dbh->get_data_by_primary_key('analysis',$exp->{aid});
	    if ($params{at_other_analysis} eq 'on') {
		my $aname=$an[2];
		my @anal;
		push @anal,$aname;
		if ($an[3]) {
		    my @met=$dbh->get_data_by_primary_key('method',$an[3]);
		    push @anal,$met[0];
		}
		if ($an[4]) {
		    my @cell=$dbh->get_data_by_primary_key('cell',$an[4]);
		    push @anal,$cell[0];
		}
		if ($an[5]) {
		    my @time=$dbh->get_data_by_primary_key('time',$an[5]);
		    push @anal,$time[0];
		}
		print "<td align='center' bgcolor=\"$colors{$bg_color}\">";
		print join(':',@anal)."</td>";
	    }
	    if ($params{at_other_reference} eq 'on' && $an[6]) {
		my @ref=$dbh->get_data_by_primary_key('ref',$an[6]);
		print "<td width='150' align='center' bgcolor=\"$colors{$bg_color}\">".$ref[0]."</td>";
	    }
# 			if ($params{at_tf_interaction} eq 'on')
# 			{
# 			    print "<td width='100' align='center' valign='top' bgcolor=\"$colors{$bg_color}\">&nbsp;</td>";
# 			}
	    if ($params{at_other_effect} eq 'on') {
		my ($table,$tableid,@dat)=$dbh->links_to_data($exp->{olink},'output');
		print "<td width='150' align='center' bgcolor=\"$colors{$bg_color}\">";
		my @data;
		for (my $i=0;$i<(@dat-3);$i++) {
		    if ($dat[$i] && $dat[$i] ne '0') {
			push @data,$dat[$i];
		    }
		}
		print join(":",@data)."</td>";
	    }
	    if ($params{at_other_evidence} eq 'on' && $an[1]) {
		my @ev=$dbh->get_data_by_primary_key('evidence',$an[1]);
		print "<td width='150' align='center' bgcolor=\"$colors{$bg_color}\">".$ev[0]."_".$ev[1]."</td>";
	    }
	    $count++;
	    print "</tr>";
	    $bg_color = 1 - $bg_color;
	}}

    if ($params{at_other_analysis} eq 'on' || $params{at_other_reference} eq 'on' || $params{at_other_effect} eq 'on' || $params{at_other_evidence} eq 'on') {

#end table only if results exist
	if(scalar(@expressors)>0)
	{
	    print "</table>";
	}
    }

#end table around evidence
print "</td></tr></table><br>";

}

sub print_tf_attr {
    my ($dbh,$tfname,$projid,$target,%params) = @_;

    my $tf = $dbh->create_tf;
    my @tfcomplexes = $tf->get_tfcomplex_by_name($tfname);
    foreach my $complex (@tfcomplexes) {
    my $bg_color = 0;
    my %colors = (0 => "#fffff0",
		  1 => "#9ad3e2"
		  );
	my $count=0;
	my $file="/space/usr/local/apache/pazar.info/tmp/".$tfname.".fa";
	open (TMP, ">$file");

	print "<input type='hidden' name='accn' value='$tfname'>\n";
	
########### start of HTML table

	print "<table width='600' bordercolor='white' bgcolor='white' border=1 cellspacing=0>\n";
	print<<COLNAMES;
	<tr>
	    <td width="100" align="center" valign="top" bgcolor="#e65656"><span class="title4">Project</span></td>
	    <td align="center" width="187" valign="top" bgcolor="#e65656"><span class="title4">Name</span></td>
	    <td align="center" bgcolor="#e65656"><span class="title4">Transcript Accession</span>
	    </td> 
	    <td align="center" bgcolor="#e65656"><span class="title4">Class</span>
	    </td> 
	    <td align="center" bgcolor="#e65656"><span class="title4">Family</span>
	    </td> 
	    </tr>
COLNAMES

	    print "<tr><td bgcolor=\"#fffff0\">".$proj."</td><td bgcolor=\"#fffff0\">".$tfname."</td>";

	my @classes = ();
	my @families = ();
	my @transcript_accessions = ();

	while (my $subunit=$complex->next_subunit) {
	    my $tid = $subunit->get_transcript_accession($dbh);
	    my $cl = $subunit->get_class ||'unknown'; 
	    my $fam = $subunit->get_fam ||'unknown';

	    push(@classes,$subunit->get_class);
	    push(@families,$subunit->get_fam);
	    push(@transcript_accessions, $subunit->get_transcript_accession($dbh));
	}
    #print subunit information
    print "<td bgcolor=\"#fffff0\">";
    #transcript accession
    print join('<br>',@transcript_accessions);
    print  "&nbsp;</td>";
    print "<td bgcolor=\"#fffff0\">";
    #class
    print join('<br>',@classes);
    print "&nbsp;</td>";
    print "<td bgcolor=\"#fffff0\">";
    #family
    print join('<br>',@families);
    print "&nbsp;</td>";
    print  "</tr></table>";

#separate tables for artificial and genomic targets
	print "<p><table bordercolor='white' bgcolor='white' border=1 cellspacing=0><tr>";
	if ($params{at_reg_seq} eq 'on' || $params{at_construct} eq 'on')
{
	    print "<td align='center' bgcolor='#61b9cf'><span class=\"title4\">Target type</span></td><td align='center' bgcolor='#61b9cf'><span class=\"title4\">Sequence</span></td>";
	    if ($params{at_reg_seq} eq 'on')
	    {
		print "<td align='center' bgcolor='#61b9cf'><span class=\"title4\">RegSeq ID</span></td>"
	    }
	}

	if ($params{at_reg_seq_name} eq 'on' || $params{at_construct_name} eq 'on')
{
    print "<td align='center' bgcolor='#61b9cf'><span class=\"title4\">Name</span></td>"
    }

if ($params{at_gene} eq 'on') 
{
    print "<td align='center' bgcolor='#61b9cf'><span class=\"title4\">Gene</span></td>";
}
if ($params{at_species} eq 'on')
{
    print "<td align='center' bgcolor='#61b9cf'><span class=\"title4\">Species</span></td>";
}

if ($params{at_coordinates} eq 'on')
{
    print "<td align='center' bgcolor='#61b9cf'><span class=\"title4\">Coordinates</span></td>";
}

if ($params{at_quality} eq 'on')
{
    print "<td align='center' bgcolor='#61b9cf'><span class=\"title4\">Quality</span></td>";
}

if ($params{at_description} eq 'on')
{
    print "<td align='center' bgcolor='#61b9cf'><span class=\"title4\">Description</span></td>";
}

if ($params{at_analysis} eq 'on')
{
    print "<td align='center' bgcolor='#61b9cf'><span class=\"title4\">Analysis</span></td>";
}

if ($params{at_reference} eq 'on')
{
    print "<td align='center' bgcolor='#61b9cf'><span class=\"title4\">Reference</span></td>";
}

if ($params{at_interaction} eq 'on')
{
    print "<td align='center' bgcolor='#61b9cf'><span class=\"title4\">Interaction</span></td>";
}
if ($params{at_evidence} eq 'on') 
{
    print "<td align='center' bgcolor='#61b9cf'><span class=\"title4\">Evidence</span></td>";
}

#print heading for ucsc/ensembl links column if reg_seq is on
if($params{at_reg_seq} eq 'on')
{
    print "<td align='center' bgcolor='#61b9cf'><span class=\"title4\">Display</td>";
}


print "</tr>\n";


if (!$complex->{targets}) {
    print "<p class=\"warning\">No target could be found for this TF!</p>\n";
    next;
}
my $seqcounter = 0;
while (my $site=$complex->next_target) {
    $seqcounter++;
    my $type=$site->get_type;
    if ($type eq 'matrix') {next;}
    if ($type eq 'reg_seq' && $params{at_reg_seq} eq 'on') {
	my $found=0;
	foreach my $targ (@$target) {
	    if ($targ->{dbid} eq $site->get_dbid && $targ->{aid} eq $site->get_analysis  && $targ->{ilink} eq $site->get_ilink  && $targ->{olink} eq $site->get_olink) {
		$found=1;
	    }
	}
	unless ($found==1) {next;}

	my $rsid = $site->get_dbid;
	my $rsid7d = sprintf "%07d",$rsid;
	my $id="RS".$rsid7d;

	print "<tr><td bgcolor=\"$colors{$bg_color}\"><input type='checkbox' name='".$tfname."_seq$seqcounter' value='".$site->get_seq."'>Genomic Target (reg_seq): </td><td bgcolor=\"$colors{$bg_color}\">".chopstr($site->get_seq,40)."</td><td bgcolor=\"$colors{$bg_color}\">".$id."</td>\n";
	my @regseq = $dbh->get_reg_seq_by_regseq_id($site->get_dbid);
#		    print Dumper(@regseq);
#		    print "<ul style=\"margin: 0pt; padding: 0pt; list-style-type: none;\">";
	if ($params{at_reg_seq_name} eq 'on') {
	    if($site->get_name)
	    {
		print "<td bgcolor=\"$colors{$bg_color}\">".$site->get_name."</td>";
	    }
	    else
	    {
		print "<td bgcolor=\"$colors{$bg_color}\">&nbsp;</td>";
	    }
	}
	if ($params{at_gene} eq 'on') {
	    my $transcript=$regseq[0]->transcript_accession || 'Transcript Not Specified';
#			print "<td>".$regseq[0]->gene_accession."</td><td>".$transcript."</td>";
	    my @ens_coords = $ensdb->get_ens_chr($regseq[0]->gene_accession);
	    my @desc = split('\[',$ens_coords[5]);
	    print "<td bgcolor=\"$colors{$bg_color}\">".$regseq[0]->gene_accession."<br>".$transcript."<br>".$desc[0]."</td>";
	}
	if ($params{at_species} eq 'on') {
	    print "<td bgcolor=\"$colors{$bg_color}\">".$regseq[0]->binomial_species."</td>";
	}
	if ($params{at_coordinates} eq 'on') {
	    print "<td bgcolor=\"$colors{$bg_color}\">".$regseq[0]->chromosome." (".$regseq[0]->strand.") ".$regseq[0]->start."-".$regseq[0]->end."</td>";
	}
	if ($params{at_quality} eq 'on') {
	    print "<td bgcolor=\"$colors{$bg_color}\">".$regseq[0]->quality."</td>";
	}
	if ($params{at_description} eq 'on') {
	    if($site->get_desc)
	    {
		print "<td bgcolor=\"$colors{$bg_color}\">".$site->get_desc."</td>";			   
	    }
	    else
	    {
		print "<td bgcolor=\"$colors{$bg_color}\">&nbsp;</td>";
	    }
	}
    }
    if ($type eq 'construct' && $params{at_construct} eq 'on') {
	my $found=0;
	foreach my $targ (@$target) {
	    if ($targ->{dbid} eq $site->get_dbid && $targ->{aid} eq $site->get_analysis  && $targ->{ilink} eq $site->get_ilink  && $targ->{olink} eq $site->get_olink) {
		$found=1;
	    }
	}
	unless ($found==1) {next;}
	print "<tr><td bgcolor=\"$colors{$bg_color}\"><input type='checkbox' name='".$tfname."_seq$seqcounter' value='".$site->get_seq."'>Artificial Target (construct): </td><td bgcolor=\"$colors{$bg_color}\">".chopstr($site->get_seq,40)."</td>\n";
#		    print "<ul style=\"margin: 0pt; padding: 0pt; list-style-type: none;\">";
	if ($params{at_construct_name} eq 'on') {
	    print "<td bgcolor=\"$colors{$bg_color}\">".$site->get_name."</td>";
	}

#fill in blank cells
	if ($params{at_gene} eq 'on') 
{
    print "<td bgcolor=\"$colors{$bg_color}\">&nbsp;</td>";
}
if ($params{at_species} eq 'on')
{
    print "<td bgcolor=\"$colors{$bg_color}\">&nbsp;</td>";
}

if ($params{at_coordinates} eq 'on')
{
    print "<td bgcolor=\"$colors{$bg_color}\">&nbsp;</td>";
}

if ($params{at_quality} eq 'on')
{
    print "<td bgcolor=\"$colors{$bg_color}\">&nbsp;</td>";
}


###
if ($params{at_description} eq 'on') {
    if($site->get_desc)
    {
	print "<td bgcolor=\"$colors{$bg_color}\">".$site->get_desc."</td>";			   
    }
    else
    {
	print "<td bgcolor=\"$colors{$bg_color}\">&nbsp;</td>";
    }
}
}

## do the following regardless of target type
my @an=$dbh->get_data_by_primary_key('analysis',$site->get_analysis);
if ($params{at_analysis} eq 'on') {
    my $aname=$an[2];
my @anal;
push @anal,$aname;
if ($an[3]) {
    my @met=$dbh->get_data_by_primary_key('method',$an[3]);
    push @anal,$met[0];
}
if ($an[4]) {
    my @cell=$dbh->get_data_by_primary_key('cell',$an[4]);
    push @anal,$cell[0];
}
if ($an[5]) {
    my @time=$dbh->get_data_by_primary_key('time',$an[5]);
    push @anal,$time[0];
}
print "<td bgcolor=\"$colors{$bg_color}\">";
print join(':',@anal)."&nbsp;</td>";
}
if ($params{at_reference} eq 'on') {
    if ($an[6])
{
    my @ref=$dbh->get_data_by_primary_key('ref',$an[6]);
    print "<td bgcolor=\"$colors{$bg_color}\">".$ref[0]."&nbsp;</td>";
}
else
{
    print "<td bgcolor=\"$colors{$bg_color}\">&nbsp;</td>"
    }
}
if ($params{at_interaction} eq 'on') {
    print "<td bgcolor=\"$colors{$bg_color}\">";
my ($table,$pazarid,@dat)=$dbh->links_to_data($site->get_olink,'output');
if ($table eq 'interaction') {

    my @data;
    for (my $i=0;$i<(@dat-3);$i++) {
	if ($dat[$i] && $dat[$i] ne '0') {
	    push @data,$dat[$i];
	}
    }
    print join(":",@data);
}
print "&nbsp;</td>";
}
if ($params{at_evidence} eq 'on') {
    if ($an[1])
{
    my @ev=$dbh->get_data_by_primary_key('evidence',$an[1]);
    print "<td bgcolor=\"$colors{$bg_color}\">".$ev[0]."_".$ev[1]."</td>";
}
else
{
    print "<td bgcolor=\"$colors{$bg_color}\">&nbsp;</td>";
}
}

#print ucsc and ensembl links at the end of the row if target is a refseq
#get the corresponding regseq object
if($params{at_reg_seq} eq 'on')
{
    if ($type eq 'reg_seq') {
	my @regseq = $dbh->get_reg_seq_by_regseq_id($site->get_dbid);
	my $target_regseq = $regseq[0];			
	print "<td>";			
	print "<a href=\"http://www.pazar.info/cgi-bin/gff_custom_track.cgi?resource=ucsc&chr=".$target_regseq->chromosome."&start=".$target_regseq->start."&end=".$target_regseq->end."&species=".$target_regseq->binomial_species."\" target='_blank'><img src='http://www.pazar.info/images/ucsc_logo.png'></a><br>";
	print "<a href=\"http://www.pazar.info/cgi-bin/gff_custom_track.cgi?resource=ensembl&chr=".$target_regseq->chromosome."&start=".$target_regseq->start."&end=".$target_regseq->end."&species=".$target_regseq->binomial_species."\" target='_blank'><img src='http://www.pazar.info/images/ensembl_logo.gif'></a>";
	print "</td>";
    }
    else
    {
	print "<td>&nbsp;</td>";
    }
}

print "</tr>";
$count++;
my $construct_name=$tfname."_site".$count;
print TMP ">".$construct_name."\n";
print TMP $site->get_seq."\n";
$bg_color = 1 - $bg_color;
}
print "</table><br>\n";

close (TMP);

if ($params{at_profile} eq 'on') {
    if ($count<2) {
	print "<p class=\"warning\">There are not enough targets to build a binding profile for this TF!</p>\n";
	exit;
    } else {

	my $patterngen =
	    TFBS::PatternGen::MEME->new(-seq_file=> "$file",
					-binary => 'meme',
					-additional_params => '-mod oops');
	my $pfm = $patterngen->pattern(); # $pfm is now a TFBS::Matrix::PFM object
#print a human readable format of the matrix
	my $prettystring = $pfm->prettyprint();
	my @matrixlines = split /\n/, $prettystring;
	$prettystring = join "<BR>\n", @matrixlines;
	$prettystring =~ s/ /\&nbsp\;/g;
	print "<table bordercolor='white' bgcolor='white' border=1 cellspacing=0 cellpadding=10><tr><td><span class=\"title4\">Position Frequency Matrix</span></td><td ><SPAN class=\"monospace\">$prettystring</SPAN></td></tr>";
#draw the logo
	my $logo = $tfname.".png";
	my $gd_image = $pfm->draw_logo(-file=>"/space/usr/local/apache/pazar.info/tmp/".$logo, -xsize=>400);
	print "<tr><td><span class=\"title4\">Logo</span></td><td><img src=\"http://www.pazar.info/tmp/$logo\">";
	print "<p class=\"small\">These PFM and Logo were generated dynamically using the MEME pattern discovery algorithm.</p></td></tr>\n";
	print "</table><br>\n";
########### end of HTML table
    }
}
}
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
