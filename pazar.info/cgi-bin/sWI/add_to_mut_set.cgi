#!/usr/bin/perl

use CGI qw( :all);
use CGI::Debug;#(report => everything, on => anything);

require '../getsession.pl';

my $docroot=$ENV{PAZARHTDOCSPATH}.'/sWI';
my $cgiroot=$ENV{SERVER_NAME} . $ENV{PAZARCGI}.'/sWI';
my $cgipath=$ENV{PAZARCGIPATH}.'/sWI';
my $selfpage="$docroot/mutation.htm";

my $query=new CGI;
my %params = %{$query->Vars};
my $input = $params{'submit'};
my $userid=$info{userid};
my $analysis=$params{'aname'};
unless ($params{'file'} ) {
	$params{'file'} = $user ."\_".$analysis . ".pos.tmp";
}
my $file=$params{'file'};
my $tmpdir="$cgipath/tmp";
chdir($tmpdir);
mkdir($userid) unless (-e $userid);
chdir $userid;
unlink ($file) if (-e $file);

SUBMIT: {
if ($input eq 'cancel') { if (-e $file) {unlink($file);} exit();}#Remove the file!
if ($input eq 'Add') { last SUBMIT;} #Do what you normally do (add and write
if ($input eq 'Done') { &add_to_file($file,\%params,$query); exit();}#JUst in case we decide we need more stuff to add
}


open (SELF,$selfpage)||die;
my (%pos,%base,%seen);
my $i=grep(/mpos/,keys %params);
foreach my $key (keys %params) {
	if ($key=~/mpos/) {
		my $key=~s/\D//g;
		my $k1=('mpos' . "$key");
		my $k2=('mutbase'."$key");
		$pos{$k1}=$params{$k1};
		$base{$k2}=uc($params{$k2});
	}
}
print $query->header;
while (my $buf=<SELF>) {
    $buf=~s/serverpath/$cgiroot/;
	if ($buf=~/body/i) {$seen{body}++;}
	if ($buf=~/\<form/i) {  
		print $buf;
		print "\<input name=\"userid\" type=\"hidden\" value=\"$userid\"\>"; 
		print "\<input name=\"aname\" type=\"hidden\" value=\"$analysis\"\>";
		print "\<input name=\"file\" type=\"hidden\" value=\"$file\"\>";
		next;
	}
	if ($buf=~/mutation position in element/i) {
		last;
	}
	#if ($buf=~/opener/) {$buf=~s/opener/opener\.opener/;}	
	if (($buf=~/opener/) && (($buf=~/mpos/)||($buf=~/mutbase/))){
		next if ($seen{opener});
		foreach my $j (1..$i) {
			$seen{opener}++;
			my $k1='mpos' . $j;
			my $k2='mutbase' . $j;
			print "opener\.$k1=document\.MUT\.$k1; opener\.$k2=document\.MUT\.$k2;\n";
		}
	}
	else {
		if ($buf=~/onload/i) { my $ind=$i+1; my $focus="mpos$ind"; $buf=~s/mpos\d+/$focus/;}
		print $buf;
	}
}
foreach my $j (1..$i) {
	my %sel=('A'=>'','C'=>'','G'=>'','T'=>'');		
	my $k1='mpos' . $j;
	my $k2='mutbase' . $j;
	my $sel=uc($params{$k2});
	$sel{$sel}=' selected';
	print $query->textfield (-name=>$k1,-default=>$pos{$k1},-size=>5); 
	print " <p>mutated to <select name=\"$k2\"  > <option value=\"A\" $sel{A}>A<\/option>
	<option value=\"C\" $sel{C}>C<\/option>  <option value=\"G\" $sel{G}>G<\/option> 
	<option value=\"T\" $sel{T}>T<\/option> <\/select>  <\/p>\n";
	print $query->br;
}	
my $ind=$i+1;
my $k1="mpos$ind";
my $k2="mutbase$ind";
	print $query->textfield (-name=>$k1,-size=>5); 
	print $query->br;
	print " <p>mutated to <select name=\"$k2\">  <option value=\"A\">A<\/option> 
	<option value=\"C\">C<\/option>  <option value=\"G\">G<\/option>  
	<option value=\"T\">T<\/option> <\/select>  <\/p>\n";
	print $query->br;
print " </p>  <hr><input value=\"Add more to this set\" name=\"Add\" type=\"submit\"><br>\n
	<p> <input name=\"submit\" id=\"submit\"  value=\"Done\"
type=\"submit\">\n
	<input onclick=\"javascript:window\.close();\" name=\"cancel\" id=\"cancel\" value=\"Cancel\" type=\"Submit\">\n
	</p></form>
</body> </html>\n";	
close SELF;
exit;


sub add_to_file {
my ($file,$params,$query)=@_;

#Clean first just in case

my %params=%{$params};

unless ($file) {die "Can't open $file";}
open (POS,">$file")||die ;
my @all=grep(/mpos/,keys %params);
foreach my $mp(@all) {
	my $i=$mp;
	$i=~s/\D//g;
	my $k1='mpos' . $i;
	my $k2='mutbase' . $i;
	my $v1=$params{$k1};
	my $v2=$params{$k2};
	print POS "$k1\t$v1\t$k2\t$v2\n";
}
close POS;
print $query->header;
print "\<body onload\=\"window.close()\"\>";
exit;
}
