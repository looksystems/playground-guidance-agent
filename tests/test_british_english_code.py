"""TDD tests for British English spelling in Python code.

This test suite verifies that Python code uses British English spelling conventions
as documented in specs/british-english-conversational-improvements.md.

These tests will FAIL initially (since code still uses American English) and should
pass after implementing the fixes.

British English conventions tested:
- Function names: summarise_* (not summarize_*)
- Function names: analyse_* (not analyze_*)
- Docstrings: -ise, -our, -ed endings
- String literals: British spelling
- Module exports: British function names

Files tested:
1. src/guidance_agent/customer/agent.py
2. src/guidance_agent/advisor/prompts.py
3. src/guidance_agent/learning/case_learning.py
4. src/guidance_agent/learning/__init__.py
5. src/guidance_agent/learning/reflection.py
6. src/guidance_agent/evaluation/__init__.py
7. src/guidance_agent/evaluation/judge_validation.py
8. src/guidance_agent/api/routers/admin.py
9. src/guidance_agent/knowledge/pension_knowledge.py
"""

import ast
import inspect
import pytest


class TestBritishEnglishInCustomerAgent:
    """Test customer/agent.py uses British English in docstrings."""

    def test_customer_agent_docstrings_use_behaviour(self):
        """Test customer agent uses 'behaviour' not 'behavior' in docstrings.

        Line 1: module docstring "behavior" → "behaviour"
        Line 17: class docstring "behavior" → "behaviour"

        This test will FAIL initially until the code is updated.
        """
        from guidance_agent.customer import agent

        # Check module docstring
        module_doc = agent.__doc__ or ""
        assert "behaviour" in module_doc.lower(), (
            "Module docstring should use British spelling 'behaviour'"
        )
        assert "behavior" not in module_doc.lower(), (
            "Module docstring should NOT use American spelling 'behavior'"
        )

        # Check CustomerAgent class docstring
        class_doc = agent.CustomerAgent.__doc__ or ""
        assert "behaviour" in class_doc.lower(), (
            "CustomerAgent class docstring should use British spelling 'behaviour'"
        )
        assert "behavior" not in class_doc.lower(), (
            "CustomerAgent class docstring should NOT use American spelling 'behavior'"
        )


class TestBritishEnglishInAdvisorPrompts:
    """Test advisor/prompts.py uses British English in string literals."""

    def test_advisor_prompts_use_optimised_and_maximise(self):
        """Test advisor prompts use 'optimised' and 'maximise' not American spellings.

        Line 188: "optimized" → "optimised"
        Line 190: "maximize" → "maximise"

        This test will FAIL initially until the code is updated.
        """
        from guidance_agent.advisor import prompts

        # Read the source file
        source_file = inspect.getsourcefile(prompts)
        with open(source_file, "r") as f:
            source_code = f.read()

        # Check for British spellings
        assert "optimised" in source_code.lower(), (
            "advisor/prompts.py should use British spelling 'optimised'"
        )
        assert "maximise" in source_code.lower(), (
            "advisor/prompts.py should use British spelling 'maximise'"
        )

        # Ensure American spellings are NOT present
        # (excluding comments about the change itself)
        lines = source_code.split("\n")
        for i, line in enumerate(lines, 1):
            # Skip comment lines
            if line.strip().startswith("#"):
                continue
            # Skip docstrings (triple quotes)
            if '"""' in line or "'''" in line:
                continue

            if "optimized" in line.lower():
                pytest.fail(
                    f"Line {i} in advisor/prompts.py uses American spelling 'optimized': {line}"
                )
            if "maximize" in line.lower():
                pytest.fail(
                    f"Line {i} in advisor/prompts.py uses American spelling 'maximize': {line}"
                )


