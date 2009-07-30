#!/usr/bin/perl

use HTML::Template;
my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};

my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");
my $temptail = HTML::Template->new(filename => "$pazarcgipath/tail.tmpl");
$template->param(TITLE => "Project outline | PAZAR");
$template->param(PAZAR_HTML => $pazar_html);
$template->param(PAZAR_CGI => $pazar_cgi);

require "$pazarcgipath/getsession.pl";
if ($loggedin eq "true") {
	$template->param(LOGOUT => qq{<span class="b">You are signed in as $info{first} $info{last}.</span> <a href="$pazar_cgi/logout.pl" class="b">Sign out</a>});
} else {
	$template->param(LOGOUT => qq{<a href="$pazar_cgi/login.pl"><span class="b">Sign in</span></a>});
}

print "Content-Type: text/html\n\n", $template->output;
print qq{
	<div class="docp">
		<div class="float-r b txt-grey">PAZAR Documentation</div>
		<div class="clear-r"></div>
	</div>
	<h1>Project outline</h1>

	<p>Algorithms and software for the analysis of transcription regulating sequences have proliferated. Methods based on phylogenetic footprinting, combinatorial interactions between transcription factors and genomics data appear regularly. Unfortunately much of the research in the field continues to re-analyze the same data. In order to advance this active field, it is critical to gain unrestricted access to a broader range of reference data. Such collections would be useful both for the measurement of software performance and, most importantly, as fertile ground for investigation. Small collections appear periodically in independent databases, often as by-products of algorithm development projects. For instance, the <a target="_blank" href="http://jaspar.cgb.ki.se/cgi-bin/jaspar_db.pl">JASPAR</a> database of binding profiles emerged in this manner.</p>

	<p>PAZAR is a software framework for the construction and maintenance of regulatory sequence data annotations; a framework which allows multiple boutique databases to function independently within a larger system (or information mall). <span class="b">Our goal is to be the public repository for regulatory data</span>.</p>

	<h3>Our principles</h3>
	<div class="p20lo">
		<ol>
			<li>To be <span class="b">open-access</span> and <span class="b">open-source</span>, providing a completely transparent development and data compilation. In this regard, the PAZAR project is now hosted by <a target="_blank" href="http://sourceforge.net/projects/pazar">SourceForge</a>, where anyone can go to browse our <a href="http://pazar.cvs.sourceforge.net/pazar/" target="_blank">CVS repository</a>. A mailing list <a href="http://lists.sourceforge.net/lists/listinfo/pazar-news" target="_blank">News and Views</a> is also available in which every major development will be posted.</li>
			<li>To function as a boutique system where curators own their data and can release it according to their own will.</li>
			<li>To be simple to use either in the curation process or the query of the database. For this purpose we are currently developing an advanced API to insulate the user from the underlying data model and to provide simple methods for the user to deposit to or query from the database.</li>
		</ol>
	</div>

	<h3>System architecture</h3>
	<div class="p20lo">
		<p>The PAZAR system is currently developed as a mySQL database featuring a complex <a href="$pazar_html/images/pazar_schema.png" target="_blank">schema</a> which allows for a high level of flexibility regarding the type of information that can be captured. The database <a href="$pazar_html/pazar_dictionary.html" target="_blank">dictionary</a> and an explanation of the <a href="$pazar_html/iosys.htm" target="_blank">IO system</a> can help you find out some of the database constraints and internal structure.</p>
	
		<p>To ease the insertion of data into the database, we are developing two curation interfaces, one allowing the curator to capture higher levels of details than the other. We have also designed an <a href="$pazar_cgi/xml.pl">XML exchange format</a> that can be used to format already existing datasets.</p>
	
		<p>As an <span class="b">open system</span>, each boutique operator within PAZAR is welcome to participate in further API development and to create and maintain their own annotation interfaces. Two forums are also available so that everyone can ask for help (at the <a href="https://sourceforge.net/forum/forum.php?forum_id=520428" target="_blank">PAZAR SourceForge help forum</a>) or make any comment or suggestion (at the <a href="https://sourceforge.net/forum/forum.php?forum_id=512784" target="_blank">PAZAR SourceForge open discussion forum</a>).</p>
	</div>

	<h3>License</h3>
	<div class="p20lo">
		<p>The PAZAR code is available under the <a href="http://www.gnu.org/copyleft/lesser.html" target="_blank">GNU Lesser General Public License (LGPL)</a>. PAZAR data in "public" or "open" data collections are available under the <a href="http://www.gnu.org/copyleft/lesser.html" target="_blank">GNU LGPL</a>, while data in "private" collections are property of the curators of those collections and permission must be explicitly provided. Only "public" and "open" collections can be accessed by anonymous users.</p>
	</div>

	<a name="publications"></a><h3>Publications and resources</h3>
	<div class="p20lo">
	
		<p>Please use the citation information below when referring to PAZAR in publication.</p>
	
		<div class="p10bo"><div class="p10 bg-lg">Portales-Casamar E, Arenillas D, Lim J, Swanson MI, Jiang S, McCallum A, Kirov S, Wasserman WW. <a target="_blank" href="http://nar.oxfordjournals.org/cgi/content/abstract/37/suppl_1/D54?maxtoshow=&HITS=10&hits=10&RESULTFORMAT=&fulltext=pazar&searchid=1&FIRSTINDEX=0&resourcetype=HWCIT" class="b">The PAZAR database of gene regulatory information coupled to the ORCA toolkit for the study of regulatory sequences.</a> <span class="i">Nucleic Acids Res</span>. 37(Database issue):D54-60. (2009)</div></div>

		<div class="p10bo"><div class="p10 bg-lg">Portales-Casamar E, Kirov S, Lim J, Lithwick S, Swanson MI, Ticoll A, Snoddy J, Wasserman WW. <a target="_blank" href="http://genomebiology.com/2007/8/10/R207" class="b">PAZAR: a Framework for Collection and Dissemination of Cis-regulatory Sequence Annotation.</a> <span class="i">Genome Biology</span> (8)R207. (2007)</div></div>

		<p><a href="$pazar_html/PAZARposter.pdf" class="b">Download our poster</a></p>
	</div>
};

print $temptail->output;
