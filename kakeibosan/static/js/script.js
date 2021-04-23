// ログイン時にローディングアニメーション表示
$('.form-signin').submit( function(){
    displayLoader();
});
// レコード追加時にローディングアニメーション表示
$(document).on('click', '.to-loading', function(){
    $('.modal').css('display', 'none');
    displayLoader();
});

function displayLoader(){
    $('.loader').css('display', 'block');
    $('.loader-bg').css('display', 'block');
}
