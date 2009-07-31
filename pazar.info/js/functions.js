var pazar_cgi = "/cgi-bin";
function showHideGeneList(inputID) {
	var theObj = document.getElementById(inputID);
	theDisp = theObj.style.display == "none" ? "block" : "none";
	theObj.style.display = theDisp;
	if (theObj.getAttribute("loaded") == "no") {
		var prev = theObj.innerHTML;
		theObj.setAttribute("loaded","yes");
		if (theObj.getAttribute("genes") < 1000) {
			theObj.innerHTML = prev + "<div class='p20lo p20bo'><div class='b p5'>Loading data now...</div></div>";
			getgenes(inputID);
		} else {
			theObj.innerHTML = prev + "<div class='p20lo p20bo'><div class='b p5'>This project contains more than 1,000 genes. It can take a while for the genes to display. <input type='button' value='Load genes anyway' onclick=\"getgenes('"+inputID+"');\"></div></div>";
		}
	}
}
function getgenes(divId) {
	var divObj = document.getElementById(divId);
	var http = false;
	if (divObj.getAttribute("genes") > 1000) {
		divObj.innerHTML = "<div class='p20lo p20bo'><div class='b p5'>Loading data now...</div></div>";
	}
	if (navigator.appName == "Microsoft Internet Explorer") {
		http = new ActiveXObject("Microsoft.XMLHTTP");
	} else {
		http = new XMLHttpRequest();
	}
	var args = "project_id=" + divObj.getAttribute("project_id");
	if (divId.match("markers"+"\$")) {
		args += "&table=marker";
	} else {
		args += "&table=gene_source";
	}
	http.open("POST", "proj2gene_list.pl",true);
	http.setRequestHeader("Content-type", "application\/x-www-form-urlencoded");
	http.setRequestHeader("Content-length", args.length);
	http.setRequestHeader("Connection", "close");
	http.onreadystatechange = function() {
		if (http.readyState == 4) {
			divObj.innerHTML=http.responseText;
			for (j=0; j<divObj.childNodes.length; j++) {
				if( divObj.childNodes[j].tagName == 'TABLE' ) {
					ts_makeSortable(divObj.childNodes[j]);
				}
			}
		}
	}
	http.send(args);
}

function correctSubmitHandler(e) {
	if (e && e.preventDefault)
		e.preventDefault();
	return false;
}
function NewOption(arg){
	//alert('The pager number & (val)')
	var args=arg.split(":");
	st=document.getElementById('start');
	st.value=args[2];
	endel=document.getElementById('end');
	endel.value=args[3];
	chrel=document.getElementById('chromosome');
	chrel.value=args[0];
	orgrel=document.getElementById('organism');
	orgrel.value=args[4];
	buildrel=document.getElementById('build');
	buildrel.value=args[5];
	seqrel=document.getElementById('sequence');
	seqrel.value=args[6];
	trel=document.getElementById('tid');
	trel.value=args[8];
	fstrel=document.getElementById('fstart');
	fstrel.value=args[9];
	fendrel=document.getElementById('fend');
	fendrel.value=args[10];
	gidrel=document.getElementById('gid');
	gidrel.value=args[7];
	strrel=document.getElementById('str');
	strrel.value=args[1];
	giddesc=document.getElementById('giddesc');
	giddesc.value=args[11];
}
function MM_callJS(jsStr) { //v2.0
	return eval(jsStr)
}

