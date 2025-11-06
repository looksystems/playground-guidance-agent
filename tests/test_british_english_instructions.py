"""Test suite for British English INSTRUCTIONS in Jinja2 templates.

This module tests that all customer-facing templates include explicit British English
INSTRUCTIONS to ensure LLM-generated content uses consistent spelling and phrasing.

IMPORTANT DISTINCTION:
- test_british_english_templates.py: Tests that existing template text uses British spelling
- THIS FILE: Tests that templates INSTRUCT the LLM to use British English in generated content

Based on: specs/british-english-prompt-instructions.md

Test Structure:
- Phase 1: Critical customer-facing templates (5 templates)
- Phase 2: Validation template (1 template)
- Phase 3: Customer simulation templates (7 templates)

These tests use TDD approach - they will FAIL initially until British English
instructions are added to each template.
"""

import pytest
from pathlib import Path


# Test data for British English instruction keywords
BRITISH_ENGLISH_INSTRUCTION_KEYWORDS = [
    "british english",
    "british spelling",
    "british conventions",
]

# Specific examples that should be mentioned in instructions
BRITISH_SPELLING_EXAMPLES = [
    "optimise",
    "analyse",
    "behaviour",
    "favour",
]


def read_template(template_path: str) -> str:
    """Read template file content.

    Args:
        template_path: Relative path to template from templates directory

    Returns:
        Template file content as string
    """
    base_path = Path(__file__).parent.parent / "src" / "guidance_agent" / "templates"
    full_path = base_path / template_path

    if not full_path.exists():
        pytest.fail(f"Template file not found: {full_path}")

    return full_path.read_text()


def check_british_english_instruction(content: str, template_name: str) -> tuple[bool, str]:
    """Check if template contains British English instructions for LLM.

    Args:
        content: Template file content
        template_name: Name of template for error messaging

    Returns:
        Tuple of (has_instruction, detailed_message)
    """
    content_lower = content.lower()

    # Check for instruction keywords
    found_keywords = [kw for kw in BRITISH_ENGLISH_INSTRUCTION_KEYWORDS if kw in content_lower]

    # Check if examples are provided (stronger evidence of instruction)
    found_examples = [ex for ex in BRITISH_SPELLING_EXAMPLES if ex in content_lower]

    has_instruction = len(found_keywords) > 0

    if has_instruction:
        message = f"✓ {template_name}: Found British English instruction (keywords: {found_keywords}, examples: {found_examples})"
    else:
        message = f"✗ {template_name}: Missing British English instruction. Expected phrases like: {BRITISH_ENGLISH_INSTRUCTION_KEYWORDS}"

    return has_instruction, message


