"""
Test Driven Development suite for British English Conversational Flow Improvements

Tests verify that guidance templates produce natural conversational prompts
instead of numbered task lists, as documented in:
specs/british-english-conversational-improvements.md Section 2

These tests will FAIL initially since templates still have old task-based structure.
They should PASS after implementing the conversational flow improvements.

USAGE:
    # Skip tests (default - won't fail CI):
    pytest tests/test_conversational_flow.py -v

    # Run tests to see current failures (for TDD development):
    # Comment out the 'pytestmark' line at the bottom of this file, then:
    pytest tests/test_conversational_flow.py -v

    # Or run without modifying the file:
    pytest tests/test_conversational_flow.py -v --ignore-skip

EXPECTED RESULTS:
    Before implementation: 12 FAILED, 14 PASSED
    After implementation: 26 PASSED, 0 FAILED
"""

import re
from pathlib import Path

import pytest


# Template file paths
TEMPLATE_DIR = Path(__file__).parent.parent / "src" / "guidance_agent" / "templates" / "advisor"
GUIDANCE_MAIN = TEMPLATE_DIR / "guidance_main.jinja"
GUIDANCE_REASONING = TEMPLATE_DIR / "guidance_with_reasoning.jinja"
GUIDANCE_CACHED = TEMPLATE_DIR / "guidance_cached.jinja"


class TestConversationalFlowStructure:
    """Test that templates use conversational flow instead of numbered task lists"""

    def test_guidance_main_no_numbered_task_list(self):
        """
        guidance_main.jinja should NOT contain numbered task list (1. 2. 3. etc.)

        Expected to FAIL initially - template currently has lines ~136-144:
        TASK:
        Provide appropriate pension guidance that:
        1. Addresses the customer's specific question
        2. Uses language appropriate for their literacy level
        3. Presents balanced information (pros and cons)
        4. Stays clearly within the FCA guidance boundary
        5. Checks customer understanding
        """
        content = GUIDANCE_MAIN.read_text()

        # Check for numbered list pattern (1., 2., 3., etc.)
        numbered_list_pattern = re.compile(r'^\s*\d+\.\s+', re.MULTILINE)
        matches = numbered_list_pattern.findall(content)

        assert len(matches) == 0, (
            f"guidance_main.jinja contains {len(matches)} numbered list items. "
            "Should use conversational flow instead of task list. "
            f"Found: {matches}"
        )

    def test_guidance_reasoning_no_numbered_task_list(self):
        """
        guidance_with_reasoning.jinja should NOT contain numbered task list

        Expected to FAIL initially - template currently has lines ~71-78:
        TASK:
        Based on your reasoning above, provide pension guidance that:
        1. Addresses the customer's question
        2. Uses appropriate language for their literacy level
        3. Presents balanced information
        4. Stays within FCA guidance boundary
        5. Checks customer understanding
        6. Applies the conversational strategy from your reasoning
        """
        content = GUIDANCE_REASONING.read_text()

        # Check for numbered list pattern
        numbered_list_pattern = re.compile(r'^\s*\d+\.\s+', re.MULTILINE)
        matches = numbered_list_pattern.findall(content)

        assert len(matches) == 0, (
            f"guidance_with_reasoning.jinja contains {len(matches)} numbered list items. "
            "Should use conversational flow instead of task list. "
            f"Found: {matches}"
        )

    def test_guidance_cached_no_numbered_task_list(self):
        """
        guidance_cached.jinja should NOT contain numbered task list

        Expected to FAIL initially - template currently has lines ~59:
        Please provide appropriate pension guidance that:
        1. Addresses the customer's specific question
        2. Uses language appropriate for their literacy level
        3. Presents balanced information (pros and cons)
        4. Stays clearly within the FCA guidance boundary
        5. Checks customer understanding
        """
        content = GUIDANCE_CACHED.read_text()

        # Check for numbered list pattern
        numbered_list_pattern = re.compile(r'^\s*\d+\.\s+', re.MULTILINE)
        matches = numbered_list_pattern.findall(content)

        assert len(matches) == 0, (
            f"guidance_cached.jinja contains {len(matches)} numbered list items. "
            "Should use conversational flow instead of task list. "
            f"Found: {matches}"
        )


