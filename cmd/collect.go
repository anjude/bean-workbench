package cmd

import (
	"path/filepath"

	"github.com/spf13/cobra"
)

var collectCmd = &cobra.Command{
	Use:   "collect",
	Short: "采集互联网来源资料",
	Long:  "调用工作台来源采集工具，收集视频字幕并生成可复核的来源资料包。",
}

func init() {
	rootCmd.AddCommand(collectCmd)
	for _, source := range []struct{ command, platform, label string }{
		{command: "bilibili", platform: "bilibili", label: "B 站"},
		{command: "youtube", platform: "youtube", label: "YouTube"},
		{command: "xhs", platform: "xiaohongshu", label: "小红书"},
		{command: "video", platform: "generic_video", label: "公开视频"},
		{command: "file", platform: "local_file", label: "本地视频文件"},
	} {
		source := source
		command := &cobra.Command{
			Use:   source.command + " <视频链接或文件路径>",
			Short: "采集 " + source.label + "字幕",
			Args:  cobra.ExactArgs(1),
			RunE: func(cmd *cobra.Command, args []string) error {
				cmd.SilenceUsage = true
				model, _ := cmd.Flags().GetString("model")
				language, _ := cmd.Flags().GetString("language")
				input := args[0]
				if source.platform == "local_file" {
					absolute, err := filepath.Abs(input)
					if err != nil {
						return err
					}
					input = absolute
				}
				return runSourceCollectorWithModel(cmd, input, model, language, source.platform)
			},
		}
		command.Flags().Bool("retry", false, "重试该视频已有的失败或受限任务")
		command.Flags().String("model", "", "无平台字幕时使用的本地转写模型；留空使用默认模型")
		command.Flags().String("language", "", "ASR 语言提示，例如 Chinese 或 English")
		collectCmd.AddCommand(command)
	}
}

func init() {
	modelsCmd := &cobra.Command{Use: "models", Short: "管理本机 ASR 模型"}
	modelsCmd.AddCommand(&cobra.Command{Use: "list", Short: "查看模型目录和本机安装状态", Args: cobra.NoArgs,
		RunE: func(cmd *cobra.Command, args []string) error {
			cmd.SilenceUsage = true
			return runCollectorCommand(cmd, []string{"models", "list"})
		},
	})
	modelsCmd.AddCommand(&cobra.Command{Use: "download <模型 ID>", Short: "下载并校验指定模型", Args: cobra.ExactArgs(1),
		RunE: func(cmd *cobra.Command, args []string) error {
			cmd.SilenceUsage = true
			return runCollectorCommand(cmd, []string{"models", "download", args[0]})
		},
	})
	rootCmd.AddCommand(modelsCmd)
}

func init() {
	collectCmd.AddCommand(&cobra.Command{Use: "jobs", Short: "查看采集任务和来源包路径", Args: cobra.NoArgs,
		RunE: func(cmd *cobra.Command, args []string) error {
			cmd.SilenceUsage = true
			return runCollectorCommand(cmd, []string{"jobs"})
		},
	})
	collectCmd.AddCommand(&cobra.Command{Use: "serve", Short: "启动本机来源采集网页", Args: cobra.NoArgs,
		RunE: func(cmd *cobra.Command, args []string) error {
			cmd.SilenceUsage = true
			return runCollectorCommand(cmd, []string{"serve"})
		},
	})
	collectCmd.AddCommand(&cobra.Command{Use: "import-zip <文件>", Short: "导入浏览器插件来源 ZIP", Args: cobra.ExactArgs(1),
		RunE: func(cmd *cobra.Command, args []string) error {
			cmd.SilenceUsage = true
			path, err := filepath.Abs(args[0])
			if err != nil {
				return err
			}
			return runCollectorCommand(cmd, []string{"import-zip", path})
		},
	})
}
