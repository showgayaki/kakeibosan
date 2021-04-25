// window読み込み終了時にローディングアニメーション終了
$(window).on('load', function(){
    hideLoader();
})
// ログイン時にローディングアニメーション表示
$('.form-signin').submit(function(){
    displayLoader();
});
// レコード追加時にローディングアニメーション表示
$(document).on('click', '.to-loading', function(){
    $('.modal').css('display', 'none');
    displayLoader();
});

// ローディングアニメーション表示
function displayLoader(){
    $('.loader').css('display', 'block');
    $('.loader-bg').css('display', 'block');
}

// ローディングアニメーション非表示
function hideLoader(){
    $('.loader').css('display', 'none');
    $('.loader-bg').css('display', 'none');
}