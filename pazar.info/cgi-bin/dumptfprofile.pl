#!/usr/bin/perl
use CGI ':standard'; 
use CGI::Carp qw(fatalsToBrowser);  

#download code taken from http://www.sitepoint.com/article/file-download-script-perl/2

my $tfname = param("tfname");

#if tfname is empty, probably because profile generated from multiple tfs
if ($tfname eq '')
{
	$tfname = 'custom_'.time();
}

#use profile name for file name
#$file_name = $$.time().".txt";
$file_name = $tfname . ".txt";
$files_location = "../tmp";


#print "Content-Type: text/html\n\n";
#get profile name supplied by user
my $userfilename = param("userfilename");

if ($userfilename ne '')
{
	$file_name = $userfilename . ".txt";
}

open($DLFILE, ">$files_location/$file_name") || Error('open', 'file');

#grab profile information
my $profilestring = param("matrix");
$profilestring =~ s/%20/\ /g;
$profilestring =~ s/br/\n/g;

#strip out A C G T
$profilestring =~ s/A  //g;
$profilestring =~ s/C  //g;
$profilestring =~ s/G  //g;
$profilestring =~ s/T  //g;

#generate timestamp
($sec,$min,$hour,$mday,$mon,$year,$wday,
$yday,$isdst)=localtime(time);
printf "%4d-%02d-%02d %02d:%02d:%02d\n",
$year+1900,$mon+1,$mday,$hour,$min,$sec;

#write to file for download

#header is tfname by default, or userfilename if given a value by user
my $header = ">".$tfname."_";

if ($userfilename ne '')
{
        $header = ">".$userfilename."_";
}

$header .= sprintf "%4d-%02d-%02d_%02d:%02d:%02d\n",
$year+1900,$mon+1,$mday,$hour,$min,$sec;

print $DLFILE $header;
print $DLFILE $profilestring;
close ($DLFILE) || Error ('close', 'file');

#set automatic download
open(DLFILE, "<../tmp/$file_name") || Error('open', 'file');  
@fileholder = <DLFILE>;  
close (DLFILE) || Error ('close', 'file');
print "Content-Type:application/x-download\n";  
print "Content-Disposition:attachment;filename=$file_name\n\n";
print @fileholder;


sub Error {
       print "Content-type: text/html\n\n";
   print "The server can't $_[0] the $_[1]: $! \n";
   exit;
 }
