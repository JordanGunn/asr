# oasr completion for fish
# This file provides tab completion for the oasr command in fish.
#
# Installation:
#   Run: oasr completion install
#   Or manually: Copy to ~/.config/fish/completions/oasr.fish

# Helper functions for dynamic completion
function __oasr_skills
    oasr registry list --quiet 2>/dev/null | grep '^  -' | sed 's/^  - //' | awk '{print $1}'
end

function __oasr_agents
    echo codex
    echo copilot
    echo claude
    echo opencode
end

function __oasr_profiles
    oasr config profiles --names 2>/dev/null
end

function __oasr_config_keys
    echo agent
    echo profile
    echo oasr.default_profile
    echo adapter.default_targets
    echo validation.strict
    echo validation.reference_max_lines
    echo oasr.completions
end

# Remove default completions
complete -c oasr -e

# Global options
complete -c oasr -l help -s h -d "Show help"
complete -c oasr -l version -d "Show version"
complete -c oasr -l config -d "Config file path" -r
complete -c oasr -l json -d "JSON output (v1|v2)" -a "v1 v2"
complete -c oasr -l quiet -d "Suppress warnings"

# Main commands
complete -c oasr -f -n __fish_use_subcommand -a registry -d "Manage skill registry"
complete -c oasr -f -n __fish_use_subcommand -a diff -d "Show tracked skill status"
complete -c oasr -f -n __fish_use_subcommand -a sync -d "Refresh tracked skills"
complete -c oasr -f -n __fish_use_subcommand -a status -d "Show manifest status"
complete -c oasr -f -n __fish_use_subcommand -a config -d "Manage configuration"
complete -c oasr -f -n __fish_use_subcommand -a profile -d "Select execution profile"
complete -c oasr -f -n __fish_use_subcommand -a clone -d "Clone skills to directory"
complete -c oasr -f -n __fish_use_subcommand -a exec -d "Execute a skill"
complete -c oasr -f -n __fish_use_subcommand -a find -d "Find skills recursively"
complete -c oasr -f -n __fish_use_subcommand -a validate -d "Validate skills"
complete -c oasr -f -n __fish_use_subcommand -a adapter -d "Generate IDE files"
complete -c oasr -f -n __fish_use_subcommand -a update -d "Update OASR tool"
complete -c oasr -f -n __fish_use_subcommand -a info -d "Show skill information"
complete -c oasr -f -n __fish_use_subcommand -a about -d "Show version and credits"
complete -c oasr -f -n __fish_use_subcommand -a help -d "Show help"
complete -c oasr -f -n __fish_use_subcommand -a completion -d "Manage shell completions"

# exec command
complete -c oasr -f -n "__fish_seen_subcommand_from exec" -l unsafe -d "Pass unsafe agent flags"
complete -c oasr -f -n "__fish_seen_subcommand_from exec" -l agent -d "Agent to use" -a "(__oasr_agents)"
complete -c oasr -f -n "__fish_seen_subcommand_from exec" -l profile -d "Policy profile" -a "(__oasr_profiles)"
complete -c oasr -f -n "__fish_seen_subcommand_from exec" -l agent-flags -d "Additional agent flags"
complete -c oasr -f -n "__fish_seen_subcommand_from exec" -s y -l yes -d "Skip confirmation"
complete -c oasr -f -n "__fish_seen_subcommand_from exec" -l confirm -d "Force confirmation"
complete -c oasr -f -n "__fish_seen_subcommand_from exec" -s p -l prompt -d "Prompt from file" -r
complete -c oasr -f -n "__fish_seen_subcommand_from exec; and not __fish_seen_subcommand_from (__oasr_skills)" -a "(__oasr_skills)" -d "Skill"

# clone command
complete -c oasr -f -n "__fish_seen_subcommand_from clone" -s t -l target -d "Target directory" -r
complete -c oasr -f -n "__fish_seen_subcommand_from clone; and not __fish_seen_subcommand_from (__oasr_skills)" -a "(__oasr_skills)" -d "Skill"

