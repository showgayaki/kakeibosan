window.addEventListener('load', displayToggleSubcategoryOptions, false);

const category = document.getElementById('category');
category.addEventListener('change', displayToggleSubcategoryOptions, false);


function displayToggleSubcategoryOptions(event){
    const subcategory = document.getElementById('subcategory');
    // categoryは、「<option value="1">固定費</option>」の形
    let categoryId = category.value;

    for(let i = 0; i < subcategory.options.length; i++){
        // subcategoryは「<option value="1-3">管理費</option>」という形になっているので、
        // 「-」でsplitして親idを取得
        let parent = subcategory.options[i].value.split('-')[0]

        // 親idが一致しないoptionは非表示にする(value: 0 の「選択してください」は除く)
        if(parent != '' && categoryId != parent){
            subcategory.options[i].classList.add('d-none');
        }else{
            subcategory.options[i].classList.remove('d-none');
        }
    }

    // changeイベントの時は、サブカテゴリーを「選択してください」にしておく
    if(event.type == 'change'){
        subcategory.value = '';
    }
}