class TestBritishEnglishInCaseLearning:
    """Test learning/case_learning.py uses British function names and docstrings."""

    def test_function_renamed_to_summarise_customer_situation(self):
        """Test function name changed from summarize_* to summarise_*.

        Line 76: Function name `summarize_customer_situation` → `summarise_customer_situation`

        This test will FAIL initially until the function is renamed.
        """
        from guidance_agent.learning import case_learning

        # Check function exists with British spelling
        assert hasattr(case_learning, "summarise_customer_situation"), (
            "case_learning module should have function 'summarise_customer_situation'"
        )

        # Check old American spelling does NOT exist
        assert not hasattr(case_learning, "summarize_customer_situation"), (
            "case_learning module should NOT have function 'summarize_customer_situation' "
            "(should be renamed to British spelling)"
        )

    def test_summarise_function_docstring_uses_british_spelling(self):
        """Test summarise_customer_situation docstring uses British spelling.

        Line 83: Parameter docstring "summarize" → "summarise"
        Line 89: Example docstring "summarize" → "summarise"

        This test will FAIL initially until docstrings are updated.
        """
        from guidance_agent.learning import case_learning

        func = case_learning.summarise_customer_situation
        docstring = func.__doc__ or ""

        assert "summarise" in docstring.lower(), (
            "Function docstring should use British spelling 'summarise'"
        )
        assert "summarize" not in docstring.lower(), (
            "Function docstring should NOT use American spelling 'summarize'"
        )

    def test_extract_case_calls_summarise_function(self):
        """Test extract_case_from_consultation calls summarise_* function.

        Line 167: Function call `summarize_customer_situation` → `summarise_customer_situation`

        This test will FAIL initially until function call is updated.
        """
        from guidance_agent.learning import case_learning
        import inspect

        # Get source code of extract_case_from_consultation
        source = inspect.getsource(case_learning.extract_case_from_consultation)

        assert "summarise_customer_situation" in source, (
            "extract_case_from_consultation should call 'summarise_customer_situation' "
            "(with British spelling)"
        )
        assert "summarize_customer_situation" not in source, (
            "extract_case_from_consultation should NOT call 'summarize_customer_situation' "
            "(should use British spelling)"
        )


class TestBritishEnglishInLearningInit:
    """Test learning/__init__.py exports British-spelled function names."""

    def test_learning_init_imports_summarise_function(self):
        """Test learning/__init__.py imports and exports summarise_* function.

        Line 14: Import `summarize_customer_situation` → `summarise_customer_situation`
        Line 36: __all__ entry "summarize_customer_situation" → "summarise_customer_situation"

        This test will FAIL initially until imports are updated.
        """
        from guidance_agent import learning
        import inspect

        # Check function is exported with British spelling
        assert hasattr(learning, "summarise_customer_situation"), (
            "learning module should export 'summarise_customer_situation'"
        )

        # Check it's in __all__ if __all__ exists
        if hasattr(learning, "__all__"):
            assert "summarise_customer_situation" in learning.__all__, (
                "learning.__all__ should include 'summarise_customer_situation'"
            )
            assert "summarize_customer_situation" not in learning.__all__, (
                "learning.__all__ should NOT include 'summarize_customer_situation'"
            )

        # Check source code uses British import
        source_file = inspect.getsourcefile(learning)
        with open(source_file, "r") as f:
            source = f.read()

        assert "summarise_customer_situation" in source, (
            "learning/__init__.py should import 'summarise_customer_situation'"
        )


class TestBritishEnglishInReflection:
    """Test learning/reflection.py uses British spelling in strings."""

    def test_reflection_uses_analyse_not_analyze(self):
        """Test reflection module uses 'analyse' not 'analyze'.

        Line 28: "analyze" → "analyse"

        This test will FAIL initially until the code is updated.
        """
        from guidance_agent.learning import reflection
        import inspect

        source_file = inspect.getsourcefile(reflection)
        with open(source_file, "r") as f:
            source = f.read()

        # Check for British spelling in non-comment lines
        lines = source.split("\n")
        found_analyse = False
        for i, line in enumerate(lines, 1):
            if line.strip().startswith("#"):
                continue
            if "analyse" in line.lower():
                found_analyse = True
            if "analyze" in line.lower() and not line.strip().startswith("#"):
                pytest.fail(
                    f"Line {i} in learning/reflection.py uses American spelling 'analyze': {line}"
                )

        assert found_analyse or "analyze" not in source.lower(), (
            "learning/reflection.py should use British spelling 'analyse'"
        )


