param(
  [string]$Root = (Resolve-Path "$PSScriptRoot\..").Path
)

$required = @(
  "AGENTS.md"
  "README.md"
  "docs/workspace.md"
  "docs/self-evolution.md"
  "docs/knowledge-base.md"
  "docs/workflows/README.md"
  "docs/templates/README.md"
  "docs/workflows/business-request-loop.md"
  "docs/workflows/business-generation-checklist.md"
  "docs/workflows/workbench-evolution.md"
  "docs/architecture/README.md"
  "docs/goals/README.md"
  "task/registry.md"
  "task/260614_workbench-init/README.md"
  "archive/README.md"
  ".agents/skills/hair/SKILL.md"
  ".agents/skills/workbench-router/SKILL.md"
  "knowledge-base/common/README.md"
  "business-repo/backend-superone/AGENTS.md"
  "business-repo/bt/AGENTS.md"
  "business-repo/frontend-investment-platform/AGENTS.md"
  "business-repo/frontend-contracts/AGENTS.md"
  "business-repo/frontend-superone/AGENTS.md"
  "business-repo/miniprogram-superone/AGENTS.md"
  "business-repo/uni-superone/AGENTS.md"
  "business-repo/uni-carbon-space/AGENTS.md"
  "business-repo/utools-bean-note/AGENTS.md"
  "business-repo/utools-bean-option/AGENTS.md"
  "business-repo/utools-superone/AGENTS.md"
)

$missing = @()
foreach ($item in $required) {
  $path = Join-Path $Root $item
  if (-not (Test-Path -LiteralPath $path)) {
    $missing += $item
  }
}

if ($missing.Count -gt 0) {
  Write-Host "Missing required files:"
  $missing | ForEach-Object { Write-Host "- $_" }
  exit 1
}

Write-Host "Workbench structure check passed."
