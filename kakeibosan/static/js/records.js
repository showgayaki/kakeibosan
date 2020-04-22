function createTable(users, records){
    const SUB_CATEGORY_COLUMN = 2;
    const COLUMNS = [
                {data: 'id', type: 'numeric', width: 1},
                {data: 'category', type: 'dropdown', source:['固定費', '光熱費', '食費', '日用品', '交通費']},
                {data: 'sub_category', type: 'dropdown'},
                {data: 'paid_to', type: 'text'},
                {data: 'amount', type: 'numeric', numericFormat:{pattern: '0,0'}},
                {data: 'bought_in', type: 'date', width: 100, dateFormat: 'YYYY-M-D', className: 'htRight htMiddle'},
                {data: 'month_to_add', type: 'date', dateFormat: 'YYYY-M', className: 'htRight htMiddle'},
                {data: 'user_id', type: 'numeric', width: 0.1}
            ]
    var table = {};
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

        let dataObject = userRecords;
        let tableSettings = {
            data: dataObject,
            columns: COLUMNS,
            colHeaders: [
                'ID',
                '種別',
                '項目',
                '支払先',
                '金額',
                '支払日',
                '計上月',
                'User_ID'
            ],
            height: 800,
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
        let userId = $(this).attr('id').split('-')[0];
        var currentRecords = [];
        $(table[userId].getSourceData()).filter(function(i, e){
            // 種別が空欄ならスルー
            if(e['category']) return e;
        }).each(function(i, e){
            currentRecords.push(e);
        });
        defaultRecords = defaultRecords.filter(x => x.user_id == userId);
        let updateRecords = fetchUpdateRecords(userId, COLUMNS, currentRecords, defaultRecords);
        createUpdateModal(updateRecords);
    })
}


function fetchUpdateRecords(userId, columns, currentRecords, defaultRecords){
    updateRecords = [];
    for(let i = 0; i < currentRecords.length; i++){
        if(defaultRecords.length === 0){
            currentRecords[i]['id'] = null;
            currentRecords[i]['user_id'] = userId;
            updateRecords.push(currentRecords[i]);
        }else{
            for(let j = 0; j < defaultRecords.length; j++){
                if(currentRecords[i]['id'] === null){
                    currentRecords[i]['user_id'] = Number(userId);
                    updateRecords.push(currentRecords[i]);
                    break;
                }else if(currentRecords[i]['id'] === defaultRecords[j]['id']){
                    for(let k = 0; k < columns.length; k++){
                        let key = columns[k]['data'];
                        if(currentRecords[i][key] !== defaultRecords[j][key]){
                            updateRecords.push(currentRecords[i]);
                            break;
                        }
                    }
                }
            }
        }
    }
    return updateRecords;
}


function createUpdateModal(records){
    if(records.length > 0){
        $('#confirmModal').find('.table-responsive').show();
        $('#records-caption').html('以下 ' + records.length + '件のデータを登録しますか？');
        let html = '';
        for(let i = 0; i < records.length; i++){
            let add = '<td class="badge_clm"><span class="badge badge-success">新規</span></td>';
            let update = '<td class="badge_clm"><span class="badge badge-info">更新</span></td>';
            let idColumn = records[i]['id'] === null? add : update;

            html += '<tr>'
            + idColumn
            + '<td>' + records[i]['category'] + '</td>'
            + '<td>' + records[i]['sub_category'] + '</td>'
            + '<td>' + records[i]['paid_to'] + '</td>'
            + '<td class="amount">' + records[i]['amount'].toLocaleString() + '</td>'
            + '<td class="bought_in">' + records[i]['bought_in'] + '</td>'
            + '<td class="month_to_add">' + records[i]['month_to_add'] + '</td>'
            + '</tr>';
        }
        $('#tbody-update').html(html);
        let btn = '<button name="save" type="button" class="btn btn-primary">OK</button>'
                + '<button type="button" class="btn btn-secondary" data-dismiss="modal">Cancel</button>';
        $('#confirmModal').find('.modal-footer').html(btn);
    }else{
        $('#confirmModal').find('.table-responsive').hide();
        let btn = '<button type="button" class="btn btn-primary" data-dismiss="modal">OK</button>';
        $('#records-caption').html('更新可能なデータがありません');
        $('#confirmModal').find('.modal-footer').html(btn);
    }
    $('#confirmModal').modal('show');

    $('#confirmModal').find('button[name=save]').click(function () {
        let currentUrl = location.href;
        let postUrl = '/kakeibosan/records'
        $.ajax({
            url: postUrl,
            data: JSON.stringify(records),
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