class TestBritishEnglishInEvaluationInit:
    """Test evaluation/__init__.py exports British-spelled function names."""

    def test_evaluation_init_imports_analyse_function(self):
        """Test evaluation/__init__.py imports and exports analyse_* function.

        Line 26: Import `analyze_confidence_calibration` → `analyse_confidence_calibration`
        Line 46: __all__ entry "analyze_confidence_calibration" → "analyse_confidence_calibration"

        This test will FAIL initially until imports are updated.
        """
        from guidance_agent import evaluation
        import inspect

        # Check function is exported with British spelling
        assert hasattr(evaluation, "analyse_confidence_calibration"), (
            "evaluation module should export 'analyse_confidence_calibration'"
        )

        # Check it's in __all__ if __all__ exists
        if hasattr(evaluation, "__all__"):
            assert "analyse_confidence_calibration" in evaluation.__all__, (
                "evaluation.__all__ should include 'analyse_confidence_calibration'"
            )
            assert "analyze_confidence_calibration" not in evaluation.__all__, (
                "evaluation.__all__ should NOT include 'analyze_confidence_calibration'"
            )

        # Check source code uses British import
        source_file = inspect.getsourcefile(evaluation)
        with open(source_file, "r") as f:
            source = f.read()

        assert "analyse_confidence_calibration" in source, (
            "evaluation/__init__.py should import 'analyse_confidence_calibration'"
        )


class TestBritishEnglishInJudgeValidation:
    """Test evaluation/judge_validation.py uses British function names and docstrings."""

    def test_function_renamed_to_analyse_confidence_calibration(self):
        """Test function name changed from analyze_* to analyse_*.

        Line 265: Function name `analyze_confidence_calibration` → `analyse_confidence_calibration`

        This test will FAIL initially until the function is renamed.
        """
        from guidance_agent.evaluation import judge_validation

        # Check function exists with British spelling
        assert hasattr(judge_validation, "analyse_confidence_calibration"), (
            "judge_validation module should have function 'analyse_confidence_calibration'"
        )

        # Check old American spelling does NOT exist
        assert not hasattr(judge_validation, "analyze_confidence_calibration"), (
            "judge_validation module should NOT have function 'analyze_confidence_calibration' "
            "(should be renamed to British spelling)"
        )

    def test_analyse_function_docstring_uses_british_spelling(self):
        """Test analyse_confidence_calibration docstring uses British spelling.

        Line 286: Example docstring "analyze" → "analyse"

        This test will FAIL initially until docstrings are updated.
        """
        from guidance_agent.evaluation import judge_validation

        func = judge_validation.analyse_confidence_calibration
        docstring = func.__doc__ or ""

        assert "analyse" in docstring.lower(), (
            "Function docstring should use British spelling 'analyse'"
        )
        assert "analyze" not in docstring.lower(), (
            "Function docstring should NOT use American spelling 'analyze'"
        )

    def test_judge_validation_calls_analyse_function(self):
        """Test internal calls use analyse_* function name.

        Line 393: Function call `analyze_confidence_calibration` → `analyse_confidence_calibration`

        This test will FAIL initially until function calls are updated.
        """
        from guidance_agent.evaluation import judge_validation
        import inspect

        # Get full source of the module
        source = inspect.getsource(judge_validation)

        # Check that analyse_* is called (not analyze_*)
        assert "analyse_confidence_calibration(" in source, (
            "judge_validation module should call 'analyse_confidence_calibration' "
            "(with British spelling)"
        )

        # Count occurrences - there might be the function definition itself
        # We're looking for calls to it, not just the definition
        lines = source.split("\n")
        call_lines = [
            line for line in lines
            if "analyse_confidence_calibration(" in line
            and not line.strip().startswith("def ")
        ]

        assert len(call_lines) > 0, (
            "Should have at least one call to 'analyse_confidence_calibration'"
        )


