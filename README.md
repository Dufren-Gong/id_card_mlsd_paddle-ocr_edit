# id_card_mlsd_paddle-ocr_edit

## 激活conda环境

conda activate <your_conda_environment_name>

## 下载依赖库

pip install -r ./模版/配置和记录/requirments.txt

## 如果要打包windows软件

cp ./模版/配置和记录/new/main.spec ./main.spec

## 根据./模版/配置和记录/安装使用记录.txt修改main.spec内容

pip install pyinstaller

pyinstaller main.spec

## 如果出现代理连接问题,获取代理ip端口[port=29758 for upnet]

git config --global http.proxy 127.0.0.1:port

git config --global https.proxy 127.0.0.1:port

## 上传git

git add .

git commit -m "<更改描述>"

git push -u origin main