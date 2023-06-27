window.addEventListener('load', displayToggleSubcategoryOptions, false);

const categorySelect = document.getElementById('categorySelect');
categorySelect.addEventListener('change', displayToggleSubcategoryOptions, false);


function displayToggleSubcategoryOptions(event){
    const subcategorySelect = document.getElementById('subcategorySelect');
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