class TestBritishEnglishInAdminRouter:
    """Test api/routers/admin.py uses British spelling in descriptions."""

    def test_admin_router_descriptions_use_analyse(self):
        """Test admin router endpoint descriptions use 'analyse' not 'analyze'.

        Line 258: Description "analyze" → "analyse"
        Line 409: Description "analyze" → "analyse"
        Line 486: Description "analyze" → "analyse"

        This test will FAIL initially until descriptions are updated.
        """
        from guidance_agent.api.routers import admin
        import inspect

        source_file = inspect.getsourcefile(admin)
        with open(source_file, "r") as f:
            source = f.read()

        # Find all occurrences of "analyse" and "analyze"
        lines = source.split("\n")
        analyse_count = sum(1 for line in lines if "analyse" in line.lower())

        # Check specific lines mentioned in spec (approximate, since line numbers may shift)
        # Look for description strings that should use British spelling
        found_descriptions = []
        for i, line in enumerate(lines, 1):
            if 'description=' in line or 'summary=' in line:
                if "analyze" in line.lower():
                    found_descriptions.append((i, line))

        assert len(found_descriptions) == 0, (
            f"Found {len(found_descriptions)} endpoint descriptions with American spelling 'analyze':\n" +
            "\n".join(f"Line {i}: {line.strip()}" for i, line in found_descriptions)
        )

        # Should have at least some British spellings in descriptions
        description_lines = [line for line in lines if 'description=' in line or 'summary=' in line]
        has_british = any("analyse" in line.lower() for line in description_lines)

        if description_lines:  # Only assert if there are description lines
            assert has_british, (
                "API endpoint descriptions should use British spelling 'analyse'"
            )


class TestBritishEnglishInPensionKnowledge:
    """Test knowledge/pension_knowledge.py uses British spelling."""

    def test_pension_knowledge_uses_maximise_income(self):
        """Test pension knowledge uses 'maximise_income' not 'maximize_income'.

        Line 198: "maximize_income" → "maximise_income"

        This test will FAIL initially until the code is updated.
        """
        from guidance_agent.knowledge import pension_knowledge
        import inspect

        source_file = inspect.getsourcefile(pension_knowledge)
        with open(source_file, "r") as f:
            source = f.read()

        assert "maximise_income" in source.lower(), (
            "pension_knowledge.py should use British spelling 'maximise_income'"
        )
        assert "maximize_income" not in source.lower(), (
            "pension_knowledge.py should NOT use American spelling 'maximize_income'"
        )

    def test_pension_knowledge_uses_favoured(self):
        """Test pension knowledge uses 'favoured' not 'favored'.

        Line 212: "favored" → "favoured"

        This test will FAIL initially until the code is updated.
        """
        from guidance_agent.knowledge import pension_knowledge
        import inspect

        source_file = inspect.getsourcefile(pension_knowledge)
        with open(source_file, "r") as f:
            source = f.read()

        assert "favoured" in source.lower(), (
            "pension_knowledge.py should use British spelling 'favoured'"
        )
        assert "favored" not in source.lower(), (
            "pension_knowledge.py should NOT use American spelling 'favored'"
        )


