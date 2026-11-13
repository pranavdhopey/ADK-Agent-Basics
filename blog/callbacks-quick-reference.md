> 📖 **Callbacks Series**: [Blog Directory](README.md)

---

# Quick Reference Card: ADK Callbacks Cheat Sheet

Keep this table handy when developing agents with Google ADK:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              GOOGLE ADK CALLBACKS MATRIX                              │
├────────────────────────┬──────────────────────────────────┬────────────────────────────┤
│ Hook Name              │ Exact Required Parameter Names   │ Return Type to Override   │
├────────────────────────┼──────────────────────────────────┼────────────────────────────┤
│ before_agent_callback  │ callback_context                 │ Optional[types.Content]    │
│ after_agent_callback   │ callback_context                 │ Optional[types.Content]    │
├────────────────────────┼──────────────────────────────────┼────────────────────────────┤
│ before_model_callback  │ callback_context, llm_request    │ Optional[LlmResponse]      │
│ after_model_callback   │ callback_context, llm_response   │ Optional[LlmResponse]      │
│ on_model_error_callback│ callback_context, llm_request,   │ Optional[LlmResponse]      │
│                        │ error                            │                            │
├────────────────────────┼──────────────────────────────────┼────────────────────────────┤
│ before_tool_callback   │ tool, args, tool_context         │ Optional[dict]             │
│ after_tool_callback    │ tool, args, tool_context,        │ Optional[dict]             │
│                        │ tool_response                    │                            │
│ on_tool_error_callback │ tool, args, tool_context, error  │ Optional[dict]             │
└────────────────────────┴──────────────────────────────────┴────────────────────────────┘
```

---

## 🎮 Hands-on Practice: Run the Demo Agent!

You can test every single concept explained in this blog right now in your terminal:

```bash
cd callback_agent
python run_agent.py
```

Try these interactive tests:
1. Type `login` / `logout` to watch `before_agent_callback` block or permit access.
2. Type `hours` to see `before_model_callback` return an instant zero-token cache hit.
3. Type `danger` to watch `before_tool_callback` block a `rm -rf` command.
4. Type `account` to watch `after_tool_callback` scrub database passwords.
5. Type `crash` to watch `on_tool_error_callback` recover smoothly from a database outage.

Happy building, and may your agents run securely and reliably in production! 🚀

---

<div align="between">
  <span>[← Previous: Part 4: Enterprise Pipeline](callbacks-part-4-enterprise-pipeline.md)</span> | <span>[Series Home: Table of Contents →](README.md)</span>
</div>