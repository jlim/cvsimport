#!/usr/bin/perl

use HTML::Template;
my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};

my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");
my $temptail = HTML::Template->new(filename => "$pazarcgipath/tail.tmpl");
$template->param(TITLE => "Step 3 - Capturing evidence | PAZAR XML format | PAZAR");
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
		<a href="$pazar_cgi/dataformats.pl" class="b">Data formats</a> &raquo; <a href="$pazar_cgi/xml.pl" class="b">PAZAR XML format</a> &raquo; Step-by-step documentation
		<div class="clear-r"></div>
	</div>
	<h1>PAZAR XML format</h1>
	<h2>Step 3 &mdash;Capturing the evidence linking a sequence to a TF or to a specific expression</h2>
	<p>This step starts inside an existing 'data' element. At this point, the 'reg_seq', 'funct_tf' and/or 'construct' elements should have been defined in this 'data' element (<a href="$pazar_cgi/step2.pl">see Step 2</a>).</p>
	
	<h3>3.1. Capturing the experiment information</h3>
	<div class="p20lo">
		<p>The "data" element stores all the annotations describing the cell, time, condition, <span class="i">etc</span>.
		<div class="p5bo"><div class="p10 bg-lg monospace b">
			<div>&lt;cell name="<span class="red">Y79</span>" pazar_id="<span class="red">ce_0001</span>" species="<span class="red">Homo sapiens</span>" status="<span class="red">cell__line</span>"/&gt;</div>
			<div>&lt;time name="<span class="red">24-28</span>" pazar_id="<span class="red">ti_0001</span>" scale="<span class="red">stages of embryogenesis</span>"/&gt;</div>
			<div>&lt;condition pazar_id="<span class="red">cd_0001</span>" cond_type="<span class="red">coexpression</span>" molecule="<span class="red">transcription factor</span>" concentration="<span class="red">1:1</span>" scale="<span class="red">ratio</span>"/&gt;</div>
		</div></div>
		<p><span class="b">Note: replace the red values with your own information.</span> The pazar IDs are internal IDs that will not be stored. They can be anything as long as they are unique throughout the file.</p>
	</div>
	<h3>3.2. Capturing the interaction or expression information</h3>
	<div class="p20lo">
		<p>The "data" element also stores the description of the interaction and/or expression quality.</p>
		<div class="p5bo"><div class="p10 bg-lg monospace b">
			<div>&lt;expression pazar_id="<span class="red">ex_0001</span>" quantitative="<span class="red">23</span>" scale="<span class="red">percent</span>"/&gt;</div>
			<div>&lt;interaction pazar_id="<span class="red">in_0001</span>" qualitative="<span class="red">good</span>"/&gt;</div>
			<div>&lt;interaction pazar_id="<span class="red">in_0002</span>" qualitative="<span class="red">none</span>"/&gt;</div>
			<div>&lt;interaction pazar_id="<span class="red">in_0003</span>" quantitative="<span class="red">14</span>" scale="<span class="red">percent</span>"/&gt;</div>
		</div></div>
		<p><span class="b">Note: replace the red values with your own information.</span> The pazar IDs are internal IDs that will not be stored. They can be anything as long as they are unique throughout the file.</p>
	</div>
	<h3>3.3. Linking it all together</h3>
	<div class="p20lo">
		<p>The "data" element can now be closed. All the data stored in it will be linked through&nbsp; "analysis" elements using the pazar_ids as IDREFS. An "analysis" element stores an experiment information, linking sequences and factors (inputs) to an interaction or expression result (output). There can be as many "analysis" element in a "pazar" element as needed. The cell and time are called as attributes of the "analysis" element. The evidence, method and ref are children elements of the "analysis" element. The sequences and factors (always use a "funct_tf" element) studied are called as attributes of the "input" element. The interaction or expression descriptions are called as attributes of the "output" element.</p>
		<p>Thus the example below describe a SELEX experiment with a TF (pazar_id="fu_0001") binding to 2 different artificial sequences (pazar_ids="co_0001" and "co_0002"), with 2 different levels of interaction (pazar_ids="in_0001" and "in_0002") -&gt; 2 'input_ouput' elements: the first describes the interaction of the TF with the first sequence, the other describes its interaction with the second sequence.</p>
		<p>Please look at the 3 PAZAR XML examples available on the <a href="$pazar_cgi/xml.pl">main page</a> if you need other examples.</p>
		<div class="p5bo"><div class="p10 bg-lg monospace b">



      <span class="b">&nbsp;
&lt;/data&gt;</span><br>



      <span class="b">&nbsp;
&lt;analysis name="<span class="red">analysis_example1</span>"</span><br class="b">



      <span class="b">&nbsp;&nbsp;&nbsp;
&lt;evidence type_evid="<span class="red">curated</span>" status_evid="<span class="red">provisional</span>"/&gt;</span><br class="b">



      <span class="b">&nbsp;&nbsp;&nbsp;
&lt;method method="<span class="red">SELEX</span>"/&gt;</span><br class="b">



      <span class="b">&nbsp;&nbsp;&nbsp;
&lt;ref pmid="<span class="red">7936637</span>"/&gt;</span><br class="b">



      <span class="b">&nbsp;&nbsp;&nbsp;
&lt;input_output&gt;</span><br class="b">



      <span class="b">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&lt;input inputs="<span class="red">fu_0001
co_0001</span>"/&gt;</span><br class="b">



      <span class="b">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&lt;output outputs="<span class="red">in_0001</span>"/&gt;</span><br class="b">



      <span class="b">&nbsp;&nbsp;&nbsp;
&lt;/input_output&gt;</span><br class="b">



      <span class="b">&nbsp;&nbsp;&nbsp;
&lt;input_output&gt;</span><br class="b">



      <span class="b">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&lt;input inputs="<span class="red">fu_0001
co_0002</span>"/&gt;</span><br class="b">



      <span class="b">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&lt;output outputs="<span class="red">in_0002</span>"/&gt;</span><br class="b">



      <span class="b">&nbsp;&nbsp;&nbsp;
&lt;/input_output&gt;</span><br class="b">



      <span class="b">&nbsp;
&lt;/analysis&gt;</div></div>

		<p><span class="b">Note: replace the red values with your own information.</span> The pazar IDs are internal IDs that will not be stored. They can be anything as long as they are unique throughout the file.</p>
	</div>
	<h3>3.4. The end</h3>
	<div class="p20lo">
		<p>Once all the data has been entered in the 'data' element and linked together through multiple 'analysis' elements, the 'pazar' element can be closed and the XML file is finished.</p>
		<div class="p5bo"><div class="p10 bg-lg monospace b">
			&lt;/pazar&gt;
		</div></div>
	</div>
	<div><a href="$pazar_cgi/step2.pl" class="b">&laquo; Go to Step 2</a></div>};

print $temptail->output;