class TestBritishEnglishInAdvisorAgent:
    """Test advisor/agent.py uses British spelling in strings."""

    def test_advisor_agent_uses_optimise_and_maximise(self):
        """Test advisor agent uses 'optimise' and 'maximise' not American spellings.

        Line 796: "optimize" → "optimise"
        Line 797: "maximize" → "maximise"

        This test will FAIL initially until the code is updated.
        """
        from guidance_agent.advisor import agent
        import inspect

        source_file = inspect.getsourcefile(agent)
        with open(source_file, "r") as f:
            source = f.read()

        # Check around lines 796-797 (approximate)
        lines = source.split("\n")
        target_lines = lines[790:805] if len(lines) > 805 else lines[790:]
        target_section = "\n".join(target_lines)

        assert "optimise" in target_section.lower() or "maximise" in target_section.lower(), (
            "advisor/agent.py around lines 796-797 should use British spellings 'optimise' and 'maximise'"
        )

        # Check for American spellings in the same section
        for i, line in enumerate(target_lines, 791):
            if "optimize" in line.lower() and not line.strip().startswith("#"):
                pytest.fail(f"Line {i} uses American spelling 'optimize': {line}")
            if "maximize" in line.lower() and not line.strip().startswith("#"):
                pytest.fail(f"Line {i} uses American spelling 'maximize': {line}")


class TestComprehensiveBritishEnglish:
    """Comprehensive tests across all Python files."""

    def test_no_american_spelling_in_function_names(self):
        """Test that no functions use American spelling conventions.

        Checks all modules for functions like summarize_*, analyze_*, etc.
        They should use British spellings: summarise_*, analyse_*, etc.
        """
        import guidance_agent.learning.case_learning as case_learning
        import guidance_agent.evaluation.judge_validation as judge_validation

        # Check case_learning module
        functions = [name for name in dir(case_learning) if callable(getattr(case_learning, name))]
        american_functions = [f for f in functions if f.startswith("summarize_") or f.startswith("analyze_")]

        assert len(american_functions) == 0, (
            f"Found functions with American spelling in case_learning: {american_functions}"
        )

        # Check judge_validation module
        functions = [name for name in dir(judge_validation) if callable(getattr(judge_validation, name))]
        american_functions = [f for f in functions if f.startswith("analyze_")]

        assert len(american_functions) == 0, (
            f"Found functions with American spelling in judge_validation: {american_functions}"
        )

    def test_british_functions_are_callable(self):
        """Test that British-spelled functions exist and are callable.

        This is a positive test to complement the negative tests above.
        """
        from guidance_agent.learning import case_learning
        from guidance_agent.evaluation import judge_validation

        # Test British-spelled functions exist
        assert hasattr(case_learning, "summarise_customer_situation"), (
            "case_learning should have 'summarise_customer_situation' function"
        )
        assert callable(case_learning.summarise_customer_situation), (
            "'summarise_customer_situation' should be callable"
        )

        assert hasattr(judge_validation, "analyse_confidence_calibration"), (
            "judge_validation should have 'analyse_confidence_calibration' function"
        )
        assert callable(judge_validation.analyse_confidence_calibration), (
            "'analyse_confidence_calibration' should be callable"
        )

    def test_all_code_avoids_american_spelling_patterns(self):
        """Scan key modules for common American spelling patterns.

        This is a meta-test to catch any American spellings we might have missed.
        """
        import guidance_agent.customer.agent
        import guidance_agent.advisor.prompts
        import guidance_agent.advisor.agent
        import inspect

        modules_to_check = [
            (guidance_agent.customer.agent, "customer/agent.py"),
            (guidance_agent.advisor.prompts, "advisor/prompts.py"),
            (guidance_agent.advisor.agent, "advisor/agent.py"),
        ]

        american_patterns = [
            "behavior", "optimize", "analyze", "maximize", "favor",
            "optimized", "analyzed", "maximized", "favored",
            "optimizes", "analyzes", "maximizes", "favors",
        ]

        for module, module_name in modules_to_check:
            source_file = inspect.getsourcefile(module)
            with open(source_file, "r") as f:
                source = f.read()

            # Skip comment lines
            lines = source.split("\n")
            for i, line in enumerate(lines, 1):
                if line.strip().startswith("#"):
                    continue

                line_lower = line.lower()
                for pattern in american_patterns:
                    if pattern in line_lower:
                        # Allow if it's in a string that explains the change
                        if "american" in line_lower or "spelling" in line_lower:
                            continue
                        pytest.fail(
                            f"{module_name} line {i} contains American spelling '{pattern}': {line.strip()}"
                        )
