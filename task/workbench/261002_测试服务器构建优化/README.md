# 261002 测试服务器构建优化

目标机器：`8.155.38.83`（root，hostname `milk2025`，Ubuntu 22.04 / kernel 5.15 / 已运行 69 天）
主目录：`/workspace/test-backend-superone`（backend-superone 测试环境）

## 结论

构建失败的主因不是 CPU，**是磁盘 I/O 太慢 + 内存无缓冲空间 + `deploy.sh` 超时设得太短**。
实测一次温缓存 `go build` 跑了 **10 分钟以上仍未结束**，而 `deploy.sh` 给 `go build` 的超时只有 **300 秒**——超时必被 SIGTERM 杀掉，然后走企微"部署失败"告警。

## 一、硬件与基线

| 项 | 实测值 | 说明 |
| --- | --- | --- |
| CPU | 2 vCPU（Xeon Platinum 2.5GHz） | `nproc`=2，`-p` 并行度上限就是 2 |
| 内存 | **1673 MB** | 极小 |
| Swap | **0** | `vm.swappiness=0`，完全没有缓冲 |
| 磁盘 | 40G，已用 20G，剩 18G | |
| 磁盘直读 | **27.7 MB/s** | `dd iflag=direct`，云盘偏慢，是核心瓶颈 |
| 静置负载 | 100% idle | 机器本身不忙，问题只在构建期 |

### 常驻负载（13 个工作负载跑在 2 核 1.6G 上）

supervisor 8 个：`superone-8081`、`superone-8082`、`superone-test-9091`、`aiunlimit-6000`、`aiunlimit-6001`、`easyipx`、`frps`、`log-tools`

docker 5 个：

| 容器 | 内存占用 | 容器上限 |
| --- | --- | --- |
| mysql | **418 MB**（占整机 25%） | 1 GB |
| postgres | 32.5 MB | 0（不限制） |
| new-api | 28.6 MB | 0（不限制） |
| redis | 2.7 MB | 0（不限制） |
| redis_bjq | 2.3 MB | 0（不限制） |

## 二、实测证据

对 `go build -o /tmp/so_warm_test ./cmd/api_service/main.go` 做一次温缓存实测：

```text
18:55:20  开始
18:59:50  link 进程 RSS 214 MB，状态 D（不可中断 I/O 等待），已跑 4'27"
          load average 2.79 / 3.34 / 2.99（2 核）
          可用内存 572 MB → 377 MB
19:04:47  仍在跑，link 已 10'07"，仍未结束 → 手动终止
```

`vmstat` 期间采样：

```text
 r  b   swpd   free   buff  cache    bi     bo   us sy id wa
 1  2      0  88892    928 563036  122652  704   3 56  7 34
 2  2      0  95228    924 556580  116399    0   2 57  6 36
```

- `wa`（I/O 等待）**34%~36%**，`bi`（块读）**~120 MB/s** → 磁盘被打满
- 可用内存掉到 377 MB，link 进程 214 MB → 内核回收页缓存 → 反复回读慢盘 → **抖动放大**
- 链接器命令行含 `-extld=gcc`，说明宿主机走了 CGO 外部链接

已于 19:07 终止压测，机器恢复：可用内存 593 MB，负载衰减至 100% idle。

## 三、根因排序

### P0 — 直接导致失败

1. **超时 300 秒严重不足。** 实测单次构建 >600 秒。`deploy.sh` 里 `run_with_timeout 300` 到点发 SIGTERM，进程被杀 → 非零退出 → 告警"go build failed"。**这是失败的直接原因，与内存/CPU 无关。**
2. **每次部署都跑 `go mod tidy`。** 它重解析整张模块图（含所有依赖的测试依赖）、依赖网络，且会改写 `go.mod`/`go.sum` —— 一旦改写就**使构建缓存失效**，下一步 `go build` 退化成全量重编。双重惩罚，同样卡在 300 秒。
3. **零 Swap。** 1673 MB 内存，mysqld 占 418 MB，构建期可用只剩 377 MB。没有 swap 兜底，抖动无处释放，极端情况直接 OOM kill（构建被杀同样表现为"构建失败"）。
4. **宿主机 `CGO_ENABLED=1`（`CC=gcc`）。** 触发 gcc 外部链接，更慢更耗内存；而 Dockerfile 里明确设的是 `CGO_ENABLED=0`，说明项目不需要 CGO，宿主机这步是白付出的代价。

### P1 — 让构建本身变慢

