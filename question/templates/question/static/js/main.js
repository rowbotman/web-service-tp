function like() {
    var like = $(this);
    var type = like.data('type');
    var pk = like.data('id');  
    var action = like.data('action');
    var dislike = like.next();
    const csrfToken = $.cookie('csrftoken');
    if (type == 'comment') {
    	$(".for-remove").addClass('correct-answer');
    	$(".for-remove").hide();
    	$(".for-show-" + pk).removeAttr('style').show()
    }
    $.ajax({
        url : "/api/" + type +"/" + pk + "/" + action + "/",
        type : 'POST',
        data : { 'obj' : pk },
        headers: {'X-CSRFToken': csrfToken},
 
        success : function (json) {
            like.find("[data-count='sum_rating']").text(json.sum_rating_count);
            dislike.find("[data-count='dislike']").text(json.dislike_count);
        }
    });
 
    return false;
}
 
function dislike() {
    var dislike = $(this);
    var type = dislike.data('type');
    var pk = dislike.data('id');  // pk ?
    var action = dislike.data('action');
    var like = dislike.prev();
    const csrfToken = $.cookie('csrftoken');
 
    $.ajax({
        url : "/api/" + type +"/" + pk + "/" + action + "/",
        type : 'POST',
        data : { 'obj' : pk },
        headers: {'X-CSRFToken': csrfToken},
 
        success : function (json) {
            dislike.find("[data-count='dislike']").text(json.dislike_count);
            like.find("[data-count='like']").text(json.like_count);

        }
    });
 
    return false;
}

// function choose() {
// 	var choose = $(this)
// 	var type = choose.data('type')
// 	var pk = choose.data('id')
// 	var action = choose.data('action');
//     const csrfToken = $.cookie('csrftoken');
//     $.ajax({
//         url : "/api/" + type +"/" + pk + "/" + action + "/",
//         type : 'POST',
//         data : { 'obj' : pk },
//         headers: {'X-CSRFToken': csrfToken},
 
//         success : function (json) {
//             choose.find("[data-count='dislike']").text(json.dislike_count);
//         }
//     });
 
//     return false;
// }

// Подключение обработчиков
$(function() {
    $('[data-action="like"]').click(like);
    $('[data-action="dislike"]').click(dislike);
    // $('[data-action="choose"]').click(choose);
});
