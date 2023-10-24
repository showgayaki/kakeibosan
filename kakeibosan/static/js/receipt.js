const receiptImage = document.getElementById('receiptImage');
const storeNameElem = document.getElementById('storeName');
const storeCategoryElem = document.getElementById('storeCategory');
const storeSubcategoryElem = document.getElementById('storeSubcategory');
const receiptDateElem = document.getElementById('receiptDate');
const receiptSubtotalElem = document.getElementById('receiptSubtotal');
const receiptTaxTotalElem = document.getElementById('receiptTaxTotal');
const receiptTotalElem = document.getElementById('receiptTotal');
const toRecordTotalElem = document.getElementById('toRecordTotal');
const tableElem = document.getElementById('itemSelectTable');
const itemDetailTbodyElem = document.getElementById('tbodyItemsDetail');
const confirmButtonElem = document.getElementById('itemSelectConfirm');


receiptImage.addEventListener('click', function(e){
    // 初期化
    e.target.value = '';
})
receiptImage.addEventListener('change', {handleEvent: postFile}, false);


async function postFile(e){
    e.stopPropagation();
    e.preventDefault();

    // ローディングアニメーション表示
    displayLoader();

    // アップロード
    const trimmedFileName = 'trimmed.jpg';
    const uploadFile = receiptImage.files[0];
    const fileName = uploadFile.name;

    const formData = new FormData();
    formData.append('receiptImage', uploadFile);  // ファイル内容を詰める

    const baseUrl = '/ocreniisan'
    const url = (fileName === trimmedFileName)? baseUrl + '?trimmed=true': baseUrl;
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
            if(json['error'] === 'trim'){
                const confirmResult = confirm(
                    json['message'] + '\n\n' +
                    json['detail'] + '\n\n' +
                    '手動でトリミングしますか？'
                );

                // confirmでOKならトリミングモーダル表示
                if(confirmResult){
                    showTrimmingModal(uploadFile, trimmedFileName);
                }
            }else{
                alert(json['message'] + '\n\n' + json['detail']);
            }
        }else{
            // 内容確認ボタン押下前のHandsOnTableの行数
            // ボタン押下時に行数が増えていたら、更新確認モーダル閉じる時に削除する用
            const defaultRowsCount = table[currentUserId].countRows();

            // 「2023」が「2013」に検知されてしますことがあるため、年を検証
            const now = new Date();
            const nowYear = now.getFullYear();
            const receiptDate = new Date(json['date']);
            const receiptYear = receiptDate.getFullYear();
            // テキトーに、2年以上前ならConfirm出す
            if(nowYear - receiptYear > 2){
                const dateFixConfirm = confirm(
                    `「${receiptYear}年」と読み取られました。そんなわけないですよね？\n「${nowYear}年」に修正しておきますか？`
                )
                if(dateFixConfirm){
                    json['date'] = json['date'].replace(receiptYear, nowYear)
                }
            }

            // 商品選択モーダル作成してモーダル表示
            buildItemSelectModal(json);

            // 内容確認ボタンのクリックイベント
            // モーダル表示・非表示で、登録・削除
            $('#itemSelectModal').on('shown.bs.modal', function(){
                confirmButtonElem.addEventListener('click', clickConfirmButton, false);
            }).on('hidden.bs.modal', function(){
                confirmButtonElem.removeEventListener('click', clickConfirmButton, false);
            })

            // 更新確認モーダル非表示時のイベント
            // 商品選択モーダル開く → 更新確認モーダル開く → 更新確認モーダル閉じる の流れを想定
            $('#confirmModal').on('hidden.bs.modal', function(){
                // confirmButtonElem.removeEventListener('click', clickConfirmButton, false);
                const currentRowsCount = table[currentUserId].countRows();

                // fetch直後より行数が増えていたら、その行を削除
                if(currentRowsCount > defaultRowsCount){
                    // データのある最終行
                    let insertRow = table[currentUserId].countRows() - 2;
                    // 挿入したデータ削除
                    table[currentUserId].alter('remove_row', insertRow);
                    $('#itemSelectModal').modal('show');
                }
            })

            // モーダルをショーウ
            $('#itemSelectModal').modal('show');

            // レシート日付用ツールチップ
            $(receiptDateElem).tooltip(
                {
                    title: '日付が今月ではないようです',
                    placement: 'top',
                    trigger: 'manual',
                    offset: '-22px, 0',
                }
            )
            // 読み取ったレシートの日付が今月じゃない場合は、ツールチップを表示する
            if(isThisMonth(json['date'])){
                ;
            }else{
                $('#itemSelectModal').on('shown.bs.modal', function(){
                    $(receiptDateElem).tooltip('show');
                })
            }
        }
    })
    .catch(error => {
        console.error(error);
    })
}


