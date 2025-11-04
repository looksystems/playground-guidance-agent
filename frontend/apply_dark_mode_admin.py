#!/usr/bin/env python3
"""
Apply dark mode styling to all admin pages systematically.
This script adds dark mode Tailwind classes following the pattern from the spec.
"""

import re
import os
from pathlib import Path

# Base path to admin pages
ADMIN_PAGES_PATH = Path("/Users/adrian/Work/guidance-agent/frontend/app/pages/admin")

# Common dark mode replacement patterns
PATTERNS = [
    # Headers and titles
    (r'class="([^"]*?)text-gray-900([^"]*?)"', r'class="\1text-gray-900 dark:text-gray-100\2"'),
    (r'class="([^"]*?)text-gray-800([^"]*?)"', r'class="\1text-gray-800 dark:text-gray-100\2"'),

    # Body text
    (r'class="([^"]*?)text-gray-700([^"]*?)"', r'class="\1text-gray-700 dark:text-gray-300\2"'),
    (r'class="([^"]*?)text-gray-600([^"]*?)"', r'class="\1text-gray-600 dark:text-gray-400\2"'),

    # Backgrounds
    (r'class="([^"]*?)bg-gray-50([^"]*?)"', r'class="\1bg-gray-50 dark:bg-gray-800\2"'),
    (r'class="([^"]*?)bg-gray-100([^"]*?)"', r'class="\1bg-gray-100 dark:bg-gray-800\2"'),
    (r'class="([^"]*?)bg-white([^"]*?)"', r'class="\1bg-white dark:bg-gray-900\2"'),

    # Borders and dividers
    (r'class="([^"]*?)border-gray-200([^"]*?)"', r'class="\1border-gray-200 dark:border-gray-700\2"'),
    (r'class="([^"]*?)border-gray-300([^"]*?)"', r'class="\1border-gray-300 dark:border-gray-600\2"'),
    (r'class="([^"]*?)divide-gray-200([^"]*?)"', r'class="\1divide-gray-200 dark:divide-gray-700\2"'),

    # Hover states
    (r'class="([^"]*?)hover:bg-gray-50([^"]*?)"', r'class="\1hover:bg-gray-50 dark:hover:bg-gray-800\2"'),

    # Icon/status colors
    (r'class="([^"]*?)text-green-600([^"]*?)"', r'class="\1text-green-600 dark:text-green-400\2"'),
    (r'class="([^"]*?)text-blue-600([^"]*?)"', r'class="\1text-blue-600 dark:text-blue-400\2"'),
    (r'class="([^"]*?)text-red-600([^"]*?)"', r'class="\1text-red-600 dark:text-red-400\2"'),
    (r'class="([^"]*?)text-yellow-600([^"]*?)"', r'class="\1text-yellow-600 dark:text-yellow-400\2"'),
    (r'class="([^"]*?)text-purple-600([^"]*?)"', r'class="\1text-purple-600 dark:text-purple-400\2"'),
    (r'class="([^"]*?)text-indigo-600([^"]*?)"', r'class="\1text-indigo-600 dark:text-indigo-400\2"'),
    (r'class="([^"]*?)text-teal-600([^"]*?)"', r'class="\1text-teal-600 dark:text-teal-400\2"'),

    # Accent backgrounds
    (r'class="([^"]*?)bg-blue-50([^"]*?)"', r'class="\1bg-blue-50 dark:bg-blue-900/20\2"'),
    (r'class="([^"]*?)bg-green-50([^"]*?)"', r'class="\1bg-green-50 dark:bg-green-900/20\2"'),
    (r'class="([^"]*?)bg-red-50([^"]*?)"', r'class="\1bg-red-50 dark:bg-red-900/20\2"'),
    (r'class="([^"]*?)bg-yellow-50([^"]*?)"', r'class="\1bg-yellow-50 dark:bg-yellow-900/20\2"'),
    (r'class="([^"]*?)bg-purple-50([^"]*?)"', r'class="\1bg-purple-50 dark:bg-purple-900/20\2"'),
    (r'class="([^"]*?)bg-indigo-50([^"]*?)"', r'class="\1bg-indigo-50 dark:bg-indigo-900/20\2"'),
    (r'class="([^"]*?)bg-teal-50([^"]*?)"', r'class="\1bg-teal-50 dark:bg-teal-900/20\2"'),

    # Border colors for accents
    (r'class="([^"]*?)border-blue-200([^"]*?)"', r'class="\1border-blue-200 dark:border-blue-800\2"'),
    (r'class="([^"]*?)border-green-200([^"]*?)"', r'class="\1border-green-200 dark:border-green-800\2"'),
    (r'class="([^"]*?)border-red-200([^"]*?)"', r'class="\1border-red-200 dark:border-red-800\2"'),
    (r'class="([^"]*?)border-yellow-200([^"]*?)"', r'class="\1border-yellow-200 dark:border-yellow-800\2"'),

    # Additional text colors
    (r'class="([^"]*?)text-red-800([^"]*?)"', r'class="\1text-red-800 dark:text-red-400\2"'),
    (r'class="([^"]*?)text-yellow-800([^"]*?)"', r'class="\1text-yellow-800 dark:text-yellow-400\2"'),
    (r'class="([^"]*?)text-green-700([^"]*?)"', r'class="\1text-green-700 dark:text-green-400\2"'),
    (r'class="([^"]*?)text-blue-700([^"]*?)"', r'class="\1text-blue-700 dark:text-blue-400\2"'),
]

# Files to process (already completed: index.vue, metrics.vue, settings.vue)
FILES_TO_PROCESS = [
    "consultations/index.vue",
    "consultations/[id].vue",
    "knowledge/fca/index.vue",
    "knowledge/fca/[id].vue",
    "knowledge/pension/index.vue",
    "knowledge/pension/[id].vue",
    "learning/memories/[id].vue",
    "learning/cases/[id].vue",
    "learning/rules/index.vue",
    "learning/rules/[id].vue",
    "users/customers/index.vue",
    "users/customers/[id].vue",
]

def apply_dark_mode(file_path):
    """Apply dark mode patterns to a single file."""
    print(f"Processing: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Apply each pattern
    for pattern, replacement in PATTERNS:
        # Only apply if dark: not already present in that class
        content = re.sub(pattern, replacement, content)

    # Check if any changes were made
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ Updated {file_path}")
        return True
    else:
        print(f"  - No changes needed for {file_path}")
        return False

def main():
    """Main function to process all admin pages."""
    print("=" * 60)
    print("Applying Dark Mode to Admin Pages")
    print("=" * 60)

    updated_count = 0
    skipped_count = 0

    for rel_path in FILES_TO_PROCESS:
        file_path = ADMIN_PAGES_PATH / rel_path
        if file_path.exists():
            if apply_dark_mode(file_path):
                updated_count += 1
            else:
                skipped_count += 1
        else:
            print(f"  ✗ File not found: {file_path}")

    print("\n" + "=" * 60)
    print(f"Complete! Updated {updated_count} files, skipped {skipped_count} files")
    print("=" * 60)

if __name__ == "__main__":
    main()
