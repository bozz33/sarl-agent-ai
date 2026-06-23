# Hermes Agent Anthropic OAuth hotfix

Base: `sarl/hermes-agent:uid10010`, Hermes Agent 0.16.0, upstream
`36ae9584`.

The initial Anthropic PKCE exchange still targeted
`https://console.anthropic.com/v1/oauth/token`. The refresh path in the same
module already prefers `https://platform.claude.com/v1/oauth/token`.

This derived image applies that endpoint to the initial exchange as well.
