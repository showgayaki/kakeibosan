// ------------------
// コピーボタン押下時
// ------------------
$('.copy-btn')
// tooltip設定
.tooltip({
    trigger: 'manual'
})
// tooltip表示後の動作を設定
.on('shown.bs.tooltip', function(){
    setTimeout((function(){
    $(this).tooltip('hide');
    }).bind(this), 1500);
})
// クリック時の動作を設定
.on('click', function(){
    // クリックした要素を取得してコピー
    const clickElem = $(this);
    copyText(clickElem);
});

function createTable(currentUserId, users, records, viewMonth){
    moment.locale('ja');
    let datePickerConfig = {
        yearSuffix: '年',
        showMonthAfterYear: true,
        showDaysInNextAndPreviousMonths: true,
        i18n: {
            previousMonth: '前月',
            nextMonth: '次月',
            months: moment.localeData()._monthsShort,
            weekdays: moment.localeData()._weekdays,
            weekdaysShort: moment.localeData()._weekdaysShort
        }
    }

    // カラムの順番(場所)が変わったら要変更
    const SUB_CATEGORY_COLUMN = 3;
    const BOUGHT_IN_COLUMN = 6;
    const COLUMNS = [
                {data: 'id', type: 'numeric', width: 1},
                {data: 'is_paid_in_advance', type: 'checkbox', width: 40, className: 'htCenter htMiddle'},
                {data: 'category', type: 'dropdown', source:['固定費', '光熱費', '食費', '日用品', '交通費']},
                {data: 'sub_category', type: 'dropdown'},
                {data: 'paid_to', type: 'text', width: 200},
                {data: 'amount', type: 'numeric', numericFormat:{pattern: '0,0'}},
                {data: 'bought_in', type: 'date', datePickerConfig: datePickerConfig, width: 110, dateFormat: 'YYYY-M-D', className: 'htRight htMiddle'},
                {data: 'month_to_add', type: 'text', width: 0.1, readOnly: true, dateFormat: 'YYYY-M', className: 'ht_month_to_add htRight htMiddle'},
                {data: 'user_id', type: 'numeric', width: 0.1},
                {data: 'del', type: 'checkbox', width: 40, className: 'htCenter htMiddle'}
            ]
    const REQUIRED_COLUMNS = {
        'category': '種別',
        'sub_category': '項目',
        'amount': '金額',
        'bought_in': '支払日',
    }
    var table = {};
    records.forEach(function(val){
        // チェックボックスにfalseをいれておく
        val['del'] = false;
    });
    // 参照渡し回避
    var defaultRecords = JSON.parse(JSON.stringify(records));

    for(let i = 0; i < users.length; i++){
        //テーブルを配置する要素を取得
        let tableId = users[i]['id'] + '-handsontable';
        let tableElement = document.getElementById(tableId);

        let userRecords = [];
        for(let j = 0; j < records.length; j++){
            if(users[i]['id'] === records[j]['user_id']){
                userRecords.push(records[j]);
            }
        }

        let tableSettings = {
            data: userRecords,
            columns: COLUMNS,
            colHeaders: [
                'ID',
                '立替',
                '種別<span class="required"> *</span>',
                '項目<span class="required"> *</span>',
                '支払先',
                '金額<span class="required"> *</span>',
                '支払日<span class="required"> *</span>',
                '計上月',
                'User_ID',
                '削除'
            ],
            rowHeights: 40,
            className: 'htMiddle',
            minSpareRows: 1,
            columnSorting: {
                initialConfig: {
                    column: BOUGHT_IN_COLUMN,
                    sortOrder: 'asc'
                }
            },
            beforeChange: function(changes, source) {
                if (source !== 'loadData') {
                    // 値に変更無し時
                    if (changes[0][2] == changes[0][3]) {
                        return;
                    };
                    change_row = changes[0][0];
                    change_prop = changes[0][1];
                    value_after_change = changes[0][3];

                    if(change_prop == 'category'){
                        // category削除時はsub_categoryを空にする
                        if(value_after_change === ''){
                            this.setDataAtRowProp(change_row, 'sub_category', '', 'autoedit');
                        }
                        switch(value_after_change){
                            case '固定費':
                                this.setCellMeta(change_row, SUB_CATEGORY_COLUMN, 'source', [
                                '家賃',
                                '管理費',
                                '手数料'
                            ]);
                            break;
                            case '光熱費':
                                this.setCellMeta(change_row, SUB_CATEGORY_COLUMN, 'source', [
                                '電気代',
                                'ガス代',
                                '水道代'
                            ]);
                            break;
                            case '食費':
                                this.setCellMeta(change_row, SUB_CATEGORY_COLUMN, 'source', [
                                '食材費',
                                '外食費'
                            ]);
                            break;
                            case '日用品':
                                this.setCellMeta(change_row, SUB_CATEGORY_COLUMN, 'source', [
                                '日用品',
                                '洗剤類'
                            ]);
                            break;
                            case '交通費':
                                this.setCellMeta(change_row, SUB_CATEGORY_COLUMN, 'source', [
                                'タイムズ',
                                'レンタカー',
                                'ガソリン代'
                            ]);
                            break;
                            default:
                                this.setCellMeta(change_row, SUB_CATEGORY_COLUMN, 'source', []);
                        }
                    }
                }
            },
            afterValidate: function(isValid, value, row, prop, source){
                // 複数カラムコピぺ時に、サブカテゴリでValidationエラーになるため再度値を入れる
                if(!isValid && source == 'CopyPaste.paste'){
                    this.setDataAtRowProp(row, prop, value, 'autoedit');
                }
            }
        };
        //テーブルを生成
        table[users[i]['id']] = new Handsontable(tableElement, tableSettings);

        // 非表示タブのHandsontableが描画されない問題回避
        $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
            table[users[i]['id']].render();
        });
        // ウィンドウリサイズ時にテーブル表示が崩れるため、リサイズ後に再描画
        let timer = false;
        $(window).resize(function(e){
            if (timer !== false) {
                clearTimeout(timer);
            }
            timer = setTimeout(function() {
                table[users[i]['id']].render();
            }, 200);
        })
    }
    // 登録ボタンクリック
    $(document).on('click', '[id$=fetch-update-records]', function(e){
        // ボタンのidは「*-fetch-update-records」
        let userId = Number($(this).attr('id').split('-')[0]);
        let isSelfData = userId === currentUserId;
        let isThisMonth = viewMonth === monthToAdd();
        // バリデーション用変数
        let validationError = [];
        let validationErrorEmpty = [];
        let validationErrorDict = {};

        if(isSelfData){
            var currentRecords = [];
            let updateRecords = [];
            $(table[userId].getSourceData()).filter(function(i, e){
                // 最終行は除く
                if(table[userId].getSourceData().length !== i + 1){
                    return e;
                }
            }).each(function(i, e){
                if(e['paid_to'] == null){
                    e['paid_to'] = '';
                }
                // 空の行はスキップ
                if((e['category'] == null || e['category'] === '') &&
                   (e['sub_category'] == null || e['sub_category'] === '') &&
                   (e['amount'] == null || e['amount'] === '') &&
                   (e['bought_in'] == null || e['bought_in'] === '')){
                       return;
                }
                // 入力の判定
                for(let item in REQUIRED_COLUMNS){
                    // 必須項目が空かどうか判定
                    if(e[item] == null || e[item] == ''){
                        validationErrorEmpty.push(REQUIRED_COLUMNS[item]);
                    }else{
                        // 形式の判定
                        switch (item){
                            case 'amount':
                                if(!Number.isInteger(e[item])){
                                    validationError.push(REQUIRED_COLUMNS[item] + '：整数で入力してください。');
                                }
                                break;
                            case 'bought_in':
                                if(!e[item].match(/^(\d{4})-(\d{1,2})-(\d{1,2})$/)){
                                    validationError.push(REQUIRED_COLUMNS[item] + '：2000-1-1の形式で入力してください。');
                                }else{
                                    let inputYear = e[item].split('-')[0];
                                    let inputMonth = e[item].split('-')[1] - 1;
                                    let inputDay = e[item].split('-')[2];
                                    let date = new Date(inputYear, inputMonth, inputDay);
                                    if(date.getFullYear() != inputYear || date.getMonth() != inputMonth || date.getDate() != inputDay){
                                        validationError.push(REQUIRED_COLUMNS[item] + '：有効な日付を入力してください。');
                                    }
                                }
                                break;
                            default:
                        }
                    }
                }
                // 空の必須項目なければ配列に追加、あればエラーモーダル表示
                if(validationError.length == 0 && validationErrorEmpty.length == 0){
                    currentRecords.push(e);
                }else{
                    validationErrorDict = {
                        'row': i + 1,
                        'empty': validationErrorEmpty,
                        'error': validationError,
                    };
                }
            });

            defaultRecords = defaultRecords.filter(x => x.user_id == userId);
            updateRecords = fetchUpdateRecords(viewMonth, userId, currentRecords, defaultRecords);
            createUpdateModal(validationErrorDict, isThisMonth, isSelfData, updateRecords);
        }else{
            createUpdateModal(validationErrorDict, isThisMonth, isSelfData, [], []);
            return false;
        }
    })
}


