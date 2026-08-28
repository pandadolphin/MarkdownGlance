# Migrating from MarkdownLivePreview

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
