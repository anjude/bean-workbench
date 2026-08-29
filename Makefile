.PHONY: help check commit

COMMIT_NAME := anjude
COMMIT_EMAIL := aboy007262@163.com
PYTHON ?= python3

help:
	@echo "可用命令："
	@echo "  make check  检查工作台基础结构"
	@echo "  make commit [message words...]  提交工作台全部变更"

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
