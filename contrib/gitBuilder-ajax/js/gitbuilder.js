$.ajaxSetup({
	async: true,
});


$(document).ready(function(){
	var length = urls.length
	for(var i =0; i<length; i++){
		summarizeUrls(urls[i], i);
	}			
});
	
	
function summarizeUrls(url, i){
	var link = url;
	
	if (typeof serverUrl !== 'undefined') {
		$.getJSON(serverUrl + "?url=" + url + "&callback=?", function(d){
			var d = d.html;
			summaryRow(link, d);
			checkStatus();
			makeShowLinks();
			makeHideLinks();
		});
	} else {
		$.get(url,function(d){
			summaryRow(link, d);
			checkStatus();
			makeShowLinks(link);
			makeHideLinks();
		});
	}
}


function summaryRow(link, d) {
	var mostrecent = $(d).filter("#most_recent").html().replace("Most Recent:","").replace(/<a href="#/g,'<a href="' + link + '#');
	var url = "<a class='normalLink' href='" + link + "'>" + link + "</a>";
	var btn = "<a title='Show it here' href='" + link + "' class='btn showDetails'>Show</a>";
	var btn2 = "<a title='hide it' href='#' class='btn hideBtn'>Hide</a>";
	var row = '<tr><td>' + url + "</td><td><div class='most_recent'>" + mostrecent + "</div></td><td class='butColumn'>" + btn + btn2 + "</td></tr>";
	$("#links tbody").append(row);
}


function makeHideLinks(){
	$(".hideBtn").click(function(){
		$(".empt").empty();
		$(this).hide();
		$(this).prev().show();
	})
}


function makeShowLinks(link){
	$(".showDetails").click(function(event){
		event.preventDefault();
		
		$(this).hide();
		$(this).next().show();
		
		$(".empt").empty();
		if (typeof serverUrl !== 'undefined') {
			var data = serverUrl + "?url=" + $(this).attr("href") + "&callback=?";
			$.getJSON(data,function(d){
				var d = d.html;
				$(".empt").append(d);
				$(".empt table").addClass("table table-striped table-bordered");
			});
		} else {
			var data = $(this).attr("href");
			$.get(data,function(d){
				$(".empt").append(d);
				$(".empt table").addClass("table table-striped table-bordered");
			});
		}
	});
}


function checkStatus(){
	$("span").each(function(index) {
		if($(this).hasClass("status-err")){
			$(this).parent().addClass("btn btn-danger")
		}
		if($(this).hasClass("status-ok")){
			$(this).parent().addClass("btn btn-success")
		}
		if($(this).hasClass("status-warn")){
			$(this).parent().addClass("btn btn-warning")
		}
			if($(this).hasClass("status-pending")){
			$(this).parent().addClass("btn")
		}
	});
}