5. **Go 工具链不匹配。** `go.mod` 声明 `go 1.24.0` + `toolchain go1.24.5`，宿主机装的却是 **go1.21.4（2023-11）**。每次构建都要切换/下载工具链；缓存一旦失效就是百 MB 级下载，必然超时。另缓存里躺着 **go1.23.11 + go1.24.5 两套**，659 MB 白白占盘。
6. **未剥离符号。** 产物 54 MB 带完整调试信息，链接阶段 I/O 和内存压力都更大。
7. **Docker 构建无缓存复用。** `Dockerfile` 基础镜像 `golang:1.21.4-alpine3.18` 同样低于 go.mod 要求的 1.24；且 `COPY . .` 在 `go mod download` 之前——**任一源码变动都击穿镜像层，全量重下 1.6 GB 模块缓存**。
8. **Docker 构建缓存从不清理。** 2.377 GB，其中 **2.287 GB 可回收**；镜像 1.387 GB 中 91% 可回收。

### P2 — 抬高基线压力

9. **mysqld 吃 418 MB**，容器上限却给到 1 GB（整机 61%），构建期极易挤爆。
10. **所有容器内存上限为 0（不限制）**，没有任何隔离。
11. 常驻服务偏多（`aiunlimit` 双实例、`easyipx`、`frps`），与构建抢 2 核。

## 四、优化项（按优先级）

### P0 止血

| # | 动作 | 命令 / 改法 |
| --- | --- | --- |
| 1 | 删除部署里的 `go mod tidy` | `deploy.sh` 去掉该段（依赖变更时手工跑一次即可） |
| 2 | 放宽构建超时 | `run_with_timeout 300` → `1800`（`go build`、supervisor reload 60→120） |
| 3 | 加 2 GB swap | 见下 |
| 4 | 宿主机关 CGO | `deploy.sh` 中 `go build` 前置 `CGO_ENABLED=0` |

swap：

```bash
fallocate -l 2G /swapfile && chmod 600 /swapfile
mkswap /swapfile && swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
sysctl -w vm.swappiness=10
echo 'vm.swappiness=10' >> /etc/sysctl.conf
```

> `fallocate` 若报不支持，改用 `dd if=/dev/zero of=/swapfile bs=1M count=2048`。
> 磁盘剩 18 GB，2 GB 无压力；swap 只在内存紧张时兜底，避免抖动和 OOM。

`deploy.sh` 构建段改法：

```bash
# 编译（去掉 tidy，加 CGO_ENABLED=0 与 -ldflags="-s -w"）
echo "start go build"
run_with_timeout 1800 env CGO_ENABLED=0 GOPROXY=https://mirrors.aliyun.com/goproxy/,direct \
  /usr/local/go/bin/go build -ldflags="-s -w" -o superone ./cmd/api_service/main.go \
  || { echo "go build failed"; send_wechat_message "$ENV" "失败" "go build failed"; exit 1; }
```

### P1 提速

| # | 动作 | 说明 |
| --- | --- | --- |
| 5 | 宿主机升级 Go 到 **1.24.5** | 消除工具链切换与下载；装完删掉 `go1.23.11` 工具链省 ~300 MB |
| 6 | `go build` 加 `-ldflags="-s -w"` | 产物显著变小，链接更快，I/O 更少 |
| 7 | Dockerfile 换 `golang:1.24-alpine` + BuildKit 缓存挂载 | 见下 |
| 8 | 清理 docker 缓存 | `docker builder prune -f && docker system prune -f` |

Go 升级：

```bash
cd /tmp && wget -q https://go.dev/dl/go1.24.5.linux-amd64.tar.gz
rm -rf /usr/local/go && tar -C /usr/local -xzf go1.24.5.linux-amd64.tar.gz
/usr/local/go/bin/go version
```

Dockerfile 关键改法：

```dockerfile
FROM golang:1.24-alpine AS builder
ENV GO111MODULE=on GOPROXY=https://goproxy.cn,direct CGO_ENABLED=0 GOOS=linux GOARCH=amd64
WORKDIR /app
COPY go.mod go.sum ./
RUN --mount=type=cache,target=/go/pkg/mod go mod download
COPY . .
RUN --mount=type=cache,target=/root/.cache/go-build \
    --mount=type=cache,target=/go/pkg/mod \
    go build -ldflags="-s -w" -o main cmd/api_service/main.go
```

要点：基础镜像对齐 go.mod；`go.mod`/`go.sum` 单独先 COPY，源码变动不再击穿依赖层；两个 cache mount 让模块缓存与构建缓存跨次复用。构建时需 `DOCKER_BUILDKIT=1`。

### P2 降压

| # | 动作 | 命令 |
| --- | --- | --- |
| 9 | mysqld 降内存 | 容器上限 1G→512M，`innodb_buffer_pool_size` 调到 128M~256M |
| 10 | 容器设内存上限 | `docker update --memory=256m --memory-swap=256m new-api postgres` 等 |
| 11 | 精简常驻 | 评估 `aiunlimit-6000/6001`、`superone-test-9091` 是否都要常驻 |
| 12 | 构建降级调度 | `nice -n 10 ionice -c2 -n7 go build ...`，避免打爆线上 8081/8082 |

