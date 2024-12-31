#!/bin/bash

cd $2/身份证照片识别
conda activate $1
pyinstaller main_new.spec

echo 更新完成
echo 旧版本$3      新版本$4 
echo 所有信息已转移到新软件内，旧软件文件夹可以整体删除
touch flag_file
exit