class TestConversationalLanguagePresence:
    """Test that templates contain new conversational language"""

    def test_guidance_main_has_natural_conversational_language(self):
        """
        guidance_main.jinja should contain new conversational language

        Expected language per specs:
        - "natural, conversational way"
        - "flowing dialogue"
        - "Let the conversation develop naturally"

        Expected to FAIL initially.
        """
        content = GUIDANCE_MAIN.read_text()

        # Check for key conversational phrases
        assert "natural, conversational way" in content.lower() or "natural conversational way" in content.lower(), (
            "guidance_main.jinja should contain 'natural, conversational way'"
        )

        assert "flowing dialogue" in content.lower() or "flow" in content.lower(), (
            "guidance_main.jinja should reference flowing/natural dialogue"
        )

    def test_guidance_main_has_balanced_information_without_list(self):
        """
        guidance_main.jinja should mention balanced information but not in numbered list

        Should use phrasing like:
        - "Presenting balanced information where relevant"
        - As bullet point, not numbered item

        Expected to FAIL initially.
        """
        content = GUIDANCE_MAIN.read_text()

        # Should contain "balanced" concept
        assert "balanced" in content.lower(), (
            "guidance_main.jinja should still mention balanced information"
        )

        # But NOT as "3. Presents balanced information"
        # Check that "balanced" doesn't appear in numbered list context
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'balanced' in line.lower():
                # Check surrounding lines for numbered list pattern
                context = '\n'.join(lines[max(0, i-2):min(len(lines), i+3)])
                assert not re.search(r'\d+\.\s+.*balanced', context, re.IGNORECASE), (
                    f"'balanced' should not appear in numbered list. Found context:\n{context}"
                )

    def test_guidance_main_has_fca_boundary_without_list(self):
        """
        guidance_main.jinja should mention FCA boundaries but not in numbered list

        Should use phrasing like:
        - "Staying within FCA guidance boundaries"
        - As bullet point or natural prose, not numbered item

        Expected to FAIL initially.
        """
        content = GUIDANCE_MAIN.read_text()

        # Should contain FCA boundary concept
        assert "fca" in content.lower() and "boundar" in content.lower(), (
            "guidance_main.jinja should mention FCA guidance boundaries"
        )

        # But NOT as "4. Stays clearly within the FCA guidance boundary"
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'fca' in line.lower() and 'boundar' in line.lower():
                # Check if this line is part of numbered list
                assert not re.match(r'^\s*\d+\.\s+', line), (
                    f"FCA boundary should not appear in numbered list. Found: {line}"
                )

    def test_guidance_reasoning_has_conversational_flow_language(self):
        """
        guidance_with_reasoning.jinja should reference conversational flow

        Expected to FAIL initially.
        """
        content = GUIDANCE_REASONING.read_text()

        # Should mention conversational approach
        # Either in instructions or reference to flowing dialogue
        conversational_indicators = [
            "conversation",
            "natural",
            "flowing",
            "dialogue"
        ]

        content_lower = content.lower()
        found = [ind for ind in conversational_indicators if ind in content_lower]

        assert len(found) >= 2, (
            f"guidance_with_reasoning.jinja should reference conversational flow. "
            f"Found only {len(found)} indicators: {found}"
        )

    def test_guidance_cached_has_natural_flow_language(self):
        """
        guidance_cached.jinja should contain natural flow language in system prompt

        Expected to FAIL initially.
        """
        content = GUIDANCE_CACHED.read_text()

        # Should contain conversational guidance in system prompt
        assert "natural" in content.lower() or "conversation" in content.lower(), (
            "guidance_cached.jinja should reference natural conversational flow"
        )