# info command
complete -c oasr -f -n "__fish_seen_subcommand_from info" -l files -d "Show file list"
complete -c oasr -f -n "__fish_seen_subcommand_from info" -l json -d "JSON output (v1|v2)" -a "v1 v2"
complete -c oasr -f -n "__fish_seen_subcommand_from info; and not __fish_seen_subcommand_from (__oasr_skills)" -a "(__oasr_skills)" -d "Skill"

# validate command
complete -c oasr -f -n "__fish_seen_subcommand_from validate" -l json -d "JSON output (v1|v2)" -a "v1 v2"
complete -c oasr -f -n "__fish_seen_subcommand_from validate; and not __fish_seen_subcommand_from (__oasr_skills)" -a "(__oasr_skills)" -d "Skill"

# status command
complete -c oasr -f -n "__fish_seen_subcommand_from status" -l json -d "JSON output (v1|v2)" -a "v1 v2"
complete -c oasr -f -n "__fish_seen_subcommand_from status; and not __fish_seen_subcommand_from (__oasr_skills)" -a "(__oasr_skills)" -d "Skill"

# config subcommands
complete -c oasr -f -n "__fish_seen_subcommand_from config; and not __fish_seen_subcommand_from set get list agent validation adapter oasr profiles man validate path" -a "set" -d "Set configuration value"
complete -c oasr -f -n "__fish_seen_subcommand_from config; and not __fish_seen_subcommand_from set get list agent validation adapter oasr profiles man validate path" -a "get" -d "Get configuration value"
complete -c oasr -f -n "__fish_seen_subcommand_from config; and not __fish_seen_subcommand_from set get list agent validation adapter oasr profiles man validate path" -a "list" -d "List all configuration"
complete -c oasr -f -n "__fish_seen_subcommand_from config; and not __fish_seen_subcommand_from set get list agent validation adapter oasr profiles man validate path" -a "agent" -d "Show agent configuration"
complete -c oasr -f -n "__fish_seen_subcommand_from config; and not __fish_seen_subcommand_from set get list agent validation adapter oasr profiles man validate path" -a "validation" -d "Show validation settings"
complete -c oasr -f -n "__fish_seen_subcommand_from config; and not __fish_seen_subcommand_from set get list agent validation adapter oasr profiles man validate path" -a "adapter" -d "Show adapter settings"
complete -c oasr -f -n "__fish_seen_subcommand_from config; and not __fish_seen_subcommand_from set get list agent validation adapter oasr profiles man validate path" -a "oasr" -d "Show core settings"
complete -c oasr -f -n "__fish_seen_subcommand_from config; and not __fish_seen_subcommand_from set get list agent validation adapter oasr profiles man validate path" -a "profiles" -d "Show profiles"
complete -c oasr -f -n "__fish_seen_subcommand_from config; and not __fish_seen_subcommand_from set get list agent validation adapter oasr profiles man validate path" -a "man" -d "Show config reference"
complete -c oasr -f -n "__fish_seen_subcommand_from config; and not __fish_seen_subcommand_from set get list agent validation adapter oasr profiles man validate path" -a "validate" -d "Validate config file"
complete -c oasr -f -n "__fish_seen_subcommand_from config; and not __fish_seen_subcommand_from set get list agent validation adapter oasr profiles man validate path" -a "path" -d "Show config file path"

# config set/get
complete -c oasr -f -n "__fish_seen_subcommand_from config; and __fish_seen_subcommand_from set get" -a "(__oasr_config_keys)" -d "Config key"
complete -c oasr -f -n "__fish_seen_subcommand_from config; and __fish_seen_subcommand_from set; and __fish_seen_subcommand_from agent" -a "(__oasr_agents)" -d "Agent"
complete -c oasr -f -n "__fish_seen_subcommand_from config; and __fish_seen_subcommand_from set; and __fish_seen_subcommand_from profile" -a "(__oasr_profiles)" -d "Profile"
complete -c oasr -f -n "__fish_seen_subcommand_from config; and __fish_seen_subcommand_from set; and __fish_seen_subcommand_from oasr.default_profile" -a "(__oasr_profiles)" -d "Profile"
complete -c oasr -f -n "__fish_seen_subcommand_from config; and __fish_seen_subcommand_from set; and __fish_seen_subcommand_from validation.strict oasr.completions" -a "true false" -d "Boolean"

