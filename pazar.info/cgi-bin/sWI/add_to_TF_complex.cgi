#!/usr/bin/perl

use CGI qw( :all);
use CGI::Debug(report => everything, on => anything);

require '../getsession.pl';

my $docroot=$ENV{PAZARHTDOCSPATH}.'/sWI';
my $cgiroot=$ENV{SERVER_NAME} . $ENV{PAZARCGI}.'/sWI';
my $cgipath=$ENV{PAZARCGIPATH}.'/sWI';

#SYNOPSYS: Addin TF that interact with the target sequence and each other to produce a certain effect
my $selfpage="$docroot/TF_complex.htm";

my @voc=qw(TF TFDB  family class);
my $query=new CGI;
my %params = %{$query->Vars};
print $query->header;
my (%tf,%tfdb,%class,%family,%modif,%seen,%interact);
my $input = $params{'submit'};
my $userid=$info{userid};
my $analysis=$params{'aname'};
unless ($params{'file'} ) {
	$params{'file'} = $userid ."\_".$analysis . ".TF.tmp";
}
my $file=$params{'file'}!~/tmp$/?$params{'file'}.'.'.$params{'type'}.'.tmp':$params{'file'};#unique file name
my $tmpdir="$cgipath/tmp";
chdir($tmpdir);
mkdir($userid) unless (-e $userid);
chdir($userid);
unlink ($file) if (-e $file);

SUBMIT: {
if ($input eq 'cancel') { if (-e $file) {unlink($file);} exit();}#Remove the file!
if ($input eq 'Add') { last SUBMIT;} #Do what you normally do (add and write)
if ($input eq 'Done') { &add_to_file($file,\%params,$query); exit();}#JUst in case we decide we need more stuff to add
}


open (SELF,$selfpage)||die;

my $i=grep(/TFDB/,keys %params);
my $k=1;
my $next=$i;
#$next=$i+1 if ($i>0);