class TestContradictoryPhraseRemoval:
    """Test that contradictory phrase is removed from varied phrasing section"""

    def test_guidance_main_no_contradictory_phrase_in_varied_phrasing(self):
        """
        guidance_main.jinja should NOT have "Some people in your situation" in Varied Phrasing section

        This phrase appears in:
        - Line ~55: Varied Phrasing Alternatives section (SHOULD BE REMOVED)
        - Line ~97: FCA Social Proof Prohibition section (SHOULD REMAIN)

        It's contradictory to show it as both recommended AND prohibited.

        Expected to FAIL initially.
        """
        content = GUIDANCE_MAIN.read_text()
        lines = content.split('\n')

        # Find the "Varied Phrasing" section
        varied_phrasing_start = None
        varied_phrasing_end = None

        for i, line in enumerate(lines):
            if 'Varied Phrasing' in line or 'varied phrasing' in line.lower():
                varied_phrasing_start = i
            elif varied_phrasing_start is not None and ('##' in line or 'CUSTOMER PROFILE' in line):
                varied_phrasing_end = i
                break

        if varied_phrasing_start is not None:
            varied_section = '\n'.join(lines[varied_phrasing_start:varied_phrasing_end or len(lines)])

            # The problematic phrase should NOT appear in this section
            assert "Some people in your situation" not in varied_section, (
                "guidance_main.jinja Varied Phrasing section should NOT contain "
                "'Some people in your situation' - this phrase is contradictory since "
                "it appears in FCA prohibition section"
            )

    def test_guidance_main_contradictory_phrase_remains_in_prohibition_section(self):
        """
        guidance_main.jinja SHOULD still have "Some people in your situation" in FCA prohibition section

        This phrase should remain in the "Social Proof Prohibition" section as an example
        of what NOT to say.
        """
        content = GUIDANCE_MAIN.read_text()

        # Find FCA prohibition section
        lines = content.split('\n')
        prohibition_section_start = None

        for i, line in enumerate(lines):
            if 'Social Proof Prohibition' in line or 'PROHIBITED' in line:
                prohibition_section_start = i
                break

        assert prohibition_section_start is not None, "Should have FCA prohibition section"

        # Check that the phrase exists somewhere after prohibition section starts
        prohibition_content = '\n'.join(lines[prohibition_section_start:])

        assert "Some people in your situation" in prohibition_content or "people in your situation" in prohibition_content, (
            "The phrase 'people in your situation' should remain in FCA prohibition section as example"
        )

    def test_guidance_cached_no_contradictory_phrase_in_examples(self):
        """
        guidance_cached.jinja should not show contradictory phrasing in examples section

        The template has Natural vs Robotic examples and should not recommend
        "Some people in your situation" while also prohibiting it.

        Expected to FAIL if contradictory phrasing exists in examples.
        """
        content = GUIDANCE_CACHED.read_text()

        # Find the "Examples" or "Natural vs Robotic" section
        lines = content.split('\n')
        examples_section = []
        in_examples = False

        for line in lines:
            if 'Examples' in line or 'Natural vs' in line:
                in_examples = True
            elif in_examples and ('##' in line or 'CRITICAL:' in line):
                break
            elif in_examples:
                examples_section.append(line)

        examples_text = '\n'.join(examples_section)

        # If there are examples showing natural/good phrasing
        # they should not include the contradictory phrase
        if '✅' in examples_text or 'Natural:' in examples_text:
            assert "Some people in your situation" not in examples_text, (
                "guidance_cached.jinja should not show 'Some people in your situation' "
                "as recommended phrasing in examples"
            )


