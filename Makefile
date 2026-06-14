.PHONY: help check

help:
	@echo "可用命令："
	@echo "  make check  检查工作台基础结构"

check:
	@pwsh -NoProfile -ExecutionPolicy Bypass -File script/check-workbench.ps1
