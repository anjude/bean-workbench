package cmd

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"

	"github.com/spf13/cobra"
)

// workbenchRoot is set by Makefile builds so an installed hr can locate sibling tools.
var workbenchRoot string

func runSourceCollectorWithModel(cmd *cobra.Command, video, model, language, platform string) error {
	collectorDir, err := findSourceCollectorDir()
	if err != nil {
		return err
	}
	entrypoint, err := findCollectorEntrypoint(collectorDir)
	if err != nil {
		return err
	}
	args := []string{"collect", "--platform", platform}
	if strings.TrimSpace(model) != "" {
		args = append(args, "--model", model)
	}
	if strings.TrimSpace(language) != "" {
		args = append(args, "--language", language)
	}
	retry, _ := cmd.Flags().GetBool("retry")
	if retry {
		args = append(args, "--retry")
	}
	args = append(args, "--", video)
	return executeCollector(cmd, entrypoint, collectorDir, args)
}

func executeCollector(cmd *cobra.Command, entrypoint, collectorDir string, args []string) error {
	process := exec.CommandContext(cmd.Context(), entrypoint, args...)
	process.Dir = collectorDir
	process.Stdout = cmd.OutOrStdout()
	process.Stderr = cmd.ErrOrStderr()
	process.Stdin = os.Stdin
	return process.Run()
}

func findSourceCollectorDir() (string, error) {
	if configured := os.Getenv("HR_SOURCE_COLLECTOR_DIR"); configured != "" {
		return validateCollectorDir(configured)
	}
	roots := []string{workbenchRoot}
	if cwd, err := os.Getwd(); err == nil {
		roots = append(roots, cwd)
	}
	if executable, err := os.Executable(); err == nil {
		roots = append(roots, filepath.Dir(executable))
	}
	for _, root := range roots {
		for dir := root; dir != ""; dir = filepath.Dir(dir) {
			candidate := filepath.Join(dir, "tools", "source-collector")
			if _, err := os.Stat(filepath.Join(candidate, "pyproject.toml")); err == nil {
				return candidate, nil
			}
			parent := filepath.Dir(dir)
			if parent == dir {
				break
			}
		}
	}
	return "", fmt.Errorf("找不到工作台 source-collector；请设置 HR_SOURCE_COLLECTOR_DIR 或在工作台目录运行 make install")
}

func validateCollectorDir(path string) (string, error) {
	absolute, err := filepath.Abs(path)
	if err != nil {
		return "", err
	}
	if _, err := os.Stat(filepath.Join(absolute, "pyproject.toml")); err != nil {
		return "", fmt.Errorf("采集器目录无效 %q：缺少 pyproject.toml", absolute)
	}
	return absolute, nil
}

func findCollectorEntrypoint(dir string) (string, error) {
	for _, venv := range []string{".venv-asr", ".venv"} {
		candidate := filepath.Join(dir, venv, "bin", "hr-source")
		if info, err := os.Stat(candidate); err == nil && !info.IsDir() {
			return candidate, nil
		}
	}
	if candidate, err := exec.LookPath("hr-source"); err == nil {
		return candidate, nil
	}
	return "", fmt.Errorf("未找到 hr-source 命令；请先按 %s/README.md 安装采集器", dir)
}

func runCollectorCommand(cmd *cobra.Command, args []string) error {
	dir, err := findSourceCollectorDir()
	if err != nil {
		return err
	}
	entry, err := findCollectorEntrypoint(dir)
	if err != nil {
		return err
	}
	return executeCollector(cmd, entry, dir, args)
}