function MM_popupMsg(msg) { //v1.0
	alert(msg);
}
function MM_openBrWindow(theURL,winName,features) { //v2.0
	window.open(theURL,winName,features);
}
function onoff(objref) {
	if (objref.disabled==true ) {
		objref.disabled=false;} 
	else {
		objref.disabled=true;}
	return;
}
function MM_findObj(n, d) { //v4.01
  var p,i,x;  if(!d) d=document; if((p=n.indexOf("?"))>0&&parent.frames.length) {
    d=parent.frames[n.substring(p+1)].document; n=n.substring(0,p);}
  if(!(x=d[n])&&d.all) x=d.all[n]; for (i=0;!x&&i<d.forms.length;i++) x=d.forms[i][n];
  for(i=0;!x&&d.layers&&i<d.layers.length;i++) x=MM_findObj(n,d.layers[i].document);
  if(!x && d.getElementById) x=d.getElementById(n); return x;
}
function MM_validateForm() { //v4.0
  var i,p,q,nm,test,num,min,max,errors='',args=MM_validateForm.arguments;
  for (i=0; i<(args.length-2); i+=3) { test=args[i+2]; val=MM_findObj(args[i]);
    if (val) { nm=val.name; if ((val=val.value)!="") {
      if (test.indexOf('isEmail')!=-1) { p=val.indexOf('@');
        if (p<1 || p==(val.length-1)) errors+='- '+nm+' must contain an e-mail address.\n';
      } else if (test!='R') { num = parseFloat(val);
        if (isNaN(val)) errors+='- '+nm+' must contain a number.\n';
        if (test.indexOf('inRange') != -1) { p=test.indexOf(':');
          min=test.substring(8,p); max=test.substring(p+1);
          if (num<min || max<num) errors+='- '+nm+' must contain a number between '+min+' and '+max+'.\n';
    } } } else if (test.charAt(0) == 'R') errors += '- '+nm+' is required.\n'; }
  } if (errors) alert('The following error(s) occurred:\n'+errors);
  document.MM_returnValue = (errors == '');
}
resetMenu = function() {
   var ddm=document.getElementsByTagName("select");
   for (var n=0; n<ddm.length; n++) {
      ddm[n].selectedIndex=0;
   }
}
function ActivateCheckBox () {
	document.form.pubmedid.disabled = false;
	if (document.form.published.value == 'Yes') {
		document.form.pubmedid.disabled = false;
	} else {
		document.form.pubmedid.disabled = true;
	}
}
function setCountEntryPl(target){
	if (document.MM_returnValue) {
		if (target == 0) {
			document.F1.action = pazar_cgi+"/sWI/geneselect.cgi";
			document.F1.target = "_self";
		}
		if (target == 1) {
			document.F1.action = pazar_cgi+"/sWI/psite_get.cgi";
			document.F1.target = "_self";
		}
	}
}
function doDelete(pid) {
	var decision = confirm("Do you really want to delete this project? Doing so will remove all public and private stored data for this project as well.");
	if (decision == true) {
		eval("document.deleteform"+pid+".submit();");       
	}
}
function doUserAdd(pid) {
	var decision = confirm("This will permanently add this user to the project. He/she will be able to change the project status. Do you wish to continue?");
	if (decision == true) {
		eval("document.useraddform"+pid+".submit();");
	}
}
function doUpdateDesc(pid) {
	var decision = confirm("This will permanently change the project description. Do you wish to continue?");
	var descLength = eval("document.updatedescform"+pid+".projdesc.value.length");
	if (decision == true) {	
		if (descLength <2001) {
			eval("document.updatedescform"+pid+".submit();");
		} else {
			alert("Please ensure that description is no more than 2000 characters (Currently "+descLength+" characters)");
		}
	}
}

// function CheckMaxLength(Object, MaxLen) {
// 	if (Object.value.length > MaxLen) {     
// 		alert("");
// 	} else {
// 		form.submit();
// 	}
// }

