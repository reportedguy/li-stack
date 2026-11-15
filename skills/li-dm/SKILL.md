---
name: li-dm
description: >-
  Write connection notes and DMs that get replies: the invite note, the first
  message after they accept, and two follow-ups. Tuned for a builder reaching
  founders and other builders: a question, feedback, a collab, a Founder
  Conversation (S9). Use
  when the user says "write a connection request", "DM this person", "cold
  message a founder", "ask for feedback", "how do I follow up", or is reaching out
  to someone specific.
---

# li-dm

The invite note is short. The first DM decides whether there's a second one.
Neither is a pitch, and neither asks a stranger for a favour.

## Before writing, get the specifics

Ask in one batched question:

1. **Who:** name, role, company.
2. **The hook:** the actual reason to reach out *now*. A post they wrote, a
   thing their company shipped, a shared college or club, a talk, a mutual
   connection. "They're a founder I admire" isn't a hook.
3. **What you want:** advice, a 15-minute call, feedback on a project, a
   referral, an internship. Be honest about it internally, even if the first
   message doesn't lead with it.

If there's no specific reason to message this person today, say so. A message
with no reason is what everyone else sends, and it's why their reply rate is
near zero.

Pull receipts from `~/.claude/linkedin/story-bank.md`: one real project or
number makes a message worth answering.

## The invite note

**200 characters on a free account (300 on Premium).** Count and show it.

```
{one specific reference to them} + {one line of who you are, with proof} + {no ask}
```

```
Your post on killing feature roadmaps changed how I scoped {{my app}}. I'm
building {{project}} and learning from people who've shipped further.
                                                         [count it: max 200]
```

## The first message, after they accept

Wait a day. Then:
- **2-4 sentences.** A screen of text is a delete.
- **Pick up the thread from the note:** continuity is why the note was specific.
- **Give before you ask:** a sharp observation about their product, a short
  teardown, a link to something you built that's relevant to them.
- **One small ask.** "Would you be open to a 15-minute call?" or "Could I send
  you a one-page teardown for feedback?" beats "Can you refer me?".
- No calendar link in message one. No resume attachment in message one.

**Founder Conversation ask (S9):** one sharp question about a decision
they made, answerable in two lines, plus "would you mind if I shared your
answer in a post, with credit?". Never post without an explicit yes.

## Follow-ups: two, then stop

- **+4 days:** add something new (a result, a question about their latest
  post, the teardown). Never "just bumping this".
- **+10 days:** close the loop. Say you'll stop, and mean it. This one gets a
  surprising share of replies because it removes the pressure.

A third follow-up converts nobody and costs the relationship.

## Never

- Never send anything automatically. Automated invites and message sequences
  violate LinkedIn's User Agreement and get accounts restricted.
- Never invent a mutual connection, a shared club, or having read something
  you haven't.
- Never open with "I hope this message finds you well" or "Dear Sir/Ma'am".
- Keep invites to about 20 a day. More gets the account throttled.

## Output

The invite note with its character count, the first message, and both
follow-ups with the day each goes out, all run through `/li-human --kind dm`.
The user sends every one by hand.
