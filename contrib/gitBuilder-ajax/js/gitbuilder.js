$.ajaxSetup({
	async: true,
});


$(document).ready(function(){
	var length = urls.length
	for(var i =0; i<length; i++){
		summarizeUrls(urls[i], i);
	}			
});
	
	
function summarizeUrls(link, i){
	if (typeof serverUrl !== 'undefined') {
		$.getJSON(serverUrl + "?url=" + link + "&callback=?", function(d){
			var d = d.html;
			summaryRow(link, d);
			checkStatus();
		});
	} else {
		$.get(link,function(d){
			summaryRow(link, d);
			checkStatus();
		});
	}
}


function summaryRow(link, d) {
	var mostrecent = $(d).filter("#most_recent").html().replace("Most Recent:","").replace(/<a href="#/g,'<a href="' + link + '#');
	var url = "<a class='normalLink' href='" + link + "'>" + link + "</a>";
	var row = "<tr><td>" + url + "</td><td><div class='most_recent'>" + mostrecent + "</div></td></tr>";
	$("#links tbody").append(row);
}


function checkStatus(){
	$("span").each(function(index) {
		if($(this).hasClass("status-err")){
			$(this).parent().addClass("btn btn-danger btn-mini")
		}
		if($(this).hasClass("status-ok")){
			$(this).parent().addClass("btn btn-success btn-mini")
		}
		if($(this).hasClass("status-warn")){
			$(this).parent().addClass("btn btn-warning btn-mini")
		}
			if($(this).hasClass("status-pending")){
			$(this).parent().addClass("btn btn-mini")
		}
	});
}
