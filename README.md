
# 幻兽帕鲁QQ机器人插件

## 当前插件为测试阶段，如有BUG请提交issue

### ★ 纯粹用爱发电，如果你喜欢的话，请给仓库点一个star支持一下2333 ★

#### 如有魔改版请遵守本插件的GPL3.0开源协议并保持开源！！最好注明来源支持一下作者hhh

#### 帕鲁别称存在插件目录/breeding/base_data/pal_data.json文件中，有新增的别称可以提交PR共享出来哦

## 插件说明

> 这是一个适用[hoshinoBot](https://github.com/Ice-Cirno/HoshinoBot)的幻兽帕鲁功能插件，数据来自：

 + 游戏解包数据
 + [配种机制分析](https://www.reddit.com/r/Palworld/comments/19d98ws/spreadsheet_all_breeding_combinations_datamined/?rdt=53595)

> 当前支持的模块（具体命令请看本页面下方功能命令和描述）

 + 帕鲁配种计算器
 + 服务端rcon管理（需要python3.8+）

## 本仓库链接

https://github.com/azmiao/PalWorldPlugin

## 最近的五条更新日志

|   更新时间   |     版本号     | 更新日志&备注          |
|:--------:|:-----------:|:-----------------|
| 24-03-03 | v0.3.0-beta | 添加rcon功能          |
| 24-01-29 | v0.2.1-beta | 修复部分神兽配种问题       |
| 24-01-26 | v0.2.0-beta | 新增帕鲁繁殖力表         |
| 24-01-25 | v0.1.0-beta | 新增帕鲁配种计算器，基本功能可用 |

## 功能命令和描述
### 帕鲁配种
|       命令       |          说明          |
|:--------------:|:--------------------:|
|     帕鲁繁殖力表     |      查询帕鲁的繁殖力表       |
| 帕鲁配种 帕鲁1+帕鲁2=? |     根据父母帕鲁计算子代帕鲁     |
|  帕鲁配种 ?+?=帕鲁1  |   查询该帕鲁可以由哪些父母育种出    |
|    帕鲁配种 帕鲁1    |       同上，仅是简写        |
| 帕鲁配种 帕鲁1+?=帕鲁2 | 根据子代和一方父母帕鲁计算另一方父母是谁 |

### 服务端rcon管理
|       命令       |          说明          |
|:--------------:|:--------------------:|
| 帕鲁rcon绑定 | 根据提示，绑定帕鲁服务器 |
| 帕鲁服务器信息 | 获取帕鲁服务器信息（对应命令 Info） |
| 谁在帕鲁 | 看看帕鲁服务器里有谁（对应命令 ShowPlayers） |
| 帕鲁关服 | 10s后安全关闭帕鲁服务器（对应命令 Shutdown 10） |
| 帕鲁广播 + 广播内容 | 向服务器发送消息（对应命令 Broadcast xxxx） |
| 帕鲁rcon指令 + 指令 | 执行指定rcon命令 |

## 插件安装

1. git clone本插件（注：建议使用git clone，不建议下载压缩包，另外请确保git环境变量正常）：

    在 HoshinoBot\hoshino\modules 目录下使用以下命令拉取本项目
    ```
    git clone https://github.com/azmiao/PalWorldPlugin
    ```

2. 安装依赖：

    到HoshinoBot\hoshino\modules\PalWorldPlugin目录下，管理员方式打开powershell
    ```
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --user
    ```

3. 在 HoshinoBot\hoshino\config\ `__bot__.py` 文件的 MODULES_ON 加入 'PalWorldPlugin'

    然后重启 HoshinoBot