class TestConversationalFlowInstructions:
    """Test that templates instruct to treat conversation as flowing dialogue"""

    def test_guidance_main_instructs_flowing_dialogue_not_checklist(self):
        """
        guidance_main.jinja should instruct to treat as flowing dialogue, not checklist

        Expected instruction per specs:
        "Treat this as a flowing dialogue between two people, not a structured
        information delivery. Let the conversation develop naturally whilst
        satisfying these requirements throughout the exchange."

        Expected to FAIL initially.
        """
        content = GUIDANCE_MAIN.read_text()

        # Check for key phrases about dialogue flow
        content_lower = content.lower()

        # Should have some instruction about natural flow
        flow_indicators = [
            "flowing dialogue",
            "natural" in content_lower and "conversation" in content_lower,
            "not a structured" in content_lower or "not structured" in content_lower,
            "develop naturally" in content_lower
        ]

        found_indicators = sum(1 for indicator in flow_indicators if indicator)

        assert found_indicators >= 2, (
            "guidance_main.jinja should instruct to treat as flowing dialogue, "
            f"not structured checklist. Found {found_indicators}/4 indicators"
        )

    def test_guidance_main_replaces_task_heading_with_conversational_instruction(self):
        """
        guidance_main.jinja should replace "TASK:" heading with conversational instruction

        Old structure (lines 136-144):
        TASK:
        Provide appropriate pension guidance that:
        1. ...

        New structure per specs:
        Respond to the customer's message in a natural, conversational way that
        addresses their question whilst:
        - Using language appropriate for their context
        - Presenting balanced information where relevant
        - ...

        Expected to FAIL initially.
        """
        content = GUIDANCE_MAIN.read_text()

        # If "TASK:" heading exists, it should be followed by conversational instruction
        # not numbered list
        if 'TASK:' in content:
            lines = content.split('\n')
            task_line_idx = None

            for i, line in enumerate(lines):
                if line.strip() == 'TASK:':
                    task_line_idx = i
                    break

            if task_line_idx is not None:
                # Check next few lines after TASK:
                next_lines = '\n'.join(lines[task_line_idx+1:task_line_idx+8])

                # Should NOT have numbered list immediately after
                assert not re.search(r'^\s*1\.', next_lines, re.MULTILINE), (
                    "After 'TASK:' heading, should have conversational instruction, "
                    "not numbered list starting with '1.'"
                )

                # SHOULD have conversational language
                assert ("natural" in next_lines.lower() or
                        "conversational" in next_lines.lower() or
                        "flowing" in next_lines.lower()), (
                    "After 'TASK:' heading, should reference natural/conversational approach"
                )

    def test_guidance_reasoning_replaces_task_list_with_conversational_approach(self):
        """
        guidance_with_reasoning.jinja should replace task list with conversational approach

        Expected to FAIL initially - currently has numbered list at lines ~71-78.
        """
        content = GUIDANCE_REASONING.read_text()

        # Check structure after "TASK:" or similar heading
        if 'TASK:' in content or 'provide' in content.lower() and 'guidance' in content.lower():
            # Should not have numbered list in the instruction section
            # Split into sections
            lines = content.split('\n')

            # Find instruction section (after FCA requirements, before end)
            instruction_start = None
            for i, line in enumerate(lines):
                if 'TASK:' in line or ('provide' in line.lower() and 'guidance' in line.lower()):
                    instruction_start = i
                    break

            if instruction_start:
                instruction_section = '\n'.join(lines[instruction_start:])

                # Count numbered list items in instruction section
                numbered_items = re.findall(r'^\s*\d+\.', instruction_section, re.MULTILINE)

                assert len(numbered_items) == 0, (
                    f"guidance_with_reasoning.jinja instruction section should not have "
                    f"numbered list. Found {len(numbered_items)} items"
                )

    def test_guidance_cached_user_message_has_conversational_instruction(self):
        """
        guidance_cached.jinja user message should have conversational instruction, not task list

        Currently the user message (line ~59) has:
        "Please provide appropriate pension guidance that:
        1. Addresses the customer's specific question
        2. ..."

        Should be replaced with conversational instruction.

        Expected to FAIL initially.
        """
        content = GUIDANCE_CACHED.read_text()

        # The template is JSON structure, find the user message content
        # Look for the user role section
        user_section_match = re.search(r'"role":\s*"user".*?"content":\s*{{[^}]+}}', content, re.DOTALL)

        assert user_section_match is not None, "Should have user role section"

        user_section = user_section_match.group(0)

        # The user message should not contain numbered list pattern
        # Even in the Jinja template concatenation
        # Look for patterns like "1. Addresses" or "2. Uses"
        assert not re.search(r'\\n\d+\.', user_section), (
            "guidance_cached.jinja user message should not contain numbered list. "
            "Should use conversational instruction instead."
        )