另：`Dockerfile` 的 `HEALTHCHECK` 用 `curl`，但运行时镜像 `alpine:3.13` 未装 curl，健康检查会一直失败（注释里也标了"未测试"）。若走 docker 部署需补 `apk add curl`，否则删掉该段。

## 五、复测建议

改完 P0 后在同一台机器上复测，对比改动前后：

```bash
cd /workspace/test-backend-superone
time CGO_ENABLED=0 /usr/local/go/bin/go build -ldflags="-s -w" -o /tmp/so_bench ./cmd/api_service/main.go
```

关注三个数：构建耗时、构建期 `wa`、可用内存最低值。目标是把耗时压到 300 秒以内，让原有超时策略重新成立。

## 六、说明

- 本次排查在测试环境机器上执行过一次真实构建压测，期间负载冲到 3.34（2 核），已于 19:07 终止并清理临时产物 `/tmp/so_warm_test`，未改动任何线上服务与配置文件。

## 七、补充：验证构建把服务器打崩了（2026-10-02 19:29 重启）

改完 P0/P1 后跑了一次验证构建（`CGO_ENABLED=0` + `-ldflags="-s -w"`，已加 `nice -n 10 ionice -c2 -n7` 降级调度），结果**系统挂死并重启**。

时间线：

```text
19:20:53  上一轮 boot 最后一条 journal 写入（此后系统无法再写日志）
19:23     验证构建启动
19:29:46  新一轮 boot 开始（journal --list-boots 确认）
19:30:20  SSH 恢复可用，uptime 显示 "up 0 min"
```

内核日志里**没有留下 OOM 记录**——系统抖动到连日志都写不出去，这是内存耗尽的典型表现，不是普通超时。

**根因**：`CGO_ENABLED=0` 改变了构建缓存键，**整份缓存失效 → 全量重编**。全量重编下 Go 按 `GOMAXPROCS=2` 并行起两个 compile 进程，叠加链接阶段（此前实测单 link 就 214 MB），把 1673 MB 内存吃干。而 swap 为 0，`swappiness=0`，内核没有任何缓冲余地 → 挂死重启。

**结论修正**：内存不是"加剧抖动"的间接因素，而是**足以致命的直接因素**。P0 里的「加 swap」从建议升级为**必要条件**；同时应限制构建并行度。

### 重启后的连带问题：supervisor 不等 MySQL

重启后 3 个 superone 实例和 2 个 aiunlimit 全为 `FATAL`，日志显示：

```text
2026/10/02 19:30:05 failed to initialize database, got error dial tcp 127.0.0.1:3306: connect: connection refused
```

supervisord 开机即拉起所有程序，但 docker 里的 MySQL 还没就绪；superone 启动失败，supervisor 重试次数用尽后转 FATAL 不再拉起。**这是既有的启动竞态，与本次改动无关**，但意味着这台机器每次重启后 superone 都不会自动恢复，必须人工 `supervisorctl restart`。

已于 19:32 手动重启恢复：8 个服务全部 RUNNING，8081/8082/9091 的 `/metrics` 均返回 HTTP 200。

### 因此新增两项（未执行，待确认）

| # | 动作 | 命令 / 改法 |
| --- | --- | --- |
| A | **加 2 GB swap**（必须） | 见 P0 #3，磁盘剩 21 GB |
| B | 构建限并行度 `-p 1` | `go build -p 1 ...`，峰值内存减半，代价是耗时增加（超时已放到 1800s，够用） |

在 A、B 落地前，**不要在这台机器上跑全量重编**（即不要触发构建缓存失效），否则会再次打崩。

## 八、实测构建耗时（2026-10-02 19:41-19:49）

加完 swap 后按 `deploy.sh` 的真实配置（未加 `-p 1`）实测三档：

| 场景 | 耗时 | 说明 |
| --- | --- | --- |
| **冷构建**（独立 `GOCACHE`，缓存全空，最坏情况） | **222 s** | swap 峰值 189 MB，可用内存全程 644-827 MB，8 个服务无影响 |
| 缓存失效后首次构建 | 126 s | 即改动 `CGO_ENABLED` 等构建参数后的第一次 |
| **增量构建**（日常部署） | **11 s** | 缓存已热 |

对比改动前：**温缓存构建 >600 秒且跑不完**，最终把系统打崩。

产物体积：54.96 MB → **38.27 MB**（`-ldflags="-s -w"` + CGO=0，缩小 30%）。

**结论：超时 1800 秒过头了，已调到 600 秒**——最坏值 222 s 的 2.7 倍余量，同时不至于让卡死的构建空转半小时。