function monthToAdd(){
    let date = new Date();
    date.setDate(1);
    let month_to_add = date.getFullYear() + '-' + (date.getMonth() + 1);
    return month_to_add
}


function fetchUpdateRecords(viewMonth, userId, currentRecords, defaultRecords){
    updateRecords = _.differenceWith(currentRecords, defaultRecords, _.isEqual);
    for(let i = 0; i < updateRecords.length; i++){
        if(!updateRecords[i]['id']){
            updateRecords[i]['id'] = null;
            updateRecords[i]['del'] = null;
        }
        // is_paid_in_advanceがnullならデフォルト（折半）入れておく
        if(updateRecords[i]['is_paid_in_advance'] == null){
            updateRecords[i]['is_paid_in_advance'] = false;
        }
        updateRecords[i]['month_to_add'] = viewMonth;
        updateRecords[i]['user_id'] = userId;
    }
    return updateRecords;
}


function createUpdateModal(validationErrorDict, isThisMonth, isSelfData, updateRecords){
    let caption = '';
    let updateModalTitle = $('#updateModalTitle');
    // validationエラーは初期化
    $('#validationError').empty();
    updateModalTitle.removeClass('text-primary');
    // デフォルトはOKボタンのみにしておく
    $('#confirmModal').find('.table-responsive').hide();
    let btn = '<button type="button" class="btn btn-primary" data-dismiss="modal">OK</button>';
    $('#confirmModal').find('.modal-footer').html(btn);

    // console.log(validationErrorDict);
    // validationエラーのDictionaryが空でなければエラー表示
    if(Object.keys(validationErrorDict).length > 0){
        let validationError = '';
        updateModalTitle.addClass('text-primary');
        updateModalTitle.html('入力エラー');
        $('#updateCaption').html(validationErrorDict['row'] + '行目のデータを確認してください。');
        // 空の場合のエラー
        if(validationErrorDict['empty'].length > 0){
            validationError += '<p class="mb-0">以下の項目が空です。</p>';
            validationError += '<ul>';
            for(let error of validationErrorDict['empty']){
                validationError += '<li>' + error + '</li>';
            }
            validationError += '</ul>';
        }
        // 有効な値でない場合のエラー
        if(validationErrorDict['error'].length > 0){
            for(let error of validationErrorDict['error']){
                validationError += '<p class="mb-0">' + error + '</p>';
            }
        }
        $('#validationError').html(validationError);
    }else{
        updateModalTitle.html('データ更新');
        if(updateRecords.length > 0){
            $('#confirmModal').find('.table-responsive').show();
            $('#updateCaption').html('以下 ' + updateRecords.length + '件のデータを更新しますか？');
            let html = '';
            for(let i = 0; i < updateRecords.length; i++){
                let add = '<td class="badge_clm"><span class="badge badge-success">新規</span></td>';
                let update = '<td class="badge_clm"><span class="badge badge-info">更新</span></td>';
                let is_paid_in_advance = updateRecords[i]['is_paid_in_advance']? '立替': '折半';
                let remove = '<td class="badge_clm"><span class="badge badge-danger">削除</span></td>';
                let badgeColumn = '';

                if(updateRecords[i]['id'] === null){
                    badgeColumn = add;
                }else if(updateRecords[i]['del'] === true){
                    badgeColumn = remove;
                }else{
                    badgeColumn = update;
                }

                html += '<tr>'
                + badgeColumn
                + '<td>' + is_paid_in_advance + '</td>'
                + '<td>' + updateRecords[i]['category'] + '</td>'
                + '<td>' + updateRecords[i]['sub_category'] + '</td>'
                + '<td>' + updateRecords[i]['paid_to'] + '</td>'
                + '<td class="amount">' + Number(updateRecords[i]['amount']).toLocaleString() + '</td>'
                + '<td class="bought_in">' + updateRecords[i]['bought_in'] + '</td>'
                + '<td class="month_to_add">' + updateRecords[i]['month_to_add'] + '</td>'
                + '</tr>';
            }
            $('#tbody-update').html(html);
            btn = '<button name="save" type="button" class="to-loading btn btn-primary">OK</button>'
                    + '<button type="button" class="btn btn-secondary" data-dismiss="modal">Cancel</button>';
            $('#confirmModal').find('.modal-footer').html(btn);
        }else{
            caption = isSelfData? '更新可能なデータがありません' : 'ほかのユーザーのデータは更新できません';
    //        if(isThisMonth){
    //            caption = isSelfData? '更新可能なデータがありません' : 'ほかのユーザーのデータは更新できません';
    //        }else{
    //            caption = '過去の月には計上できません';
    //        }
            $('#updateCaption').html(caption);
        }
    }
    // モーダル表示
    $('#confirmModal').modal('show');

    $('#confirmModal').find('button[name=save]').click(function () {
        let currentUrl = location.href;
        let postUrl = '/kakeibosan/records'
        $.ajax({
            url: postUrl,
            data: JSON.stringify(updateRecords),
            dataType: 'json',
            contentType: 'application/json',
            type: 'POST'
        })
        .then((...args) => {
            const [data, textStatus, jqXHR] = args;
            console.log('done', jqXHR.status);
            window.location.href = currentUrl;
        })
        .catch((...args) => {
            const [jqXHR, textStatus, errorThrown] = args;
            console.log('fail', jqXHR.status);
        })
        .then(() => {
            console.log('always');
        });
    });
}
