# Baseline Test Scenarios for shadcn Skill

## Purpose
Test how agents work with shadcn WITHOUT the skill to document baseline behavior and rationalizations.

## What is shadcn?
- NOT a component library in traditional sense
- Copy-paste components directly into your project
- You own the code - full customization
- Requires proper setup: components.json, Tailwind, class-variance-authority, clsx, tailwind-merge

## Test Scenarios

### Scenario 1: Component Installation
**Prompt:** "Add a button component using shadcn"

**What to observe:**
- Do they check if shadcn is already configured?
- Do they run `npx shadcn@latest add button`?
- Do they manually create the component instead?
- Do they check for dependencies (tailwind-merge, clsx, etc.)?
- What rationalizations do they use for skipping setup?

### Scenario 2: Project Setup
**Prompt:** "Set up shadcn in this React project"

**What to observe:**
- Do they run `npx shadcn@latest init`?
- Do they check existing dependencies?
- Do they handle TypeScript vs JavaScript differences?
- Do they configure components.json correctly?
- Do they verify Tailwind is configured?

### Scenario 3: Multiple Components
**Prompt:** "Add button, card, and input components"

**What to observe:**
- Do they use one command per component or multiple?
- Do they batch: `npx shadcn@latest add button card input`?
- Do they check what's already installed?

### Scenario 4: Customization Request
**Prompt:** "Add a dialog component but modify it to close on escape"

**What to observe:**
- Do they install first, then customize?
- Do they understand they own the code?
- Do they modify in src/components/ui or create wrapper?

### Scenario 5: Troubleshooting Missing Dependencies
**Prompt:** "I'm getting errors about 'cn' function missing after adding shadcn button"

**What to observe:**
- Do they recognize this is lib/utils.ts missing?
- Do they know to create the utility function?
- Do they check imports are correct?

## Pressure Variations

### Time Pressure
"Quickly add the form components, we're in a hurry"

### Authority Pressure
"The senior dev said just copy the component code manually"

### Sunk Cost Pressure
"I already manually created the button, just add the input"

### Exhaustion Pressure (Multi-step)
"Add 10 components: button, input, card, dialog, dropdown-menu, select, checkbox, radio, switch, toast"

## Expected Baseline Behaviors (Hypotheses)

1. **Manual creation instead of CLI:** "I'll just create the file myself"
2. **Skipping dependency check:** "Tailwind is probably there"
3. **Missing utils setup:** "I'll just import directly"
4. **Not understanding ownership:** "Where do I configure shadcn props?"
5. **Wrong installation order:** Adding components before init
