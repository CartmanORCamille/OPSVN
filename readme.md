# AUTO CHECK SUBMIT ORDER

## 它的作用是什么？

- 旨在推进SVN查单自动化，根据需求实现以下功能：

  - SVN自动更新
  - 窗口控制
  - 游戏内脚本控制
  - 数据分析
  - 消息反馈

## 某些参数的记录

- version.json -> windowsInfo.JX3RemakeBVT.className

  - 抢什么焦点？
  - 抢焦点的主要参数，根据这个参数比对当前句柄。
  - 无论是什么版本的客户端，只识别这里的className作为对比。

****

- config.json -> Path.Jx3BVTNeedCheck
  - 需要SVN更新的目录。  
  
****

- config.json -> Path.Jx3BVTWorkPath
  - 启动客户端的工作路径。一般不需更改。

****

- config.json -> Path.JX3ClientX64.exe
  - 启动客户端名字。一般不需更改。