提速来源拆解：`CGO_ENABLED=0`（去掉 gcc 外部链接，原 link 单步就 10 分钟以上，是最大头）+ `-ldflags="-s -w"`（符号表变小）+ Go 1.24.5 原生免切工具链 + swap 兜底不再抖动。

## 九、Dockerfile 当前并未使用

`docker images` 里有 `superone:latest` / `superone-test:latest`，但**创建于 18 个月前**，且 `docker ps` 中没有任何容器跑这两个镜像。superone 实际由 supervisor 以宿主机二进制方式启动（`superone-8081/8082/test-9091`）。

也就是说 `make build` → `docker build` 这条路目前是休眠状态，本次 Dockerfile 改动属于前瞻维护，不会影响现网部署。若确认以后也不走 docker 部署，可直接删掉 `Dockerfile` 与 `Makefile` 的 `build` 目标，比留着维护更干净。

## 十、当前已落地状态

| 项 | 位置 | 状态 |
| --- | --- | --- |
| 删除 `go mod tidy` | `deploy.sh` | ✅ 已改（服务器 + 本地仓） |
| 超时 300→**600**（实测最坏 222s，留 2.7 倍余量）、reload 60→120 | `deploy.sh` | ✅ 已改 |
| `CGO_ENABLED=0` + `-ldflags="-s -w"` | `deploy.sh` | ✅ 已改 |
| Go 1.21.4 → **1.24.5** | `/usr/local/go` | ✅ 已装（旧版备份 `/usr/local/go.bak-go1.21.4`） |
| Dockerfile 换 `golang:1.24-alpine` + cache mount + 先 COPY `go.mod`/`go.sum` | `Dockerfile` | ✅ 已改（服务器 + 本地仓） |
| 清理 docker 缓存 | 整机 | ✅ 已清，磁盘 18G → 21G |
| **加 2 GB swap** + `swappiness=10` | 整机 | ✅ 已加并持久化（`/etc/fstab` + `/etc/sysctl.conf`） |
| 构建限 `-p 1` | `deploy.sh` | ❌ **不需要**——实测冷构建仅 222s，swap 峰值 189MB，无需牺牲并行度 |
| 停掉 `new-api` 容器并禁止自启 | 容器 | ✅ 已停，restart 策略改 `no` |
| mysqld 降配、其余容器设内存上限 | 容器 | ❌ 未做（P2，非必需） |

回滚点：`deploy.sh.bak.20261002191817`、`Dockerfile.bak.20261002191917`、`/usr/local/go.bak-go1.21.4`。

本地业务仓 `business-repo/backend-superone` 的 `deploy.sh` 与 `Dockerfile` 已同步改动，处于未提交状态。

## 十一、新增依赖怎么办（已在服务器上实测验证）

**结论：不需要进服务器跑 `go mod download`，也不需要跑 `go mod tidy`。**

Go 1.16 起默认 `-mod=readonly`：`go build` **会自动下载** `go.mod` 里已声明的模块，但**不会**自动补写 `go.mod`。所以依赖声明必须由开发者在本地完成，服务器只负责编译。

标准流程：

```bash
go get github.com/xxx/yyy          # 或写好 import 后 go mod tidy
git add go.mod go.sum <业务代码>     # 三者同一次提交
```

之后正常走 `deploy.sh` 即可，新模块会在构建时自动拉取。

### 实测三场景（服务器 /tmp 临时模块，GOPROXY 为阿里云镜像）

| 场景 | 结果 |
| --- | --- |
| A. 依赖已在 `go.mod`，服务器模块缓存里没有 | ✅ `go build` 日志打出 `go: downloading github.com/pkg/errors v0.9.1`，自动下载后构建成功（无需任何 download/tidy） |
| B. 代码 import 了，但 `go.mod` 漏提交 | ❌ 明确失败：`no required module provides package github.com/pkg/errors; to add it: go get github.com/pkg/errors` |
| C. `go.mod` 有但 `go.sum` 漏提交 | ❌ 明确失败：`missing go.sum entry for module providing package ...; to add: go get dltest` |

B、C 这种明确失败正是想要的行为——漏提交会立刻拦下并发企微告警，不会静默带病上线。相比之下，原来在服务器上跑 `go mod tidy` 是**静默改写**依赖声明，既可能改出和本地不一致的结果，又会因改写 `go.mod`/`go.sum` 让构建缓存失效、下一步退化成全量重编。

唯一前提：服务器能连上 `GOPROXY`（`deploy.sh` 里已 `export GOPROXY=https://mirrors.aliyun.com/goproxy/,direct`）。若代理不可用，新依赖下载会失败并告警，属预期内的显式失败。
