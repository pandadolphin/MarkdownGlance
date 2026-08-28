# Migrating from MarkdownLivePreview

## 中文摘要

- 两个 packages 可同时安装，但默认 preview shortcuts 重叠；migration 期间需 disable 一方 key bindings 或自定义 shortcuts。
- 不自动复制 settings。`toc_minimum_length` 可直接迁移；network 与 Mermaid settings 应按新的 privacy defaults 手动确认。
- 新 Side-by-Side 模式使用 source window 内的 editor groups，不再创建独立 preview window。

Install MarkdownGlance beside MarkdownLivePreview, then invoke commands from the
Command Palette while evaluating it. Public identifiers, settings files,
resources and Python modules do not collide. The default shortcuts do collide,
so remove or override one package's bindings before relying on keyboard dispatch.

| Existing intent | MarkdownGlance setting |
| --- | --- |
| update delay | `update_delay_ms` |
| automatic TOC length | `toc_minimum_length` |
| Mermaid rendering | `enable_mermaid` (defaults to `false`) |

Review `mermaid_server`, remote scheme, timeout, payload and dimension settings
instead of copying them blindly. MarkdownGlance does not read or modify the old
package's settings.

Side-by-Side now creates or reuses a group to the right of the source. Full
Screen uses the source group and toggles back without closing the source. Remove
the old package only after the new workflow and custom key bindings are verified.
