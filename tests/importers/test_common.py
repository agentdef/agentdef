"""Unit tests for importers/_common.py: the shared markdown classifier and
AgentDefWriter."""

import sys
from pathlib import Path


from agentdef.importers._common import (  # noqa: E402
    AgentDefWriter,
    ImportReport,
    classify_header,
    extract_bullets,
    find_persona_sentence,
    generic_markdown_import,
    slugify,
    split_frontmatter,
    split_sections,
)
from agentdef.validation.validate import validate  # noqa: E402


class TestSlugify:
    def test_basic(self):
        assert slugify("My Cool Agent") == "my-cool-agent"

    def test_starts_with_digit_or_symbol(self):
        assert slugify("---!!!").startswith(("agent-", "imported-agent"))

    def test_already_valid(self):
        assert slugify("twitter-digest") == "twitter-digest"

    def test_collapses_repeated_hyphens(self):
        assert slugify("a---b   c") == "a-b-c"

    def test_underscores_are_preserved(self):
        # Underscores are valid in the manifest name pattern (^[a-z0-9][a-z0-9_-]*$),
        # so slugify doesn't need to strip or collapse them.
        assert slugify("a_b_c") == "a_b_c"


class TestSplitSections:
    def test_preamble_and_headers(self):
        text = "Some intro text.\n\n## Role\nYou are a bot.\n\n## Objectives\n- one\n- two\n"
        preamble, sections = split_sections(text)
        assert preamble == "Some intro text."
        assert [s.header for s in sections] == ["Role", "Objectives"]
        assert sections[0].content == "You are a bot."
        assert sections[1].content == "- one\n- two"

    def test_no_headers(self):
        preamble, sections = split_sections("just text\nmore text")
        assert sections == []
        assert "just text" in preamble

    def test_hash_comment_inside_fenced_code_block_is_not_a_header(self):
        # Real-world bug found while testing against github/awesome-copilot
        # agents: a '#'-prefixed shell/Python/YAML comment inside a fenced
        # ```bash/```python/```yaml code example (extremely common in
        # DevOps-flavored agent docs) was being misread as a markdown
        # header, shredding the section structure.
        text = (
            "# My Agent\n\n"
            "You are an expert.\n\n"
            "## Setup\n\n"
            "```bash\n"
            "# Install dependencies\n"
            "apt-get update\n"
            "## also not a header\n"
            "apt-get install -y curl\n"
            "```\n\n"
            "## Usage\n\n"
            "After setup, run the tool.\n"
        )
        preamble, sections = split_sections(text)
        # Correct outline nesting: one top-level H1 containing everything
        # (the '#'/'##'-prefixed comment lines inside the fence must NOT
        # show up as sibling top-level sections).
        assert [s.header for s in sections] == ["My Agent"]
        assert "# Install dependencies" in sections[0].content
        assert "## Usage" in sections[0].content

    def test_tilde_fence_also_respected(self):
        text = "# Title\n\n~~~\n# not a header\n~~~\n\n## Real Header\ncontent\n"
        preamble, sections = split_sections(text)
        assert [s.header for s in sections] == ["Title"]


class TestClassifyHeader:
    def test_known_synonyms(self):
        assert classify_header("Role") == "role"
        assert classify_header("Identity") == "role"
        assert classify_header("Communication Style") == "style"
        assert classify_header("Don't") == "avoid"
        assert classify_header("Guardrails") == "safety"

    def test_unknown_falls_back_to_core(self):
        assert classify_header("Random Section Title") == "core"


class TestExtractBullets:
    def test_bullets(self):
        assert extract_bullets("- a\n- b\n* c") == ["a", "b", "c"]

    def test_fallback_to_lines(self):
        assert extract_bullets("first line\nsecond line") == ["first line", "second line"]

    def test_numbered_list_markers_are_stripped(self):
        # Real-world bug found while building the Claude -> Copilot demo:
        # a source '## Priorities' section written as an ordered list
        # ("1. Security issues...") was falling through to the bare
        # non-empty-line fallback (since _BULLET_RE only matches -/*), so
        # the original "1. " prefix survived into the returned list. When
        # AgentDefWriter._render_agent_md re-numbers Priorities on output,
        # that produced doubled markers like "1. 1. Security issues...".
        text = "1. First thing\n2. Second thing\n3) Third thing"
        assert extract_bullets(text) == ["First thing", "Second thing", "Third thing"]


