# Mission Authoring Skill

## Purpose

Convert informal task descriptions into structured, actionable mission documents.

## Inputs

- free-text task descriptions
- conversation transcripts
- requirements notes
- verbal briefings

## Outputs

- structured mission document
- list of open questions
- scope boundary definition

## Rules

- never invent requirements not present in the input
- flag ambiguities instead of resolving them silently
- use consistent section structure across all missions
- keep language neutral and precise

## Extraction Strategy

Priority order:
1. explicit objective (what must be done)
2. deliverable format (what the output looks like)
3. constraints (what must not happen)
4. success criteria (how to judge quality)
5. context (who, when, why)

Flag as "needs clarification":
- missing audience
- missing deliverable format
- contradictory requirements
- implicit deadlines
