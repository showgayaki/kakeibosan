// ------------------
// 電卓
// ------------------
let calcTmp = 0;
let calcResult = 0;
let operator = '';
let inputStart = true;
let lastKey;//直前に押したキー
processRow = $('#calc-process-row');
resultRow = $('#calc-result-row');
$('.calc-key').on('click', function(){
    let clickKey = $(this).val();
    viewCalc(clickKey);
});

// ------------------
// キーボード操作
// ------------------
$('#calcModal').on('keydown', function(e){
    // マウスカーソルがキー上にあるとエンター押下時にクリックされてしまうのでフォーカス移動
    $('#calcModal').focus();
    // 初期化
    let inputKey = '';
    // Ctrlキー押下時
    if(e.ctrlKey){
        switch(e.keyCode){
            // Ctrl + C
            case 67:
            copyText($('#copy-calc'));
            break;
        }
    }else if(e.shiftKey){
        switch(e.keyCode){
            case 186:
            inputKey = '×';
            break;
            case 187:
            inputKey = '+';
            break;
        }
    }else{
        switch(e.keyCode){
            case 8:
            inputKey = 'backspace';
            break;
            case 13:
            inputKey = '=';
            break;
            case 67:
            inputKey = 'clear';
            break;
            case 48:
            case 96:
            inputKey = '0';
            break;
            case 49:
            case 97:
            inputKey = '1';
            break;
            case 50:
            case 98:
            inputKey = '2';
            break;
            case 51:
            case 99:
            inputKey = '3';
            break;
            case 52:
            case 100:
            inputKey = '4';
            break;
            case 53:
            case 101:
            inputKey = '5';
            break;
            case 54:
            case 102:
            inputKey = '6';
            break;
            case 55:
            case 103:
            inputKey = '7';
            break;
            case 56:
            case 104:
            inputKey = '8';
            break;
            case 57:
            case 105:
            inputKey = '9';
            break;
            case 106:
            inputKey = '×';
            break;
            case 107:
            inputKey = '+';
            break;
            case 109:
            case 189:
            inputKey = '-';
            break;
            case 110:
            case 190:
            inputKey = '.';
            break;
            case 111:
            case 191:
            inputKey = '÷';
            break;
        }
    }
    // 有効なキーが押されたら計算
    if(inputKey !== ''){
        // 演算子はid名に使えないので変換
        switch(inputKey){
            case '+':
            keyName = 'plus';
            break;
            case '-':
            keyName = 'minus';
            break;
            case '×':
            keyName = 'multiply';
            break;
            case '÷':
            keyName = 'divide';
            break;
            case '.':
            keyName = 'dot';
            break;
            case '=':
            keyName = 'equal';
            break;
            default:
            keyName = inputKey;
        }
        // 押したキーの色を変える
        const clickId = '#calc-key_' + keyName;
        $(clickId).addClass('press-calc-key').delay(200).queue(function(next){
            $(clickId).removeClass('press-calc-key');
            next();
        });
        // 計算結果表示
        viewCalc(inputKey);
    }
    console.log('inputKey:' + inputKey + ', keyCode:' + e.keyCode);
});

// ------------------
// 電卓モーダル閉じるときに初期化
// ------------------
$('#calcModal').on('hide.bs.modal', function(){
    $('#calc-process-row').text('');
    $('#calc-result-row').text('0');
    calcTmp = 0;
    calcResult = 0;
    operator = '';
    inputStart = true;
});

