#!/usr/bin/perl

use HTML::Template;

my $pazar_cgi = $ENV{PAZAR_CGI};
my $pazar_html = $ENV{PAZAR_HTML};
my $pazarcgipath = $ENV{PAZARCGIPATH};

# open the html header template
my $template = HTML::Template->new(filename => "$pazarcgipath/header.tmpl");

# fill in template parameters
$template->param(TITLE => 'PAZAR Links');
$template->param(PAZAR_HTML => $pazar_html);
$template->param(PAZAR_CGI => $pazar_cgi);

# send the obligatory Content-Type and print the template output
print "Content-Type: text/html\n\n", $template->output;

print<<Page;
<p class="title1">PAZAR - Links</p>
<hr color='black'>
<p class="title2">Content</p>
<a href="#1. Useful Software"><span class="title2">1. Useful Software</span></a><br>
<a href="#1.1 Introduction"><span class="title4 margin">1.1 Introduction</span></a><br>
<a href="#1.2 Software Classes"><span class="title4 margin">1.2 Software Classes</span></a><br>
<a href="#1.3 Software List"><span class="title4 margin">1.3 Software List</span></a><br>
<a href="#2. Regulatory Datasets"><span class="title2">2. Regulatory Datasets</span></a><br>
<p>For additional useful links see also <a href="http://bioinformatics.ubc.ca/resources/links_directory/?subcategory_id=104" target='extlinks' onClick="windowopen('about:blank','extlinks');">http://bioinformatics.ubc.ca/resources/links_directory/?subcategory_id=104</a></p>
<hr color='black'>
<a name='1. Useful Software'></a><p class="title2">1. Useful Software</p>
<a name='1.1 Introduction'></a><p class="title4 margin">1.1 Introduction</p>
<p>The data found within PAZAR can be used in association with a large array of online resources.  We do not directly provide such tools within PAZAR.  We believe the data should be accessed by sequence analysis tools through the PAZAR software interface. For now, one must still copy data from PAZAR and paste it into the web services you choose to use.  The following list of resources is not comprehensive.  If you have encountered a program that you think is noteworthy, please let us know.</p>
<a name='1.2 Software Classes'></a><p class="title4 margin">1.2 Software Classes</p>
<table class='summarytable'>
<tbody><tr>
<td class='basictd' style="text-align: center;"><b>Software Class</b></td>
<td class='basictd' style="text-align: center;"><b>Explanation</b></td></tr>
<tr>
<td class='basictd'>TFBS Discrimination</td>
<td class='basictd'>Given a count matrix summarizing the binding sites for a TF, predict TFBS in a sequence of your choice.</td></tr>
<tr>
<td class='basictd'>Pattern Discovery</td>
<td class='basictd'>Given a set of regulatory sequences, you wish to find new patterns that might be a novel type of TFBS.</td></tr>
<tr>
<td class='basictd'>TFBS Over-representation</td>
<td class='basictd'>Given a set of genes and a count matrix, you wish to determine if the pattern defined by the count matrix is significantly enriched compared to background.
Unfortunately there is no TFBS over-representation tool that allows for user-submitted binding profiles.  Tools like oPOSSUM must analyze enormous numbers of genes to perform the analysis and therefore do not offer submission (yet).</td></tr>
<tr>
<td class='basictd'>TFBS Model Comparison</td>
<td class='basictd'>You have recovered a new TFBS pattern (count matrix) and wish to see if the pattern resembles other known TFBS profiles. Once you find a pattern, it is natural to want to compare it against a database of patterns to see if it matches a characterized type of TFBS.</td></tr>
<tr>
<td class='basictd'>TFBS Combination Detection</td>
<td class='basictd'>You have a set of TFBS count matrices (1 or more), and wish to find segments in a DNA sequence significantly enriched for combinations of matches to the pattern(s).</td></tr>
<tr>
<td class='basictd'>TF Information</td>
<td class='basictd'>Sometimes you need to look up information about a gene or protein.  Everyone knows about EnrezGene and UniProt.  You might also try www.transcriptionfactors.org</td></tr>
</tbody></table>
<a name='1.3 Software List'></a><p class="title4 margin">1.3 Software List</p>
<table class='summarytable'>
<tbody><tr>
<td class='basictd' style="text-align: center;"><b>Name</b></td>
<td class='basictd' style="text-align: center;"><b>Class(es)</b></td>
<td class='basictd' style="text-align: center;"><b>URL</td></b></tr>
<tr>
<td class='basictd'>AHAB</td>
<td class='basictd'>TFBS Combination Detection</td>
<td class='basictd'><a href='http://gaspard.bio.nyu.edu/Ahab.html'>http://gaspard.bio.nyu.edu/Ahab.html</a></td></tr>
<tr>
<td class='basictd'>Cluster Buster</td>
<td class='basictd'>TFBS Combination Detection</td>
<td class='basictd'><a href='http://zlab.bu.edu/cluster-buster/cbust.html'>http://zlab.bu.edu/cluster-buster/cbust.html</a></td></tr>
<tr>
<td class='basictd'>ConSite</td>
<td class='basictd'>TFBS Discrimination</td>
<td class='basictd'><a href='http://asp.ii.uib.no:8090/cgi-bin/CONSITE/consite/'>http://asp.ii.uib.no:8090/cgi-bin/CONSITE/consite/</a></td></tr>
<tr>
<td class='basictd'>CRE works</td>
<td class='basictd'>TFBS Discrimination<br>TFBS Combination Detection</td>
<td class='basictd'><a href='http://genereg.ornl.gov/scancre/'>http://genereg.ornl.gov/scancre/</a></td></tr>
<tr>
<td class='basictd'>FOOTER</td>
<td class='basictd'>TFBS Discrimination</td>
<td class='basictd'><a href='http://biodev.hgen.pitt.edu/footer_php/Footerv2_0.php'>http://biodev.hgen.pitt.edu/footer_php/Footerv2_0.php</a></td></tr>
<tr>
<td class='basictd'>JASPAR</td>
<td class='basictd'>TFBS Model Comparison</td>
<td class='basictd'><a href='http://jaspar.genereg.net/'>http://jaspar.genereg.net/</a></td></tr>
<tr>
<td class='basictd'>MAST</td>
<td class='basictd'>TFBS Discrimination<br>TFBS Combination Detection</td>
<td class='basictd'><a href='http://meme.sdsc.edu/meme/mast.html'>http://meme.sdsc.edu/meme/mast.html</a></td><tr>
<td class='basictd'>MSCAN</td>
<td class='basictd'>TFBS Combination Detection</td>
<td class='basictd'></td></tr>
</td></tr>
<tr>
<td class='basictd'>RSA TOOLS</td>
<td class='basictd'>TFBS Discrimination<br>Pattern Discovery</td>
<td class='basictd'><a href='http://rsat.ulb.ac.be/rsat/'>http://rsat.ulb.ac.be/rsat/</a></td></tr>
<tr>
<td class='basictd'>STAMP</td>
<td class='basictd'>TFBS Model Comparison</td>
<td class='basictd'><a href='http://www.benoslab.pitt.edu/stamp/'>http://www.benoslab.pitt.edu/stamp/</a></td></tr>
<tr>
<td class='basictd'>TOUCAN</td>
<td class='basictd'>TFBS Discrimination<br>Pattern Discovery<br>TFBS Combination Detection</td>
<td class='basictd'><a href='http://homes.esat.kuleuven.be/~saerts/software/toucan.php'>http://homes.esat.kuleuven.be/~saerts/software/toucan.php</a></td></tr>
<tr>
<td class='basictd'>WebMotifs</td>
<td class='basictd'>Pattern Discovery</td>
<td class='basictd'><a href='http://fraenkel.mit.edu/webmotifs/'>http://fraenkel.mit.edu/webmotifs/</a></td></tr>
</tbody></table><br><br>
<a name='2. Regulatory Datasets'></a><p class="title2">2. Regulatory Datasets</p>

