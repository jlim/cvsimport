#!/usr/bin/perl

use DBI;
use Crypt::Imail;
use CGI::Session;
use CGI qw( :all);
use HTML::Template;
use Mail::Mailer;

# use CGI::Debug(report => "everything", on => "anything");

my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};

my $query = new CGI;
my %params = %{$query->Vars};

my $dbname = $ENV{PAZAR_name};
my $dbhost = $ENV{PAZAR_host};
my $DBUSER = $ENV{PAZAR_adminuser};
my $DBPASS = $ENV{PAZAR_adminpass};
my $DBPORT = $ENV{PAZAR_port} || 3306;
my $DBDRV = $ENV{PAZAR_drv};
my $DBURL = "DBI:$DBDRV:dbname=$dbname;host=$dbhost;port=$DBPORT";
my $dbh = DBI->connect($DBURL,$DBUSER,$DBPASS);

my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");
my $temptail = HTML::Template->new(filename => "$pazarcgipath/tail.tmpl");
$template->param(TITLE => "My projects | PAZAR");
$template->param(PAZAR_HTML => $pazar_html);
$template->param(PAZAR_CGI => $pazar_cgi);
$template->param(JAVASCRIPT_FUNCTION => q{ });

require "$pazarcgipath/getsession.pl";
if ($loggedin eq "true") {
	$template->param(LOGOUT => qq{<span class="b">You are signed in as $info{first} $info{last}.</span> <a href="$pazar_cgi/logout.pl" class="b">Sign out</a>});
} else {
	$template->param(LOGOUT => qq{<a href="$pazar_cgi/login.pl"><span class="b">Sign in</span></a>});
}
print "Content-Type: text/html\n\n", $template->output;

my $statusmsg = "";

if ($params{mode} eq "add") {
	my $sth = $dbh->prepare(qq{SELECT COUNT(*) FROM project WHERE project_name="$params{projname}"});
	$sth->execute();
	my @res = $sth->fetchrow_array;
	if ($res[0] == 0) {
		if ($params{projpass} eq $params{projpasscheck}) {
			my $im = Crypt::Imail->new();
			my $encrypted_pass = $im->encrypt("defaultuser", $params{projpass});
			my $pname = $params{projname};
			$pname =~ s/'/\\'/g;
			$pname =~ s/"/\\"/g;    
			my $pdesc = $params{projdesc};
			$pdesc =~ s/'/\\'/g;
			$pdesc =~ s/"/\\"/g;
			$dbh->do(qq{INSERT INTO project (project_id, project_name, password, status, description, edit_date) VALUES ("", "$pname", "$encrypted_pass", "$params{projstatus}", "$pdesc", null)});
			$sth = $dbh->prepare(qq{SELECT LAST_INSERT_ID()});
			$sth->execute();
			my @rs = $sth->fetchrow_array;
			$dbh->do(qq{INSERT INTO user_project (user_project_id, user_id, project_id) VALUES ("", "$params{uid}", LAST_INSERT_ID())});
			push(@projids,$rs[0]);
			$session->param("projects", \@projids);
			sendprojectcreationemail('pazar@cmmt.ubc.ca','jlim@cmmt.ubc.ca',$pname,$pdesc,$params{projstatus});
		} else {
			$statusmsg = "Paswords do not match. Please re-enter them.";
		}
	} else {
		$statusmsg = "Project name is already in use. Please choose a different project name.";
    }
    $params{mode} = "login";
}
if ($params{mode} eq "adduser") {
	my $im = Crypt::Imail->new();
	my $encrypted_pass = $im->encrypt("defaultuser", $params{projpass}); 
	my $chkh = $dbh->prepare(qq{SELECT password FROM project WHERE project_id=?});
	$chkh->execute($params{pid})||die;
	my ($dbpass) = $chkh->fetchrow_array;
	if ($dbpass eq $encrypted_pass) {
		my $sth = $dbh->prepare(qq{SELECT user_id FROM users WHERE username="$params{usertoadd}"});
		$sth->execute();
		if (my @userinfo = $sth->fetchrow_array) {
			my $uid = $userinfo[0];
			$dbh->do(qq{INSERT INTO user_project(user_project_id, user_id, project_id) VALUES ("", "$uid", "$params{pid}")});
		} else {
			$statusmsg = "Invalid username entered. User not added to project.";
		}
	} else {
		$statusmsg = "Incorrect project administrator password entered. Please check password and try again";
	}
    $params{mode} = "login";
}
if ($params{mode} eq "updatedesc") {
	my $im = Crypt::Imail->new();
	my $encrypted_pass = $im->encrypt("defaultuser", $params{projpass}); 
	my $chkh = $dbh->prepare(qq{SELECT password FROM project WHERE project_id=?});
	$chkh->execute($params{pid});
	my ($dbpass) = $chkh->fetchrow_array;
	if ($dbpass eq $encrypted_pass) {
		my $pdesc = $params{projdesc};
		$pdesc =~ s/'/\\'/g;
		$pdesc =~ s/"/\\"/g;
		$dbh->do(qq{UPDATE project SET description="$pdesc" WHERE project_id="$params{pid}"});
	} else {
		$statusmsg = "Incorrect project administrator password entered. Please check password and try again";
	}
    $params{mode} = "login";
}
if ($params{mode} eq "updatestatus") {
	$dbh->do(qq{UPDATE project SET status="$params{projstatus}" WHERE project_id="$params{pid}"});
    $params{mode} = "login";
}

