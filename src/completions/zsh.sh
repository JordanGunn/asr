#compdef oasr
# oasr completion for zsh
# This file provides tab completion for the oasr command in zsh.
#
# Installation:
#   Run: oasr completion install
#   Or manually: Add this file to your fpath and run compinit

_oasr_skills() {
    local skills
    skills=(${(f)"$(oasr registry list --quiet 2>/dev/null | grep '^  -' | sed 's/^  - //' | awk '{print $1}')"})
    _describe 'skill' skills
}

_oasr_agents() {
    local agents
    agents=(
        'codex:OpenAI Codex agent'
        'copilot:GitHub Copilot agent'
        'claude:Anthropic Claude agent'
        'opencode:OpenCode agent'
    )
    _describe 'agent' agents
}

_oasr_profiles() {
    local profiles
    profiles=(${(f)"$(oasr config profiles --names 2>/dev/null)"})
    _describe 'profile' profiles
}

_oasr_config_keys() {
    local keys
    keys=(
        'agent:Default agent'
        'profile:Default policy profile'
        'adapter.default_targets:Default adapter targets'
        'validation.strict:Strict validation'
        'validation.reference_max_lines:Reference max lines'
        'oasr.completions:Enable completions'
    )
    _describe 'config key' keys
}

_oasr_exec() {
    _arguments \
        '--agent[Agent to use]:agent:_oasr_agents' \
        '--profile[Policy profile]:profile:_oasr_profiles' \
        '--agent-flags[Additional agent flags]:flags:' \
        '(-y --yes)'{-y,--yes}'[Skip confirmation]' \
        '--confirm[Force confirmation] \
        --unsafe[Pass unsafe agent flags]' \
        '(-p --prompt)'{-p,--prompt}'[Prompt from file]:file:_files' \
        '1:skill:_oasr_skills'
}

_oasr_clone() {
    _arguments \
        '(-t --target)'{-t,--target}'[Target directory]:directory:_directories' \
        '*:skill:_oasr_skills'
}

_oasr_info() {
    _arguments \
        '--files[Show file list]' \
        '--json[JSON output (v1|v2)]' \
        '1:skill:_oasr_skills'
}

_oasr_validate() {
    _arguments \
        '--json[JSON output (v1|v2)]' \
        '*:skill:_oasr_skills'
}

_oasr_status() {
    _arguments \
        '--json[JSON output (v1|v2)]' \
        '*:skill:_oasr_skills'
}

_oasr_config() {
    local -a subcommands
    subcommands=(
        'set:Set a configuration value'
        'get:Get a configuration value'
        'list:List all configuration'
        'agent:Show agent configuration'
        'validation:Show validation settings'
        'adapter:Show adapter settings'
        'oasr:Show core settings'
        'profiles:Show profiles'
        'man:Show config reference'
        'validate:Validate config file'
        'path:Show config file path'
    )

    _arguments -C \
        '1:subcommand:->subcommand' \
        '*::arg:->args'

    case $state in
        subcommand)
            _describe 'config subcommand' subcommands
            ;;
        args)
            case ${words[1]} in
                set)
                    if [ ${#words[@]} -eq 2 ]; then
                        _oasr_config_keys
                    elif [ ${#words[@]} -eq 3 ]; then
                        case ${words[2]} in
                            agent)
                                _oasr_agents
                                ;;
                            profile|oasr.default_profile)
                                _oasr_profiles
                                ;;
                            validation.strict|oasr.completions)
                                _values 'boolean' true false
                                ;;
                            validation.reference_max_lines)
                                _message 'integer'
                                ;;
                            adapter.default_targets)
                                _message 'comma-separated list'
                                ;;
                        esac
                    fi
                    ;;
                get)
                    _oasr_config_keys
                    ;;
            esac
            ;;
    esac
}

_oasr_sync() {
    _arguments \
        '--force[Overwrite modified skills]' \
        '--prune[Remove tracked skills not in registry]' \
        '(-y --yes)'{-y,--yes}'[Skip confirmation prompt]' \
        '--json[JSON output (v1|v2)]' \
        '1:path:_directories'
}

