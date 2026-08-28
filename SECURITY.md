# Security policy

## Supported versions

The latest released version is the only one that receives fixes.

## Reporting a vulnerability

Report privately through GitHub's
[security advisory form](https://github.com/pandadolphin/MarkdownGlance/security/advisories/new).
Please do not open a public issue for a vulnerability. Expect an
acknowledgement within a week.

## What the package touches

MarkdownGlance renders Markdown inside Sublime Text and starts no external
process. Two features leave the machine, and both are bounded:

- **Remote images** are fetched off the UI thread under scheme, redirect,
  timeout, payload and dimension limits, and are cached only in memory.
  Insecure schemes are blocked by default.
- **Mermaid rendering** is disabled by default. Enabling it sends diagram
  source to the configured Mermaid server.

`MarkdownGlance: Copy Diagnostics` redacts source text, paths, URLs and Mermaid
payloads before anything reaches the clipboard.
