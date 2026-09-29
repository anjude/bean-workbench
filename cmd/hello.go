package cmd

import (
	"fmt"

	"github.com/spf13/cobra"
)

var helloCmd = &cobra.Command{
	Use:   "hello [name]",
	Short: "Say hello",
	Args:  cobra.MaximumNArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		name := "world"
		if len(args) > 0 {
			name = args[0]
		}
		fmt.Printf("Hello, %s!\n", name)
	},
}

func init() {
	rootCmd.AddCommand(helloCmd)
}