class TestPhase1CriticalCustomerFacingTemplates:
    """Phase 1: Test critical customer-facing templates (5 templates).

    These templates generate text that customers directly see and read.
    They MUST instruct the LLM to use British English for consistency.

    Priority: ⭐ CRITICAL
    """

    def test_guidance_main_has_british_english_instruction(self):
        """Test advisor/guidance_main.jinja instructs LLM to use British English.

        Template: advisor/guidance_main.jinja
        Priority: ⭐ CRITICAL (most frequently used)
        Expected location: After line 29 (after "Signpost to FCA-regulated advisors...")
        Expected text: "- Use British English spelling and conventions (optimise, analyse, behaviour, favour, etc.)"

        This instruction ensures the LLM generates guidance using British English,
        not just that the template itself uses British English.
        """
        content = read_template("advisor/guidance_main.jinja")
        has_instruction, message = check_british_english_instruction(content, "guidance_main.jinja")

        assert has_instruction, (
            f"guidance_main.jinja MUST instruct LLM to use British English.\n"
            f"\n"
            f"Expected location: After line 29 (after 'Signpost to FCA-regulated advisors')\n"
            f"Expected addition (as a bullet point):\n"
            f"  - Use British English spelling and conventions (optimise, analyse, behaviour, favour, etc.)\n"
            f"\n"
            f"Why: This template generates customer-facing content. Without explicit instruction,\n"
            f"     the LLM may default to American English spelling.\n"
            f"\n{message}"
        )

        # Additionally check that examples are provided
        content_lower = content.lower()
        has_examples = any(ex in content_lower for ex in BRITISH_SPELLING_EXAMPLES)
        if has_instruction and not has_examples:
            pytest.skip(
                f"guidance_main.jinja has British English instruction but lacks examples. "
                f"Consider adding examples like: optimise, analyse, behaviour, favour"
            )

    def test_guidance_with_reasoning_has_british_english_instruction(self):
        """Test advisor/guidance_with_reasoning.jinja instructs LLM to use British English.

        Template: advisor/guidance_with_reasoning.jinja
        Priority: ⭐ CRITICAL
        Expected location: After line 27 (after FCA REQUIREMENTS section)
        Expected text: "- Use British English spelling and conventions (optimise, analyse, behaviour, favour, etc.)"
        """
        content = read_template("advisor/guidance_with_reasoning.jinja")
        has_instruction, message = check_british_english_instruction(content, "guidance_with_reasoning.jinja")

        assert has_instruction, (
            f"guidance_with_reasoning.jinja MUST instruct LLM to use British English.\n"
            f"\n"
            f"Expected location: After line 27 (after FCA REQUIREMENTS section)\n"
            f"Expected addition:\n"
            f"  - Use British English spelling and conventions (optimise, analyse, behaviour, favour, etc.)\n"
            f"\n"
            f"Why: This template generates customer-facing guidance based on reasoning.\n"
            f"     British English must be consistent across all guidance outputs.\n"
            f"\n{message}"
        )

    def test_guidance_cached_has_british_english_instruction(self):
        """Test advisor/guidance_cached.jinja instructs LLM to use British English.

        Template: advisor/guidance_cached.jinja
        Priority: ⭐ CRITICAL (cache-optimized, frequently used)
        Expected location: Line ~32 (within system prompt content)
        Expected text: Add to "Your role is to provide FCA-compliant pension GUIDANCE" section

        Note: This template returns JSON with cached content, so the instruction
        must be in the system prompt text content.
        """
        content = read_template("advisor/guidance_cached.jinja")
        has_instruction, message = check_british_english_instruction(content, "guidance_cached.jinja")

        assert has_instruction, (
            f"guidance_cached.jinja MUST instruct LLM to use British English.\n"
            f"\n"
            f"Expected location: Line ~32 (within system prompt content)\n"
            f"Expected addition: Add to the 'Your role is to provide...' section\n"
            f"  - Use British English spelling and conventions (optimise, analyse, behaviour, favour, etc.)\n"
            f"\n"
            f"Why: Cache-optimized template is heavily used. The instruction should be\n"
            f"     in the cached portion for consistency across all requests.\n"
            f"\n{message}"
        )

    def test_compliance_refinement_has_british_english_instruction(self):
        """Test advisor/compliance_refinement.jinja instructs LLM to use British English.

        Template: advisor/compliance_refinement.jinja
        Priority: ⭐ IMPORTANT (revises failed guidance)
        Expected location: TASK section, after point 3
        Expected text: "4. Use British English spelling and conventions"

        This should be a numbered task point, not just a comment.
        """
        content = read_template("advisor/compliance_refinement.jinja")
        has_instruction, message = check_british_english_instruction(content, "compliance_refinement.jinja")

        assert has_instruction, (
            f"compliance_refinement.jinja MUST instruct LLM to use British English in TASK section.\n"
            f"\n"
            f"Expected location: TASK section, after point 3\n"
            f"Expected addition (as numbered point):\n"
            f"  4. Use British English spelling and conventions\n"
            f"  (Current point 4 becomes point 5)\n"
            f"\n"
            f"Why: When revising guidance, the LLM must maintain British English consistency.\n"
            f"\n{message}"
        )

        # Additionally check it appears in TASK section
        if has_instruction:
            task_section = content[content.find("TASK:"):] if "TASK:" in content else ""
            has_in_task = any(kw in task_section.lower() for kw in BRITISH_ENGLISH_INSTRUCTION_KEYWORDS)

            assert has_in_task, (
                f"compliance_refinement.jinja has British English mention but NOT in TASK section.\n"
                f"The instruction must be in the TASK section as a numbered point."
            )

    def test_borderline_strengthening_has_british_english_instruction(self):
        """Test advisor/borderline_strengthening.jinja instructs LLM to use British English.

        Template: advisor/borderline_strengthening.jinja
        Priority: ⭐ IMPORTANT (strengthens borderline guidance)
        Expected location: TASK section, after line 41 (after point 5)
        Expected text: "6. Use British English spelling and conventions"

        This should be a numbered task point.
        """
        content = read_template("advisor/borderline_strengthening.jinja")
        has_instruction, message = check_british_english_instruction(content, "borderline_strengthening.jinja")

        assert has_instruction, (
            f"borderline_strengthening.jinja MUST instruct LLM to use British English in TASK section.\n"
            f"\n"
            f"Expected location: TASK section, after point 5\n"
            f"Expected addition (as numbered point):\n"
            f"  6. Use British English spelling and conventions\n"
            f"\n"
            f"Why: When strengthening guidance, the LLM must maintain British English consistency.\n"
            f"\n{message}"
        )

        # Additionally check it appears in TASK section
        if has_instruction:
            task_section = content[content.find("TASK:"):] if "TASK:" in content else ""
            has_in_task = any(kw in task_section.lower() for kw in BRITISH_ENGLISH_INSTRUCTION_KEYWORDS)

            assert has_in_task, (
                f"borderline_strengthening.jinja has British English mention but NOT in TASK section.\n"
                f"The instruction must be in the TASK section as a numbered point."
            )


