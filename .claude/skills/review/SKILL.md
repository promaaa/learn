---
name: review
description: Spaced retrieval and exam-style practice on topics already taught, driven by the course's progress.md. Use for "/review", "quiz me", "revise", "révisions", "give me an exercise", "practice", "prepare for the midterm/final", and at the start of a session when topics are due.
---

# Review

Mastery means Marc can **pull an idea out of memory on a later day** and **use it on an exam problem** — not just follow it the day it was taught. This skill tests exactly that and feeds the results back into `progress.md`. It uses the `teach` skill's quiz-construction procedure, grounding rules and rendering rules; read those first.

## 1. Pick what's due

Read `progress.md`. Choose 3–6 topics, in this priority:

1. `shaky` topics.
2. `taught` topics not reviewed for 3 or more days.
3. `solid` topics not seen for 10 or more days.

Mix chapters (interleaving: e.g. a rotation-composition question next to a DH one). Recognising *which* tool a problem needs is half the exam. If Marc names a topic or an exam, restrict to it. Only review topics that have been taught (`—` topics are for `teach`).

## 2. Retrieval quiz

For each topic, 1–2 quiz questions (`AskUserQuestion`, batches of up to 4), mixing three kinds:

- **Why**: "why is the product of two rotations about the current frame post-multiplied?"
- **Small computation**: something done in your head or on paper in a minute, e.g. the inverse of a given homogeneous transform.
- **Trap**: the classic misconception for that topic (fixed vs current frame order, Rᵀ vs R, the DH parameter measured along zᵢ₋₁ vs xᵢ, q vs −q, quaternion product order).

Grade each one (✓/✗, correct answer, explanation), and write the questions, answers and explanations to `lessons/review-YYYY-MM-DD.md`.

## 3. One exam-style problem (at least one per review)

Like a *colle*: a problem in the shape of the slides' examples, sized for 10–20 minutes, for Marc to work on paper. Before grading, compute the reference solution with numpy or sympy. Marc sends the final result or the key steps. Grade the **method** as well as the result; when the result is wrong, find the exact step where it went wrong and name the step.

## 4. Update `progress.md`

- Retrieval **and** exam problem passed, on a later day than the teaching → `solid`.
- Retrieval passed only → stays `taught`; update "Last seen".
- A miss → `shaky`, with a one-line note of what went wrong.
- A misconception (a confidently wrong model, not a slip) → add it to "Misconceptions caught" and offer to re-teach that node with `teach` (Phase 3, for that node only) before moving on.

End with a two-line status in chat: how many topics are solid out of the total, and the next thing due.
