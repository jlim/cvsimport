#!/usr/bin/perl

use DBI;
use Crypt::Imail;
use CGI::Session;
use CGI qw( :all);
use HTML::Template;

# use CGI::Debug( report => "everything", on => "anything" );

my $query = new CGI;
my %params = %{$query->Vars};

my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};
my $dbname = $ENV{PAZAR_name};
my $dbhost = $ENV{PAZAR_host};
my $DBUSER = $ENV{PAZAR_adminuser};
my $DBPASS = $ENV{PAZAR_adminpass};
my $DBPORT = $ENV{PAZAR_port}||3306;
my $DBDRV = $ENV{PAZAR_drv};
my $DBURL = qq{DBI:$DBDRV:dbname=$dbname;host=$dbhost;port=$DBPORT};
my $temptail = HTML::Template->new(filename => "$pazarcgipath/tail.tmpl");

my $session = new CGI::Session("driver:File", undef, {Directory=>"/tmp"});
$session->expire('+4h');

my $dbh = DBI->connect($DBURL,$DBUSER,$DBPASS);
my $im = Crypt::Imail->new();
my $encrypted_pass = $im->encrypt($params{username}, $params{password}); 
my $chkh = $dbh->prepare(qq{SELECT user_id, aff, first_name, last_name FROM users WHERE username=? AND password=?});
$chkh->execute($params{username},$encrypted_pass);
my ($userid,$aff,$first,$last) = $chkh->fetchrow_array;

if ($userid ne "") {
    my %info = (
    	user => $params{username},
    	pass => $params{password},
    	userid => $userid,
    	aff => $aff,
    	first => $first,
    	last => $last);
    my @projids = ();
	my $sth = $dbh->prepare(qq{SELECT project_id FROM user_project WHERE user_id=?});
	$sth->execute($userid);
	while(my @results = $sth->fetchrow_array) {
		push(@projids,$results[0]);
	}
    $session->param("info", \%info);
    $session->param("projects", \@projids);
    $cookie = $query->cookie(
    	-name=>"PAZAR_COOKIE",
		-value=>$session->id,
		-expires=>"",
		-path=>"/");
	print $query->header(-cookie=>$cookie);
	my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");
	$template->param(TITLE => "Sign in | PAZAR");
	$template->param(PAZAR_HTML => $pazar_html);
	$template->param(PAZAR_CGI => $pazar_cgi);
	if ($loggedin eq "true") {
		$template->param(LOGOUT => qq{<span class="b">You are signed in as $info{first} $info{last}.</span> <a href="$pazar_cgi/logout.pl" class="b">Sign out</a>});
	} else {
		$template->param(LOGOUT => qq{<a href="$pazar_cgi/login.pl"><span class="b">Sign in</span></a>});
	}
	print $template->output;
    if ($params{project} eq "true") {
		print qq{
			<form name="editprojects" method="POST" action="$pazar_cgi/editprojects.pl">
				<input type="hidden" name="username">      
				<input type="hidden" name="password">
				<input type="hidden" name="mode" value="login">
			</form>
			<script language="JavaScript">
				document.editprojects.submit();
			</script>};
    } elsif ($params{submission} eq "true") {
		print qq{
			<form name="submission" method="POST" action="$pazar_cgi/sWI/entry.pl">
				<input type="hidden" name="username">      
				<input type="hidden" name="password">
				<input type="hidden" name="mode" value="login">
			</form>
			<script language="JavaScript">
				document.submission.submit();
			</script>};
    } else {
		print qq{
			<script language="JavaScript">
				document.location.href="$pazar_cgi/index.pl";
			</script>};
	}
} else {
	my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");
	$template->param(TITLE => "Sign in | PAZAR");
	$template->param(PAZAR_HTML => $pazar_html);
	$template->param(PAZAR_CGI => $pazar_cgi);
	if ($loggedin eq "true") {
		$template->param(LOGOUT => qq{<span class="b">You are signed in as $info{first} $info{last}.</span> <a href="$pazar_cgi/logout.pl" class="b">Sign out</a>});
	} else {
		$template->param(LOGOUT => qq{<a href="$pazar_cgi/login.pl"><span class="b">Sign in</span></a>});
	}

	print "Content-Type: text/html\n\n", $template->output;
    print qq{<div class="emp">Sign in unsuccessful. Please try again.</div>};	
    print qq{
		<h1>Sign in</h1>
		<div class="p10bo">
			<form method="POST" action="$pazar_cgi/dologin.pl">
				<table cellspacing="0" cellpadding="0" border="0">
					<tbody>
						<tr>
							<td class="p10ro p5bo b">Email</td>
							<td class="p10ro p5bo"><input type="text" name="username"></td>
						</tr><tr>
							<td class="p10ro p5bo b">Password</td>
							<td class="p10ro p5bo"><input type="password" name="password"></td>
						</tr><tr>
							<td class="p10ro p5bo">&nbsp;</td>
							<td class="p10ro p5bo"><input type="submit" name="login" value="Sign in"></td>
						</tr>
					</tbody>
				</table>
			</form>
		</div>
		<div class="b">New User? <a href="$pazar_cgi/register.pl" class="b">Click here to register.</a></div>
		<div class="b">Forgotten password? <a href="mailto:pazar\@cmmt.ubc.ca">Click here to request a new password.</a></div>
	};
}
print $temptail->output;