class TestFindPersonaSentence:
    def test_found(self):
        text = "Some preamble. You are a helpful assistant. More text."
        assert find_persona_sentence(text) == "You are a helpful assistant."

    def test_not_found(self):
        assert find_persona_sentence("No persona sentence here.") is None

    def test_sentence_wrapped_across_a_soft_newline(self):
        # Real-world bug found while testing against github/awesome-copilot
        # agents (diffblue-cover.agent.md): prose is often hard-wrapped at
        # ~100 columns, so a 'You are ...' sentence commonly continues after
        # a single newline rather than staying on one line. The old regex
        # (`[^.\n]*\.`) refused to cross that newline and simply missed the
        # sentence entirely.
        text = (
            "You are the *Cover Java Unit Test Generator* agent - a special purpose agent to create\n"
            "unit tests for java applications using Cover."
        )
        result = find_persona_sentence(text)
        assert result is not None
        assert "unit tests for java applications" in result
        assert "\n" not in result  # wrapped newline normalized to a space

    def test_stops_at_paragraph_break_not_just_any_period(self):
        text = "You are an agent\nfor this repo.\n\nUnrelated next paragraph. More."
        result = find_persona_sentence(text)
        assert result == "You are an agent for this repo."
        assert "Unrelated" not in result

    def test_broader_persona_phrasings_recognized(self):
        # Not every agent doc phrases its identity sentence as "You are ...".
        assert find_persona_sentence("Your role is to review pull requests.") is not None
        assert find_persona_sentence("You help developers ship code faster.") is not None
        assert find_persona_sentence("You act as a release manager.") is not None


class TestSplitFrontmatter:
    def test_basic_frontmatter(self):
        text = "---\nname: foo\ndescription: A simple agent.\n---\n\nBody text.\n"
        meta, body = split_frontmatter(text)
        assert meta == {"name": "foo", "description": "A simple agent."}
        assert body == "Body text."

    def test_no_frontmatter(self):
        meta, body = split_frontmatter("Just a body, no frontmatter.\n")
        assert meta == {}
        assert body == "Just a body, no frontmatter.\n"

    def test_unquoted_colon_in_description_falls_back_to_lenient_parse(self):
        # Real-world bug found while batch-testing github/awesome-claude-
        # code-subagents (gdpr-ccpa-compliance.md and 25 similar files
        # across the claude and copilotstudio corpora): a plain-scalar
        # frontmatter value containing its own unescaped ": " later in the
        # line (e.g. "Triggers on: 'GDPR', 'CCPA'") makes yaml.safe_load
        # raise ScannerError, because YAML's plain-scalar grammar reads
        # that colon-space as an attempt to open a nested mapping. The old
        # code caught this with a broad `except Exception: return {}, text`
        # and silently treated the entire frontmatter block as absent,
        # which then leaked verbatim into instructions/core.md as ordinary
        # preamble text. split_frontmatter must recover the fields instead
        # of giving up.
        text = (
            "---\n"
            "name: gdpr-ccpa-compliance\n"
            "description: Use when the user needs to understand GDPR or CCPA "
            "compliance. Triggers on: 'GDPR', 'CCPA', privacy law questions.\n"
            "tools: Read, Grep\n"
            "---\n\n"
            "You are a privacy compliance expert.\n"
        )
        meta, body = split_frontmatter(text)
        assert meta["name"] == "gdpr-ccpa-compliance"
        assert "Triggers on: 'GDPR'" in meta["description"]
        assert meta["tools"] == "Read, Grep"
        assert not body.startswith("---")
        assert "name:" not in body

    def test_extended_dash_closing_fence_is_still_recognized(self):
        # Real-world bug found while batch-testing github/awesome-claude-
        # agents (frontend-developer.md): the closing frontmatter fence was
        # a long run of dashes (a markdown thematic break, "------...---")
        # rather than exactly "---". The regex used to require an exact
        # "---" close, so the whole frontmatter block (plus the blank line
        # after it) was left completely unparsed and dumped into
        # instructions/core.md as raw "name: ...\ndescription: ..." text.
        text = (
            "---\n"
            "name: frontend-developer\n"
            "description: Builds UIs.\n"
            "--------------------------------------------------------\n\n"
            "# Frontend Developer\n\n"
            "You build user interfaces.\n"
        )
        meta, body = split_frontmatter(text)
        assert meta == {"name": "frontend-developer", "description": "Builds UIs."}
        assert "name:" not in body
        assert body.startswith("# Frontend Developer")

    def test_nested_mapping_frontmatter_still_uses_strict_yaml(self):
        # Legitimately complex frontmatter (e.g. nested MCP server config)
        # must still go through real YAML parsing, not the lenient
        # line-based fallback, so nested structure isn't flattened.
        text = (
            "---\n"
            "name: foo\n"
            "config:\n"
            "  timeout: 30\n"
            "  retries: 3\n"
            "---\n\n"
            "Body.\n"
        )
        meta, body = split_frontmatter(text)
        assert meta["config"] == {"timeout": 30, "retries": 3}


