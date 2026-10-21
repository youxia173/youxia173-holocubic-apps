# youxia173-holocubic-apps

游侠173 的 HoloCubic 社区应用。每个应用一个目录，之后的新应用也放在这个仓库里。

## 桌宠诺诺

`lite` 分支是精简版 1.1.6。吃饭只保留饭盒，没有拉面、汉堡可乐和女巫师变身。睡觉、看书、游戏、撸猫、激光逗猫和舞蹈仍在。网页可设置活动时长、公历生日、左右天气或休息倒计时，以及上下班时间。完整版在 `full` 和 `main`。

| 目录 | 内容 |
| --- | --- |
| `nono/代码/` | 应用根目录，对应设备 `/sd/apps/nono/` |
| `nono/安装包/` | 1.1.6 精简安装包，约 38.6 MB |
| `nono/说明/` | 动作、养成、生日和网页设置说明 |

解压安装包，把里面的 `nono` 文件夹放到 SD 卡的 `apps` 目录。覆盖更新时保留 `user-settings.json`、`needs.json`、`weather-history.json` 和 `holiday-cache.json`。

Windows 版源码、便携包和 exe 只留在本地，不放进这个仓库。

## 黄金矿工

| 目录 | 内容 |
| --- | --- |
| `gold-miner/代码/` | 应用根目录，对应设备 `/sd/apps/gold_miner/` |
| `gold-miner/安装包/` | 完整安装包，首次安装和覆盖更新都用这一份 |
| `gold-miner/说明/` | 安装步骤和按键 |

解压安装包，把里面的 `gold_miner` 文件夹放到 SD 卡的 `apps` 目录，不要多套一层。

## 网页手柄

在官方 HID Pad 上增加网页接管，当前版本 1.1.4。

| 目录 | 内容 |
| --- | --- |
| `hidpad/代码/` | 应用根目录，对应设备 `/sd/apps/hidpad/` |
| `hidpad/安装包/` | 更新包。设备上已有官方手柄服务时使用 |
| `hidpad/说明/` | 按键、改键和接管说明 |

这是更新包，不包含 `modules/hidpad.so` 和 `config.json`，安装时不要覆盖这两份设备文件。打开 `http://设备IP/hidpad/remote/` 即可使用。