function localeStringToNumber(localeString){
    return Number(localeString.replace(',', ''))
}


function buildItemSelectModal(json){
    // [{'固定費': ['家賃', '管理費', '手数料', '更新料', '駐輪場']},...]の配列の形で来る
    for(let i = 0; i < categoryList.length; i++){
        // サブカテゴリー名から、カテゴリー名を取得する
        if(Object.values(categoryList[i])[0].includes(json['subcategory'])){
            storeCategoryElem.innerHTML = Object.keys(categoryList[i])[0];
            break;
        }
    }

    storeNameElem.innerHTML = json['store'];
    storeSubcategoryElem.innerHTML = json['subcategory'];
    receiptDateElem.value = json['date'];
    receiptTaxTotalElem.innerHTML = (json['total'] - json['subtotal']).toLocaleString();
    receiptSubtotalElem.innerHTML = (json['subtotal'] === null)? '-----': json['subtotal'].toLocaleString();
    receiptTotalElem.innerHTML = json['total'].toLocaleString();

    const customCheckbox = function(checkboxId){
        return `
            <div class="form-check">
                <input id="` + checkboxId + `" class="form-check-input" type="checkbox" value="" checked>
                <span class="form-check-sign">
                    <span class="check"></span>
                </span>
            </div>
        `
    }

    // レシート連続読み取りすると前回の内容が残るので、ここで初期化
    itemDetailTbodyElem.innerHTML = '';
    tableElem.style.marginBottom = '';

    for(let i = 0; i < json['items'].length; i++){
        const itemName = json['items'][i]['name'];
        const amount = json['items'][i]['amount'];

        const rowId = 'item_' + i;
        const checkboxId = 'checkbox_' + i;
        const inputAmountId = 'inputAmount_' + i;
        const deleteId = 'deleteItem_' + i;

        const itemsDetail = `
        <tr id="${rowId}" class="item-row">
            <td class="item-checkbox">${customCheckbox(checkboxId)}</td>
            <td>
                <label class="item-name-label" for="${checkboxId}">${itemName}</label>
            </td>
            <td class="amount">
                <input id="${inputAmountId}" class="amount-input" type="text" pattern="\d*" value="${amount.toLocaleString()}">
            </td>
            <td class="amount item-tax"></td>
            <td class="amount item-taxin"></td>
            <td><i id="${deleteId}" class="fa fa-trash-alt text-primary delete-icon"></i>
        </tr>
        `
        // tbody内のおしりに挿入
        itemDetailTbodyElem.insertAdjacentHTML('beforeend', itemsDetail);

        // チェックボックスOn・Off時のイベントリスナー
        const toRecordElem = document.getElementById(checkboxId);
        toRecordElem.addEventListener('change', {handleEvent: itemSelectCheckboxEvent}, false);

        // 金額入力欄のイベントリスナー
        const inputAmountElem = document.getElementById(inputAmountId);
        inputAmountElem.addEventListener('input', {elem: inputAmountElem, json: json, handleEvent:inputAmountEvent});

        // ゴミ箱アイコンクリック時のイベントリスナー
        const deleteItemElem = document.getElementById(deleteId);
        deleteItemElem.addEventListener('click', {rowId: rowId, json: json, handleEvent: deleteIconClickEvent}, false)
    }

    const rowsElem = itemDetailTbodyElem.querySelectorAll('.item-row');
    const selected = insertTaxAndTotalByItem(rowsElem, json);
    toRecordTotalElem.innerHTML = selected.toLocaleString();

    // 日付inputに入力時のイベントリスナー
    receiptDateElem.addEventListener('input', {
        handleEvent: function(){
            if(isThisMonth(receiptDateElem.value)){
                $(receiptDateElem).tooltip('hide');
            }else{
                $(receiptDateElem).tooltip('show');
            }
            registerData['bought_in'] = receiptDateElem.value;
        },
    })

    // undoボタンクリック時のイベントリスナー
    const itemSelectUndoElem = document.getElementById('itemSelectUndo');
    itemSelectUndoElem.addEventListener('click', {json: json, handleEvent: undoButtonClickEvent}, false)
}


