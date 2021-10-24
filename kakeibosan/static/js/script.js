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
    displayLoader();
});
// ログアウトモーダル表示時にOKボタンにフォーカス。エンターでログアウトできるように。
$('#logoutModal').on('shown.bs.modal', function(){
    $('#logoutOk').trigger('focus');
})
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

// ------------------
// コピー
// ------------------
function copyText(elem){
    // コピー対象のvalueを取得
    const val = elem.val();
    // tdから直接はコピーできないためテキストエリアを経由
    let $textarea = $('<textarea></textarea>');
    $textarea.text(val);
    elem.append($textarea);
    $textarea.select();
    // コピーしてtextareaは削除
    const copyResult = document.execCommand('copy');
    $textarea.remove();
    // コピー結果によって表示変更
    if(copyResult){
    elem.attr('data-original-title', 'コピーしました');
    }else{
    elem.attr('data-original-title', 'コピー失敗しました');
    }
    // tooltip表示
    elem.tooltip('show');
}