<table class='summarytable'>

  <tbody>

    <tr>

      <td class='basictd' style="width: 98px; text-align: center;"><b>Name</b></td>

      <td class='basictd' style="width: 406px; text-align: center;"><b>Description</b></td>

      <td class='basictd' style="text-align: center; width: 361px;"><b>URL</b></td>

    </tr>

    <tr>

      <td class='basictd' style="width: 98px; color: rgb(0, 0, 0);">ABS</td>

      <td class='basictd' style="width: 406px;">Database of Annotated regulatory Binding Sites from orthologous promoters</td>

      <td class='basictd' style="width: 361px;"><a href="http://genome.imim.es/datasets/abs2005/downloads.html" mce_href="http://genome.imim.es/datasets/abs2005/downloads.html" rel="nofollow" linktype="raw" linktext="http://genome.imim.es/datasets/abs2005/downloads.html">http://genome.imim.es/datasets/abs2005/downloads.html</a></td>

    </tr>

    <tr>

      <td class='basictd' style="width: 98px; color: rgb(0, 0, 0);">AGRIS AtcisDB and AtTFDB</td>

      <td class='basictd' style="width: 406px; color: rgb(0, 0, 0);">Arabidopsis thaliana cis-regulatory db and&nbsp; transcription factor db</td>

      <td class='basictd' style="width: 361px;"><font color="#9999ff"></font><font color="#9999ff"><a href="http://arabidopsis.med.ohio-state.edu/" mce_href="http://arabidopsis.med.ohio-state.edu/" rel="nofollow" linktype="raw" linktext="http://arabidopsis.med.ohio-state.edu/">http://arabidopsis.med.ohio-state.edu/</a></font></td>

    </tr>

    <tr>

      <td class='basictd' style="width: 98px; color: rgb(0, 0, 0);">AtProbe</td>

      <td class='basictd' style="width: 406px; color: rgb(0, 0, 0);">Arabidopsis thaliana promoter binding element database</td>

      <td class='basictd' style="width: 361px;"><font color="#9999ff"></font><font color="#9999ff"><a href="http://rulai.cshl.edu/cgi-bin/atprobe/atprobe.pl" mce_href="http://rulai.cshl.edu/cgi-bin/atprobe/atprobe.pl" rel="nofollow" linktype="raw" linktext="http://rulai.cshl.edu/cgi-bin/atprobe/atprobe.pl">http://rulai.cshl.edu/cgi-bin/atprobe/atprobe.pl</a></font></td>

    </tr>

    <tr>

      <td class='basictd' style="width: 98px; color: rgb(0, 0, 0);">AthaMap</td>

      <td class='basictd' style="width: 406px; color: rgb(0, 0, 0);">Genome-wide map of potential transcription factor binding sites in <i>Arabidopsis thaliana</i></td>

      <td class='basictd' style="width: 361px;"><font color="#9999ff"></font><font color="#9999ff"><a href="http://www.athamap.de/" mce_href="http://www.athamap.de/" rel="nofollow" linktype="raw" linktext="http://www.athamap.de/">http://www.athamap.de/</a></font></td>

    </tr>

    <tr>

      <td class='basictd' style="width: 98px;">BOND</td>

      <td class='basictd' style="width: 406px;">The Biomolecular Object Network Databank (BOND) is a&nbsp;resource to perform cross-database 
		searches of available sequence, interaction, complex and pathway information.</td>

      <td class='basictd' style="width: 361px;"><a href="http://bond.unleashedinformatics.com/Action?" mce_href="http://bond.unleashedinformatics.com/Action?" rel="nofollow" linktype="raw" linktext="http://bond.unleashedinformatics.com/Action?">http://bond.unleashedinformatics.com/Action?</a></td>

    </tr>

    <tr>

      <td class='basictd' style="width: 98px;">CEPDB</td>

      <td class='basictd' style="width: 406px;">C. elegans Promoter Db</td>

      <td class='basictd' style="width: 361px;"><a href="http://rulai.cshl.edu/cgi-bin/CEPDB/home.cgi" mce_href="http://rulai.cshl.edu/cgi-bin/CEPDB/home.cgi" rel="nofollow" linktype="raw" linktext="http://rulai.cshl.edu/cgi-bin/CEPDB/home.cgi">http://rulai.cshl.edu/cgi-bin/CEPDB/home.cgi</a></td>

    </tr>

    <tr>

      <td class='basictd' style="width: 98px;">cisreg.ca</td>

      <td class='basictd' style="width: 406px;">Contains musle and liver data sets </td>

      <td class='basictd' style="width: 361px;"><a href="http://www.cisreg.ca/tjkwon/" mce_href="http://www.cisreg.ca/tjkwon/" rel="nofollow" linktype="raw" linktext="http://www.cisreg.ca/tjkwon/">http://www.cisreg.ca/tjkwon/</a></td>

    </tr>

    <tr>

      <td class='basictd' style="width: 98px;">Compel</td>

      <td class='basictd' style="width: 406px; font-family: Times New Roman; color: rgb(0, 0, 0);"><font size="+2"><strong></strong></font>Composite regulatory elements: structure, function and classification</td>

      <td class='basictd' style="width: 361px;"><a href="http://compel.bionet.nsc.ru/new/compel/compel.html" mce_href="http://compel.bionet.nsc.ru/new/compel/compel.html" rel="nofollow" linktype="raw" linktext="http://compel.bionet.nsc.ru/new/compel/compel.html">http://compel.bionet.nsc.ru/new/compel/compel.html</a></td>

    </tr>

    <tr>

      <td class='basictd' style="width: 98px; color: rgb(0, 0, 0);">DATF</td>

      <td class='basictd' style="width: 406px; color: rgb(0, 0, 0);">The Database of Arabidopsis Transcription Factors (DATF)</td>

      <td class='basictd' style="width: 361px;"><font color="#9999ff"></font><font color="#9999ff"><a href="http://datf.cbi.pku.edu.cn/" mce_href="http://datf.cbi.pku.edu.cn/" rel="nofollow" linktype="raw" linktext="http://datf.cbi.pku.edu.cn/">http://datf.cbi.pku.edu.cn/</a></font></td>

    </tr>

    <tr>

      <td class='basictd' style="width: 98px; color: rgb(0, 0, 0);">DBTSS</td>

      <td class='basictd' style="width: 406px;">Database of Transcriptional Start Sites</td>

      <td class='basictd' style="width: 361px;"><a href="http://dbtss.hgc.jp/" mce_href="http://dbtss.hgc.jp/" rel="nofollow" linktype="raw" linktext="http://dbtss.hgc.jp/">http://dbtss.hgc.jp/</a></td>

    </tr>

    <tr>

      <td class='basictd' style="width: 98px; color: rgb(0, 0, 0);">DoOP</td>

      <td class='basictd' style="width: 406px;">Orthologous clusters of promoters</td>

      <td class='basictd' style="width: 361px;"><a href="http://doop.abc.hu/" mce_href="http://doop.abc.hu/" rel="nofollow" linktype="raw" linktext="http://doop.abc.hu/">http://doop.abc.hu/</a></td>

    </tr>

    <tr>

      <td class='basictd' style="width: 98px;">DBSD</td>

      <td class='basictd' style="width: 406px;">Drosophila Binding Site Database</td>

      <td class='basictd' style="width: 361px;"><a href="http://rulai.cshl.org/dbsd/index.html" mce_href="http://rulai.cshl.org/dbsd/index.html" rel="nofollow" linktype="raw" linktext="http://rulai.cshl.org/dbsd/index.html">http://rulai.cshl.org/dbsd/index.html</a> <br>

