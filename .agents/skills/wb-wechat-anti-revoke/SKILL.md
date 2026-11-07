---
name: wb-wechat-anti-revoke
description: 在 macOS 上安装、检查或回滚 WeChatIntercept 微信防撤回补丁；用户提到微信防撤回、antirevoke、patch.sh 失效或微信升级后补丁失效时使用。
---

# 微信防撤回补丁

通过本机 WeChatIntercept 项目给 macOS 微信安装防撤回 hook。此操作会改写微信主程序并用 ad-hoc 签名替换原签名；微信更新可能覆盖补丁。用户明确提出安装或修复时可执行。

## 本机位置

- 微信：`/Applications/WeChat.app`
- 补丁项目：`/Users/bean/workspace/code/WeChatIntercept`
- 上游仓库：[a244573118/WeChatIntercept](https://github.com/a244573118/WeChatIntercept)；本机克隆当前记录的提交为 `a39fbc91b5bfba85a366f57d2bb08b2ffdf43d5b`（2026-06-11）。更新或排错时可据此追溯来源；本机项目的改动和工作区状态仍须先检查。
- 二进制备份与回滚：`/Users/bean/WeChatBackup/`
- 安装日志：`/tmp/antirevoke_debug.log`

这些路径是当前机器配置。迁移到其他机器时，先检查并修订路径，不要假设目录存在。

## 安装或修复

1. 读取微信 `CFBundleShortVersionString` 和 `CFBundleVersion`，并确认补丁项目存在。先查看项目脚本当前内容和工作区改动，不覆盖项目中的用户修改。
2. 检查微信是否运行。需要安装时先正常退出微信；不要无提示强制结束用户进程。
3. 在 `/Users/bean/WeChatBackup/` 保存当前主程序原件。文件名同时包含版本和 build，例如 `WeChat-4.1.15-270135-original`；若文件已存在，先比较哈希，不覆盖不一致的备份。
4. 不直接运行 `patch.sh` 默认安装入口：它调用 `remove_provenance()`，会删除并重打包整个 `/Applications/WeChat.app`。按本机环境生成跳过该函数调用的临时副本后运行：

   ```sh
   cd /Users/bean/workspace/code/WeChatIntercept
   sed 's/^    remove_provenance$/    echo "[skip provenance repack]"/' patch.sh > /tmp/patch_wechat_noprov.sh
   chmod +x /tmp/patch_wechat_noprov.sh
   /tmp/patch_wechat_noprov.sh
   ```

5. 只安装核心防撤回 hook。`--monitor-install` 是另一个高开销的 LLDB 消息监听常驻服务，除非用户单独要求，不安装。
6. 检查 `otool -L /Applications/WeChat.app/Contents/MacOS/WeChat` 是否包含 `WeChatAntiRevoke.dylib`，并查看 `/tmp/antirevoke_debug.log`。只有看到 `trampoline 安装成功` 和 `就绪，等待撤回消息` 才报告 hook 已生效。单看安装器启动成功或 dylib 加载成功不够。

## 版本适配

补丁对未预置的微信 build 会先尝试特征码搜索。日志出现 `[未适配]` 或 `快速路径未命中` 本身不代表失败；若特征码搜索命中且 trampoline 安装成功，则 hook 已就绪。若搜索失败或 hook 未就绪，停止，不要声称防撤回有效。

本机曾在应用包显示 4.1.15 / build 270135 时，运行日志识别到核心微信 4.2.0 / build 270350；特征码搜索找到目标并成功安装 arm64 trampoline。排查时以运行时日志中的核心版本、build 和 hook 结果为准，同时记录应用包版本信息。

## 回滚

`patch.sh --uninstall` 只移除 dylib，可能把仍引用 dylib 的 `LC_LOAD_DYLIB` 留在主程序里，导致微信无法启动。优先用安装前备份的**同一 build**恢复主程序，然后重签名并启动微信。回滚脚本 `/Users/bean/WeChatBackup/restore.sh` 必须指向本次匹配的备份；执行前先检查脚本内容和备份哈希。不要使用指向旧版备份的回滚脚本。

## 可选消息监听

只有用户明确要求撤回通知附带原文时才讨论 `--monitor-install`。该服务通过 LLDB attach 微信进程、扫描大型代码段并持续缓存近期消息，实测会占用数 GB 内存，attach 时 CPU 峰值很高。安装、卸载和状态查询需在用户自己的图形登录终端完成；不要在助手 shell 中尝试 bootstrap LaunchAgent。缓存位于 `/tmp/wechat_msg_cache.tsv`，可能包含聊天正文。
