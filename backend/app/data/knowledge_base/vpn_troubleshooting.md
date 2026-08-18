# VPN Troubleshooting Guide

## Standard Setup

Blacksmith Data uses **GlobalProtect VPN** for all remote access to internal systems.

- **Download:** Available on the internal software portal (https://software.blacksmithdata.internal).
- **Gateway address:** vpn.blacksmithdata.internal
- **Login:** Use your standard company credentials (same as email/Slack).

## Common Issues

**"Connection timed out" error:**
- Check your local internet connection first.
- Ensure you are not connected to another VPN service simultaneously.
- Restart the GlobalProtect client and retry.

**"Authentication failed" error:**
- Confirm your password hasn't expired (see Password Reset Policy).
- If you recently reset your password, you may need to fully quit and reopen the VPN client for it to pick up new credentials.

**VPN connects but internal sites are unreachable:**
- Confirm you're connected to the correct gateway (vpn.blacksmithdata.internal, not a personal/other VPN).
- Try disconnecting and reconnecting — DNS settings sometimes fail to apply on first connect.

## Escalation

If none of the above resolves the issue, raise a ticket in #it-helpdesk on Slack with a screenshot of the error and the time it occurred.