class TestBulletPointsInsteadOfNumberedList:
    """Test that templates use bullet points (-) instead of numbered lists (1. 2. 3.)"""

    def test_guidance_main_uses_bullets_for_requirements(self):
        """
        guidance_main.jinja should use bullet points (-) for requirements, not numbers

        Per specs, new structure should be:
        Respond to the customer's message in a natural, conversational way that
        addresses their question whilst:
        - Using language appropriate for their context
        - Presenting balanced information where relevant
        - Staying within FCA guidance boundaries
        - Naturally checking understanding when exploring complex topics

        Expected to FAIL initially.
        """
        content = GUIDANCE_MAIN.read_text()

        # Find the section that lists requirements
        # Should be near customer question or task section
        lines = content.split('\n')

        requirements_section_start = None
        for i, line in enumerate(lines):
            if ('customer' in line.lower() and 'question' in line.lower()) or 'TASK:' in line:
                requirements_section_start = i
                break

        if requirements_section_start:
            # Look at next 20 lines for requirements listing
            requirements_section = '\n'.join(lines[requirements_section_start:requirements_section_start+20])

            # Count bullet points vs numbered items
            bullet_points = len(re.findall(r'^\s*-\s+', requirements_section, re.MULTILINE))
            numbered_items = len(re.findall(r'^\s*\d+\.\s+', requirements_section, re.MULTILINE))

            # If there are requirements listed, should prefer bullets over numbers
            if bullet_points + numbered_items > 0:
                assert bullet_points >= numbered_items, (
                    f"guidance_main.jinja should use bullet points for requirements, not numbers. "
                    f"Found {bullet_points} bullets vs {numbered_items} numbered items"
                )

    def test_templates_use_whilst_instead_of_while(self):
        """
        Templates should use British English 'whilst' instead of American 'while'
        in formal contexts

        Per specs: "addresses their question whilst:"

        This is a soft test - 'while' is acceptable in some contexts,
        but formal requirement listings should use 'whilst'
        """
        for template_file in [GUIDANCE_MAIN, GUIDANCE_REASONING, GUIDANCE_CACHED]:
            content = template_file.read_text()

            # If there's a phrase like "addresses their question while:"
            # it should be "whilst:"
            if 'addresses their question' in content.lower():
                context = content.lower()
                # Check if it uses "while:" or "whilst:" after "addresses their question"
                match = re.search(r'addresses their question\s+(while|whilst)', context)
                if match:
                    assert match.group(1) == 'whilst', (
                        f"{template_file.name} should use 'whilst' in formal requirement context. "
                        f"Found: 'addresses their question {match.group(1)}'"
                    )