function verifyProjectCreate() {
	var themessage = "You are required to complete the following fields: ";
	var iChars = "!@#$%^&*()+=-[]\\\';,./{}|\":<>?";
	var pnameSpecialChar = 0;
	if (document.createprojectform.projname.value=="") {
		themessage = themessage + "\\n - User Name";
	}
	if (document.createprojectform.projpass.value=="") {
		themessage = themessage + "\\n -  Project password";
	}
	if (document.createprojectform.projpasscheck.value=="") {
		themessage = themessage + "\\n -  Project password re-entry";
	}
	if (themessage == "You are required to complete the following fields: ") {
		themessage = "";
	}
	if (document.createprojectform.projpasscheck.value != document.createprojectform.projpass.value) {
		if (themessage == "") {
			themessage = "Passwords do not match. Please check them";
		} else {
			themessage = themessage + "\\n Passwords do not match, please check them";
		}
	}
	for (var i = 0; i < document.createprojectform.projname.value.length; i++) {
		if (iChars.indexOf(document.createprojectform.projname.value.charAt(i)) != -1) {
			pnameSpecialChar = 1;	   
		}
	}
	if (pnameSpecialChar == 1) {
		themessage = themessage + "\\nThe entered project name contains special characters. \nThese are not allowed. Please choose a different project name\n";
	}
	//alert if fields are empty and cancel form submit
	if (themessage == "") {
		var descLength = document.createprojectform.projdesc.value.length;
		if(descLength < 2001) {
			document.createprojectform.submit();
		} else {
			alert("Please ensure that description is no more than 2000 characters (Currently "+descLength+" characters)");
		}
	} else {
		alert(themessage);
		return false;
	}
}
function showHide(inputID) {
	theObj = document.getElementById(inputID)
	theDisp = theObj.style.display == 'none' ? 'block' : 'none'
	theObj.style.display = theDisp
}
function myXMLHttpRequest() {
	var xmlhttplocal;
	try {
		xmlhttplocal = new ActiveXObject("Msxml2.XMLHTTP")
	} catch (e) {
		try {
			xmlhttplocal = new ActiveXObject("Microsoft.XMLHTTP")
		} catch (E) {
			xmlhttplocal = false;
		}
	}
	if (!xmlhttplocal && typeof XMLHttpRequest != 'undefined') {
		try {
			var xmlhttplocal = new XMLHttpRequest();
		} catch (e) {
			var xmlhttplocal = false;
		}
	}
	return(xmlhttplocal);
}
function xGetElementById(e) {
	if (typeof(e)=="string") {
		if (document.getElementById) {
			e=document.getElementById(e);
		} else if (document.all) {
			e=document.all[e];
		} else { 
			e=null;
		}
	}
	return e;
}

