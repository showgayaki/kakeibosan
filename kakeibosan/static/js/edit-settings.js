const subcategorySelect = document.getElementById('subcategorySelect');

if(subcategorySelect != null){
    window.addEventListener('load', displayToggleSubcategoryOptions, false);

    const categorySelect = document.getElementById('categorySelect');
    categorySelect.addEventListener('change', displayToggleSubcategoryOptions, false);
}


const chartColorText = document.getElementById('settingsChartColorText');
const colorPicker = document.getElementById('settingsColorPicker');

if(chartColorText != null && colorPicker != null){
    // ページ表示時にはchartColorTextに値が挿入されるので、その色をcolorPickerに反映させる
    window.addEventListener('load', function(){
        colorPicker.value = colorCode(chartColorText.value);
    }, false);

    // colorPickerで色選択時にchartColorTextに反映させる
    colorPicker.addEventListener('input', function(){
        chartColorText.value = colorPicker.value;
    }, false)

    // カラーコード手入力時の処理
    chartColorText.addEventListener('input', function(){
        let colorCode = colorCode(chartColorText.value)
        if(colorCode != undefined){
            colorPicker.value = colorCode;
        }
    }, false)
}


function colorCode(text){
    if(text.match('^#([0-9a-fA-F]{3})$')){
        // 短縮系カラーコードのときの処理
        // #000 なら #000000の形にする
        let red = text[1].repeat(2);
        let green = text[2].repeat(2);
        let blue = text[3].repeat(2);
        // #001122の形でカラーピッカーのvalueに入れる
        return text[0] + red + green + blue
    }else if(text.match('^#([0-9a-fA-F]{6})$')){
        return text
    }else if(text == ''){
        return '#000000'
    }
}


function displayToggleSubcategoryOptions(event){
    // categoryは、「<option value="1">固定費</option>」の形
    let categoryId = categorySelect.value;

    for(let i = 0; i < subcategorySelect.options.length; i++){
        // subcategoryは「<option value="1-3">管理費</option>」という形になっているので、
        // 「-」でsplitして親idを取得
        let parent = subcategorySelect.options[i].value.split('-')[0]

        // 親idが一致しないoptionは非表示にする(value: 0 の「選択してください」は除く)
        if(parent != '' && categoryId != parent){
            subcategorySelect.options[i].classList.add('d-none');
        }else{
            subcategorySelect.options[i].classList.remove('d-none');
        }
    }

    // changeイベントの時は、サブカテゴリーを「選択してください」にしておく
    if(event.type == 'change'){
        subcategorySelect.value = '';
    }
}
