# README
# 基础设施：ESXi 服务器与虚拟机部署指南

## 1. ESXi 主机网络与授权
* [cite_start]先把 ESXi 刷到主板上，安装完成后设置密码 [cite: 1]。
* [cite_start]输入密码配置网络 [cite: 2]。
* [cite_start]Ipv4：`192.168.11.110` [cite: 3]。
* [cite_start]DNS：`192.168.11.1` [cite: 4]。
* [cite_start]管理网址：`192.168.11.110` [cite: 5]。
* [cite_start]密码为刚刚设置的密码：`@Admin123i` [cite: 6]。
* [cite_start]进入网页，更改许可证输入密钥 [cite: 7]。
* [cite_start]永久密钥：`4V492-44210-48830-931GK-2PRJ4` [cite: 8]。

## 2. 虚拟机新建与显卡直通
* [cite_start]进行显卡直通：主机—>管理—>硬件—>选择相应显卡—>切换直通 [cite: 9]。
* [cite_start]新建虚拟机 [cite: 10]：
  * [cite_start]1 需要先下载镜像，然后上载到服务器内 [cite: 11]。
  * [cite_start]2 接下来选择相应的版本，进行资源分配 [cite: 12][cite_start]。目前两台虚拟机，每个都是 20 核，内存 48G，硬盘 1T，分别一张 4090 [cite: 13]。
  * [cite_start]3 启动项加上之前上载的镜像，进行系统安装 [cite: 14]。
  * [cite_start]4 目前 windows 镜像与 Ubuntu 镜像装完都有显卡驱动，不需要重装 [cite: 15]。
  * [cite_start]5 Ubuntu 的 Shh 需要重新配置：`user@192.168.11.188` 密码 `Admin123i` [cite: 16]。