*Note that this website is not yet functional but will be soon.</td>

    </tr>

    <tr>

      <td class='basictd' style="width: 98px;">Drosophila DNase I Footprint Database</td>

      <td class='basictd' style="width: 406px;">Webpage providing access to results of the systematic 
        curation and genome annotation of 1,365 DNase I footprints for the fruitfly 
        <em>D. melanogaster</em></td>

      <td class='basictd' style="width: 361px;"><a href="http://www.flyreg.org/" mce_href="http://www.flyreg.org/" rel="nofollow" linktype="raw" linktext="http://www.flyreg.org/">http://www.flyreg.org/</a></td>

    </tr>

    <tr>

      <td class='basictd' style="width: 98px; color: rgb(0, 0, 0);">DRTF</td>

      <td class='basictd' style="width: 406px; color: rgb(0, 0, 0);">Database of Rice Transcription Factors</td>

      <td class='basictd' style="width: 361px;"><font color="#9999ff"></font><font color="#9999ff"><a href="http://drtf.cbi.pku.edu.cn/" mce_href="http://drtf.cbi.pku.edu.cn/" rel="nofollow" linktype="raw" linktext="http://drtf.cbi.pku.edu.cn/">http://drtf.cbi.pku.edu.cn/</a></font></td>

    </tr>

    <tr>

      <td class='basictd' style="width: 98px; color: rgb(0, 0, 0);">ECRBase</td>

      <td class='basictd' style="width: 406px;">Database of Evolutionary Conserved Regions (ECRs), Promoters, and