if ($params{mode} eq "useremove") {
	my $sth = $dbh->prepare(qq{SELECT COUNT(*) FROM user_project WHERE project_id="$params{pid}"});
	$sth->execute();
	my @usercount = $sth->fetchrow_array;
	my $numusers = $usercount[0];
	if ($numusers > 1) {
		my $rh = $dbh->prepare(qq{DELETE FROM user_project WHERE user_id="$params{uid}" AND project_id="$params{pid}"});
		$rh->execute();
	} else {
		$statusmsg = "No other users in this project. There must be 2 or more users in a project before you can remove yourself";
	}
    $params{mode} = "login";
}
if ($params{mode} eq "delete") {
    my $project_id = $params{pid};
	my $im = Crypt::Imail->new();
	my $encrypted_pass = $im->encrypt("defaultuser", $params{projpass}); 
	my $chkh = $dbh->prepare(qq{SELECT password FROM project WHERE project_id=?});
	$chkh->execute($params{pid});
	my ($dbpass) = $chkh->fetchrow_array;
	if ($dbpass eq $encrypted_pass) {
		$sth = $dbh->prepare(qq{SHOW tables});
		$sth->execute();
		my %table_ids;
		my @tables;
		while (my $table = $sth->fetchrow_array) {
			my $table_id = $table . "_id";
			my $clh = $dbh->prepare(qq{DESC $table});
			$clh->execute();
			my $i = 0;
			while (my $col = $clh->fetchrow_hashref) {
				if ($col->{Field} eq "project_id") {
					$i = 1;
				}
			}
			if ($i == 1) {
				my $prh = $dbh->prepare(qq{SELECT $table_id FROM $table WHERE project_id=?});
				$prh->execute($project_id) || die;
				while (my $id = $prh->fetchrow_array) {
					push (@{$table_ids{$table}},$id);
				}
				my $delh = $dbh->prepare(qq{DELETE FROM $table WHERE project_id=?});
				$delh->execute($project_id)||die;
			} else {
				push (@tables, $table);
			}
		}
		foreach (@tables) {
			if ($_ eq "analysis_i_link") {
				foreach my $tbl_id (@{$table_ids{"analysis_input"}}) {
					my $delh = $dbh->prepare(qq{DELETE FROM analysis_i_link WHERE analysis_input_id=?});
					$delh->execute($tbl_id)||die;
				}
			} elsif ($_ eq "analysis_o_link") {
				foreach my $tbl_id (@{$table_ids{"analysis_output"}}) {
					my $delh = $dbh->prepare(qq{DELETE FROM analysis_o_link WHERE analysis_output_id=?});
					$delh->execute($tbl_id)||die;
				}
			} elsif ($_ eq "anchor_reg_seq") {
				foreach my $tbl_id (@{$table_ids{"reg_seq"}}) {
					my $delh = $dbh->prepare(qq{DELETE FROM anchor_reg_seq WHERE reg_seq_id=?});
					$delh->execute($tbl_id)||die;
				}
			} elsif ($_ eq "matrix_info") {
				foreach my $tbl_id (@{$table_ids{"matrix"}}) {
					my $delh = $dbh->prepare(qq{DELETE FROM matrix_info WHERE matrix_id=?});
					$delh->execute($tbl_id)||die;
				}
			} elsif ($_ eq "mutation") {
				foreach my $tbl_id (@{$table_ids{"mutation_set"}}) {
					my $delh = $dbh->prepare(qq{DELETE FROM mutation WHERE mutation_set_id=?});
					$delh->execute($tbl_id)||die;
				}
			} elsif ($_ eq "reg_seq_set") {
				foreach my $tbl_id (@{$table_ids{"matrix"}}) {
					my $delh = $dbh->prepare(qq{DELETE FROM reg_seq_set WHERE matrix_id=?});
					$delh->execute($tbl_id)||die;
				}
			} elsif ($_ eq "tf_complex") {
				foreach my $tbl_id (@{$table_ids{"funct_tf"}}) {
					my $delh = $dbh->prepare(qq{DELETE FROM tf_complex WHERE funct_tf_id=?});
					$delh->execute($tbl_id)||die;
				}
			}
		}
	} else {
		$statusmsg = "Incorrect project administrator password entered. Please check password and try again";
	}
	$params{mode} = "login";
}

