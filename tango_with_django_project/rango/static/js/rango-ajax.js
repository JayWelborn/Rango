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

    $('#suggestion').keyup(function() {
        var query = $(this).val();
        console.log(query)
        $.get('/rango/suggest/', {suggestion: query}, function(data){
            $('#cats').html(data);
        });
    });
});