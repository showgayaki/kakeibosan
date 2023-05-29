# kakeibosan(家計簿さん)
二人用家計簿アプリ。  
pipenv && flask && uWSGI && Nginx  
テンプレートは[now-ui-dashbord](https://github.com/creativetimofficial/now-ui-dashboard)を使用。

##　.env
ルートディレクトリ直下に、.envファイルを作って以下のように記載する。
```
SECRET_KEY=YourSecretKey
DB_ROOT_PASS=YourRootPassword
DB_HOST=kakeibosan_db
DB_NAME=kakeibosan
DB_USER=kakeibosan
DB_PASS=YourUserPassword
```

## Docker使わない場合
###　kakeibosanインストール
`$ git clone https://github.com/showgayaki/kakeibosan.git`  
`$ cd ./kakeibosan`

（仮想環境をプロジェクトディレクトリ配下に作る場合  
`$ export PIPENV_VENV_IN_PROJECT=true`）

`$ pipenv install`

### nginxインストール && 設定
#### インストール
`$ sudo apt install nginx`  

#### 設定ファイルを編集
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


### サービス設定
#### サービス登録
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
#### 自動起動設定
`$ sudo systemctl enable kakeibosan`

あとは  
`$ sudo systemctl start kakeibosan`

するか、マシン再起動すればOKなはず。

`$ systemctl status kakeibosan`  
で、active(running)になっていればOK。

### ファイル更新時
どっちか必要。
#### kakeibosanサービス再起動
`$ sudo systemctl restart kakeibosan`
#### nginx再起動
`$ sudo nginx -s reload`


## Dockerでやる場合
### 本番
docker compose build && docker compose up -d
####　更新時
docker compose down && docker compose build --no-cache && docker compose up -d

### 開発時
dbディレクトリ直下に、本番からdumpしてきたsqlファイルを保存。

docker compose down && docker compose -f docker-compose.dev.yml build --no-cache && docker compose -f docker-compose.dev.yml up -d

[感謝](https://qiita.com/kujira_engineer/items/b4442e4d37b117205aea)

## デモ的なもの
[https://kakeibosan.herokuapp.com/login](https://kakeibosan.herokuapp.com/login)