if ($params{mode} eq "login" || $loggedin eq "true" || $params{mode} eq "") {
	if ($params{submission} eq "true") {
		print qq{
		<form name="submission" method="POST" action="$pazar_cgi/sWI/entry.pl">
			<input type="hidden" name="username">      
			<input type="hidden" name="password">
			<input type="hidden" name="statusmsg" value="$statusmsg">
			<input type="hidden" name="mode" value="login">
		</form>
		<script language="JavaScript">
			document.submission.submit();
		</script>};
	} elsif ($loggedin eq "true") {
		my $sth = $dbh->prepare(qq{SELECT project_id FROM user_project WHERE user_id=?});
		$sth->execute($info{userid});
		print qq{<div class="emp">$statusmsg</div>} if $statusmsg;
		print qq{
			<h1>My projects</h1>
			<div class="p10lo">};
			
		my %fields;
		my $sth3=$dbh->prepare("show tables");
		$sth3->execute()||die;
		while (my $table=$sth3->fetchrow_array) {
			my $fields=$dbh->prepare("desc $table");
			$fields->execute()||die;
		    while (my @field_list = $fields->fetchrow_array) {
			    push (@{$fields{$table}}, $field_list[0]);
			}
		}

		my $proc = 0;
		while (my @results = $sth->fetchrow_array) {
			$proc++;
			my $proj_id = $results[0];
			my $sth2 = $dbh->prepare(qq{SELECT * FROM project WHERE project_id=?});
			$sth2->execute($proj_id);
			my @projdetails = $sth2->fetchrow_array;
			
			#get last edit_date in all tables
			my $last_date;
			foreach my $table (keys %fields) {
				my @fields=@{$fields{$table}};
				if (grep(/edit_date/, @fields) && grep(/project_id/, @fields)) {
					my $sth4=$dbh->prepare("select max(edit_date) from $table where project_id=?");
					$sth4->execute($proj_id)||die;
					my $date=$sth4->fetchrow_array;
					if ($last_date) {
						if ($date gt $last_date) {
							$last_date=$date;
						}
					} else {
						$last_date=$date;
					}
				}
			}
			
			my $userlisthandle = $dbh->prepare(qq{SELECT username FROM users, user_project WHERE users.user_id=user_project.user_id AND user_project.project_id=?});
			$userlisthandle->execute($proj_id);
			my $userstring = "";
			while (my @users = $userlisthandle->fetchrow_array) {
				my $user = $users[0];
				$userstring .= qq{<a href="mailto:$user" class="b">$user</a>, };
			}
			chop($userstring);
			chop($userstring);
			print qq{
				<div class="show" id="1_pro$proj_id">
				<h3>
					<div class="float-r">
						<input type="button" onclick="toggleRows('pro$proj_id','2','2');" value="edit properties"> 
						<input type="button" onclick="document.location.href='$pazar_cgi/project.pl?project_name=$projdetails[1]';" value="view data">
					</div>
					<span class="txt-ora">$projdetails[1]</span>
				</h3>
				<div class="p10lo">
					<div class="p5 br-a bg-lg">
						<div class="p5bo"><span class="b">By</span> $userstring</div>
						<div class="p5bo"><span class="b">Project status</span> &mdash; $projdetails[3] &nbsp; &nbsp; <span class="b">Last edited</span> &mdash; $last_date</div>
						<div><span class="b">Description</span> &mdash; $projdetails[4]</div>
					</div>
				</div>
				</div>};
			print qq{
				<div class="hide" id="2_pro$proj_id">
				<h3>
					<div class="float-r">
						<input type="button" onclick="toggleRows('pro$proj_id','1','2');" value="close edit panel"> 
						<input type="button" onclick="document.location.href='$pazar_cgi/project.pl?project_name=$projdetails[1]';" value="view data">
					</div>
					<span class="txt-ora">$projdetails[1]</span>
				</h3>
				<div class="p10lo">
					<div class="p5 br-a">
						<span class="b">By</span> $userstring
					</div><div class="p5 bg-ye">
						<div class="float-r">
							<form method="POST" action="$pazar_cgi/editprojects.pl">
								<input type="hidden" name="username" value="$info{user}">
								<input type="hidden" name="password" value="$info{pass}">
								<input type="hidden" name="mode" value="useremove">
								<input type="hidden" name="pid" value="$proj_id">
								<input type="hidden" name="uid" value="$info{userid}">
								<input type="submit" value="Remove myself">
							</form>
						</div>
						<form name="useraddform$proj_id" id="useraddform$proj_id" method="POST" action="$pazar_cgi/editprojects.pl">
							<span class="txt-red b">Add user</span> &mdash;
							<input type="hidden" name="username" value="$info{user}">
							<input type="hidden" name="password" value="$info{pass}">
							<input type="hidden" name="pid" value="$proj_id">
							<input type="hidden" name="mode" value="adduser">
							username <input type="text" name="usertoadd" size="25"> &nbsp; 
							project password <input type="password" name="projpass" size="25"> 
							<input type="button" onclick="doUserAdd($proj_id);" value="Add user">
						</form>
					</div><div class="p5 bg-dy">
						<form method="post" action="$pazar_cgi/editprojects.pl">
						<span class="b">Project status</span> &mdash; 
						<select name="projstatus">
							<option name="$projdetails[3]" value="$projdetails[3]">$projdetails[3]</option>
							<option name="restricted" value="restricted">restricted</option>
							<option name="open" value="open">open</option>
							<option name="published" value="published">published</option>
						</select>
						<input type="hidden" name="username" value="$info{user}">
						<input type="hidden" name="password" value="$info{pass}">
						<input type="hidden" name="mode" value="updatestatus">
						<input type="hidden" name="pid" value="$proj_id">
						<input type="submit" value="Update status"> &nbsp; &nbsp; 
						<span class="b">Last edited</span> &mdash; $last_date
						</form>
					</div><div class="p5 bg-ye">
						<form name="updatedescform$proj_id" id="updatedescform$proj_id" method="POST" action="$pazar_cgi/editprojects.pl">
						<div class="b">Description</div>
						<div class="">
							<textarea name="projdesc" class="w100p" rows="4">$projdetails[4]</textarea>
							<input type="hidden" name="username" value="$info{user}">
							<input type="hidden" name="password" value="$info{pass}">
							<input type="hidden" name="pid" value="$proj_id">
							<input type="hidden" name="mode" value="updatedesc">
						</div>
						<div class="p5to tr">
							Project password 
							<input type="password" name="projpass" size="25"> 
							<input type="button" onclick="doUpdateDesc($proj_id);" value="Update description"></form>
						</div>
					</div><div class="p5 bg-dy">
						<form name="deleteform$proj_id" id="deleteform$proj_id" method="POST" action="$pazar_cgi/editprojects.pl">
							<input type="hidden" name="username" value="$info{user}">
							<input type="hidden" name="password" value="$info{pass}">
							<input type="hidden" name="mode" value="delete">
							<input type="hidden" name="pid" value="$proj_id">
							<span class="txt-red b">Delete this project</span> &mdash; 
							enter project password
							<input type="password" name="projpass" size="25">
							<input type="button" onclick="doDelete($proj_id);" value="Delete">
						</form>
					</div><div class="p5 tr"></div>
				</div>
				</div>};
		}
		if ($proc == 0) {
			print qq{<div class="emp">You are not enrolled in any projects at this time. Why not create a new one?</div>};
		}
		print qq{</div>};
                if ($proc != 0)
                {
                        print qq{<h2>Forgotten Project Passwords?</h2><br>Click this button to have your project administrative passwords sent to you by email.<br>* Note that you will only receive passwords for projects that you created <form method=\"post\" action=\"emailprojectpasswords.pl\"><input type=\"submit\" value=\"Request Passwords\"></form>};
                }

		print qq{			
			<h2>Create a new project</h2>
			<div class="p20lo">
			<form name="createprojectform" method="post" action="$pazar_cgi/editprojects.pl">
				<input type="hidden" name="mode" value="add">
				<input type="hidden" name="uid" value="$info{userid}">
				<input type="hidden" name="username" value="$info{user}">
				<input type="hidden" name="password" value="$info{pass}">
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
				<div class="p5to"><input type="button" onclick="verifyProjectCreate();" value="Create new project"></div>
			</form>
			</div>};
	} else {
		print qq{
			<h1>My projects</h1>
			<div class="emp">Please <a href="$pazar_cgi/login.pl">sign in</a> to view or edit your projects.</div>};
	}
}
print $temptail->output;


sub sendprojectcreationemail
{

    my $from_address = shift;
    my $to_address = shift;
    my $project_name = shift;
    my $project_description = shift;
    my $project_status = shift;
    my $subject = "PAZAR project ".$project_name." created";
    my $body = "A new project called $project_name has been created in PAZAR with the following status: $project_status\n\nProject description: $project_description";

    my $mailer = Mail::Mailer->new("sendmail");
    $mailer->open({From => $from_address,
                   To => $to_address,
                   Subject => $subject})
    or die "Can't open: $!\n";

    print $mailer $body;
    $mailer->close;

}

