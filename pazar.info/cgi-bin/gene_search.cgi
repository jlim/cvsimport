#!/usr/local/bin/perl

use lib '/space/usr/local/src/ensembl-36/ensembl/modules/';
use lib '/space/usr/local/src/bioperl-live/';

use strict;

use pazar;

use CGI qw(:standard);
use CGI::Carp qw(fatalsToBrowser);
use CGI::Debug( report => 'everything', on => 'anything' );

use constant DB_DRV  => 'mysql';
use constant DB_NAME => $ENV{PAZAR_name};
use constant DB_USER => $ENV{PAZAR_pubuser};
use constant DB_PASS => $ENV{PAZAR_pubpass};
use constant DB_HOST => $ENV{PAZAR_host};

my $get = new CGI;
my $action = $get->param('submit');

#initialize the html page
print $get->header("text/html");

#connect to the database
my $dbh = pazar->new( 
	  	   -host    =>    DB_HOST,
                   -user    =>    DB_USER,
                   -pass    =>    DB_PASS,
                   -dbname  =>    DB_NAME,
		   -drv     =>    DB_DRV);

print<<template_header;
<html>
<head>
<title>PAZAR Project Manager</title>
<script language="javascript">
<!--
function VersionNavigateur(Netscape, Explorer)
{
if ((navigator.appVersion.substring(0,3) >= Netscape && navigator.appName == 'Netscape') ||
(navigator.appVersion.substring(0,3) >= Explorer && navigator.appName.substring(0,9) == 'Microsoft'))
return true;
else return false;
}
//-->
</script>
<link type="text/css" rel="stylesheet" href="pazar.css"></head>
<body leftmargin="0" topmargin="0" bgcolor="#ffffff" marginheight="0" marginwidth="0">
<div align="left">
  <table border="0" cellpadding="0" cellspacing="0" height="100%" width="85%">
    <tbody><tr>
      <td valign="top">
      <table border="0" cellpadding="0" cellspacing="0" width="660">
        <tbody><tr>
          <td width="143">
          <img src="../images/pazar_01.gif" border="0" height="102" width="143"></td>
          <td width="517">
          <img src="../images/pazar_02.gif" border="0" height="102" width="517"></td>
        </tr>
      </tbody></table>
      <table border="0" cellpadding="0" cellspacing="0" width="100%" height="100%">
        <tbody><tr>
          <td align="center" background="../images/pazar_bg.gif" valign="top" width="143">
          <table border="0" cellpadding="0" cellspacing="0" width="100%">
            <tbody><tr>
              <td width="100%">
              <a href="" onmouseover="if (VersionNavigateur(3.0,4.0)) img1.src='../images/up_03.gif'" onmouseout="img1.src='../images/pazar_03.gif'"><img name="img1" src="../images/pazar_03.gif" onload="tempImg=new Image(0,0); tempImg.src='../images/up_03.gif'" border="0" height="51" width="143"></a></td>
            </tr>
            <tr>
              <td width="100%">
              <a href="http://www.pazar.info/cgi-bin/register.pl" onmouseover="if (VersionNavigateur(3.0,4.0)) img2.src='../images/up_05.gif'" onmouseout="img2.src='../images/pazar_05.gif'"><img name="img2" src="../images/pazar_05.gif" onload="tempImg=new Image(0,0); tempImg.src='../images/up_05.gif'" border="0" height="51" width="143"></a></td>
            </tr>
            <tr>
              <td width="100%">
              <a href="http://www.pazar.info/cgi-bin/editprojects.pl" onmouseover="if (VersionNavigateur(3.0,4.0)) img3.src='../images/up_06.gif'" onmouseout="img3.src='../images/pazar_06.gif'"><img name="img3" src="../images/pazar_06.gif" onload="tempImg=new Image(0,0); tempImg.src='../images/up_06.gif'" border="0" height="51" width="143"></a></td>
            </tr>
            <tr>
              <td width="100%">
              <a href="" onmouseover="if (VersionNavigateur(3.0,4.0)) img4.src='../images/up_07.gif'" onmouseout="img4.src='../images/pazar_07.gif'"><img name="img4" src="../images/pazar_07.gif" onload="tempImg=new Image(0,0); tempImg.src='../images/up_07.gif'" border="0" height="51" width="143"></a></td>
            </tr>
            <tr>
              <td width="100%">
              <a href="http://www.pazar.info/search.htm" onmouseover="if (VersionNavigateur(3.0,4.0)) img5.src='../images/up_08.gif'" onmouseout="img5.src='../images/pazar_08.gif'"><img name="img5" src="../images/pazar_08.gif" onload="tempImg=new Image(0,0); tempImg.src='../images/up_08.gif'" border="0" height="51" width="143"></a></td>
            </tr>
            <tr>
              <td width="100%">
              <img src="../images/pazar_09.gif" border="0" height="51" width="143"></td>
            </tr>
            <tr>
              <td width="100%">
              <a href="http://www.pazar.info/XML.htm" onmouseover="if (VersionNavigateur(3.0,4.0)) img6.src='../images/up_10.gif'" onmouseout="img6.src='../images/pazar_10.gif'"><img name="img6" src="../images/pazar_10.gif" onload="tempImg=new Image(0,0); tempImg.src='../images/up_10.gif'" border="0" height="51" width="143"></a></td>
            </tr>
            <tr>
              <td width="100%">
              <a href="" onmouseover="if (VersionNavigateur(3.0,4.0)) img7.src='../images/up_11.gif'" onmouseout="img7.src='../images/pazar_11.gif'"><img name="img7" src="../images/pazar_11.gif" onload="tempImg=new Image(0,0); tempImg.src='../images/up_11.gif'" border="0" height="51" width="143"></a></td>
            </tr>
            <tr>
              <td width="100%">
              <a href="" onmouseover="if (VersionNavigateur(3.0,4.0)) img8.src='../images/up_12.gif'" onmouseout="img8.src='../images/pazar_12.gif'"><img name="img8" src="../images/pazar_12.gif" onload="tempImg=new Image(0,0); tempImg.src='../images/up_12.gif'" border="0" height="51" width="143"></a></td>
            </tr>
          </tbody></table>
          </td>
          <td align="left" valign="top">
          <font><br>
template_header


my $gene = $get->param('geneID');

if (!$gene) {
    print "<big>Please provide a gene ID!</big>\n";
} else {
 
my $reg_seqs = $dbh->get_psms_by_accn($gene);
print "$reg_seqs\n";

if (!$reg_seqs) {
    print "<big>No regulatory sequence was found for this gene!</big>\n";
} else {
foreach my $psm (@{$reg_seqs}) {
		print $psm->id,"\t",$psm->start,"\t",$psm->end,"\t",$psm->seq,"\n";
}
}}
print "</td></tr></tbody></table></center></body></html>";




sub select {

    my ($dbh, $sql) = @_;
    my $sth=$dbh->prepare($sql);
    $sth->execute or die "$dbh->errstr\n";
    return $sth;
}
