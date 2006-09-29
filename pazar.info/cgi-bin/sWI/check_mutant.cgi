#!/usr/bin/perl

use CGI qw( :all);
#use CGI::Debug(report => everything, on => anything);

our $query=new CGI;
my %params = %{$query->Vars};

print $query->header;

my $mutseq=&get_mutseq(\%params);
print $query->h1("Mutant Sequence");
&print_seq($mutseq);
print $query->br;
print $query->br;
print $query->button(-name=>'close',
		     -value=>'Close window',
		     -onClick=>"window.close()");
print $query->br;
print $query->end_form;
exit();

sub get_mutseq {
    my ($params)=@_;
    my %params=%{$params};
    my $seq=lc($params{sequence});
    $params{mutdel}=~s/\s*//g;
    $params{pointmutation}=~s/\s*//g;
    if ($params{mutdel}=~/[^\d;-]/) {&print_deletion_error;}
    if ($params{pointmutation}=~/[^\d;-acgtACGT]/) {&print_pointmutation_error;}
###Handle Deletions
    my @deletions=split(/;/,$params{mutdel});
    my @delstart;
    my @delend;
    foreach my $del (@deletions) {
	my @dels=split(/-/,$del);
        if ($dels[0]=~/[^\d]/) {&print_deletion_error;}
        if ($dels[1]=~/[^\d]/) {&print_deletion_error;}
        unless ($dels[1]>$dels[0]) {&print_deletion_error;}
	push @delstart,$dels[0];
	push @delend,$dels[1];
    }
    unless (@delstart==@delend) {&print_deletion_error;}
    for ($i=0; $i<@delstart;$i++) {
	my $start=$delstart[$i]-1;
	my $length=$delend[$i]-$delstart[$i]+1;
	my $substr='X'x$length;
	substr($seq,$start,$length)=$substr;
    }
 
###Handle Point Mutations
    my @mutations=split(/;/,$params{pointmutation});
    my @nt;
    my @pos;
    foreach my $mut (@mutations) {
	my $nt=uc($mut);
	$nt=~s/\d//g;
	my $pos=$mut;
	$pos=~s/[a-zA-Z]//g;
        if ($nt=~/[^ACGT]/ || length($nt)!=1) {&print_pointmutation_error;}
        if ($pos=~/[^\d]/) {&print_pointmutation_error;}
	push @nt,$nt;
	push @pos,$pos;
    }
    unless (@nt==@pos) {&print_pointmutation_error;}
    for ($j=0; $j<@nt;$j++) {
	my $base=$pos[$j]-1;
	substr($seq,$base,1)=$nt[$j];
    }
    return $seq;
}

sub print_deletion_error {
    print "The format of your deletion description is not correct.\n";
    print "It should be [start nt]-[end nt] separated by semi-colons if there are more than one (e.g. 100-200;300-400). You also have to use the numbering scheme provided on the webpage besides the original sequence.\n";
    exit();
}

sub print_pointmutation_error {
    print "The format of your point mutation description is not correct.\n";
    print "It should be [position][mutant nt] separated by semi-colons if there are more than one (e.g. 5A;7T). You also have to use the numbering scheme provided on the webpage besides the original sequence.\n";
    exit();
}

sub print_seq {
    print "<p style=\"font-family: monospace;\">";
    my $seq=shift;
    $seq=~s/\s*//g;
#    print $seq;
    my $c = 10;
    my $nc = 5;
    my $space='&nbsp';
    my $l = length($seq);
    my $col1 = length($l);
    my @letters = split(//, $seq);
    if ($l>=1) {
	my $first="1";
	print &add_spaces(\$first, \$col1);
    }
    for (my $i=0; $i<=$#letters; $i++) {
	if ( (($i+1)/($c*$nc)) == int(($i+1)/($c*$nc)) ) {
	    print $letters[$i]."<br>";
	    unless ($i == $#letters) { my $s = $i+2; print &add_spaces(\$s, \$col1); } 
	} elsif ( (($i+1)/($c)) == int(($i+1)/($c)) ) {
	    print $letters[$i]." ";
	} else {
	    print $letters[$i];
	}
    }
    unless ( (($#letters+1)/($c*$nc)) == int(($#letters+1)/($c*$nc)) ) { print "<br>"; }
print "</p>";
}

sub add_spaces {
  my ($str, $l) = @_;
  my $long = ($$l - (length($$str)));
  my $final=$$str;
  for (my $i=0; $i<=$long; $i++) {
    $final.="&nbsp;";
  }
  return($final);
}
