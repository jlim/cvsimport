#!/usr/bin/perl

use HTML::Template;
use CGI qw( :all);
#use CGI::Debug(report => everything, on => anything);
use pazar;

require '../getsession.pl';

my $query=new CGI;

my $docroot=$ENV{PAZARHTDOCSPATH}.'/sWI';
my $cgiroot=$ENV{SERVER_NAME} . $ENV{PAZARCGI}.'/sWI';
my $docpath=$ENV{SERVER_NAME}.'/sWI';

my %params = %{$query->Vars};
my $user=$info{user};
my $pass=$info{pass};
my $proj=$params{project};

die 'Not logged in' unless (($user)&&($pass));

my $auxdb=$params{auxDB};

my $pazar=new pazar(-drv=>'mysql',-dbname=>$ENV{PAZAR_name},-user=>$ENV{PAZAR_pubuser}, -pazar_user=>$user, -pazar_pass=>$pass,
                        -pass=>$ENV{PAZAR_pubpass}, -host=>$ENV{PAZAR_host}, -project=>$proj);

my @voc=qw(TF TFDB  family class modifications);

my (%tf,%tfdb,%class,%family,%modif,%seen,%interact);
my $input = $params{'submit'};
    print $query->header;
my $analysis=$params{'aname'};
unless ($info{userid}) {

    print $query->h3("An error occurred- not a valid user? If you believe this is an error e-mail us and describe the problem");

    exit();
}

my $alterpage=$input=~/CRE/?"$docroot/TFcentric_CRE.htm":"$docroot/SELEX.htm";
open (TFC,$alterpage)||die "Page $alterpage removed?";

while (my $buf=<TFC>) {
    $buf=~s/serverpath/$cgiroot/;
    $buf=~s/htpath/$docpath/;
    if (($buf=~/form/i)&&($buf=~/method/i)&&($buf=~/post/i)) {
	print $buf;
        &forward_args($query,\%params);        
    }
    else {
        if (($buf=~/interact0/)&&($buf!~/validateForm/)) {
            my $val=$params{interact0};
            $buf=~s/>/value=\"$val\">/;
        }
        if (($buf=~/reference/)&&($buf!~/validateForm/)) {
            my $val=$params{reference};
            $buf=~s/>/value=\"$val\">/;
        }
        print $buf;
        if ($buf=~m/Method \(select from list/) {
	        my @methods;
    	    push @methods,('',$pazar->get_method_names);
	        print $query->scrolling_list('methodname',\@methods,1,'true');
        }
    }
}
close TSC;
# print out the html tail template
my $template_tail = HTML::Template->new(filename => '../tail.tmpl');
print $template_tail->output;

exit();

sub forward_args {
my ($query,$params)=@_;
my %params=%$params;
my @noforward=qw(interact0 qualitative reference inttype interactscale methodname newmethod newmethoddesc sequence constructname artificialcomment);
foreach my $key (keys %params) {
    next if (grep(/$key/,@noforward));
    print $query->hidden($key,$params{$key}) unless ($key=~/new/);
}
 print $query->hidden('CREtype',$params{submit});

}