Transcription Factor Binding Sites in Vertebrate Genomes created using
ECR Browser alignments</td>

      <td class='basictd' style="width: 361px;"><a href="http://ecrbase.dcode.org/" mce_href="http://ecrbase.dcode.org/" rel="nofollow" linktype="raw" linktext="http://ecrbase.dcode.org/">http://ecrbase.dcode.org/</a></td>

    </tr>

    <tr>

      <td class='basictd' style="width: 98px;">EDGEdb</td>

      <td class='basictd' style="width: 406px;">PDI, PPI and gene expression data
generated by the Walhout laboratory and others are made available to
the community through EDGEdb (elegans differential gene expression data)</td>

      <td class='basictd' style="width: 361px;"><a href="http://edgedb.umassmed.edu/IndexAction.do" mce_href="http://edgedb.umassmed.edu/IndexAction.do" rel="nofollow" linktype="raw" linktext="http://edgedb.umassmed.edu/IndexAction.do">http://edgedb.umassmed.edu/IndexAction.do</a></td>

    </tr>

    <tr>

      <td class='basictd' style="width: 98px; color: rgb(0, 0, 0);">EPD</td>

      <td class='basictd' style="width: 406px; color: rgb(0, 0, 0);">Eukaryotic Promoter Database</td>

      <td class='basictd' style="width: 361px;"><font color="#9999ff"></font><font color="#9999ff"><a href="http://www.epd.isb-sib.ch/" mce_href="http://www.epd.isb-sib.ch/" rel="nofollow" linktype="raw" linktext="http://www.epd.isb-sib.ch/">http://www.epd.isb-sib.ch/</a></font></td>

    </tr>

    <tr>

      <td class='basictd' style="width: 98px;">ERTargetDB&nbsp;</td>

      <td class='basictd' style="width: 406px;">ERTargetDB integrates information from ongoing 
          Chip-on-chip experiments and promoter sequence conservation 
          from the OMGProm database.</td>

      <td class='basictd' style="width: 361px;"><a href="http://bioinformatics.med.ohio-state.edu/ERTargetDB/" mce_href="http://bioinformatics.med.ohio-state.edu/ERTargetDB/" rel="nofollow" linktype="raw" linktext="http://bioinformatics.med.ohio-state.edu/ERTargetDB/">http://bioinformatics.med.ohio-state.edu/ERTargetDB/</a></td>

    </tr>

    <tr>

      <td class='basictd' style="width: 98px;">Globin Gene Server</td>

      <td class='basictd' style="width: 406px;">Experimental data on the regulation of the globin gene cluster</td>

      <td class='basictd' style="width: 361px;"><a href="http://globin.cse.psu.edu/" mce_href="http://globin.cse.psu.edu/" rel="nofollow" linktype="raw" linktext="http://globin.cse.psu.edu/">http://globin.cse.psu.edu/</a></td>

    </tr>

    <tr>

      <td class='basictd' style="width: 98px;">Harbison Lab</td>

      <td class='basictd' style="width: 406px;">Datasets useful in comparative genomics and in erythroid gene regulation</td>

      <td class='basictd' style="width: 361px;"><a href="http://www.bx.psu.edu/%7Eross/dataset/DatasetHome.html" mce_href="http://www.bx.psu.edu/~ross/dataset/DatasetHome.html" rel="nofollow" linktype="raw" linktext="http://www.bx.psu.edu/~ross/dataset/DatasetHome.html">http://www.bx.psu.edu/~ross/dataset/DatasetHome.html</a></td>

    </tr>

    <tr>

      <td class='basictd' style="width: 98px;">HemoPDB</td>

      <td class='basictd' style="width: 406px;">Hematopoiesis Promoter Db</td>

      <td class='basictd' style="width: 361px;"><a href="http://bioinformatics.med.ohio-state.edu/HemoPDB/" mce_href="http://bioinformatics.med.ohio-state.edu/HemoPDB/" rel="nofollow" linktype="raw" linktext="http://bioinformatics.med.ohio-state.edu/HemoPDB/">http://bioinformatics.med.ohio-state.edu/HemoPDB/</a></td>

    </tr>

    <tr>

      <td class='basictd' style="width: 98px; color: rgb(0, 0, 0);">JASPAR</td>

      <td class='basictd' style="width: 406px;">high-quality transcription factor binding profile database.</td>

      <td class='basictd' style="width: 361px;"><a href="http://jaspar.cgb.ki.se/cgi-bin/jaspar_db.pl" mce_href="http://jaspar.cgb.ki.se/cgi-bin/jaspar_db.pl" rel="nofollow" linktype="raw" linktext="http://jaspar.cgb.ki.se/cgi-bin/jaspar_db.pl">http://jaspar.cgb.ki.se/cgi-bin/jaspar_db.pl</a></td>

    </tr>

    <tr>

      <td class='basictd' style="width: 98px;"><font color="#000000">LSPD</font></td>

      <td class='basictd' style="width: 406px;"><font color="#000000">The Liver Specific Gene Promoter Database</font></td>

      <td class='basictd' style="width: 361px;"><font color="#000000"></font><font color="#000000"><a href="http://rulai.cshl.edu/LSPD/" mce_href="http://rulai.cshl.edu/LSPD/" rel="nofollow" linktype="raw" linktext="http://rulai.cshl.edu/LSPD/">http://rulai.cshl.edu/LSPD/</a></font></td>

    </tr>

    <tr>

      <td class='basictd' style="width: 98px;">MPD</td>

      <td class='basictd' style="width: 406px;">Mammalian Promoter Db (human, mouse and rat)</td>

      <td class='basictd' style="width: 361px;"><a href="http://rulai.cshl.edu/CSHLmpd2" mce_href="http://rulai.cshl.edu/CSHLmpd2" rel="nofollow" linktype="raw" linktext="http://rulai.cshl.edu/CSHLmpd2">http://rulai.cshl.edu/CSHLmpd2</a></td>

    </tr>

    <tr>

      <td class='basictd' style="width: 98px; color: rgb(0, 0, 0);">MPromDb</td>

      <td class='basictd' style="width: 406px;">Mammalian Promoter Db with experimentally supported annotations</td>

      <td class='basictd' style="width: 361px;"><a href="http://bioinformatics.med.ohio-state.edu/MPromDb/" mce_href="http://bioinformatics.med.ohio-state.edu/MPromDb/" rel="nofollow" linktype="raw" linktext="http://bioinformatics.med.ohio-state.edu/MPromDb/">http://bioinformatics.med.ohio-state.edu/MPromDb/</a></td>

    </tr>

    <tr>

      <td class='basictd' style="width: 98px; color: rgb(0, 0, 0);">MTIR</td>

      <td class='basictd' style="width: 406px;">Muscle-specific regulation of transcription</td>

      <td class='basictd' style="width: 361px;"><a href="http://www.cbil.upenn.edu/MTIR/HomePage.html" mce_href="http://www.cbil.upenn.edu/MTIR/HomePage.html" rel="nofollow" linktype="raw" linktext="http://www.cbil.upenn.edu/MTIR/HomePage.html">http://www.cbil.upenn.edu/MTIR/HomePage.html</a></td>

    </tr>

    <tr>

      <td class='basictd' style="width: 98px; color: rgb(0, 0, 0);">OMGProm</td>

      <td class='basictd' style="width: 406px;">Orthologous Mammalian Gene Promoters</td>

      <td class='basictd' style="width: 361px;"><a href="http://bioinformatics.med.ohio-state.edu/OMGProm/" mce_href="http://bioinformatics.med.ohio-state.edu/OMGProm/" rel="nofollow" linktype="raw" linktext="http://bioinformatics.med.ohio-state.edu/OMGProm/">http://bioinformatics.med.ohio-state.edu/OMGProm/</a></td>

    </tr>

    <tr>

      <td class='basictd' style="width: 98px;">ooTFD</td>

      <td class='basictd' style="width: 406px;">object-oriented Transcription Factors Db</td>

      <td class='basictd' style="width: 361px;"><a href="http://www.ifti.org/ootfd/" mce_href="http://www.ifti.org/ootfd/" rel="nofollow" linktype="raw" linktext="http://www.ifti.org/ootfd/">ttp://www.ifti.org/ootfd/</a></td>

    </tr>

    <tr>

      <td class='basictd' style="width: 98px;">OPD</td>

      <td class='basictd' style="width: 406px;">Osteo-Promoter Db (promoters of genes in the osteogenic pathway)</td>

      <td class='basictd' style="width: 361px;"><a href="http://www.opd.tau.ac.il/" mce_href="http://www.opd.tau.ac.il/" rel="nofollow" linktype="raw" linktext="http://www.opd.tau.ac.il/">http://www.opd.tau.ac.il/</a></td>

    </tr>

    <tr>

      <td class='basictd' style="width: 98px; color: rgb(0, 0, 0);">Oreganno</td>

      <td class='basictd' style="width: 406px;">Open regulatory annotation database</td>

      <td class='basictd' style="width: 361px;"><a href="http://oreganno.org/" mce_href="http://oreganno.org" rel="nofollow" linktype="raw" linktext="http://oreganno.org">http://oreganno.org</a></td>

    </tr>

    <tr>

      <td class='basictd' style="width: 98px; color: rgb(0, 0, 0);">PLACE</td>

      <td class='basictd' style="width: 406px; color: rgb(0, 0, 0);">Plant Cis-acting Regulatory DNA Elements</td>

      <td class='basictd' style="width: 361px;"><font color="#9999ff"></font><font color="#9999ff"><a href="http://www.dna.affrc.go.jp/PLACE/" mce_href="http://www.dna.affrc.go.jp/PLACE/" rel="nofollow" linktype="raw" linktext="http://www.dna.affrc.go.jp/PLACE/">http://www.dna.affrc.go.jp/PLACE/</a></font></td>

    </tr>

    <tr>

      <td class='basictd' style="width: 98px; color: rgb(0, 0, 0);">Plant CARE</td>

      <td class='basictd' style="width: 406px; color: rgb(0, 0, 0);">Cis-Acting regulatory element.database</td>

      <td class='basictd' style="width: 361px;"><font color="#9999ff"></font><font color="#9999ff"><a href="http://intra.psb.ugent.be:8080/PlantCARE/" mce_href="http://intra.psb.ugent.be:8080/PlantCARE/" rel="nofollow" linktype="raw" linktext="http://intra.psb.ugent.be:8080/PlantCARE/">http://intra.psb.ugent.be:8080/PlantCARE/</a><br>

      <span style="color: rgb(0, 0, 0);">*Note: This database does not appear to currently be online.</span></font></td>

    </tr>

    <tr>

      <td class='basictd' style="width: 98px; color: rgb(0, 0, 0);">Plant Prom DB</td>

      <td class='basictd' style="width: 406px; color: rgb(0, 0, 0);">Plant Promoter Sequences</td>

      <td class='basictd' style="width: 361px;"><font color="#9999ff"></font><font color="#9999ff"><a href="http://mendel.cs.rhul.ac.uk/mendel.php?topic=plantprom" mce_href="http://mendel.cs.rhul.ac.uk/mendel.php?topic=plantprom" rel="nofollow" linktype="raw" linktext="http://mendel.cs.rhul.ac.uk/mendel.php?topic=plantprom">http://mendel.cs.rhul.ac.uk/mendel.php?topic=plantprom</a></font></td>

    </tr>

    <tr>

      <td class='basictd' style="width: 98px; color: rgb(0, 0, 0);">RARTF</td>

      <td class='basictd' style="width: 406px; color: rgb(0, 0, 0);">RIKEN Arabidopsis Transcription Factor db</td>

      <td class='basictd' style="width: 361px;"><font color="#9999ff"></font><font color="#9999ff"><a href="http://rarge.gsc.riken.jp/rartf/" mce_href="http://rarge.gsc.riken.jp/rartf/" rel="nofollow" linktype="raw" linktext="http://rarge.gsc.riken.jp/rartf/">http://rarge.gsc.riken.jp/rartf/</a></font></td>

    </tr>

    <tr>

      <td class='basictd' style="width: 98px; color: rgb(0, 0, 0);">REDfly</td>

      <td class='basictd' style="width: 406px; color: rgb(0, 0, 0);">Regulatory Element Database for Drosophila</td>

      <td class='basictd' style="width: 361px;"><a href="http://redfly.ccr.buffalo.edu/?content=/search.php" mce_href="http://redfly.ccr.buffalo.edu/?content=/search.php" rel="nofollow" linktype="raw" linktext="http://redfly.ccr.buffalo.edu/?content=/search.php">http://redfly.ccr.buffalo.edu/?content=/search.php</a></td>

    </tr>

    <tr>

      <td class='basictd' style="width: 98px; color: rgb(0, 0, 0);">RiceTFDB</td>

      <td class='basictd' style="width: 406px; color: rgb(0, 0, 0);">Rice genes involved in transcriptional control</td>

      <td class='basictd' style="width: 361px;"><font color="#9999ff"></font><font color="#9999ff"><a href="http://ricetfdb.bio.uni-potsdam.de/v2.1/" mce_href="http://ricetfdb.bio.uni-potsdam.de/v2.1/" rel="nofollow" linktype="raw" linktext="http://ricetfdb.bio.uni-potsdam.de/v2.1/">http://ricetfdb.bio.uni-potsdam.de/v2.1/</a></font></td>

    </tr>

    <tr>

      <td class='basictd' style="width: 98px;"> RIKEN TFdb</td>

      <td class='basictd' style="width: 406px;">Mouse Transcription Factor Db</td>

      <td class='basictd' style="width: 361px;"><a href="http://genome.gsc.riken.jp/TFdb/" mce_href="http://genome.gsc.riken.jp/TFdb/" rel="nofollow" linktype="raw" linktext="http://genome.gsc.riken.jp/TFdb/">http://genome.gsc.riken.jp/TFdb/</a></td>

    </tr>

    <tr>

      <td class='basictd' style="width: 98px;">rSNP</td>

      <td class='basictd' style="width: 406px;">Influence of single nucleotide mutations in     regulatory gene regions</td>

      <td class='basictd' style="width: 361px;"><a href="http://wwwmgs.bionet.nsc.ru/mgs/systems/rsnp/" mce_href="http://wwwmgs.bionet.nsc.ru/mgs/systems/rsnp/" rel="nofollow" linktype="raw" linktext="http://wwwmgs.bionet.nsc.ru/mgs/systems/rsnp/">http://wwwmgs.bionet.nsc.ru/mgs/systems/rsnp/</a></td>

    </tr>

    <tr>

      <td class='basictd' style="width: 98px;">SCPD</td>

      <td class='basictd' style="width: 406px;">S. cerevisiae Promoter Db</td>

      <td class='basictd' style="width: 361px;"><a href="http://rulai.cshl.edu/SCPD/" mce_href="http://rulai.cshl.edu/SCPD/" rel="nofollow" linktype="raw" linktext="http://rulai.cshl.edu/SCPD/">http://rulai.cshl.edu/SCPD/</a></td>

    </tr>

    <tr>

      <td class='basictd' style="width: 98px;">Stanford Encode Project</td>

      <td class='basictd' style="width: 406px;">ENCyclopedia Of DNA Elements</td>

      <td class='basictd' style="width: 361px;"><a href="http://www-shgc.stanford.edu/genetics/encode.html" mce_href="http://www-shgc.stanford.edu/genetics/encode.html" rel="nofollow" linktype="raw" linktext="http://www-shgc.stanford.edu/genetics/encode.html">http://www-shgc.stanford.edu/genetics/encode.html</a></td>

    </tr>

    <tr>

      <td class='basictd' style="width: 98px;">transcription factors dd</td>

      <td class='basictd' style="width: 406px;"> transcription factors of humans and other organisms</td>

      <td class='basictd' style="width: 361px;"><a href="http://www.proteinlounge.com/trans_home.asp" mce_href="http://www.proteinlounge.com/trans_home.asp" rel="nofollow" linktype="raw" linktext="http://www.proteinlounge.com/trans_home.asp">http://www.proteinlounge.com/trans_home.asp</a><br>

