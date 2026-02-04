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
    $profiles = oasr config profiles --names 2>$null | ForEach-Object {
        $_
    } | Sort-Object -Unique
    return $profiles
}

function Get-OasrConfigKeys {
    return @(
        'agent',
        'profile',
        'oasr.default_profile',
        'adapter.default_targets',
        'validation.strict',
        'validation.reference_max_lines',
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
            'registry', 'diff', 'sync', 'config', 'profile', 'clone', 'exec', 'use',
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
                        @('--agent', '--profile', '--agent-flags', '-y', '--yes', '--confirm', '-p', '--prompt', '--unsafe') |
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

        'config' {
            if ($elementCount -eq 3) {
                @('set', 'get', 'list', 'agent', 'validation', 'adapter', 'oasr', 'profiles', 'man', 'validate', 'path') |
                    Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
                    [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
                }
                return
            }

            $prevWord = if ($elementCount -gt 2) { $elements[$elementCount - 2].Value } else { '' }
            if ($prevWord -eq 'set' -and $elementCount -eq 4) {
                Get-OasrConfigKeys | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
                    [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', "Key: $_")
                }
                return
            }

            if ($prevWord -eq 'set' -and $elementCount -eq 5) {
                $key = $elements[3].Value
                switch ($key) {
                    'agent' {
                        Get-OasrAgents | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
                            [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', "Agent: $_")
                        }
                        return
                    }
                    'profile' { 
                        Get-OasrProfiles | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
                            [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', "Profile: $_")
                        }
                        return
                    }
                    'oasr.default_profile' {
                        Get-OasrProfiles | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
                            [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', "Profile: $_")
                        }
                        return
                    }
                    'validation.strict' { 
                        @('true', 'false') | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
                            [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
                        }
                        return
                    }
                    'oasr.completions' { 
                        @('true', 'false') | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
                            [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
                        }
                        return
                    }
                }
            }

            if ($elements[2].Value -eq 'get' -and $elementCount -eq 4) {
                Get-OasrConfigKeys | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
                    [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', "Key: $_")
                }
                return
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

        'profile' {
            if ($elementCount -eq 3) {
                Get-OasrProfiles | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
                    [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', "Profile: $_")
                }
                return
            }
        }
    }
}

# Register the completion
Register-ArgumentCompleter -Native -CommandName oasr -ScriptBlock $oasrCompletion
