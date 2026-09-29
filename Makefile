.PHONY: help check commit install build test clean

COMMIT_NAME := anjude
COMMIT_EMAIL := aboy007262@163.com
PYTHON ?= python3

# Go CLI (bw)
BINARY := bw
GOBIN := $(shell go env GOPATH)/bin

help:
	@echo "可用命令："
	@echo "  make check    检查工作台基础结构"
	@echo "  make commit [message words...]  提交工作台全部变更"
	@echo "  make build    编译 bw 到当前目录"
	@echo "  make install  安装 bw 到 $(GOBIN)（需该目录在 PATH 中）"
	@echo "  make test     运行 bw 的 Go 测试"
	@echo "  make clean    删除编译产物"

check:
	@command -v $(PYTHON) >/dev/null 2>&1 || { echo "错误: 未找到 $(PYTHON)，可用 make check PYTHON=/path/to/python3 指定"; exit 1; }
	@$(PYTHON) script/check-workbench.py

commit:
	@git add -A
	if [ -z "$(strip $(filter-out $@,$(MAKECMDGOALS)))" ]; then \
		git -c user.name="$(COMMIT_NAME)" -c user.email="$(COMMIT_EMAIL)" commit -m "chore: update workbench"; \
	else \
		git -c user.name="$(COMMIT_NAME)" -c user.email="$(COMMIT_EMAIL)" commit -m "$(strip $(filter-out $@,$(MAKECMDGOALS)))"; \
	fi

build:
	go build -o $(BINARY) .

install:
	@mkdir -p $(GOBIN)
	go build -o $(GOBIN)/$(BINARY) .
	@echo "Installed $(BINARY) to $(GOBIN)/$(BINARY)"
	@echo "Make sure $(GOBIN) is in your PATH to run 'bw' from anywhere."

test:
	go test ./cmd/...

clean:
	rm -f $(BINARY)
