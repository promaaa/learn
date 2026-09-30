---
name: review
description: Spaced retrieval and exam-style practice on topics already taught, driven by the course's progress.md. Use for "review", "quiz me", "revise", "révisions", "give me an exercise", "practice", "prepare for the midterm/final", and at the start of a session when topics are due.
---

# Review

Mastery means the learner can **pull an idea out of memory on a later day** and **use it on an exam problem** — not just follow it the day it was taught. This skill tests exactly that and feeds the results back into `progress.md`. It uses the `teach` skill's quiz-construction procedure, accuracy rules and LaTeX formatting.

## 1. Pick what's due

Read `progress.md`. Choose 3–6 topics, in this priority:

1. `shaky` topics.
2. `taught` topics not reviewed for 3 or more days.
3. `solid` topics not seen for 10 or more days.

Mix chapters (interleaving: a rotation-composition question next to a DH one). Recognising *which* tool a problem needs is half the exam. If the learner names a topic or an exam, restrict to it. Only review topics that have been taught (`—` topics are for `teach`).

If no log is linked, create `lessons/review-YYYY-MM-DD.md` with a `# Review — <date>` heading, then ask the learner to run `/md-log lessons/review-YYYY-MM-DD.md`.

## 2. Retrieval quiz

1–2 `quiz` questions per topic, mixing three kinds:

- **Why**: "why are rotations about the current frame post-multiplied?"
- **Small computation**: about a minute on paper, e.g. the inverse of a given homogeneous transform.
- **Trap**: the classic misconception for that topic (fixed vs current frame order, $R$ vs $R^T$, which DH parameter is measured along $z_{i-1}$ vs $x_i$, $q$ vs $-q$, quaternion product order).

## 3. One exam-style problem (at least one per review)

Like a *colle*: a problem shaped like the slides' examples, sized for 10–20 minutes on paper. Compute the reference solution with numpy or sympy before grading. The learner sends the result or the key steps. Grade the **method** as well as the result; when the result is wrong, find the exact step where it went wrong and name the step.

## 4. Update `progress.md`

- Retrieval **and** exam problem passed, on a later day than the teaching → `solid`.
- Retrieval passed only → stays `taught`; update "Last seen".
- A miss → `shaky`, with a one-line note of what went wrong.
- A misconception (a confidently wrong model, not a slip) → add it to "Misconceptions caught" and offer to re-teach that node with `teach` (Phase 3, for that node only).

End with a two-line status: how many topics are solid out of the total, and the next thing due.
