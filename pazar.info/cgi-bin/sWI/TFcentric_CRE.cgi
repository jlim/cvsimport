#!/usr/bin/perl


use CGI qw( :all);
#use CGI::Debug(report => everything, on => anything);
use pazar;

my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};
my $pazarhtdocspath = $ENV{PAZARHTDOCSPATH};

require "$pazarcgipath/getsession.pl";

my $query=new CGI;

my $docroot=$pazarhtdocspath.'/sWI';
my $cgiroot=$pazar_cgi.'/sWI';
my $docpath=$pazar_html.'/sWI';

my %params = %{$query->Vars};
my $user=$info{user};
my $pass=$info{pass};
my $proj=$params{project};

print $query->header;

unless (($user)&&($pass)) {
    print $query->h3('Not logged in');
    exit;
}

my $auxdb=$params{auxDB};

my $pazar=new pazar(-drv=>$ENV{PAZAR_drv},-dbname=>$ENV{PAZAR_name},-user=>$ENV{PAZAR_pubuser}, -pazar_user=>$user, -pazar_pass=>$pass,
                        -pass=>$ENV{PAZAR_pubpass}, -host=>$ENV{PAZAR_host}, -project=>$proj);

my @voc=qw(TF TFDB  family class modifications);

my (%tf,%tfdb,%class,%family,%modif,%seen,%interact);
my $input = $params{'submit'};

my $analysis=$params{'aname'};
unless ($info{userid}) {

    print $query->h3("An error occurred- not a valid user? If you believe this is an error e-mail us and describe the problem");

    exit();
}

my @cell_names=$pazar->get_all_cell_names;
my @tissue_names=$pazar->get_all_tissue_names;

my $alterpage=$input=~/CRE/?"$docroot/TFcentric_CRE.htm":"$docroot/SELEX.htm";
open (TFC,$alterpage)||print $query->h3("Page $alterpage removed?");

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
        if ($buf=~/<p>Method Name/) {
	    my @methods=$pazar->get_method_names;
    	    my @sorted_methods = sort @methods;
	    unshift @sorted_methods, 'Select from existing methods';
	    print $query->scrolling_list('methodname',\@sorted_methods,1,'true');
        }
        if ($buf=~/<input name=\"cell\" type=\"text\" id=\"cell\"/i && @cell_names) {
	    my @sorted_cells = sort @cell_names;
	    unshift @sorted_cells, 'Select from existing cell names';
	    print "<b>  OR  </b>";
	    print $query->scrolling_list('mycell',\@sorted_cells,1,'true');
	}
        if ($buf=~/<input name=\"tissue\" type=\"text\" id=\"tissue\"/i && @tissue_names) {
	    my @sorted_tissues = sort @tissue_names;
	    unshift @sorted_tissues, 'Select from existing tissue names';
	    print "<b>  OR  </b>";
	    print $query->scrolling_list('mytissue',\@sorted_tissues,1,'true');
	}

    }
}
close TSC;
exit();

sub forward_args {
my ($query,$params)=@_;
my %params=%$params;
my @noforward=qw(interact0 qualitative reference inttype interactscale methodname newmethod newmethoddesc sequence constructname artificialcomment CREtype);
foreach my $key (keys %params) {
    next if (grep(/$key/,@noforward));
    print $query->hidden($key,$params{$key}) unless ($key=~/new/);
}
 print $query->hidden('CREtype',$params{submit});

}
