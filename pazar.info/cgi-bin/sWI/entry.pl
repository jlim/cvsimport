#!/usr/bin/perl

use HTML::Template;
use CGI qw( :all);
use pazar;

# use CGI::Debug(report => "everything", on => "anything");

my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};
my $pazarhtdocspath = $ENV{PAZARHTDOCSPATH};

my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");
my $temptail = HTML::Template->new(filename => "$pazarcgipath/tail.tmpl");
$template->param(ONLOAD_FUNCTION => "resetMenu();");
$template->param(TITLE => "Submit data | PAZAR");
$template->param(PAZAR_HTML => $pazar_html);
$template->param(PAZAR_CGI => $pazar_cgi);
$template->param(JAVASCRIPT_FUNCTION => qq{ });


require "$pazarcgipath/getsession.pl";
if ($loggedin eq "true") {
	$template->param(LOGOUT => qq{<span class="b">You are signed in as $info{first} $info{last}.</span> 
	<a href="$pazar_cgi/logout.pl" class="b">Sign out</a>});
} else {
	$template->param(LOGOUT => qq{<a href="$pazar_cgi/login.pl"><span class="b">Sign in</span></a>});
}

print "Content-Type: text/html\n\n", $template->output;
my $docroot = $pazarhtdocspath . "/sWI";
my $cgiroot = $pazar_cgi . "/sWI";
my $query = new CGI;
my %params = %{$query->Vars};
my $npage = "$docroot/entryform1.htm";

if ($loggedin eq "true") {
	my $pazar = pazar->new( 
		-host => $ENV{PAZAR_host},
		-user => $ENV{PAZAR_pubuser},
		-pass => $ENV{PAZAR_pubpass},
		-dbname => $ENV{PAZAR_name},
		-drv => $ENV{PAZAR_drv});
	my @projnames;
	foreach my $pid (@projids) {
		my $sth = $pazar->prepare(qq{SELECT project_name FROM project WHERE project_id=?});
		$sth->execute($pid);
		my $result = $sth->fetchrow_array;
		if ($result ne "") {
			push @projnames, $result;
		}
	}
	my $scrl = $query->scrolling_list("project",\@projnames,1,"true");
	print qq{
		<h1>Submit data</h1>
		<div class="p20lo p20bo">
			<p class="b">Some hints</p>
			<ul>
				<li>You can use this interface to enter data to an already existing project or to a new one. For the latter, you just have to create a new project below and it will be added in your list of existing projects.</li>
				<li><span class="b">&quot;TF centric submissions&quot;</span> are based on a specific TF from which you want to annotate binding sites. <span class="b">&quot;CRE centric submissions&quot;</span> are annotations of a cis regulatory element from which you have evidence of a role in gene regulation (binding or other).</li>
			</ul>
		</div>
		<h2>Submit to existing project</h2>
		<div class="p20lo p20bo">
			<form action="" method="POST" name="F1">
				<div class="b">Submit to project: $scrl with 
					<input name="TFcentric" type="submit" id="TFcentric" onClick="MM_validateForm('project','','R'); return setCountEntryPl(1); return document.MM_returnValue" value="TF centric submissions"> or <input name="CREcentric" type="submit" id="CREcentric" value="CRE centric submissions" onClick="MM_validateForm('project','','R'); return setCountEntryPl(0); return document.MM_returnValue">
				</div>
			</form>
		</div>};

# 	open (NPAGE,$npage) || die;
# 	while (my $buf = <NPAGE>) {
# 		if ($buf =~ /action/i) {
# 			$buf =~ s/serverpath/$cgiroot/i;
# 		}
# 		print $buf;
# 		if ($buf =~ /<hr><br><p><b>Submit to Project/i) {
# 			print $query->scrolling_list("project",\@projnames,1,"true");
# 		}
# 	}

	print qq{<div class="emp">$params{statusmsg}</div>} if $params{statusmsg};
	print qq{
		<h2>Create a new project</h2>
		<div class="p20lo">
		<form name="createprojectform" method="post" action="$pazar_cgi/editprojects.pl">
			<input type="hidden" name="mode" value="add">
			<input type="hidden" name="uid" value="$info{userid}">
			<input type="hidden" name="username" value="$info{user}">
			<input type="hidden" name="password" value="$info{password}">
			<input type="hidden" name="submission" value="true">
			<table class="w470 br-a" cellspacing="0" cellpadding="0"><tbody>
				<tr class="bg-lg">
					<td class="tl p5 b w160">Project name</td>
					<td class="tl p5"><input type="text" name="projname" maxlength="20" class="w300"></td>
				</tr><tr>
					<td class="tl p5 b">Status</td>
					<td class="tl p5">
						<select name="projstatus">
							<option name="restricted" value="restricted">restricted</option>
							<option name="published" value="published">published</option>
							<option name="open" value="open">open</option>
						</select>
					</td>
				</tr><tr class="bg-lg">
					<td class="tl p5 b">Description</td>
					<td class="tl p5"><textarea name="projdesc" class="w300" rows="10"></textarea></td>
				</tr><tr>
					<td class="tl p5 b">Administrator password</td>
					<td class="tl p5"><input type="password" name="projpass" maxlength="20" class="w300"></td>
				</tr><tr class="bg-lg">
					<td class="tl p5 b">Re-enter password</td>
					<td class="tl p5"><input type="password" name="projpasscheck" maxlength="20" class="w300"></td>
				</tr>
			</tbody></table>
			<div class="p5to"><input type="button" onClick="verifyProjectCreate();" value="Create new project"></div>
		</form>
		</div>};
} else {
	print qq{
		<h1>Submit data</h1>
		<div class="emp">Please <a href="$pazar_cgi/login.pl">sign in</a> to submit data.</div>
	};
}
print $temptail->output;
