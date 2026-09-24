.PHONY: release

msg ?= update

# Usage: make release msg="your commit message"
release:
	git add .
	git commit -m "$(msg)" || true
