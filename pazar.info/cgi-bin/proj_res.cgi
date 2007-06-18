#!/usr/bin/perl

use HTML::Template;
#use Data::Dumper;
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

my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};
my $pazarhtdocspath = $ENV{PAZARHTDOCSPATH};

require "$pazarcgipath/getsession.pl";
 
# open the html header template
my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");

# fill in template parameters
$template->param(TITLE => "PAZAR - Project Search Results");
$template->param(PAZAR_HTML => $pazar_html);
$template->param(PAZAR_CGI => $pazar_cgi);
$template->param(JAVASCRIPT_FUNCTION => q{
function verifyCheckedBoxes() {            
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
	window.open('about:blank','logowin', 'resizable=1,scrollbars=yes, menubar=no, toolbar=no directories=no, height=600, width=600');
	document.sequenceform.submit();
    }

        }});

if($loggedin eq 'true')
{
    #log out link
    $template->param(LOGOUT => "$info{first} $info{last} logged in. "."<a href=\'$pazar_cgi/logout.pl\'>Log Out</a>");
}
else
{
    #log in link
    $template->param(LOGOUT => "<a href=\'$pazar_cgi/login.pl\'>Log In</a>");
}

# send the obligatory Content-Type and print the template output
print "Content-Type: text/html\n\n", $template->output;

my $get = new CGI;
my %param = %{$get->Vars};
foreach my $item (keys %param) {
    my @vals;
    foreach my $val ($get->param($item)) {
	push @vals, $val;
    }
    $param{$item}=join(';',@vals);
}

###getting the project_name
my $proj=$param{project_name};

###database connection
my $dbh0= pazar->new( 
		       -host          =>    $ENV{PAZAR_host},
		       -user          =>    $ENV{PAZAR_pubuser},
		       -pass          =>    $ENV{PAZAR_pubpass},
		       -dbname        =>    $ENV{PAZAR_name},
		       -drv           =>    $ENV{PAZAR_drv},
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
		       -drv           =>    $ENV{PAZAR_drv},
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
		       -drv           =>    $ENV{PAZAR_drv},
		       -project       =>    $proj);
}

my $ensdb = pazar::talk->new(DB=>'ensembl',USER=>$ENV{ENS_USER},PASS=>$ENV{ENS_PASS},HOST=>$ENV{ENS_HOST},DRV=>'mysql');

my $projid = $dbh->get_projectid();

print "<p class=\"title1\">PAZAR - \'$proj\' Search Results</p>";

###
### gene-centric view
###

