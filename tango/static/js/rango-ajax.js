$(document).ready(function() {

    $('#likes').click(function() {
        var catid;
        catid = $(this).attr("data-catid");
        $.get('/rango/like_category/', {category_id: catid}, function(data) {
            $('#like_count').html(data);
            $('#likes').hide();
        });
    });

    $('#suggestion').keyup(function() {
        var query;
        query = $(this).val();
        $.get('/rango/suggest_category/', {query: query}, function(data) {
            $('#cats').html(data);
        });
    });

	$("#search_results").on("click", "button.btn", function(event) {
        event.preventDefault();
        event.stopPropagation();
    	var catid, title, url;
    	catid = $(this).attr("data-catid");
    	title = $(this).attr("data-title");
    	url = $(this).attr("data-url");
    	$.get('/rango/auto_add_page/', 
    		{catid: catid, title: title, url: url},
    		function(data){
    			$('#pages').html(data);
    		});
    });

});