// ------------------
// 計算結果表示
// ------------------
function viewCalc(clickKey){
    // Clearキー押下時の処理
    if(clickKey === 'clear'){
        processRow.html('');
        resultRow.html('0');
        calcResult = 0;
        operator = ''
        inputStart = true;
    }else if(clickKey === 'backspace'){
    if(!inputStart){
        // 最後の一文字を削除
        let slice = resultRow.html().slice(0, -1);
        // 表示変更
        resultRow.html(slice);
    }
    }else if(clickKey === '+' || clickKey === '-' || clickKey === '×' || clickKey === '÷' || clickKey === '='){
    inputStart = true;
    calcTmp = Number(resultRow.html());

    if(clickKey === '='){
        // 直前が「＝」キーでなければ計算する
        if(lastKey !== '='){
            inputStart = true;
            calcResult = calc(operator, calcTmp, calcResult);
            // 表示変更
            processRow.html(processRow.html() + resultRow.html() + clickKey + calcResult);
            resultRow.html(calcResult);
        }else{
            return false;
        }
    }else if(operator === '='){// 「=」押下後、引き続き計算するときの処理
        // 表示変更
        processRow.html(processRow.html() + clickKey);
    }else if(lastKey === '+' || lastKey === '-' || lastKey === '×' || lastKey === '÷'){// 演算子を変更したときの処理
        // 表示変更
        processRow.html(processRow.html().slice(0, -1) + clickKey);
    }else{
        calcResult = (operator !== '')? calc(operator, calcTmp, calcResult): Number(resultRow.html());
        // 表示変更
        processRow.html(processRow.html() + resultRow.html() + clickKey);
        resultRow.html(calcResult);
    }
    // 演算子更新
    operator = clickKey;
    }else{// 数字キー押下時の処理
        // 1文字目の入力時
        if(inputStart){
            // ドットが押された場合は、「0.*」にする
            clickKey = (clickKey === '.')? '0' + clickKey: clickKey;
            resultRow.html(clickKey);
            // 入力が0なら再度1文字目とする
            inputStart = (clickKey === '0')? true: false;
            // 「=」押下後、次の計算に入るときは初期化
            if(operator === '='){
            calcTmp = 0;
            calcResult = 0;
            operator= '';
            processRow.html('');
            }
        }else{
            // 2個以上のドットと2個以上の0は許さない
            if((clickKey === '.' && resultRow.html().indexOf('.') !== -1)
            || (clickKey === '0' && resultRow.html() === '0')){
            return false;
            }
            resultRow.html(resultRow.html() + clickKey);
        }
    }
    // コピーボタンのvalue更新
    $('#copy-calc').val(calcResult);
    // 直前に押したキー更新
    lastKey = clickKey;

    // 計算領域でスクロールバーが表示されたら右端までスクロールさせる
    if($(processRow).get(0).scrollWidth > $(processRow)[0].offsetWidth){
        let differnceWidth = $(processRow).get(0).scrollWidth - $(processRow)[0].offsetWidth;
        $(processRow).scrollLeft(differnceWidth);
    }
}

// ------------------
// 四則演算
// ------------------
function calc(ope, tmp, result){
    // IEEE754の誤差回避
    // 小数点位置の最大値を取得
    const tmpDotPosition = getDotPosition(tmp);
    const resultDotPosition = getDotPosition(result);
    const max = Math.max(tmpDotPosition, resultDotPosition);
    // 小数点を含んでいたら大きい方の桁に合わせて整数化、文字列化する
    tmp = (tmp.toString().indexOf('.') !== -1)? Number((tmp.toFixed(max) + '').replace('.', '')): tmp;
    result = (result.toString().indexOf('.') !== -1)? Number((result.toFixed(max) + '').replace('.', '')): result;
    // 10^N の値を計算
    const power = Math.pow(10, max);

    switch(ope){
    case '+':
        result += tmp;
        break;
    case '-':
        result = result - tmp;
        break;
    case '×':
        result = result * tmp;
        break;
    case '÷':
        result = result / tmp;
        break;
    default:
        result = tmp;
    }
    return result / power;
}

// ------------------
// 小数点位置取得
// ------------------
function getDotPosition(val){
    const strVal = String(val);
    let dotPosition = 0;
    // 小数点があったら位置を取得
    if(strVal.lastIndexOf('.') !== -1){
        dotPosition = (strVal.length - 1) - strVal.lastIndexOf('.');
    }
    return dotPosition;
}
