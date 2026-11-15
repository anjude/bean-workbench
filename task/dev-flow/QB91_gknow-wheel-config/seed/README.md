# 首批系统转盘配置

- `first-batch.json`：3 个系统转盘、202 个候选项的 admin API 导入文件；`where-to-go` 使用 `filter_first`，默认筛选项为深圳。
- `assets/`：从 `uni-gknow/src/static/icons/tools/` 的三个原 SVG 导出的 288×288 PNG；原 SVG 保留在业务仓。test 上传地址已写入 seed。
- `sync.mjs`：只向空目标创建并发布配置；任意目标 `wheel_key` 已存在时直接失败，不覆盖现有配置。

运行前确认目标环境并设置 API 地址：

```bash
WHEEL_API_BASE_URL=http://localhost:18080 node task/dev-flow/QB91_gknow-wheel-config/seed/sync.mjs
```

脚本从 `.agents/local-config/image-upload/admin.jwt` 读取 Gknow 管理员凭证，不打印 token；也可通过 `WHEEL_ADMIN_TOKEN_FILE` 指向其他权限为 600 的凭证文件。重复运行时需先人工确认目标 wheel 的更新或删除范围，不把脚本结果当成覆盖授权。
