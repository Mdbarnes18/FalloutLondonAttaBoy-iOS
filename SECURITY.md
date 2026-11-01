# Security policy

## Network exposure

The Pip-Boy companion protocol uses UDP 28000 for PC discovery and TCP 27000 for the data and command stream. The protocol has **no authentication and no encryption**. Anyone who can reach the game service on those ports may be able to read game data and send commands.

Use this app only on a trusted private network. Do not port-forward these ports or expose them to the public internet.

## Reporting a vulnerability

Please report security issues privately using GitHub's **Report a vulnerability** option on this repository's Security tab rather than opening a public issue. Include the affected platform, app version, impact, and steps to reproduce. Avoid attaching personal data, private Team FOLON material, or proprietary game assets.

## Scope

This project is a client for a local game companion service. Vulnerabilities in Fallout 4, Fallout: London, the Pip-Boy service itself, or third-party sideloading/package tools should be reported to their respective maintainers.
