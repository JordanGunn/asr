# oasr completion for bash
# This file provides tab completion for the oasr command in bash.
#
# Installation:
#   Run: oasr completion install
#   Or manually: source this file in your ~/.bashrc

_oasr_skills() {
    # Get skill names from registry
    local skills
    skills=$(oasr registry list --quiet 2>/dev/null | grep "^  -" | sed 's/^  - //' | awk '{print $1}')
    COMPREPLY=($(compgen -W "$skills" -- "${COMP_WORDS[COMP_CWORD]}"))
}

_oasr_agents() {
    # Known agent names
    COMPREPLY=($(compgen -W "codex copilot claude opencode" -- "${COMP_WORDS[COMP_CWORD]}"))
}

_oasr_profiles() {
    # Get profile names from config
    local profiles
    profiles=$(oasr config profiles --names 2>/dev/null)
    COMPREPLY=($(compgen -W "$profiles" -- "${COMP_WORDS[COMP_CWORD]}"))
}

_oasr_config_keys() {
    # Common config keys
    COMPREPLY=($(compgen -W "agent profile oasr.default_profile adapter.default_targets validation.strict validation.reference_max_lines oasr.completions" -- "${COMP_WORDS[COMP_CWORD]}"))
}

_oasr_completion_shells() {
    COMPREPLY=($(compgen -W "bash zsh fish powershell install uninstall" -- "${COMP_WORDS[COMP_CWORD]}"))
}

_oasr() {
    local cur prev words cword
    _init_completion || return

    # Top-level commands
    if [ $COMP_CWORD -eq 1 ]; then
        COMPREPLY=($(compgen -W "registry diff sync config profile clone exec find validate adapter update info help completion about status" -- "$cur"))
        return 0
    fi

    # Get the main command
    local command="${COMP_WORDS[1]}"

    case "$command" in
        exec)
            case "$prev" in
                --agent)
                    _oasr_agents
                    return 0
                    ;;
                --profile)
                    _oasr_profiles
                    return 0
                    ;;
                --agent-flags)
                    # No completion for agent flags
                    return 0
                    ;;
                -p|--prompt)
                    # File completion for prompt
                    _filedir
                    return 0
                    ;;
                *)
                    # Complete skill names and flags
                    if [[ "$cur" == -* ]]; then
                        COMPREPLY=($(compgen -W "--agent --profile --agent-flags -y --yes --confirm -p --prompt --unsafe" -- "$cur"))
                    else
                        _oasr_skills
                    fi
                    return 0
                    ;;
            esac
            ;;

        clone)
            case "$prev" in
                -t|--target)
                    # Directory completion
                    _filedir -d
                    return 0
                    ;;
                *)
                    if [[ "$cur" == -* ]]; then
                        COMPREPLY=($(compgen -W "-t --target" -- "$cur"))
                    else
                        _oasr_skills
                    fi
                    return 0
                    ;;
            esac
            ;;

        info|validate|status)
            if [[ "$cur" == -* ]]; then
                case "$command" in
                    info)
                        COMPREPLY=($(compgen -W "--files --json" -- "$cur"))
                        ;;
                    validate|status)
                        COMPREPLY=($(compgen -W "--json" -- "$cur"))
                        ;;
                esac
            else
                _oasr_skills
            fi
            return 0
            ;;

        config)
            if [ $COMP_CWORD -eq 2 ]; then
                COMPREPLY=($(compgen -W "set get list agent validation adapter oasr profiles man validate path" -- "$cur"))
                return 0
            fi

            local subcommand="${COMP_WORDS[2]}"
            case "$subcommand" in
                set|get)
                    if [ $COMP_CWORD -eq 3 ]; then
                        _oasr_config_keys
                    elif [ $COMP_CWORD -eq 4 ] && [ "$subcommand" = "set" ]; then
                        # Value completion based on key
                        local key="${COMP_WORDS[3]}"
                        case "$key" in
                            agent)
                                _oasr_agents
                                ;;
                            profile|oasr.default_profile)
                                _oasr_profiles
                                ;;
                            validation.strict|oasr.completions)
                                COMPREPLY=($(compgen -W "true false" -- "$cur"))
                                ;;
                            adapter.default_targets)
                                return 0
                                ;;
                            validation.reference_max_lines)
                                return 0
                                ;;
                        esac
                    fi
                    return 0
                    ;;
            esac
            ;;

        registry)
            if [ $COMP_CWORD -eq 2 ]; then
                COMPREPLY=($(compgen -W "add rm sync list validate prune" -- "$cur"))
                return 0
            fi

            local subcommand="${COMP_WORDS[2]}"
            case "$subcommand" in
                add)
                    # Directory or URL completion
                    if [[ "$cur" == http* ]] || [[ "$cur" == git@* ]]; then
                        # No completion for URLs
                        return 0
                    else
                        _filedir -d
                    fi
                    ;;
                rm)
                    _oasr_skills
                    ;;
                prune)
                    if [[ "$cur" == -* ]]; then
                        COMPREPLY=($(compgen -W "--dry-run" -- "$cur"))
                    fi
                    ;;
            esac
            ;;

        completion)
            if [ $COMP_CWORD -eq 2 ]; then
                _oasr_completion_shells
                return 0
            fi
            
            if [[ "$cur" == -* ]]; then
                COMPREPLY=($(compgen -W "--force --dry-run --install" -- "$cur"))
            fi
            ;;

        adapter)
            if [ $COMP_CWORD -eq 2 ]; then
                COMPREPLY=($(compgen -W "list generate" -- "$cur"))
                return 0
            fi
            ;;

        profile)
            if [ $COMP_CWORD -eq 2 ]; then
                _oasr_profiles
                return 0
            fi
            ;;

        sync)
            case "$prev" in
                --json)
                    COMPREPLY=($(compgen -W "v1 v2" -- "$cur"))
                    ;;
                *)
                    if [[ "$cur" == -* ]]; then
                        COMPREPLY=($(compgen -W "--force --prune -y --yes --json" -- "$cur"))
                    fi
                    ;;
            esac
            return 0
            ;;
        find|validate|diff|update|help)
            # These commands have limited or no additional completion
            return 0
            ;;
    esac
}

# Register the completion function
complete -F _oasr oasr
