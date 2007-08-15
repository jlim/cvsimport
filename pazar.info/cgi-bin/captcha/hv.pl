#!/usr/bin/perl


# ------------------------------ Human Verification ---------------------------------
# Copyright (c) 2004 - Sckriptke - Enrique F. Castañón
# Licensed under the GNU GPL.
# hv.cgi Version 0.1, 4 abril 2004
# -----------------------------------------------------------------------------------
# http://Skriptke.ltn.net/hv/
# -----------------------------------------------------------------------------------
#
# This script generate a verification image for validating forms.
# 
# Usage:
# 
# Insert in your form:
# <input type="text" name="code"> 
# <script language="JavaScript" src="http://www.yourdomain.com/scrip_path"></script>
# 
# This script generate two variables: hv_hash, hv_sess
#
# Insert similares lines en your script:
#
#    ...
#    use CGI;
#    $q = new CGI;
#    ...
#
#    use Digest::MD5 qw(md5_hex);
#    my $skey    = 'ChangeIt';         # password, same as this
#    my $code    = $q->param('code');  # user put code
#    my $session = $q->param('hv_sess');
#    my $hash    = $q->param('hv_hash');
#    my $expire  = 60*10;   # seconds expire session
#
#    if (time - $session > $expire ) {  
#      # Your error expitation code
#    }
#    if ($hash ne md5_hex($code,$skey,$session) ) {  
#      # Your error no valid hash code
#    }
#
# -------------------
# <script language="JavaScript" src="hv.cgi"></script>
# Show randon digits 4..6
# <script language="JavaScript" src="hv.cgi?7"></script>
# Show 7 digits


# ----------------- CONFIGURATION ----------------
my $skey       = 'ChangeIt';                     # Secret key. Change it. This same as your script
my $tmp_dir    = './tmp';                        # tmp directory
my $img_dir    = './img/filter6';                # image directory
my $top_url    = $ENV{'PAZAR_HTML'};    # top URL (http://www.yourdomain.con/)
my $cgi_url    = '/cgi-bin/captcha/hv.pl';         # path to script
my $referrer   = 0;                              # check referrer, 0 off - 1 on
my $max_age    = 10;                             # max time cache (0 = no cache)
my $max_digits = 12;                             # max digits
my $clear_tmp  = 1;                              # Clear tmp dir (1 yes, 0 no)
my $clear_rnd  = 200;                            # 1 > (rand $clear_rnd)
my $noise      = 22;                             # noise % image 
# ------------------------------------------------

use bmp;
use Digest::MD5  qw(md5_hex);

my ($type,$hash) = split(/-/,$ENV{'QUERY_STRING'});
my $expiration_time = scalar(gmtime(time()-$max_age));

if ( $hash ) {
  &show_image($type,$hash);
} else {
  $type = 4 + int rand 3 if ! $type; # entre 4 y 6 digitos
  $type = $max_digits if $type > $max_digits;
  &show_script($type);
}

exit;

sub show_script {
  my ($type) = @_;
  
  my @digits;
  for (1..$type) {
    $digits[$_] = int (rand 10);
  }
  my $sess = time;
  my $hash = md5_hex(join('',@digits),$skey,$sess);
  my $tmp_file = $tmp_dir.'/'.'0'.'-'.$hash.'.deleteme';
  
  open (TMP, ">$tmp_file");
  print TMP join('',@digits);
  close TMP; 
  
  print "Cache-control: max-age=$max_age\n";
  print "Cache-control: Private\n";
  print "Cache-control: no-cache\n" if !$max_age;
  print "Expires: $expiration_time GMT\n";
  print "Content-type: application/x-javascript\n\n";
  print 'document.write(\'';
  print '<input type="Hidden" name="hv_hash" value="',$hash,'">';
  print '<input type="Hidden" name="hv_sess" value="',$sess,'">';
  print '<img border="0" align="absmiddle" src="',$top_url.$cgi_url,'?','0','-',$hash,'">';
  print '\');'; 
  
} 

sub show_image {
  my ($type, $hash) = @_;
  
  &error() if ( ($ENV{'HTTP_REFERER'} !~ /$top_url/) && $referrer );
  
  my $tmp_file = $tmp_dir.'/'.$type.'-'.$hash.'.deleteme';
  
  open (TMP, "$tmp_file") || &error();
  my $digit = <TMP>;
  close TMP;

  my $image = new bmp();
  foreach (split(//,$digit)) {
    my $bmp = new bmp("$img_dir/$_.bmp");
    $image->addr($bmp);
  }
  $image->noise($noise);
  
  unlink($tmp_file);
  
  # limpia $tmp_dir de vez en cuando
  if ($clear_tmp) {
    if ( 1 > (rand $clear_rnd) ) {
      opendir(DIR,"$tmp_dir");  
      foreach (readdir(DIR)) {  
        if ( /^\d-.*\.deleteme$/ ) {
          my $last_mod = (stat ("$tmp_dir/".$_))[10];
          unlink("$tmp_dir/".$_) if ( (time - $last_mod) > (60*30) );
        }
          
      }  
      closedir DIR;
    }
  }
  
  print "Cache-control: max-age=$max_age\n";
  print "Cache-control: Private\n";
  print "Cache-control: no-cache\n" if !$max_age;
  print "Expires: $expiration_time GMT\n";  
  print "Content-type: image/bmp\n\n";
  #binmode STDOUT; # win32
  print $image->out();
  
}

sub error {
  print "Cache-control: max-age=0\n";
  print "Cache-control: no-cache\n";
  print "Content-type: image/bmp\n\n";
  open (IMAGE, "$img_dir/error.bmp");
  binmode IMAGE;
  while (defined ( my $c = getc(IMAGE) ) ) {
    print $c;
  }
  close IMAGE;
  
  exit;
}

