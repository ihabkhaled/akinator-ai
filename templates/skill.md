---
name: <kebab-case-name>
description: <THE TRIGGER, not the summary. Write the situation in the words someone uses when they are in it - "Use when a schema change needs to reach a running environment, or when a migration failed halfway". A description that describes the skill instead of its trigger will never fire.>
---

# <Skill Title>

> Template. Copy to `skills/<name>/SKILL.md`, keep all six parts, delete this
> line and every angle-bracket placeholder.

<One or two sentences: what this skill is for and why it exists. If there is a
cost that motivated it - an hour lost, a production incident, a mistake made
twice - say so. Motivation is what makes a procedure get followed.>

## When to use

<Concrete situations, written as symptoms present themselves, not as they are
understood afterwards. The reader does not yet know what their problem is.>

- <situation>
- <situation>

## When NOT to use

<The neighboring situations this does not cover, and where to go instead. This
is what stops the skill from firing on the wrong problem.>

- <situation> - use <other skill> instead.
- <situation>

## Procedure

### Preconditions

<What must be true before starting, and how to check each one. The step that
fails is always the one whose precondition was assumed.>

- [ ] <precondition> - check with `<command>`

### Steps

1. <Step, with the actual command.>

   ```bash
   <command>
   ```

   <What you should see if it worked.>

2. <Step.>

   <If steps can overlap, say so explicitly:>
   > **Parallel-safe:** steps 2a, 2b and 2c are independent - run them
   > concurrently.
   > **Must be sequential:** step 3 depends on step 2 because <reason>.
   > **Must never be parallel:** <what, and what breaks if it is>.

3. <Step.>

## Failure modes and pitfalls

<What goes wrong, what it looks like when it goes wrong, and what the misleading
symptom is. This section is usually why the skill is worth more than the docs.>

- **<Failure>** - looks like <symptom>, is actually <cause>. <What to do.>
- **<Failure>** - <...>

## Definition of done

<Checkable conditions - observable facts, not intentions.>

- [ ] <condition>
- [ ] <condition>