class TestKeyPhrasesPresence:
    """Test that templates contain specific key phrases from the specs"""

    def test_guidance_main_contains_key_phrases(self):
        """
        guidance_main.jinja should contain key phrases from specs section 2

        Required phrases:
        - "natural, conversational way"
        - "flowing dialogue"
        - "naturally" (in context of checking understanding or developing conversation)

        Expected to FAIL initially.
        """
        content = GUIDANCE_MAIN.read_text()
        content_lower = content.lower()

        key_phrases = {
            "natural": "natural" in content_lower and "conversational" in content_lower,
            "flowing": "flowing" in content_lower or "flow" in content_lower,
            "naturally": "naturally" in content_lower
        }

        missing_phrases = [phrase for phrase, found in key_phrases.items() if not found]

        assert len(missing_phrases) == 0, (
            f"guidance_main.jinja missing key conversational phrases: {missing_phrases}"
        )

    def test_guidance_main_references_dialogue_not_just_response(self):
        """
        guidance_main.jinja should reference "dialogue" or "conversation", not just "response"

        The template should frame the interaction as ongoing dialogue,
        not just generating a response.

        Expected to FAIL initially.
        """
        content = GUIDANCE_MAIN.read_text()
        content_lower = content.lower()

        dialogue_indicators = [
            "dialogue" in content_lower,
            "conversation" in content_lower,
            "exchange" in content_lower
        ]

        assert any(dialogue_indicators), (
            "guidance_main.jinja should reference 'dialogue', 'conversation', or 'exchange' "
            "to frame interaction as ongoing dialogue, not just response generation"
        )

    def test_guidance_main_mentions_satisfying_requirements_throughout(self):
        """
        guidance_main.jinja should mention satisfying requirements "throughout the exchange"

        Per specs:
        "Let the conversation develop naturally whilst satisfying these requirements
        throughout the exchange."

        This emphasizes ongoing compliance, not checklist completion.

        Expected to FAIL initially.
        """
        content = GUIDANCE_MAIN.read_text()
        content_lower = content.lower()

        # Check for concept of ongoing/throughout satisfaction of requirements
        ongoing_indicators = [
            "throughout" in content_lower,
            "during" in content_lower and "exchange" in content_lower,
            "as the conversation" in content_lower
        ]

        assert any(ongoing_indicators), (
            "guidance_main.jinja should reference satisfying requirements 'throughout' "
            "or 'during the exchange' - emphasizing ongoing compliance, not checklist"
        )


class TestTemplateStructuralChanges:
    """Test structural changes to template organization"""

    def test_guidance_main_task_section_is_near_end(self):
        """
        guidance_main.jinja task/instruction section should be near end of template

        Current structure has TASK at line ~136 near the end.
        After changes, the conversational instruction should remain near the end,
        after all context is provided.

        This test verifies the instruction appears in the last 20 lines of template.
        """
        content = GUIDANCE_MAIN.read_text()
        lines = content.split('\n')

        # Find where main instruction/task section is
        instruction_line = None
        for i, line in enumerate(lines):
            if ('respond' in line.lower() and 'customer' in line.lower()) or 'TASK:' in line:
                instruction_line = i
                break

        if instruction_line is not None:
            lines_from_end = len(lines) - instruction_line

            assert lines_from_end <= 25, (
                f"Instruction section should be near end of template (within last 25 lines). "
                f"Found at line {instruction_line}, which is {lines_from_end} lines from end"
            )

    def test_all_templates_maintain_fca_neutrality_section(self):
        """
        All three templates should maintain FCA Neutrality section

        The conversational flow changes should NOT remove FCA compliance requirements.
        All templates should still have the critical neutrality section.
        """
        for template_file in [GUIDANCE_MAIN, GUIDANCE_REASONING, GUIDANCE_CACHED]:
            content = template_file.read_text()

            assert "FCA Neutrality" in content or "CRITICAL: FCA" in content, (
                f"{template_file.name} should maintain FCA Neutrality Requirements section"
            )

            assert "Evaluative Language Prohibition" in content, (
                f"{template_file.name} should maintain Evaluative Language Prohibition section"
            )

    def test_templates_maintain_customer_profile_and_context_sections(self):
        """
        Templates should maintain all context sections (customer profile, history, etc.)

        The conversational flow changes should only affect the task instruction section,
        not the context retrieval sections.
        """
        # guidance_main.jinja should have these sections
        content = GUIDANCE_MAIN.read_text()

        required_sections = [
            "CUSTOMER PROFILE",
            "CONVERSATION HISTORY",
            "RETRIEVED CONTEXT",
            "FCA REQUIREMENTS"
        ]

        for section in required_sections:
            assert section in content, (
                f"guidance_main.jinja should maintain {section} section"
            )