function isThisMonth(receiptDate){
    receiptDate = new Date(receiptDate);
    const now = new Date();
    if((receiptDate.getFullYear() === now.getFullYear())
    && receiptDate.getMonth() === now.getMonth()){
        return true;
    }else{
        return false;
    }
}


function insertTaxAndTotalByItem(rowsElem, json){
    const taxTotal = json['total'] - json['subtotal'];

    let selectTotal = 0;
    for(let i = 0; i < rowsElem.length; i++){
        const checkboxElem = rowsElem[i].querySelector('.form-check-input');
        const amountElem = rowsElem[i].querySelector('.amount-input');
        const itemAmount = localeStringToNumber(amountElem.value);

        const itemTaxElem = rowsElem[i].querySelector('.item-tax');
        const itemTaxInElem = rowsElem[i].querySelector('.item-taxin');
        const calcTax = function(){
            // 小計がnullの時は、商品ごとの金額は税込なはず
            if(json['subtotal'] === null){
                itemTaxElem.innerHTML = '---';

                return 0;
            }else{
                // 商品ごとの税額は、小計と商品金額の割合で求める（軽減税率を考慮とか無理なので）
                // 単にMath.roundで丸めると1円とかズレるので、1000倍して丸めて割る1000で桁を元に戻してまた丸める
                // それでもズレる時あり
                const thousandfold = Math.round((itemAmount / json['subtotal']) * 1000);
                const taxByItem = Math.round((thousandfold / 1000) * taxTotal);
                itemTaxElem.innerHTML = taxByItem.toLocaleString();

                return taxByItem;
            }
        }
        const taxByItem = calcTax();
        const taxInByItem = itemAmount + taxByItem;

        itemTaxInElem.innerHTML = taxInByItem.toLocaleString();
        checkboxElem.value = taxInByItem;

        selectTotal += taxInByItem;
    }

    return selectTotal
}


function itemSelectCheckboxEvent(e){
    const toRecordTotal = localeStringToNumber(toRecordTotalElem.innerHTML);
    const itemAmountTaxIn = localeStringToNumber(e.target.value);

    // チェックつける：計上金額に足す、チェック外す：計上金額から引く
    const calcToRecord = (e.target.checked)? (toRecordTotal + itemAmountTaxIn): (toRecordTotal - itemAmountTaxIn);
    toRecordTotalElem.innerHTML = calcToRecord.toLocaleString();
}


function inputAmountEvent(){
    // 入力された値を三桁区切りにして、チェックボックスのvalueに入れる
    const formattedValue = localeStringToNumber(this.elem.value).toLocaleString();
    this.elem.value = formattedValue;

    const rowsElem = itemDetailTbodyElem.querySelectorAll('.item-row:not(.d-none)');
    const selected = insertTaxAndTotalByItem(rowsElem, this.json);

    toRecordTotalElem.innerHTML = selected.toLocaleString();
}


function deleteIconClickEvent(){
    // 商品削除するとtableの高さが変わってしまうので、見た目の高さを維持するために
    // 商品削除時に1行のheightをtableのmargin-bottomに足す
    // (tableのheightに足すと、tableの1行の高さが変わってしまうのでmargin-bottomに足すことにした)

    // 1行の高さを取得
    const trElem = document.getElementById(this.rowId);
    const trHeight = trElem.clientHeight;

    // tableのmargin-bottomを取得
    const tableStyle = window.getComputedStyle(tableElem);
    const marginBottom = Number(tableStyle.marginBottom.replace('px', ''));

    trElem.classList.add('hide-row');

    const promise = new Promise((resolve, reject) => {
        resolve(trElem);
    }).then((tr) => {
        return new Promise((resolve, reject) => {
            // CSSのアニメーション後に実行
            setTimeout(() => {
                // 非表示(d-none)にして、hide-rowクラスは削除
                tr.classList.add('d-none');
                tr.classList.remove('hide-row');
                // 削除した行の高さ分をmargin-bottomに足す
                tableElem.style.marginBottom = (marginBottom + trHeight).toString() + 'px';

                resolve(tr);
            }, 400)
        })
    }).then((tr) => {
        const rowsElem = itemDetailTbodyElem.querySelectorAll('.item-row:not(.d-none)');
        const selected = insertTaxAndTotalByItem(rowsElem, this.json);

        toRecordTotalElem.innerHTML = selected.toLocaleString();
    })
}


