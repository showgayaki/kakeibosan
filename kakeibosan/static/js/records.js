function createTable(currentUserId, users, records){
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
    let lastSixMonths = lastHalfYear();

    const SUB_CATEGORY_COLUMN = 2;
    const COLUMNS = [
                {data: 'id', type: 'numeric', width: 1},
                {data: 'category', type: 'dropdown', source:['固定費', '光熱費', '食費', '日用品', '交通費']},
                {data: 'sub_category', type: 'dropdown'},
                {data: 'paid_to', type: 'text'},
                {data: 'amount', type: 'numeric', numericFormat:{pattern: '0,0'}},
                {data: 'bought_in', type: 'date', datePickerConfig: datePickerConfig, width: 100, dateFormat: 'YYYY-M-D', className: 'datepicker htRight htMiddle'},
                {data: 'month_to_add', type: 'dropdown', height: 250, source: lastSixMonths, dateFormat: 'YYYY-M', className: 'monthpicker htRight htMiddle'},
                {data: 'user_id', type: 'numeric', width: 0.1},
                {data: 'del', type: 'checkbox', width: 40, className: 'htCenter htMiddle'}
            ]
    var table = {};
    // チェックボックスにfalseをいれておく
    records.forEach(function(val){
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
                '種別',
                '項目',
                '支払先',
                '金額',
                '支払日',
                '計上月',
                'User_ID',
                '削除'
            ],
            rowHeights: 40,
            className: 'htMiddle',
            minSpareRows: 1,
            columnSorting: {
                initialConfig: {
                    column: 5,
                    sortOrder: 'asc'
                }
            },
            afterChange: function(changes, source) {
                if (source === 'edit') {
                    // 値に変更無し時
                    if (changes[0][2] == changes[0][3]) {
                        return;
                    };
                    change_row = changes[0][0];
                    change_prop = changes[0][1];
                    change_after_value = changes[0][3];

                    if (change_prop == 'category') {
                        // sub_categoryを空にする。
                        this.setDataAtRowProp(change_row, 'sub_category','','autoedit');
                        switch (change_after_value) {
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
            }
        };
        //テーブルを生成
        table[users[i]['id']] = new Handsontable(tableElement, tableSettings);

        // 非表示タブのHandsontableが描画されない問題回避
        $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
          table[users[i]['id']].render();
        });
    }
    // 登録ボタンクリック
    $(document).on('click', '[id$=fetch-update-records]', function(e){
        // ボタンのidは「*-fetch-update-records」
        let userId = Number($(this).attr('id').split('-')[0]);
        let isSelfData = userId === currentUserId;

        if(isSelfData){
            var currentRecords = [];
            $(table[userId].getSourceData()).filter(function(i, e){
                // 最終行は除く
                if(table[userId].getSourceData().length !== i + 1) return e;
            }).each(function(i, e){
                currentRecords.push(e);
            });
            defaultRecords = defaultRecords.filter(x => x.user_id == userId);
            let updateRecords = fetchUpdateRecords(userId, currentRecords, defaultRecords);
            createUpdateModal(isSelfData, updateRecords, defaultRecords);
        }else{
            createUpdateModal(isSelfData, [], []);
        }
    })
}


function lastHalfYear(){
    const HALF_YEAR = 6;
    let date = new Date();
    let lastHalfYear = [];
    for(let i = 0; i < HALF_YEAR; i++){
        let month = '';
        if(i === 0){
            date.setDate(1);
        }else{
            date.setMonth(date.getMonth() - 1);
        }
        month = date.getFullYear() + '-' + (date.getMonth() + 1);
        lastHalfYear.push(month)
    }
    return lastHalfYear
}


function fetchUpdateRecords(userId, currentRecords, defaultRecords){
    updateRecords = _.differenceWith(currentRecords, defaultRecords, _.isEqual);
    for(let i = 0; i < updateRecords.length; i++){
        updateRecords[i]['user_id'] = userId;
    }
    return updateRecords;
}


function createUpdateModal(isSelfData, updateRecords, defaultRecords){
    if(updateRecords.length > 0){
        $('#confirmModal').find('.table-responsive').show();
        $('#records-caption').html('以下 ' + updateRecords.length + '件のデータを更新しますか？');
        let html = '';
        for(let i = 0; i < updateRecords.length; i++){
            let add = '<td class="badge_clm"><span class="badge badge-success">新規</span></td>';
            let update = '<td class="badge_clm"><span class="badge badge-info">更新</span></td>';
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
            + '<td>' + updateRecords[i]['category'] + '</td>'
            + '<td>' + updateRecords[i]['sub_category'] + '</td>'
            + '<td>' + updateRecords[i]['paid_to'] + '</td>'
            + '<td class="amount">' + Number(updateRecords[i]['amount']).toLocaleString() + '</td>'
            + '<td class="bought_in">' + updateRecords[i]['bought_in'] + '</td>'
            + '<td class="month_to_add">' + updateRecords[i]['month_to_add'] + '</td>'
            + '</tr>';
        }
        $('#tbody-update').html(html);
        let btn = '<button name="save" type="button" class="btn btn-primary">OK</button>'
                + '<button type="button" class="btn btn-secondary" data-dismiss="modal">Cancel</button>';
        $('#confirmModal').find('.modal-footer').html(btn);
    }else{
        let caption = isSelfData? '更新可能なデータがありません' : 'ほかのユーザーのデータは更新できません';
        $('#confirmModal').find('.table-responsive').hide();
        let btn = '<button type="button" class="btn btn-primary" data-dismiss="modal">OK</button>';
        $('#records-caption').html(caption);
        $('#confirmModal').find('.modal-footer').html(btn);
    }
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