class TestAgentDefWriterValidates:
    def test_minimal_writer_output_passes_validation(self, tmp_path):
        writer = AgentDefWriter(str(tmp_path / "agent"), "Test Agent", description="A test agent.")
        writer.set_role("You are a test agent.")
        writer.add_objectives(["do the thing"])
        writer.add_core_text("Always be polite.")
        out = writer.write()

        result = validate(str(out))
        assert result.valid, result.summary()

    def test_writer_with_skills_workflows_tools(self, tmp_path):
        writer = AgentDefWriter(str(tmp_path / "agent2"), "Full Agent")
        writer.set_role("You are a full-featured agent.")
        writer.add_skill("Summarization", "# Summarization Skill\n\nSummarize text.")
        writer.add_workflow("Main Flow", "# Main Flow\n\n1. Do it.")
        writer.add_tool("Web Search", "# Web Search\n\nSearches the web.")
        out = writer.write()

        assert (out / "skills" / "summarization" / "SKILL.md").exists()
        assert (out / "workflows" / "main-flow.md").exists()
        assert (out / "tools" / "web-search.md").exists()

        result = validate(str(out))
        assert result.valid, result.summary()

    def test_numbered_priorities_are_not_double_numbered(self, tmp_path):
        # End-to-end regression for the bug caught while building the
        # Claude -> Copilot demo: a '## Priorities' section authored as an
        # ordered markdown list must not come out as "1. 1. ..." once
        # AgentDefWriter re-numbers it on render.
        text = (
            "# Some Agent\n\n"
            "## Role\nYou review things.\n\n"
            "## Priorities\n"
            "1. Security issues block merge, always\n"
            "2. Correctness bugs block merge unless trivially fixable\n"
        )
        writer = AgentDefWriter(str(tmp_path / "prio-agent"), "prio-agent")
        report = ImportReport(source="test", framework="generic")
        generic_markdown_import(text, writer, report)
        out = writer.write(report)

        agent_md = (out / "agent.md").read_text()
        assert "1. Security issues block merge, always" in agent_md
        assert "1. 1." not in agent_md
        assert "2. 2." not in agent_md

        result = validate(str(out))
        assert result.valid, result.summary()


class TestGenericMarkdownImport:
    def test_full_classification(self, tmp_path):
        text = (
            "# Acme Support Agent\n\n"
            "## Role\nYou are a customer support agent for Acme.\n\n"
            "## Objectives\n- resolve tickets\n- stay polite\n\n"
            "## Style\n- concise\n- friendly\n\n"
            "## Avoid\n- making promises about refunds\n\n"
            "## Skills\n\n"
            "### Ticket Triage\nClassify incoming tickets by urgency.\n\n"
            "### Refund Lookup\nLook up refund status.\n\n"
            "## Workflows\n\n"
            "### Handle Ticket\n1. Read ticket\n2. Classify\n3. Respond\n"
        )
        writer = AgentDefWriter(str(tmp_path / "acme"), "acme-support")
        report = ImportReport(source="test", framework="generic")
        generic_markdown_import(text, writer, report)
        out = writer.write(report)

        assert "customer support agent" in (out / "agent.md").read_text()
        assert (out / "skills" / "ticket-triage" / "SKILL.md").exists()
        assert (out / "skills" / "refund-lookup" / "SKILL.md").exists()
        assert (out / "workflows" / "handle-ticket.md").exists()

        result = validate(str(out))
        assert result.valid, result.summary()

    def test_no_role_section_infers_one(self, tmp_path):
        text = "You are a helpful note-taking assistant.\n\n## Tasks\nTake notes during meetings.\n"
        writer = AgentDefWriter(str(tmp_path / "notes"), "notes-agent")
        report = ImportReport(source="test", framework="generic")
        generic_markdown_import(text, writer, report)
        out = writer.write(report)

        agent_md = (out / "agent.md").read_text()
        assert "helpful note-taking assistant" in agent_md
        assert any("inferred" in m.lower() for m in report.inferred)

        result = validate(str(out))
        assert result.valid, result.summary()

    def test_no_preamble_no_persona_falls_back_to_first_sentence(self, tmp_path):
        # Real-world bug found while testing against github/awesome-copilot
        # agents (apify-integration-expert.agent.md): a doc with no leading
        # preamble (opens directly on an H1) and no 'You are ...'/'You
        # help ...'-style sentence anywhere used to fall all the way through
        # to the bare "(role not specified in source)" placeholder, even
        # though perfectly good descriptive text was sitting right there in
        # the first section.
        text = (
            "# Widget Integration Agent\n\n"
            "## Details\n\n"
            "This agent connects Widgets to your codebase and keeps them in sync. "
            "It adapts to your existing stack.\n\n"
            "## Safety\n\nNever commit secrets.\n"
        )
        writer = AgentDefWriter(str(tmp_path / "widget"), "widget-agent")
        report = ImportReport(source="test", framework="generic")
        generic_markdown_import(text, writer, report)
        out = writer.write(report)

        agent_md = (out / "agent.md").read_text()
        assert "(role not specified in source)" not in agent_md
        assert "connects Widgets to your codebase" in agent_md
        assert any("first sentence" in m.lower() for m in report.inferred)

        result = validate(str(out))
        assert result.valid, result.summary()
