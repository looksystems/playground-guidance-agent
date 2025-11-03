"""Jinja2 template engine for prompt management."""

from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader, select_autoescape


class TemplateEngine:
    """Manages Jinja2 templates for prompts."""

    def __init__(self, template_dir: Path | None = None):
        """Initialize the template engine.

        Args:
            template_dir: Directory containing templates.
                         Defaults to src/guidance_agent/templates/
        """
        if template_dir is None:
            template_dir = Path(__file__).parent.parent / "templates"

        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=False,  # Prompts are not HTML, disable autoescape
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Register custom filters
        self._register_filters()

    def _register_filters(self):
        """Register custom Jinja filters from helper functions."""
        from guidance_agent.advisor.prompts import (
            format_customer_profile,
            format_conversation,
            format_cases,
            format_rules,
            format_memories,
        )

        self.env.filters['customer_profile'] = format_customer_profile
        self.env.filters['conversation'] = format_conversation
        self.env.filters['cases'] = format_cases
        self.env.filters['rules'] = format_rules
        self.env.filters['memories'] = format_memories

    def render(self, template_name: str, **context: Any) -> str:
        """Render a template with the given context.

        Args:
            template_name: Name of template file (e.g., 'advisor/guidance_main.jinja')
            **context: Template variables

        Returns:
            Rendered template string
        """
        template = self.env.get_template(template_name)
        return template.render(**context)

    def render_messages(self, template_name: str, **context: Any) -> list[dict]:
        """Render a template that returns a message array.

        Used for cache-optimized prompts that return message structures.

        Args:
            template_name: Name of template file
            **context: Template variables

        Returns:
            List of message dicts
        """
        import json
        template = self.env.get_template(template_name)
        rendered = template.render(**context)
        return json.loads(rendered)


# Global template engine instance
_engine = None

def get_template_engine() -> TemplateEngine:
    """Get the global template engine instance."""
    global _engine
    if _engine is None:
        _engine = TemplateEngine()
    return _engine


def render_template(template_name: str, **context: Any) -> str:
    """Convenience function to render a template.

    Args:
        template_name: Name of template file
        **context: Template variables

    Returns:
        Rendered template string
    """
    return get_template_engine().render(template_name, **context)
