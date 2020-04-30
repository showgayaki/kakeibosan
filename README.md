# kakeibosan(家計簿さん)
二人用家計簿アプリ。  
pipenv && flask && uWSGI && Nginx  
テンプレートは[now-ui-dashbord](https://github.com/creativetimofficial/now-ui-dashboard)を使用。

## kakeibosanインストール
`$ git clone [ここのURL].git`  
`$ cd ./kakeibosan`

（仮想環境をプロジェクトディレクトリ配下に作る場合  
`$ export PIPENV_VENV_IN_PROJECT=true`）

`$ pipenv install`

## nginxインストール && 設定
### インストール
`$ sudo apt install nginx`  

### 設定ファイルを編集
`$ sudo vi /etc/nginx/sites-available/default`

以下location〜箇所を追記。
```
server {
        〜〜〜省略〜〜〜
        location /kakeibosan {
                include uwsgi_params;
                uwsgi_pass unix:///tmp/uwsgi.sock;
        }

        location ^~ /kakeibosan/static/ {
                include  /etc/nginx/mime.types;
                root /home/ubuntu/apps/kakeibosan/;
        }
}
```


## サービス設定
### サービス登録
`$ sudo vi /etc/systemd/system/kakeibosan.service`    

ExecStartとUserは、環境によって要書き換え。

```
[Unit]
Description=kakeibosan

[Service]
Type=simple
Restart=always
ExecStart=/home/ubuntu/apps/kakeibosan/run.sh
User=ubuntu

[Install]
WantedBy=multi-user.target
```
### 自動起動設定
`$ sudo systemctl enable kakeibosan`

あとは  
`$ sudo systemctl start kakeibosan`

するか、マシン再起動すればOKなはず。

`$ systemctl status kakeibosan`  
で、active(running)になっていればOK。

## ファイル更新時
どっちか必要。
### kakeibosanサービス再起動
`$ sudo systemctl restart kakeibosan`
### nginx再起動
`$ sudo nginx -s reload`

## デモ的なもの
coming soon...