function undoButtonClickEvent(){
    const rowsElem = itemDetailTbodyElem.querySelectorAll('.d-none');
    if(rowsElem.length === 0){
        // 非表示にされている行がなければ抜ける
        return
    }

    const rowHeight = itemDetailTbodyElem.querySelector('.item-row:not(.d-none)').clientHeight;
    let tableMarginBottom = Number(tableElem.style.marginBottom.replace('px', ''));

    for(let i = 0; i < rowsElem.length; i++){
        rowsElem[i].classList.remove('d-none');
        tableMarginBottom -= rowHeight;
    }
    tableElem.style.marginBottom = tableMarginBottom.toString() + 'px';
    toRecordTotalElem.innerHTML = this.json['total'];
}


function showTrimmingModal(uploadFile, trimmedFileName){
    // よくわかんないけど、下記URLを参考
    // https://github.com/fengyuanchen/cropperjs/blob/main/docs/examples/cropper-in-modal.html
    const trimmingReceiptImageElem = document.getElementById('trimmingReceiptImage');
    const blobUrl = URL.createObjectURL(uploadFile);
    trimmingReceiptImageElem.src = blobUrl;

    let cropBoxData;
    let canvasData;
    let cropper;

    $('#trimmingModal').on('shown.bs.modal', function(){
        cropper = new Cropper(trimmingReceiptImageElem, {
            autoCropArea: 0.5,
            ready: function(){
                //Should set crop box data first here
                cropper.setCropBoxData(cropBoxData).setCanvasData(canvasData);
            }
        });

        // 用が済んだらURL.revokeObjectURL();でメモリを解放したほうがいいらしい
        URL.revokeObjectURL(blobUrl);
    }).on('hidden.bs.modal', function(){
        cropBoxData = cropper.getCropBoxData();
        canvasData = cropper.getCanvasData();
        cropper.destroy();
    });

    // アップロードボタン押下イベント
    const uploadTrimmedImageBtnElem = document.getElementById('uploadTrimmedImage');
    uploadTrimmedImageBtnElem.addEventListener('click', function(){
        const canvas = cropper.getCroppedCanvas();

        // よくわかんないけど、下記URLを参考
        // https://cobakura.com/articles/crop-image/
        canvas.toBlob(function(imageBlob){
            const trimmedImageFile = new File([imageBlob], trimmedFileName, {type: 'image/jpeg'});
            const dt = new DataTransfer();

            dt.items.add(trimmedImageFile);
            receiptImage.files = dt.files;

            // changeイベント発火でpostFile実行して、トリミング後の画像をアップロード
            const changeEvent = new Event('change');
            receiptImage.dispatchEvent(changeEvent);

            // モーダル閉じる
            $('#trimmingModal').modal('hide');
        })
    })

    $('#trimmingModal').modal('show');
}

async function clickConfirmButton(){
    // テーブルの行数
    const insertRow = table[currentUserId].countRows() - 1;
    // データ挿入
    table[currentUserId].setDataAtRowProp(insertRow, 'category', storeCategoryElem.innerHTML);
    table[currentUserId].setDataAtRowProp(insertRow, 'subcategory', storeSubcategoryElem.innerHTML);
    table[currentUserId].setDataAtRowProp(insertRow, 'paid_to', storeNameElem.innerHTML);
    table[currentUserId].setDataAtRowProp(insertRow, 'amount', localeStringToNumber(toRecordTotalElem.innerHTML));
    table[currentUserId].setDataAtRowProp(insertRow, 'bought_in', receiptDateElem.value);

    $('#itemSelectModal').modal('hide');
    // ちょっと待ってからモーダル表示
    const _sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
    await _sleep(100);
    // 登録ボタン押下でモーダル表示
    const registerButtom = document.getElementById(currentUserId + '-fetch-update-records');
    registerButtom.click();
}
