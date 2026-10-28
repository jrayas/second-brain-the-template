---
paths:
  - "Exercises/**"
  - "Scenarios/**"
---

# Exercises and scenarios: hidden answers

A trailing `-` after a callout type makes it start collapsed, which hides the answer until the reader clicks.

## exercise

```markdown
# Title

## Question
(State the problem fully, with all given values and units.)

> [!hint]- Hint 1
> ...
> [!hint]- Hint 2
> ...

## Your answer
(Try it before opening the answer below.)

> [!success]- Answer
> ...
> [!info]- Working and reasoning
> ...
```

## scenario

```markdown
# Title

## Situation
(Realistic context: product, stage of the project, what has happened.)

## Constraints
(Budget, schedule, equipment, what is and is not known.)

## Your decision
(State exactly what the reader must decide. Encourage them to commit to an answer before opening the callouts.)

> [!question]- Answer
> ...
> [!info]- Reasoning
> ...
> [!failure]- Common wrong answers and why they tempt people
> ...
> [!tip]- What a senior engineer notices
> ...
```

## Rules for hidden answers

- An answer must follow from the facts and principles stated in the question or in the linked concept notes. Do not depend on unstated numbers.
- Where an answer contains a calculation, show the working, and add every numerical answer to the domain's `NEEDS-VERIFICATION.md`.
- A wrong hidden answer is worse than a missing one. If unsure, change the question so the answer is clear, or lower `confidence` and flag it.
- Scenarios need a defensible best answer plus honest trade-offs, not a single trick answer.
- `senior_signal` states, in one sentence, what separates a good answer from a great one.
- `answer_verified` stays `false`: only a person sets it to `true`.