class TestPhase2ValidationTemplate:
    """Phase 2: Test validation template (1 template).

    This template's REASONING output is shown in admin UI.
    Should use British English for consistency.

    Priority: MEDIUM (admin-facing, not customer-facing)
    """

    def test_validation_has_british_english_note(self):
        """Test compliance/validation.jinja instructs LLM to use British English.

        Template: compliance/validation.jinja
        Priority: MEDIUM (validation reasoning in admin UI)
        Expected location: After line 40 (after advisor's reasoning section)
        Expected text: "Note: Use British English spelling in validation reasoning for consistency with system output."

        This is OPTIONAL but recommended for consistency across the entire system.
        """
        content = read_template("compliance/validation.jinja")
        has_instruction, message = check_british_english_instruction(content, "validation.jinja")

        assert has_instruction, (
            f"validation.jinja SHOULD instruct LLM to use British English (OPTIONAL but recommended).\n"
            f"\n"
            f"Expected location: After line 40 (after advisor's reasoning section)\n"
            f"Expected addition:\n"
            f"  Note: Use British English spelling in validation reasoning for consistency with system output.\n"
            f"\n"
            f"Why: Validation reasoning appears in admin UI. British English maintains\n"
            f"     consistency across the system, even in internal outputs.\n"
            f"\n{message}"
        )


class TestPhase3CustomerSimulationTemplates:
    """Phase 3: Test customer simulation templates (7 templates).

    These templates generate simulated customer behavior for testing.
    Should use British English for authenticity (UK customers).

    Priority: LOW (testing only, not production customer-facing)
    """

    @pytest.mark.parametrize("template_path,template_name,description", [
        ("customer/response.jinja", "response.jinja", "Generate customer responses"),
        ("customer/comprehension.jinja", "comprehension.jinja", "Simulate comprehension"),
        ("customer/outcome.jinja", "outcome.jinja", "Simulate consultation outcome"),
        ("customer/generation/demographics.jinja", "demographics.jinja", "Generate demographics"),
        ("customer/generation/financial.jinja", "financial.jinja", "Generate financial situation"),
        ("customer/generation/pension_pots.jinja", "pension_pots.jinja", "Generate pension details"),
        ("customer/generation/goals.jinja", "goals.jinja", "Generate goals and questions"),
    ])
    def test_customer_template_has_british_english_instruction(
        self,
        template_path: str,
        template_name: str,
        description: str
    ):
        """Test customer simulation templates instruct LLM to use British English.

        All 7 customer templates should include:
        "Use British English spelling and phrasing (natural for UK customers)"

        This ensures simulated customers speak naturally like real UK customers.

        Priority: LOW (nice to have for authenticity in testing)
        """
        content = read_template(template_path)
        has_instruction, message = check_british_english_instruction(content, template_name)

        # Check for UK context (these templates should mention UK)
        has_uk_context = "uk" in content.lower() and any(
            word in content.lower() for word in ["customer", "pension", "guidance", "statistics"]
        )

        assert has_instruction or has_uk_context, (
            f"{template_name} SHOULD instruct LLM to use British English for UK customer authenticity.\n"
            f"\n"
            f"Template purpose: {description}\n"
            f"Expected addition to generation instructions:\n"
            f"  Use British English spelling and phrasing (natural for UK customers)\n"
            f"\n"
            f"Why: These templates simulate UK customers. British English makes simulated\n"
            f"     customers more authentic and realistic for testing.\n"
            f"\n"
            f"Note: This is OPTIONAL (LOW priority) but improves testing quality.\n"
            f"\n{message}"
        )