# profile command
complete -c oasr -f -n "__fish_seen_subcommand_from profile" -a "(__oasr_profiles)" -d "Profile"

# registry subcommands
complete -c oasr -f -n "__fish_seen_subcommand_from registry; and not __fish_seen_subcommand_from add rm sync list validate prune" -a "add" -d "Add skill to registry"
complete -c oasr -f -n "__fish_seen_subcommand_from registry; and not __fish_seen_subcommand_from add rm sync list validate prune" -a "rm" -d "Remove skill from registry"
complete -c oasr -f -n "__fish_seen_subcommand_from registry; and not __fish_seen_subcommand_from add rm sync list validate prune" -a "sync" -d "Sync remote skills"
complete -c oasr -f -n "__fish_seen_subcommand_from registry; and not __fish_seen_subcommand_from add rm sync list validate prune" -a "list" -d "List registry skills"
complete -c oasr -f -n "__fish_seen_subcommand_from registry; and not __fish_seen_subcommand_from add rm sync list validate prune" -a "validate" -d "Validate registry"
complete -c oasr -f -n "__fish_seen_subcommand_from registry; and not __fish_seen_subcommand_from add rm sync list validate prune" -a "prune" -d "Clean up registry"

# registry rm
complete -c oasr -f -n "__fish_seen_subcommand_from registry; and __fish_seen_subcommand_from rm" -a "(__oasr_skills)" -d "Skill"

# registry prune
complete -c oasr -f -n "__fish_seen_subcommand_from registry; and __fish_seen_subcommand_from prune" -l dry-run -d "Show what would be removed"

# completion command
complete -c oasr -f -n "__fish_seen_subcommand_from completion; and not __fish_seen_subcommand_from bash zsh fish powershell install uninstall" -a "bash" -d "Bash completion"
complete -c oasr -f -n "__fish_seen_subcommand_from completion; and not __fish_seen_subcommand_from bash zsh fish powershell install uninstall" -a "zsh" -d "Zsh completion"
complete -c oasr -f -n "__fish_seen_subcommand_from completion; and not __fish_seen_subcommand_from bash zsh fish powershell install uninstall" -a "fish" -d "Fish completion"
complete -c oasr -f -n "__fish_seen_subcommand_from completion; and not __fish_seen_subcommand_from bash zsh fish powershell install uninstall" -a "powershell" -d "PowerShell completion"
complete -c oasr -f -n "__fish_seen_subcommand_from completion; and not __fish_seen_subcommand_from bash zsh fish powershell install uninstall" -a "install" -d "Auto-detect and install"
complete -c oasr -f -n "__fish_seen_subcommand_from completion; and not __fish_seen_subcommand_from bash zsh fish powershell install uninstall" -a "uninstall" -d "Remove completions"

# completion flags
complete -c oasr -f -n "__fish_seen_subcommand_from completion" -l force -d "Force reinstall"
complete -c oasr -f -n "__fish_seen_subcommand_from completion" -l dry-run -d "Preview without installing"
complete -c oasr -f -n "__fish_seen_subcommand_from completion" -l install -d "Install completions for shell"

# adapter subcommands
complete -c oasr -f -n "__fish_seen_subcommand_from adapter; and not __fish_seen_subcommand_from list generate" -a "list" -d "List adapters"
complete -c oasr -f -n "__fish_seen_subcommand_from adapter; and not __fish_seen_subcommand_from list generate" -a "generate" -d "Generate adapter files"