if ($param{submit}=~/gene/i) {
    my @reg_seqs;
    undef(my @filters);
### species filter
    if ($param{species_filter} eq 'on') {
	if (!$param{species}) {print "<p class=\"warning\">You need to select one or more species when using the species filter!<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"$pazar_cgi/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
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
            if (!$reg_seqs[0]) {print "<p class=\"warning\">No regulatory sequence was found for species: ".join(',',@species)."<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"$pazar_cgi/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
	} else {

### region filter
	    if (scalar(@species)>1) {print "<p class=\"warning\">You have to choose a unique species when using the region filter!<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"$pazar_cgi/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
	    if ($param{chr_filter} eq 'on') {
		unless ($param{bp_filter} eq 'on') {
		    @reg_seqs=$dbh->get_reg_seq_by_chromosome($param{chromosome},$param{species});
	if (!grep(/chromosome filter/, @filters)) {
		    my $filter='chromosome filter: '.$param{chromosome};
		    push @filters, $filter;
		}
                    if (!$reg_seqs[0]) {print "<p class=\"warning\">No regulatory sequence was found on chromosome $param{chromosome} in species $param{species}<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"$pazar_cgi/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
		} else {
                    if (!$param{bp_start} || !$param{bp_end}) {print "<p class=\"warning\">You need to specify the start and end of the region you're interested in when using the base pair filter!<br><form><input type=\"button\" name=\"change_filters\" value=\"Modify Filters\" onclick=\"parent.location.href='$pazar_cgi/project.pl&project_name=\"$proj\"'\"></form></p>\n"; exit;}
		    if ($param{bp_start}>=$param{bp_end}) {print "<p class=\"warning\">The start coordinate needs to be lower that the end!<br><form><input type=\"button\" name=\"change_filters\" value=\"Modify Filters\" onclick=\"parent.location.href='$pazar_cgi/project.pl&project_name=\"$proj\"'\"></form></p>\n"; exit;}
	if (!grep(/region filter/, @filters)) {
		    my $filter='region filter: '.$param{chromosome}.':'.$param{bp_start}.'-'.$param{bp_end};
		    push @filters, $filter;
		}
		    @reg_seqs=$dbh->get_reg_seq_by_region($param{bp_start},$param{bp_end},$param{chromosome},$param{species});
                    if (!$reg_seqs[0]) {print "<p class=\"warning\">No regulatory sequence was found between bp $param{bp_start} and $param{bp_end} on chromosome $param{chromosome} in species $param{species}<br><form><input type=\"button\" name=\"change_filters\" value=\"Modify Filters\" onclick=\"parent.location.href='$pazar_cgi/project.pl&project_name=\"$proj\"'\"></form></p>\n"; exit;}
		}
	    }
	}
    } else {
	if ($param{region_filter} eq 'on') {print "<p class=\"warning\">You have to select a species if you want to use the region filter!<br><form><input type=\"button\" name=\"change_filters\" value=\"Modify Filters\" onclick=\"parent.location.href='$pazar_cgi/project.pl&project_name=\"$proj\"'\"></form></p>\n"; exit;}
    }

### gene filter
    if ($param{gene_filter} eq 'on') {
	if ($reg_seqs[0]) {print "<p class=\"warning\">You cannot use species and region filters when using the gene filter!<br><form><input type=\"button\" name=\"change_filters\" value=\"Modify Filters\" onclick=\"parent.location.href='$pazar_cgi/project.pl&project_name=\"$proj\"'\"></form></p>\n"; exit;}
	if (!$param{gene}) {print "<p class=\"warning\">You need to select one or more gene when using the gene filter!<br><form><input type=\"button\" name=\"change_filters\" value=\"Modify Filters\" onclick=\"parent.location.href='$pazar_cgi/project.pl&project_name=\"$proj\"'\"></form></p>\n"; exit;}
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
	if (!$reg_seqs[0]) {print "<p class=\"warning\">No regulatory sequence was found for the genes ".join(',',@genes)."!<br><form><input type=\"button\" name=\"change_filters\" value=\"Modify Filters\" onclick=\"parent.location.href='$pazar_cgi/project.pl&project_name=\"$proj\"'\"></form></p>\n"; exit;}

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
    my $display_counter=0;
    my $bg_color = 0;
    my %colors = (0 => "#fffff0",
	          1 => "#BDE0DC"
	          );

    foreach my $regseq (@sorted_regseqs) {

### length filter
	if ($param{length_filter} eq 'on' && $param{length} ne '0') {
	    if (!$param{length} || $param{length}<=0) {print "<p class=\"warning\">You need to specify a length greater than 0 when using the length filter!<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"$pazar_cgi/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
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
	        if (!$param{tf}) {print "<p class=\"warning\">You need to select one or more TF when using the TF filter!<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"$pazar_cgi/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
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
	        if (!$param{evidence}) {print "<p class=\"warning\">You need to select one or more evidence type when using the evidence filter!<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"$pazar_cgi/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
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
	        if (!$param{method}) {print "<p class=\"warning\">You need to select one or more method type when using the method filter!<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"$pazar_cgi/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
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
	        if (!$param{evidence}) {print "<p class=\"warning\">You need to select one or more evidence type when using the evidence filter!<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"$pazar_cgi/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
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
	        if (!$param{method}) {print "<p class=\"warning\">You need to select one or more method type when using the method filter!<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"$pazar_cgi/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
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
	    print "<p><span class=\"title3\">Selected filters: </span><br>".join('; ',@filters)."<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"$pazar_cgi/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p><h1>PAZAR Gene View</h1>";
	}
	if ($exprs[0] || $inters[0] || $datalinks==2) {
	    $filt=1;
	    my $gene_accn = $regseq->gene_accession;
	    my $gene_desc = $regseq->gene_description || '';
	    my $gene_sp = $regseq->binomial_species;
	    my $pazargeneid = write_pazarid($regseq->PAZAR_gene_ID,'GS');
	    if ($gene_accn ne $prev_gene_accn) {
		if ($prev_gene_accn) {print "</table><br><br>";}
		$bg_color = 0;
		my @ens_coords = $ensdb->get_ens_chr($gene_accn);
		$ens_coords[5]=~s/\[.*\]//g;
		$ens_coords[5]=~s/\(.*\)//g;
		$ens_coords[5]=~s/\.//g;
		my $geneDescription = $ens_coords[5]||'-';

#print header

print<<HEADER_TABLE;
<table class="summarytable">
<tr><td class="genetabletitle"><span class="title4">Species</span></td><td class="basictd">$gene_sp</td></tr>
<tr><td class="genetabletitle"><span class="title4">PAZAR Gene ID</span></td><td class="basictd"><form name="genelink$pazargeneid[0]" method='post' action="$pazar_cgi/gene_search.cgi" enctype='multipart/form-data'><input type='hidden' name='geneID' value="$gene_accn"><input type='hidden' name='ID_list' value='EnsEMBL_gene'><input type="submit" class="submitLink" value="$pazargeneid">&nbsp;</form></td></tr>
<tr><td class="genetabletitle"><span class="title4">Gene Name (user defined)</span></td><td class="basictd">$gene_desc</td></tr>
<tr><td class="genetabletitle"><span class="title4">EnsEMBL Gene ID</span></td><td class="basictd">$gene_accn</td></tr>
<tr><td class="genetabletitle"><span class="title4">EnsEMBL Gene Description</span></td><td class="basictd">$geneDescription</td></tr>
</table><br>
HEADER_TABLE

########### start of HTML sequence table
print<<COLNAMES;	    
		<table class="searchtable"><tr>
COLNAMES
    print "<td class=\"genedetailstabletitle\" width='100'><span class=\"title4\">RegSeq ID</span><br><span class=\"smallredbold\">click an ID to enter Sequence View</span></td>";
    print "<td width='150' class=\"genedetailstabletitle\"><span class=\"title4\">Sequence Name</span></td>";
    print "<td width='300' class=\"genedetailstabletitle\"><span class=\"title4\">Sequence</span></td>";
    print "<td width='300' class=\"genedetailstabletitle\"><span class=\"title4\">Coordinates</span></td>";
    print "<td width='100' class=\"genedetailstabletitle\"><span class=\"title4\">Display Genomic Context</span></td>";
    print "</tr>";

                $prev_gene_accn = $gene_accn;
	    }
	    &print_gene_attr($regseq,\%colors,$bg_color,$display_counter);
	    print "</tr>";
	    $display_counter++;
	    $bg_color =  1 - $bg_color;
	}
    }
    if (!@filters) {push @filters, 'none';}
    if ($res==1 && $filt==0) {
	print "<p class=\"warning\">No regulatory sequence was found using this set of filters!<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"$pazar_cgi/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>";
    }
    if ($res==0) {
	print "<p><span class=\"title3\">Selected filters: </span><br>".join('; ',@filters)."<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"$pazar_cgi/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>";
	print "<p class=\"warning\">No regulatory sequence was found using this set of filters!</p>";
    }

###
### TF-centric view
###

} elsif ($param{submit}=~/tf/i) {

### TF filter
    my @complexes;
    undef(my @filters);
    if ($param{tf_filter} eq 'on') {
	if (!$param{tf}) {print "<p class=\"warning\">You need to select one or more TF when using the TF filter!<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"$pazar_cgi/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
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
        if (!$complexes[0]) {print "<p class=\"warning\">No TF was found with the following names: ".join(',',@tfs)."<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"$pazar_cgi/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
    }

### TF class filter
    if ($param{class_filter} eq 'on') {
	if ($complexes[0]) {print "<p class=\"warning\">You cannot use the TF filter and TF class filter at the same time!<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"$pazar_cgi/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
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
        if (!$complexes[0]) {print "<p class=\"warning\">No TF was found within the following class: ".$cf[0]."<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"$pazar_cgi/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
    }

### species filter
    if ($param{species_filter} eq 'on') {
	if (!$param{species}) {print "<p class=\"warning\">You need to select one or more species when using the species filter!<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"$pazar_cgi/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
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
	    if (!$complexes[0]) {print "<p class=\"warning\">No TF was found from the following species: ".join(',',@species)."<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"$pazar_cgi/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
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
		print "<p><span class=\"title3\">Selected filters: </span><br>".join('; ',@filters)."<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"$pazar_cgi/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>";
		print "<p class=\"warning\">No TF was found in this project using this set of filters!<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"$pazar_cgi/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n";
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
	    if (scalar(@species)>1) {print "<p class=\"warning\">You have to choose a unique species when using the region filter!<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"$pazar_cgi/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
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
                    if (!$reg_seqs[0]) {print "<p class=\"warning\">No regulatory sequence was found on chromosome $param{chromosome} in species $param{species}<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"$pazar_cgi/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
		} else {
                    if (!$param{bp_start} || !$param{bp_end}) {print "<p class=\"warning\">You need to specify the start and end of the region you're interested in when using the base pair filter!<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"$pazar_cgi/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
		    if ($param{bp_start}>=$param{bp_end}) {print "<p class=\"warning\">The start coordinate needs to be lower that the end!<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"$pazar_cgi/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
		    if (!grep(/region filter/, @filters)) {
			my $filter='region filter: '.$param{chromosome}.':'.$param{bp_start}.'-'.$param{bp_end};
			push @filters, $filter;
		    }
		    my @seqs=$dbh->get_reg_seq_by_region($param{bp_start},$param{bp_end},$param{chromosome},$param{species});
		    foreach my $regseq (@seqs) {
			push @reg_seqs, $regseq->accession_number;
		    }

                    if (!$reg_seqs[0]) {print "<p class=\"warning\">No regulatory sequence was found between bp $param{bp_start} and $param{bp_end} on chromosome $param{chromosome} in species $param{species}<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"$pazar_cgi/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
		}
	    }
	}
    } else {
	if ($param{region_filter} eq 'on') {print "<p class=\"warning\">You have to select a species if you want to use the region filter!<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"$pazar_cgi/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
    }

### gene filter
    if ($param{gene_filter} eq 'on') {
	if ($param{species_filter} eq 'on') {print "<p class=\"warning\">You cannot use species and region filters when using the gene filter!<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"$pazar_cgi/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
	if (!$param{gene}) {print "<p class=\"warning\">You need to select one or more gene when using the gene filter!<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"$pazar_cgi/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
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
	if (!$reg_seqs[0]) {print "<p class=\"warning\">No regulatory sequence was found for the genes ".join(',',@genes)."!<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"$pazar_cgi/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
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
		    if (!$param{length} || $param{length}<=0) {print "<p class=\"warning\">You need to specify a length greater than 0 when using the length filter!<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"$pazar_cgi/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
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
		    if (!$param{evidence}) {print "<p class=\"warning\">You need to select one or more evidence type when using the evidence filter!<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"$pazar_cgi/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
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
		    if (!$param{method}) {print "<p class=\"warning\">You need to select one or more method type when using the method filter!<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"$pazar_cgi/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>\n"; exit;}
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
	print "<p><span class=\"title3\">Selected filters: </span><br>".join('; ',@filters)."<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"$pazar_cgi/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p>";
	print "<p class=\"warning\">No regulatory sequence and/or TF was found using this set of filters!<br></p>";
    } else{
	print "<p><span class=\"title3\">Selected filters: </span><br>".join('; ',@filters)."<br><form name=\"modify_filters\" METHOD=\"post\" ACTION=\"$pazar_cgi/project.pl\" enctype=\"multipart/form-data\" target=\"_self\"><input type=\"hidden\" name=\"project_name\" value=\"$proj\"><input type=\"submit\" name=\"submit\" value=\"Modify Filters\"></form></p><h1>PAZAR TF View</h1>";
####start of form
	print "<form name='sequenceform' method='post' target='logowin' action='$pazar_cgi/tf_logo.pl'>";
	my $seqcounter = 0;
	foreach my $tf (keys %inters) {
	$seqcounter=&print_tf_attr($dbh,$tf,\@{$inters{$tf}},$seqcounter);
	}
####hidden form inputs
print "<table bordercolor='white' bgcolor='white'><tr><td class=\"title2\">Click Go to recalculate matrix and logo based on selected sequences</td>";
print "<td><input type='button' value='Go' onClick=\"verifyCheckedBoxes();\"></td></tr>
<tr><td>(you can combine sequences from multiple TFs)</td></tr></table>";
print "</form>";
####end of form
    }
}

###  print out the html tail template
my $template_tail = HTML::Template->new(filename => "$pazarcgipath/tail.tmpl");
print $template_tail->output;

sub select {
    my ($dbh, $sql) = @_;
    my $sth=$dbh->prepare($sql);
    $sth->execute or die "$dbh->errstr\n";
    return $sth;
}

sub print_gene_attr {
    my ($regseq,$colors,$bg_color,$regseq_counter) = @_;
    my %colors=%{$colors};

#print out default information
		print "<tr>";
		print "<form name='details$regseq_counter' method='post' action='$pazar_cgi/seq_search.cgi' enctype='multipart/form-data'><input type='hidden' name='regid' value='".$regseq->accession_number."'>";
		
		my $id=write_pazarid($regseq->accession_number,'RS');
		print "<td width='100' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'><input type=\"submit\" class=\"submitLink\" value=\"".$id."\"></div></td></form>";

		my $seqname=$regseq->id||'-';
		print "<td width='150' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'>".$seqname."&nbsp;</div></td>";	       

		my $seqstr=chopstr($regseq->seq,40);
		print "<td height=100 width=300 class=\"basictd\" bgcolor=\"$colors{$bg_color}\"><div style=\"font-family:monospace;height:100; width:300;overflow:auto;\">".$seqstr."</div></td>";

		print "<td width='300' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'>chr".$regseq->chromosome.":".$regseq->start."-".$regseq->end." (strand ".$regseq->strand.")</div></td>";

		print "<form name='display$regseq_counter' method='post' action='$pazar_cgi/gff_custom_track.cgi' enctype='multipart/form-data' target='_blank'>";

		print "<td width='100' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'><input type='hidden' name='chr' value='".$regseq->chromosome."'><input type='hidden' name='start' value='".$regseq->start."'><input type='hidden' name='end' value='".$regseq->end."'><input type='hidden' name='species' value='".$regseq->binomial_species."'><input type='hidden' name='resource' value='ucsc'><a href='#' onClick=\"javascript:document.display$regseq_counter.resource.value='ucsc';document.display$regseq_counter.submit();\"><img src='$pazar_html/images/ucsc_logo.png'></a><!--<input type='submit' name='ucsc' value='ucsc' onClick=\"javascript:document.display$regseq_counter.resource.value='ucsc';\">--><br><br><a href='#' onClick=\"javascript:document.display$regseq_counter.resource.value='ensembl';document.display$regseq_counter.submit();\"><img src='$pazar_html/images/ensembl_logo.gif'></a><!--<input type='submit' name='ensembl' value='ensembl' onClick=\"javascript:document.display$regseq_counter.resource.value='ensembl';\">--></div></td></form>";
}

sub print_tf_attr {
    my ($dbh,$tfname,$target,$seqcounter) = @_;

    my $tf = $dbh->create_tf;
    my @tfcomplexes = $tf->get_tfcomplex_by_name($tfname);
    foreach my $complex (@tfcomplexes) {
	my $bg_color = 0;
	my %colors = (0 => "#fffff0",
		      1 => "#FFB5AF"
		      );
	my $count=0;
	$tfname=~s/\//-/g;
	my $file="$pazarhtdocspath/tmp/".$tfname.".fa";
	open (TMP, ">$file");

	print "<input type='hidden' name='accn' value='$tfname'>\n";
	
	my $pazartfid=write_pazarid($complex->dbid,'TF');

	my @classes = ();
	my @families = ();
	my @transcript_accessions = ();

	while (my $subunit=$complex->next_subunit) {
	    my $class=!$subunit->get_class?'-':$subunit->get_class;
	    my $fam=!$subunit->get_fam?'-':$subunit->get_fam;
	    push(@classes,$class);
	    push(@families,$fam);
	    push(@transcript_accessions, $subunit->get_transcript_accession($dbh));
	}
	my $traccns=join('<br>',@transcript_accessions);
	my $trclasses=join('<br>',@classes);
	my $trfams=join('<br>',@families);

########### start of HTML table
	print<<COLNAMES;
	<table class="summarytable">
	    <tr><td class="tftabletitle"><span class="title4">TF Name</span></td><td class="basictd">$tfname</td></tr>
	    <tr><td class="tftabletitle"><span class="title4">PAZAR TF ID</span></td><td class="basictd"><a href="$pazar_cgi/tf_search.cgi?geneID=$tfname">$pazartfid</a></td></tr>
	    <tr><td class="tftabletitle"><span class="title4">Transcript Accession</span></td><td class="basictd">$traccns</td></tr>
	    <tr><td class="tftabletitle"><span class="title4">Class</span></td><td class="basictd">$trclasses</td></tr>
	    <tr><td class="tftabletitle"><span class="title4">Family</span></td><td class="basictd">$trfams</td></tr>
	    </table><br>
COLNAMES

########### start of HTML table
	print<<COLNAMES2;	    
	<table class="evidencetableborder"><tr>
	    <td width="100" class="tfdetailstabletitle"><span class="title4">Sequence Type</span></td>
	    
COLNAMES2
	print "<td class=\"tfdetailstabletitle\" width='100'><span class=\"title4\">Sequence ID</span><br><span class=\"smallbold\">click an ID to enter Sequence View</span></td>";
	print "<td width='150' class=\"tfdetailstabletitle\"><span class=\"title4\">Gene ID</span></td>";
	print "<td width='300' class=\"tfdetailstabletitle\"><span class=\"title4\">Sequence</span></td>";
	print "<td width='300' class=\"tfdetailstabletitle\"><span class=\"title4\">Sequence Info</span></td>";
	print "<td width='100' class=\"tfdetailstabletitle\"><span class=\"title4\">Display Genomic Context</span></td>";
	print "</tr>";

	if (!$complex->{targets}) {
	    print "<p class=\"warning\">No target could be found for this TF!</p><br>";
	    next;
	}
	my @rsids;
	my @coids;
	while (my $site=$complex->next_target) {
	    $seqcounter++;
	    my $type=$site->get_type;
	    if ($type eq 'matrix') {next;}

	    if ($type eq 'reg_seq') {
		my $found=0;
		foreach my $targ (@$target) {
		    if ($targ->{dbid} eq $site->get_dbid && $targ->{aid} eq $site->get_analysis  && $targ->{ilink} eq $site->get_ilink  && $targ->{olink} eq $site->get_olink) {
			$found=1;
		    }
		}
		unless ($found==1) {next;}
		my $rsid=$site->get_dbid;
		if (grep/^$rsid$/,@rsids) {next;}
		push @rsids, $rsid;
		my $id=write_pazarid($rsid,'RS');
		my $seqname=!$site->get_name?'':$site->get_name;
		my $reg_seq = $dbh->get_reg_seq_by_regseq_id($site->get_dbid);
		my $pazargeneid = write_pazarid($reg_seq->PAZAR_gene_ID,'GS');
		my $gene_accession=$reg_seq->gene_accession;
		my @ens_coords = $ensdb->get_ens_chr($reg_seq->gene_accession);
		$ens_coords[5]=~s/\[.*\]//g;
		$ens_coords[5]=~s/\(.*\)//g;
		$ens_coords[5]=~s/\.//g;
		my $species = $ensdb->current_org();
		$species = ucfirst($species)||'-';

		my $coord="chr".$reg_seq->chromosome.":".$reg_seq->start."-".$reg_seq->end." (strand ".$reg_seq->strand.")";

		print "<tr><td width='100' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'><input type='checkbox' name='seq$seqcounter' value='".$site->get_seq."'><br>Genomic<br>Sequence</div></td>";
		print "<td width='100' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'><a href=\"$pazar_cgi/seq_search.cgi?regid=$rsid\">".$id."</a><br>$seqname</div></td>";
		print "<td width='150' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'><a href=\"$pazar_cgi/gene_search.cgi?geneID=$gene_accession\">".$pazargeneid."</a><br><b>$ens_coords[5]</b><br>$species</div></td>";
		print "<td width='300' class=\"basictd\" bgcolor=\"$colors{$bg_color}\"><div style=\"font-family:monospace;height:100; width:300;overflow:auto;\">".chopstr($site->get_seq,40)."</div></td>";
		print "<td width='300' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'><b>Coordinates:</b><br>".$coord."</div></td>";
		print "<td width='100' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'><a href=\"$pazar_cgi/gff_custom_track.cgi?resource=ucsc&chr=".$reg_seq->chromosome."&start=".$reg_seq->start."&end=".$reg_seq->end."&species=".$reg_seq->binomial_species."\" target='_blank'><img src='$pazar_html/images/ucsc_logo.png'></a><br><br>";
		print "<a href=\"$pazar_cgi/gff_custom_track.cgi?resource=ensembl&chr=".$reg_seq->chromosome."&start=".$reg_seq->start."&end=".$reg_seq->end."&species=".$reg_seq->binomial_species."\" target='_blank'><img src='$pazar_html/images/ensembl_logo.gif'></a>";
		print "</div></td>";
	    }
	    if ($type eq 'construct') {
		my $found=0;
		foreach my $targ (@$target) {
		    if ($targ->{dbid} eq $site->get_dbid && $targ->{aid} eq $site->get_analysis  && $targ->{ilink} eq $site->get_ilink  && $targ->{olink} eq $site->get_olink) {
			$found=1;
		    }
		}
		unless ($found==1) {next;}
		my $coid=$site->get_dbid;
		if (grep/^$coid$/,@coids) {next;}
		push @coids, $coid;
		my $id=write_pazarid($coid,'CO');
		my $seqname=$site->get_name==0?'':$site->get_name;
		my $desc=$site->get_desc||'-';
		print "<tr><td width='100' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'><input type='checkbox' name='seq$seqcounter' value='".$site->get_seq."'><br>Artificial<br>Sequence</div></td>";
		print "<td width='100' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'><b>".$id."</b><br>$seqname</div></td>";
		print "<td width='150' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'>-</div></td>";
		print "<td width='300' class=\"basictd\" bgcolor=\"$colors{$bg_color}\"><div style=\"font-family:monospace;height:100; width:300;overflow:auto;\">".chopstr($site->get_seq,40)."</div></td>";
		print "<td width='300' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\"><div class='overflow'><b>Description:</b><br>".$desc."</div></td>";
		print "<td width='100' class=\"basictdcenter\" bgcolor=\"$colors{$bg_color}\">&nbsp</td>";
	    }
	    print "</tr>";
	    $count++;
	    my $construct_name=$tfname."_site".$count;
	    print TMP ">".$construct_name."\n";
	    print TMP $site->get_seq."\n";
	    $bg_color = 1 - $bg_color;
	}
	print "</table>";
	close (TMP);

	if ($count<2) {
	    print "<p class=\"warning\">There are not enough targets to build a binding profile for this TF!</p><br>";
	    next;
	} else {

	    my $patterngen =
		TFBS::PatternGen::MEME->new(-seq_file=> "$file",
					    -binary => 'meme',
					    -additional_params => '-revcomp -mod oops');
	    my $pfm = $patterngen->pattern(); # $pfm is now a TFBS::Matrix::PFM object

	    if (!$pfm) {
		print "<p class=\"warning\">No motif could be found!<br>Try running the motif discovery again with a sub-selection of sequences.</p><br>";
		next;
	    } else {
#print a human readable format of the matrix
		my $prettystring = $pfm->prettyprint();
		my @matrixlines = split /\n/, $prettystring;
		$prettystring = join "<BR>\n", @matrixlines;
		$prettystring =~ s/ /\&nbsp\;/g;
		print "<br><table bordercolor='white' bgcolor='white' border=1 cellspacing=0 cellpadding=10><tr><td><span class=\"title4\">Position Frequency Matrix</span></td><td ><SPAN class=\"monospace\">$prettystring</SPAN></td></tr>";
#draw the logo
		my $logo = $tfname.".png";
		my $gd_image = $pfm->draw_logo(-file=>"$pazarhtdocspath/tmp/".$logo, -xsize=>400);
		print "<tr><td><span class=\"title4\">Logo</span></td><td><img src=\"$pazar_html/tmp/$logo\">";
		print "<p class=\"small\">These PFM and Logo were generated dynamically using the MEME pattern discovery algorithm.</p></td></tr>";
		print "</table><br>";
########### end of HTML table
	    }
	}
	print "<br><br>";
    }
    return $seqcounter;
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


sub write_pazarid {
    my $id=shift;
    my $type=shift;
    my $id7d = sprintf "%07d",$id;
    my $pazarid=$type.$id7d;
    return $pazarid;
}