function VersionNavigateur(Netscape, Explorer) {
	if ((navigator.appVersion.substring(0, 3) >= Netscape && navigator.appName == 'Netscape') || (navigator.appVersion.substring(0, 3) >= Explorer && navigator.appName.substring(0, 9) == 'Microsoft')) {
		return true; 
	}
	else {
		return false; 
	}
}
function ajaxcall (tableId, divTarget, all) {
	var divObj = xGetElementById(divTarget); 
	divObj.innerHTML = "<div class='emp'>Generating PFM, please wait...</div>"; 
	var xhttp = new myXMLHttpRequest(); 
	tableObj = xGetElementById(tableId); 
	sites = 0; 
	args = "caller=tfsearch"; 
	var tbody = tableObj.getElementsByTagName("tbody"); 
	var trs = tbody[0].getElementsByTagName("tr"); 
	for (x = 1; x < trs.length; x++) {
		tds = trs[x].getElementsByTagName("td"); 
		cb = tds[0].firstChild.firstChild; 
		if ((cb.checked == true) || (all == 1)) {
			args += "&seq=" + cb.value; 
			sites++; 
		}
	}
	if (sites == 0) {
		tableObj = xGetElementById("sml"+tableId); 
		tbody = tableObj.getElementsByTagName("tbody"); 
		trs = tbody[0].getElementsByTagName("tr"); 
		for (x = 1; x < trs.length; x++) {
			tds = trs[x].getElementsByTagName("td"); 
			cb = tds[0].firstChild.firstChild; 
			if ((cb.checked == true) || (all == 1)) {
				args += "&seq=" + cb.value; 
				sites++; 
			}
		}
	}
	// pass the tf name to ajax page
	var tfnameDivObj = xGetElementById("Hidden"+tableId); 
	args += "&tfname=" + tfnameDivObj.innerHTML + "&tfpid=" + tableId;
	if (sites < 2) {
		divObj.innerHTML = "<div class='emp'>There are not enough targets to build a binding profile for this TF.</div>";
	}
	xhttp.open("POST", "meme_call.pl", true);
	xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	xhttp.setRequestHeader("Content-length", args.length);
	xhttp.setRequestHeader("Connection", "close");
	xhttp.onreadystatechange=function() {
		if (xhttp.readyState==4) {
			outputData = xhttp.responseText;
			divObj.innerHTML = outputData; 
		}
	}	
	xhttp.send(args); 
}
function multiTF (divTarget) {
	divObj = xGetElementById(divTarget); 
	divObj.innerHTML = "Generating PFM, please wait..."; 
	var http = false; 
	args = "caller=tfsearch"; 
	var divs = document.getElementsByTagName("div");
	for (i = 0; i < divs.length; i++) {
		if (divs[i].className == "seqTableDiv") {
			baseName = divs[i].id; 
			baseName = baseName.replace(/desc/,"");
			sites = 0; 
			tableObj = xGetElementById(baseName); 
			var tbody = tableObj.getElementsByTagName("tbody"); 
			var trs = tbody[0].getElementsByTagName("tr"); 
			for (x = 1; x < trs.length; x++) {
				tds = trs[x].getElementsByTagName("td"); 
				cb = tds[0].firstChild.firstChild; 
				if (cb.checked == true) {
					args += "&seq=" + cb.value; 
					sites++; 
				}
			}
			if (sites == 0) {
				tableObj = xGetElementById("sml"+baseName); 
				tbody = tableObj.getElementsByTagName("tbody"); 
				trs = tbody[0].getElementsByTagName("tr"); 
				for (x = 1; x < trs.length; x++) {
					tds = trs[x].getElementsByTagName("td"); 
					cb = tds[0].firstChild.firstChild; 
					if (cb.checked == true) {
						args += "&seq=" + cb.value; 
					}
				}
			}
		}
	}
	if (navigator.appName == "Microsoft Internet Explorer") {
		http = new ActiveXObject("Microsoft.XMLHTTP"); 
	}
	else {
		http = new XMLHttpRequest(); 
	}
	http.open("POST", "meme_call.pl", true); 
	http.setRequestHeader("Content-type", "application/x-www-form-urlencoded"); 
	http.setRequestHeader("Content-length", args.length); 
	http.setRequestHeader("Connection", "close"); 
	http.onreadystatechange = function() {
		if (http.readyState == 4) {
			divObj.innerHTML = http.responseText; 
		}
	}
	http.send(args); 
}
document.getElementsByClassName = function(cl) {
	var retnode = []; 
	var myclass = new RegExp('\\b' + cl + '\\b'); 
	var elem = this.getElementsByTagName('*'); 
	for (var i = 0; i < elem.length; i++) {
		var classes = elem[i].className; 
		if (myclass.test(classes)) retnode.push(elem[i]); 
	}
	return retnode; 
}; 
function setCount(target) {
	if (target == 0) {
		document.tf_search.action = pazar_cgi+"/tf_list.cgi"; 
		document.tf_search.target = "Window1"; 
		window.open('about:blank', 'Window1', 'resizable=1,scrollbars=yes, menubar=no, toolbar=no directories=no, height=800, width=800'); 
	}
	if (target == 1) {
		document.tf_search.target = "_self"; 
	}
	if (target == 2) {
		document.tf_search.action = pazar_cgi+"/tfbrowse_alpha.pl"; 
		document.tf_search.target = "Window2"; 
		window.open('about:blank', 'Window2', 'resizable=1,scrollbars=yes, menubar=no, toolbar=no directories=no, height=600, width=650'); 
	}
}
function verifyCheckedBoxes() {
	var numChecked = 0; 
	var counter; 
	// iterate through sequenceform elements
	for(counter = 0; counter < document.sequenceform.length; counter++) {
		if (document.sequenceform.elements[counter].checked) {
			numChecked++; 
		}
	}
	if (numChecked < 2) {
		alert('You must select at least 2 sequences. Number of sequences selected: ' + numChecked); 
	}
	else {
		window.open('about:blank', 'logowin', 'resizable=1,scrollbars=yes, menubar=no, toolbar=no directories=no, height=600, width=600'); 
		document.sequenceform.submit(); 
	}
}
function selectallseq (tableId) {
	tableObj = xGetElementById(tableId); 
	var tbody = tableObj.getElementsByTagName('tbody'); 
	var trs = tbody[0].getElementsByTagName('tr'); 
	for (x = 1; x < trs.length; x++) {
		tds = trs[x].getElementsByTagName('td'); 
		cb = tds[0].firstChild.firstChild; 
		cb.checked = true; 
	}
	tableObj2 = xGetElementById("sml" + tableId); 
	var tbody2 = tableObj2.getElementsByTagName('tbody'); 
	var trs2 = tbody2[0].getElementsByTagName('tr'); 
	for (x = 1; x < trs2.length; x++) {
		tds2 = trs2[x].getElementsByTagName('td'); 
		cb2 = tds2[0].firstChild.firstChild; 
		cb2.checked = true; 
	}
}
function resetallseq (tableId) {
	tableObj = xGetElementById(tableId); 
	var tbody = tableObj.getElementsByTagName('tbody'); 
	var trs = tbody[0].getElementsByTagName('tr'); 
	for (x = 1; x < trs.length; x++) {
		tds = trs[x].getElementsByTagName('td'); 
		cb = tds[0].firstChild.firstChild; 
		cb.checked = false; 
	}
	tableObj2 = xGetElementById("sml" + tableId); 
	var tbody2 = tableObj2.getElementsByTagName('tbody'); 
	var trs2 = tbody2[0].getElementsByTagName('tr'); 
	for (x = 1; x < trs2.length; x++) {
		tds2 = trs2[x].getElementsByTagName('td'); 
		cb2 = tds2[0].firstChild.firstChild; 
		cb2.checked = false; 
	}
}
function selectbytype (tableId, target) {
	tableObj = xGetElementById(tableId); 
	var tbody = tableObj.getElementsByTagName("tbody"); 
	var trs = tbody[0].getElementsByTagName("tr"); 
	for (x = 1; x < trs.length; x++) {
		if (trs[x].className == target) {
			tds = trs[x].getElementsByTagName("td"); 
			cb = tds[0].firstChild.firstChild; 
			cb.checked = true; 
		}
	}
	tableObj2 = xGetElementById("sml"+tableId); 
	var tbody2 = tableObj2.getElementsByTagName("tbody"); 
	var trs2 = tbody2[0].getElementsByTagName("tr"); 
	for (x = 1; x < trs2.length; x++) {
		if (trs2[x].className == target) {
			tds2 = trs2[x].getElementsByTagName("td"); 
			cb2 = tds2[0].firstChild.firstChild; 
			cb2.checked = true; 
		}
	}
}
function init () {
	var divs = document.getElementsByTagName("div"); 
	for (i = 0; i < divs.length; i++) {
		if (divs[i].className == "seqTableDiv") {
			baseName = divs[i].id; 
			baseName = baseName.replace(/^desc/,"");
			try {
				ajaxcall(baseName,"memediv"+baseName, 1); 
			}
			catch (err) {
				alert(err); 
			}
		}
	}
}
function confirm_entry(tfid) {
	input_box = confirm("Are you sure you want to delete this TF?"); 
	if (input_box == true) {
		// submit tfid to delete page
		location.href = "deletetf.pl?tfid=" + tfid; 
	}
}
function toggleRows(sname, snumb, stotal) {
	for (var i = 1; i <= stotal; i++) {
		document.getElementById(i + "_" + sname).className = "hide"; 
	}
	document.getElementById(snumb + "_" + sname).className = "show"; 
}
function moveXY(obj, x, y) {
	//	obj = getStyleObject(myObject);
	obj.style.top = y + "px";
 	obj.style.left = x + "px";
}
function findPos(obj) {
	var curleft = curtop = 0;
	if (obj.offsetParent) {
		do {
			curleft += obj.offsetLeft;
			curtop += obj.offsetTop;
		} while (obj = obj.offsetParent);
		return [curleft,curtop];
	}
}
function popup(loca,text,poic) {
	xy = findPos(loca);
	pop = document.getElementById("popup");
	poi = document.getElementById("popin");
	pot = document.getElementById("popte");
	moveXY(pop, xy[0], xy[1]);
	pop.className="show";
	pot.className=poic;
	pot.innerHTML=text;
}
function popcl() {
	pop = document.getElementById("popup");
	pop.className="hide";
}
var state=0;
function CheckBox() {
	if (state == 1) {
		document.filters.chr_filter.checked = false;
		state = 0;
	}
	if (state == 0) {
		document.filters.chr_filter.checked = true;
		state = 1;
	}
}
function toche(chek,tdiv) {
	if (chek.checked == true) {
		document.getElementById(tdiv).className="show";
	} else {
		document.getElementById(tdiv).className="hide";
	}
}