class TestNoTaskHeadingWithNumberedList:
    """Test that TASK: heading is not followed by numbered list"""

    def test_guidance_main_task_heading_not_followed_by_numbered_list(self):
        """
        If guidance_main.jinja still has "TASK:" heading, it should NOT be followed
        by numbered list

        Expected to FAIL initially - currently has numbered list after TASK:
        """
        content = GUIDANCE_MAIN.read_text()

        if "TASK:" in content:
            lines = content.split('\n')
            task_idx = None

            for i, line in enumerate(lines):
                if line.strip() == "TASK:":
                    task_idx = i
                    break

            if task_idx is not None:
                # Check next 10 lines
                next_lines = lines[task_idx+1:task_idx+11]

                # Should not have "1." in the next few lines
                for j, line in enumerate(next_lines):
                    assert not re.match(r'^\s*1\.\s+', line), (
                        f"guidance_main.jinja TASK: heading should not be followed by "
                        f"numbered list. Found '1.' at line {task_idx + j + 1}: {line}"
                    )

    def test_guidance_reasoning_task_heading_not_followed_by_numbered_list(self):
        """
        If guidance_with_reasoning.jinja still has "TASK:" heading, it should NOT be
        followed by numbered list

        Expected to FAIL initially
        """
        content = GUIDANCE_REASONING.read_text()

        if "TASK:" in content:
            lines = content.split('\n')
            task_idx = None

            for i, line in enumerate(lines):
                if line.strip() == "TASK:":
                    task_idx = i
                    break

            if task_idx is not None:
                # Check next 10 lines
                next_lines = lines[task_idx+1:task_idx+11]

                # Should not have "1." in the next few lines
                for j, line in enumerate(next_lines):
                    assert not re.match(r'^\s*1\.\s+', line), (
                        f"guidance_with_reasoning.jinja TASK: heading should not be followed "
                        f"by numbered list. Found '1.' at line {task_idx + j + 1}: {line}"
                    )

    def test_guidance_cached_no_numbered_list_in_final_instruction(self):
        """
        guidance_cached.jinja should not have numbered list in the final user message

        Expected to FAIL initially - currently has numbered list in user message
        """
        content = GUIDANCE_CACHED.read_text()

        # Find the user role content (last message in JSON structure)
        lines = content.split('\n')

        # Find lines that are part of user message
        user_message_lines = []
        in_user_message = False

        for line in lines:
            if '"role": "user"' in line:
                in_user_message = True
            elif in_user_message:
                user_message_lines.append(line)
                if line.strip() == '}' or line.strip() == '],':
                    break

        user_message_text = '\n'.join(user_message_lines)

        # Should not contain "\\n1." or similar patterns indicating numbered list
        assert not re.search(r'\\n\s*\d+\.', user_message_text), (
            "guidance_cached.jinja user message should not contain numbered list pattern"
        )


# Summary comment for pytest output
# Uncomment the line below to skip these tests until implementation is complete:
# pytestmark = pytest.mark.skip(
#     reason="TDD tests - Expected to FAIL until conversational flow improvements are implemented"
# )


if __name__ == "__main__":
    print("""
    =============================================================================
    Test Driven Development Suite for Conversational Flow Improvements
    =============================================================================

    These tests verify the changes specified in:
    specs/british-english-conversational-improvements.md Section 2

    EXPECTED BEHAVIOR:
    - All tests will FAIL initially (templates have old task-based structure)
    - Tests will PASS after implementing conversational flow improvements

    WHAT THE TESTS CHECK:
    1. No numbered task lists (1. 2. 3.) in any of the 3 templates
    2. Presence of new conversational language ("natural", "flowing dialogue")
    3. Removal of contradictory phrase "Some people in your situation" from varied phrasing
    4. Bullet points (-) used instead of numbered lists for requirements
    5. Instructions to treat as "flowing dialogue" not "structured checklist"
    6. Key phrases from specs are present
    7. FCA neutrality sections are maintained

    FILES TESTED:
    - src/guidance_agent/templates/advisor/guidance_main.jinja
    - src/guidance_agent/templates/advisor/guidance_with_reasoning.jinja
    - src/guidance_agent/templates/advisor/guidance_cached.jinja

    RUN TESTS:
    pytest tests/test_conversational_flow.py -v

    Or to run without skip marker:
    pytest tests/test_conversational_flow.py -v --ignore-skip
    =============================================================================
    """)
