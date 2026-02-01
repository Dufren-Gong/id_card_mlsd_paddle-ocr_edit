#!/bin/bash

# echo -n "请输入git更改描述:"
# read commit_message

git add .
# git commit -m "$commit_message"
git commit -m $1
git push -u origin main