#print "Next is : $next i is $i";
foreach my $key (keys %params) {
            next if ($key eq 'aname')||($key eq 'file')||($key=~/TFcomplex/)||($key=~/modification/);
            #print $key,"__";
            if (($key=~/TF\d/i)||($key=~/TF$/i)) { my $id=$key; $id=~s/\D//g; $id=$id=~/d/?$id:$next; $tf{$id}=$params{$key};}
            if ($key=~/TFDB/i) { my $id=$key; $id=~s/\D//g; $id=$id=~/d/?$id:$next; $tfdb{$id}=$params{$key}; }
            if ($key=~/class/i) { my $id=$key; $id=~s/\D//g; $id=$id=~/d/?$id:$next; $class{$id}=$params{$key}; }
            if ($key=~/family/i) { my $id=$key; $id=~s/\D//g; $id=$id=~/d/?$id:$next; $family{$id}=$params{$key}; }
            if ($key=~/interact/i) { my $id=$key; $id=~s/\D//g; $id=$id=~/d/?$id:$next; $interact{$id}=$params{$key}; }
 #           if ($key=~/modific/i) { my $id=$key; $id=~s/\D//g; $id=$id=~/\d/?$id:$next; $modif{$id}=$params{$key};  }
            
            print "\<input name=\"$key\" type=\"hidden\" value=\"$params{$key}\"\>"; 
}
my $started=1;
while (my $buf=<SELF>) {
    $buf=~s/serverpath/$cgiroot/;
    if (($buf=~/modifications/i)&&($params{modifications})) {
        $buf=~s/name/value=\"$params{modifications}\" name/;
    }
    if (($buf=~/TFcomplex/i)&&($params{TFcomplex})) {
        $buf=~s/name/value=\"$params{TFcomplex}\" name/;
    }
    print $buf;
	if ($buf=~/body/i) {$seen{body}++;}
	if ($buf=~/\<form/i) {$seen{form}++;} 
	if ($buf=~/modifications/i) {$seen{modif}++;} 
	if (($buf=~/\<hr\>/)&&($seen{modif})&&($started)) { 
        $started=0;
		print "\<input name=\"aname\" type=\"hidden\" value=\"$analysis\"\>";
		print "\<input name=\"file\" type=\"hidden\" value=\"$file\"\>";
#        for my $j (1..$i) {
#            my $k1='TF' . $j;
#	        my $k2='TFDB' . $j;
#	        my $sel=uc($params{$k2});
        print $query->br;
        
        foreach my $k (1..$i) {
            print "Added complex member $k",$query->br;
            foreach my $key (@voc) {
                my $addon;
                $addon=$k-1 if ($i>0);
                my $ukey=$key . ($addon?$addon:'');
                my $lkey=$key . $k;
                #print "UKEY $ukey:";
                my $val;
                #print "k is $k";
                VAL: {
                    if ($key eq 'TF') {$val=$tf{$k}; last VAL;}
                    if ($key eq 'TFDB') {$val=$tfdb{$k}; last VAL;}
                    if ($key eq 'class') {$val=$class{$k}; last VAL;}
                    if ($key eq 'family') {$val=$family{$k}; last VAL;}
                    if ($key eq 'interact') {$val=$interact{$k}; last VAL;}
                   # if ($key eq 'modifications') {$val=$modif{$k}; next VAL;}
                }
                print $lkey,' ',$query->textfield (-label=>$lkey,-name=>$lkey,-size=>16, -value=>$val), $query->br; 
            }
            print $query->hr;
        }
		next;
	}
    
}
	#if ($buf=~/opener/) {$buf=~s/opener/opener\.opener/;}	
=obs
	if (($buf=~/opener/) && ($buf=~/TF/)){
		next if ($seen{opener});
		foreach my $j (1..$i) {
			$seen{opener}++;
			my $k1='TF' . $j;
			my $k2='TFDB' . $j;
			print "opener\.$k1=document\.TF\.$k1; opener\.$k2=document\.TF\.$k2;\n";
		}
	}
	else {
		if ($buf=~/onload/i) { my $ind=$i+1; my $focus="TF$ind"; $buf=~s/TF\d+/$focus/;}
		print $buf;
	}
}

foreach my $j (1..$i) {
	my %sel=('nm'=>'','ensembl_transcript'=>'','ensembl'=>'','locuslink'=>'','swissprot'=>'','accn'=>'');		
	my $k1='TF' . $j;
	my $k2='TFDB' . $j;
	my $sel=uc($params{$k2});
	$sel{$sel}=' selected';
	print $query->textfield (-name=>$k1,-default=>$pos{$k1},-size=>5); 
	print " <p>mutated to <select name=\"$k2\"  > <option value=\"A\" $sel{A}>A<\/option>
	<option value=\"C\" $sel{C}>C<\/option>  <option value=\"G\" $sel{G}>G<\/option> 
	<option value=\"T\" $sel{T}>T<\/option> <\/select>  <\/p>\n";
	print $query->br;
}	

my $ind=$i+1;
my $k1="TF$ind";
my $k2="TFDB$ind";
	print $query->textfield (-name=>$k1,-size=>5); 
	print $query->textfield (-name=>$k2,-size=>5); 
	print $query->br;
	print " <p>TFDB<select name=\"$k2\">  <option value=\"A\">A<\/option> 
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
=cut
exit;


sub add_to_file {
my ($file,$params,$query)=@_;

#Clean first just in case

my %params=%{$params};

open (POS,">$file")|| die "Can't open $file";
my @numbered=qw(TF TFDB interact class family);
foreach my $mp(keys %params) {
my $key=$mp;
    $key .='0' if ((grep (/\b$mp\b/,@numbered))&&($mp!~/\d/));
	print POS "$key\t",$params{$mp},"\n" unless ($mp=~/file/); 
}
close POS;
print $query->header;
print "\<body onload\=\"window.close()\"\>";
exit;
}
