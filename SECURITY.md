# Security

## Network exposure

The Pip-Boy companion protocol (UDP 28000 / TCP 27000) has **no authentication and no encryption**. Anyone who can reach the game on those ports can read its data and send commands. Use this app only on a trusted private network, and never port-forward these ports to the internet.

## Reporting a vulnerability

Please report security issues privately using GitHub's **"Report a vulnerability"** option on the repository's Security tab rather than a public issue. Include the platform, app version, and steps to reproduce.

## Scope

This project is a client for a local game service. Issues in the game, the Pip-Boy service itself, or sideloading tools should be reported to their respective maintainers.
