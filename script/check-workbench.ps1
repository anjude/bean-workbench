param(
  [string]$Root = (Resolve-Path "$PSScriptRoot\..").Path
)

$required = @(
  "AGENTS.md",
  "README.md",
  "docs/workspace.md",
  "docs/self-evolution.md",
  "docs/knowledge-base.md",
  "docs/workflows/README.md",
  "docs/templates/README.md",
  "docs/architecture/README.md",
  "docs/goals/README.md",
  "task/registry.md",
  "task/260614_workbench-init/README.md",
  "archive/README.md",
  ".agents/skills/hair/SKILL.md",
  ".agents/skills/workbench-router/SKILL.md",
  "knowledge-base/common/README.md"
)

$missing = @()
foreach ($item in $required) {
  $path = Join-Path $Root $item
  if (-not (Test-Path -LiteralPath $path)) {
    $missing += $item
  }
}

if ($missing.Count -gt 0) {
  Write-Host "缺少必要文件："
  $missing | ForEach-Object { Write-Host "- $_" }
  exit 1
}

Write-Host "工作台结构检查通过。"