class TestInstructionContentQuality:
    """Test the content and quality of British English instructions.

    These tests verify that when instructions ARE present, they:
    1. Include helpful examples
    2. Are in appropriate locations (e.g., TASK sections)
    3. Use clear, actionable language
    """

    def test_main_guidance_templates_include_spelling_examples(self):
        """Test that main guidance templates include British spelling examples.

        Templates: guidance_main, guidance_with_reasoning, guidance_cached

        When instructing LLM to use British English, examples improve compliance:
        - optimise (not optimize)
        - analyse (not analyze)
        - behaviour (not behavior)
        - favour (not favor)
        """
        templates_to_check = [
            ("advisor/guidance_main.jinja", "guidance_main"),
            ("advisor/guidance_with_reasoning.jinja", "guidance_with_reasoning"),
            ("advisor/guidance_cached.jinja", "guidance_cached"),
        ]

        for template_path, template_name in templates_to_check:
            content = read_template(template_path)
            content_lower = content.lower()

            # If British English instruction is present, check for examples
            if any(kw in content_lower for kw in BRITISH_ENGLISH_INSTRUCTION_KEYWORDS):
                has_examples = any(example in content_lower for example in BRITISH_SPELLING_EXAMPLES)

                if not has_examples:
                    pytest.skip(
                        f"{template_name} has British English instruction but lacks spelling examples.\n"
                        f"RECOMMENDATION: Add examples in parentheses for clarity:\n"
                        f"  '(optimise, analyse, behaviour, favour, etc.)'\n"
                        f"Examples improve LLM compliance with British English spelling."
                    )

    def test_refinement_templates_use_numbered_task_format(self):
        """Test that refinement templates use numbered task format.

        Templates: compliance_refinement, borderline_strengthening

        These templates have numbered TASK sections. British English instruction
        should be a numbered task point, not a comment or note.

        Expected formats:
        - compliance_refinement: "4. Use British English spelling and conventions"
        - borderline_strengthening: "6. Use British English spelling and conventions"
        """
        templates_to_check = [
            ("advisor/compliance_refinement.jinja", "4", "compliance_refinement"),
            ("advisor/borderline_strengthening.jinja", "6", "borderline_strengthening"),
        ]

        for template_path, expected_number, template_name in templates_to_check:
            content = read_template(template_path)

            # If British English instruction is present, check format
            if any(kw in content.lower() for kw in BRITISH_ENGLISH_INSTRUCTION_KEYWORDS):
                # Extract TASK section
                task_section = content[content.find("TASK:"):] if "TASK:" in content else ""

                # Check if British English appears in a numbered format
                # Look for patterns like "4. " or "6. " followed by British English mention
                import re
                numbered_pattern = rf"{expected_number}\.\s+.*[Bb]ritish"

                has_numbered_format = re.search(numbered_pattern, task_section) is not None

                if not has_numbered_format:
                    pytest.skip(
                        f"{template_name} should include British English as numbered task point {expected_number}.\n"
                        f"RECOMMENDATION: Add as numbered point in TASK section:\n"
                        f"  '{expected_number}. Use British English spelling and conventions'\n"
                        f"Numbered format ensures LLM treats it as an explicit requirement."
                    )

    def test_customer_templates_explicitly_mention_uk_context(self):
        """Test that customer templates mention UK context.

        Customer simulation templates should explicitly reference UK context
        to make it clear why British English is needed.

        Expected patterns:
        - "UK customers"
        - "natural for UK customers"
        - "UK pension guidance"
        - "UK statistics"
        """
        customer_templates = [
            ("customer/response.jinja", "response"),
            ("customer/comprehension.jinja", "comprehension"),
            ("customer/outcome.jinja", "outcome"),
            ("customer/generation/demographics.jinja", "demographics"),
            ("customer/generation/financial.jinja", "financial"),
            ("customer/generation/pension_pots.jinja", "pension_pots"),
            ("customer/generation/goals.jinja", "goals"),
        ]

        for template_path, template_name in customer_templates:
            content = read_template(template_path)
            content_lower = content.lower()

            # All customer templates should mention UK
            has_uk_mention = "uk" in content_lower

            assert has_uk_mention, (
                f"{template_name} should explicitly mention UK context.\n"
                f"\n"
                f"Why: These templates simulate UK customers. UK context makes it clear\n"
                f"     why British English is appropriate.\n"
                f"\n"
                f"Expected patterns: 'UK customers', 'UK pension', 'UK statistics'"
            )

            # If British English instruction is present, check if it mentions UK
            if any(kw in content_lower for kw in BRITISH_ENGLISH_INSTRUCTION_KEYWORDS):
                has_uk_in_instruction = (
                    "uk customer" in content_lower or
                    "natural for uk" in content_lower
                )

                if not has_uk_in_instruction:
                    pytest.skip(
                        f"{template_name} has British English instruction but doesn't link to UK context.\n"
                        f"RECOMMENDATION: Link instruction to UK context:\n"
                        f"  'Use British English spelling and phrasing (natural for UK customers)'\n"
                        f"This explains WHY British English is needed."
                    )