*Note: a subscription is required to view search results</td>

    </tr>

    <tr>

      <td class='basictd' style="width: 98px;">TRANSFAC</td>

      <td class='basictd' style="width: 406px;">eukaryotic transcription factors and their binding profiles</td>

      <td class='basictd' style="width: 361px;"><a href="http://www.gene-regulation.de/" mce_href="http://www.gene-regulation.de/" rel="nofollow" linktype="raw" linktext="http://www.gene-regulation.de/">http://www.gene-regulation.de/</a><br>

*Note: Downloads from the public version are not available</td>

    </tr>

    <tr>

      <td class='basictd' style="width: 98px;">TRED</td>

      <td class='basictd' style="width: 406px;">Transcriptional Regulatory Element Database</td>

      <td class='basictd' style="width: 361px;"><a href="http://rulai.cshl.edu/cgi-bin/TRED/tred.cgi?process=home" mce_href="http://rulai.cshl.edu/cgi-bin/TRED/tred.cgi?process=home" rel="nofollow" linktype="raw" linktext="http://rulai.cshl.edu/cgi-bin/TRED/tred.cgi?process=home">http://rulai.cshl.edu/cgi-bin/TRED/tred.cgi?process=home</a></td>

    </tr>

    <tr>

      <td class='basictd' style="width: 98px;">TRRD</td>

      <td class='basictd' style="width: 406px;">Transcription Regulatory Regions Db</td>

      <td class='basictd' style="width: 361px;"><a href="http://wwwmgs.bionet.nsc.ru/mgs/gnw/trrd/" mce_href="http://wwwmgs.bionet.nsc.ru/mgs/gnw/trrd/" rel="nofollow" linktype="raw" linktext="http://wwwmgs.bionet.nsc.ru/mgs/gnw/trrd/">http://wwwmgs.bionet.nsc.ru/mgs/gnw/trrd/</a></td>

    </tr>

    <tr>

      <td class='basictd' style="width: 98px;">VISTA Enhancer Browser</td>

      <td class='basictd' style="width: 406px;">A database of tissue-specific human enhancers.</td>

      <td class='basictd' style="width: 361px;"><a href="http://enhancer.lbl.gov/" mce_href="http://enhancer.lbl.gov" rel="nofollow" linktype="raw" linktext="http://enhancer.lbl.gov">http://enhancer.lbl.gov</a></td>

    </tr>
</tbody>
</table><br>
Page


# print out the html tail template
my $template_tail = HTML::Template->new(filename => "$pazarcgipath/tail.tmpl");
print $template_tail->output;
