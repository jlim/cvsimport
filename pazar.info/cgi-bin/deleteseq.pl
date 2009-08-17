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


#connect to the database
my $pazar = pazar->new(
                      -host          =>    $ENV{PAZAR_host},
                      -user          =>    $ENV{PAZAR_pubuser},
                      -pass          =>    $ENV{PAZAR_pubpass},
                      -dbname        =>    $ENV{PAZAR_name},
                      -drv           =>    $ENV{PAZAR_drv},
                      -globalsearch  =>    'yes');


#check if logged in

if($loggedin eq "true") {
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
		if($proj == $projectid) {
	    	#comments are editable
	    	$seqeditable = "true";
		}
    }
    #make sure user is a member of the project
    if($seqeditable eq "true") {
		if ($sequenceid =~ /^CO/) {
			$sequenceid =~ s/\D//g;
			$sequenceid =~ s/^0+//;
			$dbh->do("delete from construct where construct_id=".$sequenceid);
			print "Construct with ID ".$sequenceid." has been deleted<br>";
	
			$dbh->do("delete from dataset where construct_id=".$sequenceid." AND project_id=".$projectid);
			print "Associated datasets have been deleted<br>";
	
			$dbh->do("delete from reg_seq_construct where construct_id=".$sequenceid." AND project_id=".$projectid);
			print "Associated constructs have been deleted<br>";

			## delete associated analysis entries
	
			## get analysis ids
			my $all=$pazar->get_analysis_by_construct_id($sequenceid);
			foreach my $row (@$all) {
				my ($analysisid,$ainputid)=@$row;
					
				## use deleteanalysis.pl code##############################
		
				$dbh->do("delete from analysis where analysis_id=".$analysisid);
				##    print "delete from analysis where analysis_id=".$analysisid."<br>";
				print "Analysis with ID: ".$analysisid." deleted<br>";
		
				my $sth1 = $dbh->prepare("select analysis_input_id from analysis_input where analysis_id=$analysisid");
				$sth1->execute;
				while(my $href1 = $sth1->fetchrow_hashref) {
					my $sth3 = $dbh->prepare("select analysis_i_link_id,analysis_o_link_id from analysis_i_link where analysis_input_id=".$href1->{analysis_input_id});
					$sth3->execute;
					#iterate through analysis_i_link records
					while(my $href3 = $sth3->fetchrow_hashref) {
						#select the analysis output from the analysis_o_link
						my $sth4 = $dbh->prepare("select distinct(analysis_output_id) from analysis_o_link where analysis_i_link_id=".$href3->{analysis_i_link_id}." OR analysis_o_link_id=".$href3->{analysis_o_link_id}); # maybe too inclusive?
						$sth4->execute;
			
						#iterate over analysis output ids
						while(my $href4 = $sth4->fetchrow_hashref) {
							#figure out how many analysis_o_links refer to the analysis_output record
							my $olinks_sth = $dbh->prepare("select analysis_o_link_id from analysis_o_link where analysis_o_link_id!=".$href3->{analysis_o_link_id}." AND analysis_output_id=".$href4->{analysis_output_id});
							$olinks_sth->execute;
							my $numreferringolinks = 0;
							while(my $olinks_href = $olinks_sth->fetchrow_hashref) {
								$numreferringolinks++;
							}
		
							if($numreferringolinks == 0) {
								#select io_type_id from analysis_output
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
								while(my $outputs_href = $outputs_sth->fetchrow_hashref) {
									$numreferringoutputs++;
								}
			
								#delete the io_type	    
								if($numreferringoutputs == 0) {
									$dbh->do("delete from io_type where io_type_id=".$output_iotypeid);
									##  print "output iotype: delete from io_type where io_type_id=".$output_iotypeid."<br>";
								}
						
								#delete the analysis output
								$dbh->do("delete from analysis_output where analysis_output_id=".$href4->{analysis_output_id});
				##				print "delete from analysis_output where analysis_output_id=".$href4->{analysis_output_id}."<br>";
								print "Deleted analysis output with ID: ".$href4->{analysis_output_id}."<br>";
				
							}
						}
						
						#delete analysis_o_link
						$dbh->do("delete from analysis_o_link where analysis_o_link_id=".$href3->{analysis_o_link_id});
				##	    print "delete from analysis_o_link where analysis_o_link_id=".$href3->{analysis_o_link_id}."<br>";
				
						#delete analysis_i_link
						$dbh->do("delete from analysis_i_link where analysis_i_link_id=".$href3->{analysis_i_link_id});
				##	    print "delete from analysis_i_link where analysis_i_link_id=".$href3->{analysis_i_link_id}."<br>";
					}	       
					
					#check if io_type only associated with analysis inputs being deleted
					#if so
					
					my $inputiosth = $dbh->prepare("select io_type_id from analysis_input where analysis_input_id=".$href1->{analysis_input_id});
					$inputiosth->execute;
					my $inputiohref = $inputiosth->fetchrow_hashref;
					my $input_iotypeid = $inputiohref->{io_type_id};
				
					#figure out how many analysis inputs refer to the io_type record
					my $inputs_sth = $dbh->prepare("select analysis_input_id from analysis_input where analysis_input_id!=".$href1->{analysis_input_id}." AND io_type_id=".$input_iotypeid);
					$inputs_sth->execute;
					my $numreferringinputs = 0;
					while(my $inputs_href = $inputs_sth->fetchrow_hashref) {
						$numreferringinputs++;
					}	
				
					if($numreferringinputs == 0) {
						#make sure these io records aren't linked to other analysis inputs (not being deleted)
						$dbh->do("delete from io_type where io_type_id=".$input_iotypeid);
						print "delete from io_type where io_type_id=".$input_iotypeid."<br>";
					}
					$dbh->do("delete from analysis_input where analysis_input_id=".$href1->{analysis_input_id});
					print "Deleted analysis input with ID: ".$href1->{analysis_input_id}."<br>";
				}
				print "Analysis was successfully deleted<br>";
			}

	#######################################################

			#get matrix_id referenced with the construct_id (may return >1)
			my $matrixsth = $dbh->prepare("select matrix_id from reg_seq_set where construct_id=".$sequenceid);
			$matrixsth->execute;
			while (my $matrixhref = $matrixsth->fetchrow_hashref) {
			
				#find out how many other reg_seq_set records refer to this matrix
				my $matrixsth2 = $dbh->prepare("select * from reg_seq_set where construct_id!=".$sequenceid."AND matrix_id=".$matrixhref->{matrix_id});
				$matrixsth2->execute;
		
				my $matrixcounter = 0;
				while(my $matrixhref2 = $matrixsth2->fetchrow_hashref) {
					$matrixcounter++;
				}
		
				#delete matrix and matrix info if construct being deleted is the only one referencing this matrix
				if($matrixcounter == 0) {
					$dbh->do("delete from matrix where matrix_id=".$matrixhref->{matrix_id}." AND project_id=".$projectid);
					print "Associated matrix info with ID ".$matrixhref->{matrix_id} . " has been deleted<br>";
				}
			}
			$dbh->do("delete from reg_seq_set where construct_id=".$sequenceid);

			print "Construct $sequenceid and associated data was successfully deleted<br>";
		} else {
			$dbh->do("delete from reg_seq where reg_seq_id=".$sequenceid);
			print "Sequence with ID ".$sequenceid." has been deleted<br>";
	
			$dbh->do("delete from dataset where reg_seq_id=".$sequenceid." AND project_id=".$projectid);
			print "Associated datasets have been deleted<br>";
	
			$dbh->do("delete from conserved_el where reg_seq_id=".$sequenceid." AND project_id=".$projectid);
			print "Associated conserved elements have been deleted<br>";
	
			$dbh->do("delete from reg_seq_construct where reg_seq_id=".$sequenceid." AND project_id=".$projectid);
			print "Associated constructs have been deleted<br>";
		
			$dbh->do("delete from anchor_reg_seq where reg_seq_id=".$sequenceid);
		
			## delete associated analysis entries
	
			## get analysis ids
			my $all=$pazar->get_analysis_by_regseq_id($sequenceid);
			foreach my $row (@$all) {
				my ($analysisid,$ainputid)=@$row;
					
				## use deleteanalysis.pl code##############################
		
				$dbh->do("delete from analysis where analysis_id=".$analysisid);
				print "Analysis with ID: ".$analysisid." deleted<br>";
		
				my $sth1 = $dbh->prepare("select analysis_input_id from analysis_input where analysis_id=$analysisid");
				$sth1->execute;
				while(my $href1 = $sth1->fetchrow_hashref) {
					my $sth3 = $dbh->prepare("select analysis_i_link_id,analysis_o_link_id from analysis_i_link where analysis_input_id=".$href1->{analysis_input_id});
					$sth3->execute;
					#iterate through analysis_i_link records
					while(my $href3 = $sth3->fetchrow_hashref) {
						#select the analysis output from the analysis_o_link
						my $sth4 = $dbh->prepare("select distinct(analysis_output_id) from analysis_o_link where analysis_i_link_id=".$href3->{analysis_i_link_id}." OR analysis_o_link_id=".$href3->{analysis_o_link_id}); # maybe too inclusive?
						$sth4->execute;
			
						#iterate over analysis output ids
						while(my $href4 = $sth4->fetchrow_hashref) {
							#figure out how many analysis_o_links refer to the analysis_output record
							my $olinks_sth = $dbh->prepare("select analysis_o_link_id from analysis_o_link where analysis_o_link_id!=".$href3->{analysis_o_link_id}." AND analysis_output_id=".$href4->{analysis_output_id});
							$olinks_sth->execute;
							my $numreferringolinks = 0;
							while(my $olinks_href = $olinks_sth->fetchrow_hashref) {
								$numreferringolinks++;
							}
		
							if($numreferringolinks == 0) {
								#select io_type_id from analysis_output
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
								while(my $outputs_href = $outputs_sth->fetchrow_hashref) {
									$numreferringoutputs++;
								}
			
								#delete the io_type	    
								if($numreferringoutputs == 0) {
									$dbh->do("delete from io_type where io_type_id=".$output_iotypeid);
								}
						
								#delete the analysis output
								$dbh->do("delete from analysis_output where analysis_output_id=".$href4->{analysis_output_id});
								print "Deleted analysis output with ID: ".$href4->{analysis_output_id}."<br>";
				
							}
						}
						
						#delete analysis_o_link
						$dbh->do("delete from analysis_o_link where analysis_o_link_id=".$href3->{analysis_o_link_id});
				
						#delete analysis_i_link
						$dbh->do("delete from analysis_i_link where analysis_i_link_id=".$href3->{analysis_i_link_id});
					}	       
					
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
					while(my $inputs_href = $inputs_sth->fetchrow_hashref) {
						$numreferringinputs++;
					}	
				
					if($numreferringinputs == 0) {
						#make sure these io records aren't linked to other analysis inputs (not being deleted)
						$dbh->do("delete from io_type where io_type_id=".$input_iotypeid);
						print "delete from io_type where io_type_id=".$input_iotypeid."<br>";
					}
					$dbh->do("delete from analysis_input where analysis_input_id=".$href1->{analysis_input_id});
					print "Deleted analysis input with ID: ".$href1->{analysis_input_id}."<br>";
				}
				print "Analysis was successfully deleted<br>";
			}
	#######################################################
	
			#get matrix_id referenced with the reg_seq_id (may return >1)
			my $matrixsth = $dbh->prepare("select matrix_id from reg_seq_set where reg_seq_id=".$sequenceid);
			$matrixsth->execute;
			while (my $matrixhref = $matrixsth->fetchrow_hashref) {
				#find out how many other reg_seq_set records refer to this matrix
				my $matrixsth2 = $dbh->prepare("select * from reg_seq_set where reg_seq_id!=".$sequenceid."AND matrix_id=".$matrixhref->{matrix_id});
				$matrixsth2->execute;
		
				my $matrixcounter = 0;
				while(my $matrixhref2 = $matrixsth2->fetchrow_hashref) {
					$matrixcounter++;
				}
		
				#delete matrix and matrix info if reg_seq being deleted is the only one referencing this matrix
				if($matrixcounter == 0) {
					$dbh->do("delete from matrix where matrix_id=".$matrixhref->{matrix_id}." AND project_id=".$projectid);
					print "Associated matrix info with ID ".$matrixhref->{matrix_id} . " has been deleted<br>";
				}
			}
			$dbh->do("delete from reg_seq_set where reg_seq_id=".$sequenceid);

			print "Sequence $sequenceid and associated data was successfully deleted<br>";
		}
	} else {
		#if no, display error
		print "You are not authorized to delete this sequence";
	}
} else {
    print "You must be logged in to delete this sequence";
}
