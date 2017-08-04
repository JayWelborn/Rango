// don't start script until DOM is fully loaded
$(document).ready(function() {
    // ensure script is loaded
    console.log('Hi');

    $('#likes').click(function(){
        // gets category ID from HTML attribute generated
        // by django in the template
        var catid = $(this).attr("data-catid")

        $.get('/rango/like', {cat_id: catid}, function(data) {
            console.log(data)
            $('#like_count').text(data);
            $('#likes').hide();
        });
    });

    $('.add_page').click(function(){
        // adds page to category
        
        var url = $(this).attr("data-url")
        var name = $(this).attr("data-name")
        var cat_id = $(this).attr("data-catid")
        var current_button = $(this)

        $.get('/rango/add_page', {url: url, name: name, cat_id: cat_id}, function(data) {
            console.log($(this))
            current_button.next('.page_added').text('Page Added');
            current_button.hide();
            $('#pages').html(data)
        });
    });

    $('#suggestion').keyup(function() {
        var query = $(this).val();
        console.log(query)
        $.get('/rango/suggest/', {suggestion: query}, function(data){
            $('#cats').html(data);
        });
    });
});