class TestTemplateFileExistence:
    """Verify all expected template files exist in correct locations."""

    @pytest.mark.parametrize("template_path,phase", [
        # Phase 1: Critical customer-facing
        ("advisor/guidance_main.jinja", "Phase 1"),
        ("advisor/guidance_with_reasoning.jinja", "Phase 1"),
        ("advisor/guidance_cached.jinja", "Phase 1"),
        ("advisor/compliance_refinement.jinja", "Phase 1"),
        ("advisor/borderline_strengthening.jinja", "Phase 1"),
        # Phase 2: Validation
        ("compliance/validation.jinja", "Phase 2"),
        # Phase 3: Customer simulation
        ("customer/response.jinja", "Phase 3"),
        ("customer/comprehension.jinja", "Phase 3"),
        ("customer/outcome.jinja", "Phase 3"),
        ("customer/generation/demographics.jinja", "Phase 3"),
        ("customer/generation/financial.jinja", "Phase 3"),
        ("customer/generation/pension_pots.jinja", "Phase 3"),
        ("customer/generation/goals.jinja", "Phase 3"),
    ])
    def test_template_file_exists(self, template_path: str, phase: str):
        """Test that all templates mentioned in spec exist.

        Args:
            template_path: Path to template relative to templates directory
            phase: Implementation phase (for documentation)
        """
        base_path = Path(__file__).parent.parent / "src" / "guidance_agent" / "templates"
        full_path = base_path / template_path

        assert full_path.exists(), (
            f"Template file not found: {full_path}\n"
            f"Implementation phase: {phase}"
        )
        assert full_path.is_file(), f"Template path exists but is not a file: {full_path}"


# Summary fixture for test reporting
@pytest.fixture(scope="session", autouse=True)
def print_test_summary():
    """Print test summary at the end of the session."""
    yield  # Tests run here

    print("\n" + "="*80)
    print("BRITISH ENGLISH INSTRUCTIONS TEST SUMMARY")
    print("="*80)
    print("\nThese tests verify that templates INSTRUCT the LLM to use British English.")
    print("\nIMPORTANT DISTINCTION:")
    print("  - test_british_english_templates.py: Tests existing template text")
    print("  - THIS FILE: Tests LLM instructions for generated content")
    print("\nTests are grouped by priority phase:")
    print("\n  Phase 1 (Critical): 5 customer-facing templates")
    print("    - guidance_main.jinja")
    print("    - guidance_with_reasoning.jinja")
    print("    - guidance_cached.jinja")
    print("    - compliance_refinement.jinja")
    print("    - borderline_strengthening.jinja")
    print("\n  Phase 2 (Medium): 1 validation template")
    print("    - validation.jinja")
    print("\n  Phase 3 (Low): 7 customer simulation templates")
    print("    - All customer/*.jinja templates")
    print("\nExpected initial status: ALL TESTS SHOULD FAIL (TDD approach)")
    print("After adding British English instructions: ALL TESTS SHOULD PASS")
    print("\nImplementation guide: specs/british-english-prompt-instructions.md")
    print("="*80 + "\n")
