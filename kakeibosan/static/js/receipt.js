const receiptImage = document.getElementById('receiptImage');
receiptImage.addEventListener('change', {handleEvent: postFile}, false);


async function postFile(e){
    e.stopPropagation();
    e.preventDefault();

    // ローディングアニメーション表示
    displayLoader();

    // アップロードデータ
    const formData = new FormData();
    formData.append('receiptImage', receiptImage.files[0]);  // ファイル内容を詰める

    const url = '/ocreniisan';
    const param = {
        method: 'POST',
        mode: 'cors',
        cache: 'no-cache',
        credentials: 'same-origin',
        redirect: 'follow',
        referrer: 'no-referrer',
        body: formData
    }
    let isFetched = false;

    await fetch(url, param)
    .then(res => {
        // ローディングアニメーション非表示
        hideLoader();
        if (res.status === 200) {
            return res.json()
        }else{
            console.warn('Something went wrong on api server!');
        }
    })
    .then(json => {
        console.log(json);
        if('error' in json){
            alert(json['error']);
        }else{
            let category = '';
            let subCategory = json['sub_category'];
            for(let key in CATEGORY){
                if(CATEGORY[key].includes(subCategory)){
                    category = key;
                }
            }
            // テーブルの行数
            let insertRow = table[currentUserId].countRows() - 1;
            // データ挿入
            table[currentUserId].setDataAtRowProp(insertRow, 'category', category);
            table[currentUserId].setDataAtRowProp(insertRow, 'sub_category', subCategory);
            table[currentUserId].setDataAtRowProp(insertRow, 'paid_to', json['store']);
            table[currentUserId].setDataAtRowProp(insertRow, 'amount', json['total']);
            table[currentUserId].setDataAtRowProp(insertRow, 'bought_in', json['date']);

            isFetched = true;
        }
    })
    .catch(error => {
        console.error(error);
    })

    if(isFetched){
        // ちょっと待ってからモーダル表示
        const _sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
        await _sleep(100);
        // 登録ボタン押下でモーダル表示
        const registerButtom = document.getElementById(currentUserId + '-fetch-update-records');
        registerButtom.click();
    }
}
