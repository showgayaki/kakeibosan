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
            alert(json['error'] + '\n' + '\n' + json['detail']);
        }else{
            let registerData = {};

            registerData['subcategory'] = json['subcategory'];
            // [{'固定費': ['家賃', '管理費', '手数料', '更新料', '駐輪場']},...]の配列の形で来る
            for(let i = 0; i < categoryList.length; i++){
                // サブカテゴリー名から、カテゴリー名を取得する
                if(Object.values(categoryList[i])[0].includes(registerData['subcategory'])){
                    registerData['category'] = Object.keys(categoryList[i])[0];
                    break;
                }
            }
            registerData['paid_to'] = json['store'];
            registerData['amount'] = json['total'];
            registerData['bought_in'] = json['date'];

            // 商品選択モーダル作成してモーダル表示
            registerData = buildItemSelectModal(json, registerData);
            $('#itemSelectModal').modal('show');

            // モーダル表示 → 閉じる → 別のレシートでモーダル表示 → confirmButtonクリック
            // とすると、1回目のデータも挿入されてしまう。
            // addEventListenerだと追加で登録されてしまうようなのでremoveEventListenerしたい。
            // ------------------
            // confirmButton.addEventListener('click', {data: registerData, handleEvent: clickConfirmButton}, false);
            // confirmButton.removeEventListener('click', {data: registerData, handleEvent: clickConfirmButton}, false);
            // ------------------
            // 上記の記載だと、removeEventListenerが効かないようなので、第二引数をいったん変数に入れて取っておく。
            // （addEventListenerとremoveEventListenerの引数がまったく同じでないと削除できないらしい）
            const confirmEventObject = {data: registerData, handleEvent: clickConfirmButton};
            const confirmButton = document.getElementById('itemSelectConfirm');
            confirmButton.addEventListener('click', confirmEventObject, false);

            const closeButton = document.getElementById('itemSelectClose');
            closeButton.addEventListener('click', function(){
                confirmButton.removeEventListener('click', confirmEventObject, false);
            }, false)
        }
    })
    .catch(error => {
        console.error(error);
    })
}


function buildItemSelectModal(json, registerData){
    const storeName = document.getElementById('storeName');
    const receiptDate = document.getElementById('receiptDate');
    const itemSelectSubTotal = document.getElementById('itemSelectSubTotal');
    const itemSelectTaxTotal = document.getElementById('itemSelectTaxTotal');
    const itemTotal = document.getElementById('itemTotal');
    const itemSelectTotal = document.getElementById('itemSelectTotal');

    storeName.innerHTML = '店名：' + json['store'];
    receiptDate.innerHTML = '日付：' + json['date'];
    itemSelectSubTotal.innerHTML = json['subtotal'].toLocaleString();
    itemSelectTaxTotal.innerHTML = json['tax_total'].toLocaleString();
    itemTotal.innerHTML = json['total'].toLocaleString();
    itemSelectTotal.innerHTML = json['total'].toLocaleString();

    let itemDetailTbody = document.getElementById('tbodyItemsDetail');
    let itemsDetail = '';
    let customCheckbox = function(row, amount){
        return `
            <div class="form-check">
                <label class="form-check-label">
                    <input class="form-check-input" type="checkbox" name="item" value="` + amount + `" checked  ` + `data-row="` + row + `">
                        <span class="form-check-sign">
                            <span class="check"></span>
                        </span>
                </label>
            </div>
        `
    }

    for(let i = 0; i < json['items'].length; i++){
        itemsDetail += `
        <tr>
            <td class="item-checkbox">` + customCheckbox(i, json['items'][i]['amount_tax_in']) +`</td>
            <td>` + json['items'][i]['name'] + `</td>
            <td class="amount">` + json['items'][i]['amount'].toLocaleString() + `</td>
            <td class="amount">` + json['items'][i]['tax'].toLocaleString() + `</td>
            <td class="amount">` + json['items'][i]['amount_tax_in'].toLocaleString() + `</td>
        </tr>
        `
    }
    itemDetailTbody.innerHTML = itemsDetail;

    const itemSelectCheckboxes = document.querySelectorAll('input[type="checkbox"][name="item"]');
    for(let checkbox of itemSelectCheckboxes){
        checkbox.addEventListener('change', function(){
            let itemAmountTaxIn = Number(checkbox.value.replace(',', ''));
            if(checkbox.checked){
                registerData['amount'] = registerData['amount'] + itemAmountTaxIn;
            }else{
                registerData['amount'] = registerData['amount'] - itemAmountTaxIn;
            }
            itemSelectTotal.innerHTML = registerData['amount'].toLocaleString();
        });
    }

    return registerData;
}


async function clickConfirmButton(e){
    // テーブルの行数
    let insertRow = table[currentUserId].countRows() - 1;
    // データ挿入
    table[currentUserId].setDataAtRowProp(insertRow, 'category', this.data['category']);
    table[currentUserId].setDataAtRowProp(insertRow, 'subcategory', this.data['subcategory']);
    table[currentUserId].setDataAtRowProp(insertRow, 'paid_to', this.data['paid_to']);
    table[currentUserId].setDataAtRowProp(insertRow, 'amount', this.data['amount']);
    table[currentUserId].setDataAtRowProp(insertRow, 'bought_in', this.data['bought_in']);

    $('#itemSelectModal').modal('hide');
    // ちょっと待ってからモーダル表示
    const _sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
    await _sleep(100);
    // 登録ボタン押下でモーダル表示
    const registerButtom = document.getElementById(currentUserId + '-fetch-update-records');
    registerButtom.click();
}
