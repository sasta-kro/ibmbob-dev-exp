# AGENTS.md

## User Preferences
### Wording and Formatting
In the codebase, and in the documentations:
- no em-dashes
- no emojis
- no personal pronouns such as "you", "your", "I", "we", "us", etc. Only use 3rd person objective tone
- Use simple English grammar and vocab (technical and related terms are allowed)

### Codebase Style
- Modular architecture and reusable code
- Descriptive variable names
- Descriptive function names
- The code itself should be descriptive enough to explain what it is doing without comments.
- Comments are should be for 'why' and not 'what' as the 'what' should be knowable just from the code itself.

---

## Meta Documentation
- Do NOT read the .meta-docs/ directory unless explicitly asked.


---

## Memory System

- **Long-term:** `./.memory/MEMORY.md`, curated long-term memory.
- **Lessons Learned:** So mistakes don't repeat. At `./memory/lessons_learned.md`
- **Architecture Decisions:** so I don't go in a refactor spiral of trying out already-tried solutions that do not work. At `./architectural_decision_logs.md`

- You can **read, edit, and update** files in `.memory/` freely.
- Over time, review and update MEMORY.md with what's worth keeping

Capture what matters. Decisions, context, things to remember. Skip the secrets unless asked to keep them.

### Memory File Rules — READ BEFORE WRITING
- **MEMORY.md edits must preserve existing content.** When updating MEMORY.md, only add, edit specific entries, or remove outdated ones. Never rewrite the entire file from scratch unless explicitly told to.
- **If a file in `.memory` already exists, read it first.** Before writing to ANY `.memory` file, read what's already there. Then decide: append, edit specific sections, or make a new file.
- **When in doubt, append.** Duplicate sections are fixable. Lost content is not.

### 📝 Write It Down - No "Mental Notes"!
- **Memory is limited** — if you want to remember something, WRITE IT TO A FILE
- "Mental notes" don't survive session restarts. Files do.
- When someone says "remember this" → update `MEMORY.md` or relevant file
- When you learn a lesson → update `.memory/lessons_learned.md`.
- When you make a mistake → document it so future-you doesn't repeat it
- **Text > Brain**

---
