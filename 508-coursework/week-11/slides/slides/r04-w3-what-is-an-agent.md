---
minutes: 0
---

# Session 3 · Completion, Chat, Agent, and ReAct.

<table>
<thead>
<tr><th>Mode</th><th>Given</th><th>Returns</th><th>Who acts</th><th>When it stops</th></tr>
</thead>
<tbody>
<tr><td><strong>Completion</strong></td><td>a prompt prefix</td><td>continuation text</td><td>no one</td><td>token limit or stop sequence</td></tr>
<tr><td><strong>Chat</strong></td><td>the transcript so far</td><td>one reply</td><td>you</td><td>after one reply</td></tr>
<tr><td><strong>Agent</strong></td><td>record: rules, tools, observations</td><td>a reply or a tool call (JSON)</td><td><strong>the harness program</strong></td><td>no more tool calls (or step cap)</td></tr>
<tr><td><strong>ReAct</strong></td><td>same full record</td><td>thought → tool call or reply</td><td><strong>the harness program</strong></td><td>when it judges evidence suffices</td></tr>
</tbody>
</table>

<p class="sub">Same model inside — what changes is the <strong>program outside</strong>: <code>Agent = Model + Instructions (Skills) + Tools + Loop</code>.</p>

::read::
Session 3: A language model only predicts tokens; an agent wraps that model in an external program loop that supplies instructions, executes tool calls (files, shell, APIs), appends observations to the transcript, and enforces permissions.
