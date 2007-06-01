#!/usr/bin/perl -w

use strict;
use DBI;

my $dbname = $ENV{PAZAR_name};
my $dbhost = $ENV{PAZAR_host};

my $DBUSER = $ENV{PAZAR_adminuser};
my $DBPASS = $ENV{PAZAR_adminpass};
my $DBDRV  = $ENV{PAZAR_drv};
my $DBURL  = "DBI:$DBDRV:dbname=$dbname;host=$dbhost";

my $dbh = DBI->connect($DBURL,$DBUSER,$DBPASS)
    or die "Can't connect to pazar database";

my $project=shift;

#select project_id
my $sth=$dbh->prepare("select project_id from project where project_name=?")||die;
$sth->execute($project);
my $project_id = $sth->fetchrow_array;

#select all ids from project specific records
$sth=$dbh->prepare("show tables");
$sth->execute()||die;
my %table_ids;
my @tables;
while (my $table  = $sth->fetchrow_array) {
    my $table_id = $table."_id";
    my $clh=$dbh->prepare("desc $table");
    $clh->execute()||die;
    my $i=0;
    while (my $col  = $clh->fetchrow_hashref) {
	if ($col->{Field} eq 'project_id') {
	    $i=1;
	}
    }
    if ($i == 1) {
	my $prh=$dbh->prepare("select $table_id from $table where project_id=?")||die;
	$prh->execute($project_id)||die;
	while (my ($id)  = $prh->fetchrow_array) {
	    push (@{$table_ids{$table}},$id);
	}
	my $delh=$dbh->prepare("delete from $table where project_id=?");
        $delh->execute($project_id)||die;
    } else {
	push (@tables, $table);
    }
}

foreach (@tables) {
    if ($_ eq 'analysis_i_link') {
	foreach my $tbl_id (@{$table_ids{'analysis_input'}}) {
	    my $delh=$dbh->prepare("delete from analysis_i_link where analysis_input_id=?");
	    $delh->execute($tbl_id)||die;
	}
    } elsif ($_ eq 'analysis_o_link') {
	foreach my $tbl_id (@{$table_ids{'analysis_output'}}) {
	    my $delh=$dbh->prepare("delete from analysis_o_link where analysis_output_id=?");
	    $delh->execute($tbl_id)||die;
	}
    } elsif ($_ eq 'anchor_reg_seq') {
	foreach my $tbl_id (@{$table_ids{'reg_seq'}}) {
	    my $delh=$dbh->prepare("delete from anchor_reg_seq where reg_seq_id=?");
	    $delh->execute($tbl_id)||die;
	}
    } elsif ($_ eq 'matrix_info') {
	foreach my $tbl_id (@{$table_ids{'matrix'}}) {
	    my $delh=$dbh->prepare("delete from matrix_info where matrix_id=?");
	    $delh->execute($tbl_id)||die;
	}
    } elsif ($_ eq 'mutation') {
	foreach my $tbl_id (@{$table_ids{'mutation_set'}}) {
	    my $delh=$dbh->prepare("delete from mutation where mutation_set_id=?");
	    $delh->execute($tbl_id)||die;
	}
    } elsif ($_ eq 'reg_seq_set') {
	foreach my $tbl_id (@{$table_ids{'matrix'}}) {
	    my $delh=$dbh->prepare("delete from reg_seq_set where matrix_id=?");
	    $delh->execute($tbl_id)||die;
	}
    } elsif ($_ eq 'tf_complex') {
	foreach my $tbl_id (@{$table_ids{'funct_tf'}}) {
	    my $delh=$dbh->prepare("delete from tf_complex where funct_tf_id=?");
	    $delh->execute($tbl_id)||die;
	}
    }
}


    