_oasr_profile() {
    _arguments \
        '1:profile subcommand:(list show edit rm new wizard)' \
        '2:profile:->profile' \
        '*::arg:->args'

    case $state in
        profile)
            case ${words[2]} in
                show)
                    _oasr_profiles
                    ;;
                rm)
                    _arguments '1:profile:_oasr_profiles' \
                               '(-y --yes)'{-y,--yes}'[Skip confirmation prompt]'
                    ;;
                edit)
                    _arguments '1:select flag:(-s --select)' \
                               '2:profile:_oasr_profiles' \
                               '3:profile:_oasr_profiles'
                    ;;
                new)
                    _arguments '1:copy flag:(-c --copy-from)'
                    ;;
            esac
            ;;
        args)
            case ${words[2]} in
                edit)
                    if [[ ${words[3]} == "-s" || ${words[3]} == "--select" ]]; then
                        _oasr_profiles
                    elif [[ -n ${words[3]} ]]; then
                        _oasr_profiles
                    fi
                    ;;
                new)
                    if [[ ${words[3]} == "-c" || ${words[3]} == "--copy-from" ]]; then
                        _oasr_profiles
                    fi
                    ;;
            esac
            ;;
    esac
}

_oasr_registry() {
    local -a subcommands
    subcommands=(
        'add:Add skill to registry'
        'rm:Remove skill from registry'
        'sync:Sync remote skills'
        'list:List registry skills'
        'validate:Validate registry'
        'prune:Clean up registry'
    )

    _arguments -C \
        '1:subcommand:->subcommand' \
        '*::arg:->args'

    case $state in
        subcommand)
            _describe 'registry subcommand' subcommands
            ;;
        args)
            case ${words[1]} in
                add)
                    _alternative \
                        'directories:directory:_directories' \
                        'urls:url:(http:// https:// git@)'
                    ;;
                rm)
                    _oasr_skills
                    ;;
                prune)
                    _arguments '--dry-run[Show what would be removed]'
                    ;;
            esac
            ;;
    esac
}

_oasr_completion() {
    local -a shells
    shells=(
        'bash:Bash completion'
        'zsh:Zsh completion'
        'fish:Fish completion'
        'powershell:PowerShell completion'
        'install:Auto-detect and install'
        'uninstall:Remove completions'
    )

    _arguments \
        '--force[Force reinstall]' \
        '--install[Install completions for shell]' \
        '--dry-run[Preview without installing]' \
        '1:shell:->shell'

    case $state in
        shell)
            _describe 'shell' shells
            ;;
    esac
}

_oasr_adapter() {
    local -a subcommands
    subcommands=(
        'list:List adapters'
        'generate:Generate adapter files'
    )

    _arguments -C \
        '1:subcommand:->subcommand' \
        '*::arg:->args'

    case $state in
        subcommand)
            _describe 'adapter subcommand' subcommands
            ;;
    esac
}

_oasr() {
    local -a commands
    commands=(
        'registry:Manage skill registry'
        'diff:Show tracked skill status'
        'sync:Refresh tracked skills'
        'status:Show manifest status'
        'config:Manage configuration'
        'profile:Select execution profile'
        'clone:Clone skills to directory'
        'exec:Execute a skill'
        'find:Find skills recursively'
        'validate:Validate skills'
        'adapter:Generate IDE-specific files'
        'update:Update OASR tool'
        'info:Show skill information'
        'about:Show version and credits'
        'help:Show help'
        'completion:Manage shell completions'
    )

    _arguments -C \
        '(--help -h)'{--help,-h}'[Show help]' \
        '--version[Show version]' \
        '--config[Config file path]:file:_files' \
        '--json[JSON output (v1|v2)]' \
        '--quiet[Suppress warnings]' \
        '1:command:->command' \
        '*::arg:->args'

    case $state in
        command)
            _describe 'oasr command' commands
            ;;
        args)
            case ${words[1]} in
                exec)
                    _oasr_exec
                    ;;
                profile)
                    _oasr_profile
                    ;;
                clone)
                    _oasr_clone
                    ;;
                info)
                    _oasr_info
                    ;;
                validate)
                    _oasr_validate
                    ;;
                status)
                    _oasr_status
                    ;;
                config)
                    _oasr_config
                    ;;
                sync)
                    _oasr_sync
                    ;;
                profile)
                    _oasr_profile
                    ;;
                registry)
                    _oasr_registry
                    ;;
                completion)
                    _oasr_completion
                    ;;
                adapter)
                    _oasr_adapter
                    ;;
            esac
            ;;
    esac
}
