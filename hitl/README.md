# Human-in-the-Loop (HITL) — Future Implementation
#
# This directory will contain Human-in-the-Loop hooks for cases where the
# AI Copilot's recommendations require explicit administrator approval before
# any action is taken.
#
# Planned use cases:
#
#   - High-impact recommendations (e.g., "restock 500 units of product X")
#     that the user may want to confirm before acting on
#   - Ambiguous queries where confidence is low and human clarification is needed
#   - Escalation paths when the agent detects critical business alerts
#
# Planned contents:
#
#   approval_node.py
#     - ADK function node that pauses workflow execution and awaits human input
#     - Integrates with ADK's interrupt/resume mechanism
#
#   hitl_middleware.py
#     - Determines when HITL is required based on recommendation severity
#     - Routes to approval_node when confidence < threshold or severity == "high"
#
# ADK reference:
#   https://google.github.io/adk-docs/human-in-the-loop/
