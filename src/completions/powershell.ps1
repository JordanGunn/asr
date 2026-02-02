# oasr completion for PowerShell
# This file provides tab completion for the oasr command in PowerShell.
#
# Installation:
#   Run: oasr completion install
#   Or manually: Add this to your PowerShell profile ($PROFILE)

# Helper functions for dynamic completion
function Get-OasrSkills {
    $skills = oasr registry list --quiet 2>$null | Select-String '^\s+-' | ForEach-Object {
        $_.Line -replace '^\s+- ', '' -split ' ' | Select-Object -First 1
    }
    return $skills
}

function Get-OasrAgents {
    return @('codex', 'copilot', 'claude', 'opencode')
}

function Get-OasrProfiles {
    $profiles = oasr config list 2>$null | Select-String '^profiles\.' | ForEach-Object {
        if ($_ -match '^profiles\.([^=]+)=') {
            $matches[1]
        }
    } | Sort-Object -Unique
    return $profiles
}

function Get-OasrConfigKeys {
    return @(
        'agent',
        'profile',
        'adapter.default',
        'validation.strict',
        'validation.show_references',
        'oasr.completions'
    )
}

# Main completion function
$oasrCompletion = {
    param($wordToComplete, $commandAst, $cursorPosition)

    $command = $commandAst.CommandElements[0].Value
    $elements = $commandAst.CommandElements
    $elementCount = $elements.Count

    # First argument - main commands
    if ($elementCount -eq 2) {
        $commands = @(
            'registry', 'diff', 'sync', 'config', 'clone', 'exec', 'use',
            'find', 'validate', 'clean', 'adapter', 'update', 'info',
            'help', 'completion'
        )
        $commands | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
            [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
        }
        return
    }

    $subcommand = $elements[1].Value

    switch ($subcommand) {
        'exec' {
            $prevWord = if ($elementCount -gt 2) { $elements[$elementCount - 2].Value } else { '' }
            
            switch ($prevWord) {
                '--agent' {
                    Get-OasrAgents | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
                        [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', "Agent: $_")
                    }
                    return
                }
                '--profile' {
                    Get-OasrProfiles | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
                        [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', "Profile: $_")
                    }
                    return
                }
                default {
                    if ($wordToComplete -like '-*') {
                        @('--agent', '--profile', '--agent-flags', '-y', '--yes', '--confirm', '-p', '--prompt') |
                            Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
                            [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
                        }
                    } else {
                        Get-OasrSkills | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
                            [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', "Skill: $_")
                        }
                    }
                    return
                }
            }
        }

        'completion' {
            if ($elementCount -eq 3) {
                @('bash', 'zsh', 'fish', 'powershell', 'install', 'uninstall') | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
                    [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
                }
                return
            }

            if ($wordToComplete -like '-*') {
                @('--force', '--dry-run') | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
                    [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
                }
            }
            return
        }
    }
}

# Register the completion
Register-ArgumentCompleter -Native -CommandName oasr -ScriptBlock $oasrCompletion