function confirm_entry_seq_search(seqid,projid) {
	input_box=confirm("Are you sure you want to delete this sequence?");
	if (input_box==true) { 
		// submit sequence id to delete page
		location.href="deleteseq.pl?sid="+seqid+"&pid="+projid;
	}
}

function setCount_seq_search(target) {
	if (target == 0) {
		document.gene_search.action = pazar_cgi+"/gene_list.cgi";
		document.gene_search.target = "Window1";
		window.open('about:blank','Window1', 'scrollbars=yes, menubar=no, toolbar=no directories=no, height=800, width=800');
	}
	if (target == 1) {
		var myTextField = document.getElementById('ID_list');
		if (myTextField.value == "PAZAR_seq") {
			document.gene_search.target = "_self";
			document.gene_search.action = pazar_cgi+"/seq_search.cgi";
		} else {
			document.gene_search.target = "_self";
			document.gene_search.action = pazar_cgi+"/gene_search.cgi";
		}
	}
	if(target == 2) {
		document.gene_search.action = pazar_cgi+"/genebrowse_alpha.pl";
		document.gene_search.target="Window2";
		window.open('about:blank','Window2', 'resizable=1,scrollbars=yes, menubar=no, toolbar=no directories=no, height=600, width=650');
	}
}

function setCount_exp_search(target) {
	if (target == 0) {
		document.gene_search.action = pazar_cgi+"/gene_list.cgi";
		document.gene_search.target = "Window1";
		window.open('about:blank','Window1','scrollbars=yes,menubar=no,toolbar=no directories=no,height=800,width=800');
	}
	if (target == 1) {
		var myTextField = document.getElementById('ID_list');
		if (myTextField.value == "PAZAR_seq") {
			document.gene_search.target = "_self";
			document.gene_search.action = pazar_cgi+"/seq_search.cgi";
		} else {
			document.gene_search.target = "_self";
			document.gene_search.action = pazar_cgi+"/gene_search.cgi";
		}
	}
	if (target == 2) {
		document.gene_search.action = pazar_cgi+"/genebrowse_alpha.pl";
		document.gene_search.target = "Window2";
		window.open('about:blank','Window2','resizable=1,scrollbars=yes,menubar=no,toolbar=no directories=no,height=600,width=650');
	}
}

function confirm_entry_exp_search(aid,projid) {
	input_box = confirm("Are you sure you want to delete this analysis?");
	if (input_box == true) { 
		// Submit analysis id to delete page...
		location.href="deleteanalysis.pl?aid="+aid+"&pid="+projid;
	}
}