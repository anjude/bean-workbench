package cmd

import (
	"os"

	"github.com/spf13/cobra"
)

var rootCmd = &cobra.Command{
	Use:   "bw",
	Short: "bw - 工作台命令行工具",
	Long:  `bw 是工作台的个人命令行工具集，基于 Cobra 构建，用于承载各类本地自动化与实用命令。`,
}

func Execute() {
	if err := rootCmd.Execute(); err != nil {
		os.Exit(1)
	}
}