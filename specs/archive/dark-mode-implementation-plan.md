# Dark Mode Implementation & Playwright Review Plan

## Overview

This document outlines the comprehensive plan to implement dark mode across the entire Pension Guidance Service application (both customer and admin sections) and then use Playwright MCP to review, screenshot, and document the implementation quality.

## Current State Analysis

**Frontend Stack:**
- Framework: Nuxt 3 (v3.15.4)
- UI Library: Nuxt UI 3.0 (built on Tailwind CSS)
- Styling: Tailwind CSS with utility classes
- State Management: Pinia
- Type Safety: TypeScript

**Dark Mode Status:**
- ❌ NO dark mode currently implemented
- ❌ No color mode configuration in `nuxt.config.ts`
- ❌ No dark mode toggle component
- ❌ All colors hardcoded for light theme only
- ✅ Using Nuxt UI (has built-in dark mode support)
- ✅ Using Tailwind CSS (supports `dark:` variants)

**Scope:**
- 3 layouts (default, chat, admin)
- 3 customer-facing pages
- 17 admin-facing pages
- ~15 reusable components

## Phase 1: Dark Mode Implementation

### Step 1: Configure Nuxt UI Color Mode

**File:** `frontend/nuxt.config.ts`

**Changes Required:**
```typescript
export default defineNuxtConfig({
  colorMode: {
    preference: 'system', // default to system preference
    fallback: 'light',     // fallback when detection fails
    classSuffix: '',       // no suffix needed for Tailwind
  },
  // ... existing config
})
```

**Expected Outcome:** Enable Nuxt UI's color mode module with system preference detection.

---

### Step 2: Create Dark Mode Toggle Component

**New File:** `frontend/app/components/common/ColorModeToggle.vue`

**Features:**
- Use `useColorMode()` composable from Nuxt UI
- Toggle between light/dark/system modes
- Visual sun/moon icon indicator
- Persist preference to localStorage (handled by Nuxt UI)
- Accessible button with proper ARIA labels

**Implementation Pattern:**
```vue
<template>
  <button @click="toggleColorMode" aria-label="Toggle dark mode">
    <Icon :name="colorMode.value === 'dark' ? 'i-heroicons-moon' : 'i-heroicons-sun'" />
  </button>
</template>

<script setup lang="ts">
const colorMode = useColorMode()

const toggleColorMode = () => {
  colorMode.preference = colorMode.value === 'dark' ? 'light' : 'dark'
}
</script>
```

---

### Step 3: Update Layouts (3 files)

#### 3.1 Customer Default Layout
**File:** `frontend/app/layouts/default.vue`

**Changes:**
- Add `ColorModeToggle` component to header navigation
- Update background: `bg-gray-50` → `bg-gray-50 dark:bg-gray-900`
- Update header: `bg-white` → `bg-white dark:bg-gray-800`
- Update text colors: `text-gray-900` → `text-gray-900 dark:text-gray-100`
- Update borders: `border-gray-200` → `border-gray-200 dark:border-gray-700`

#### 3.2 Chat Layout
**File:** `frontend/app/layouts/chat.vue`

**Changes:**
- Add `ColorModeToggle` component to header
- Update full-height background colors
- Update header/footer sections with dark variants
- Ensure chat container has appropriate dark background

#### 3.3 Admin Layout
**File:** `frontend/app/layouts/admin.vue`

**Changes:**
- Add `ColorModeToggle` component to admin header/sidebar
- Update sidebar: `bg-gray-900` → `bg-gray-900 dark:bg-gray-950`
- Update sidebar text: ensure proper contrast in dark mode
- Update main content area background
- Update navigation active/hover states for dark mode

**Pattern for All Layouts:**
```vue
<!-- Light colors → Dark variants -->
bg-white       → bg-white dark:bg-gray-900
bg-gray-50     → bg-gray-50 dark:bg-gray-800
bg-gray-100    → bg-gray-100 dark:bg-gray-800
text-gray-900  → text-gray-900 dark:text-gray-100
text-gray-600  → text-gray-600 dark:text-gray-400
text-gray-500  → text-gray-500 dark:text-gray-500
border-gray-200 → border-gray-200 dark:border-gray-700
border-gray-300 → border-gray-300 dark:border-gray-600
```

---

### Step 4: Update Customer Pages (3 files)

#### 4.1 Home Page (`/`)
**File:** `frontend/app/pages/index.vue`

**Changes:**
- Update page container background
- Update card backgrounds for profile form section
- Update text colors for headings and descriptions
- Update input field styling (handled by Nuxt UI components)

#### 4.2 History Page (`/history`)
**File:** `frontend/app/pages/history.vue`

**Changes:**
- Update page background
- Update consultation card backgrounds
- Update search/filter bar styling
- Update empty state styling
- Update table/list item borders and hover states

#### 4.3 Live Chat Page (`/consultation/[id]`)
**File:** `frontend/app/pages/consultation/[id].vue`

**Changes:**
- Update chat container background
- Update message bubble backgrounds (user vs AI messages)
- Update input area styling
- Update timestamp and metadata text colors
- Ensure proper contrast for streaming indicators

---

### Step 5: Update Admin Pages (17 files)

#### 5.1 Dashboard & Analytics (3 pages)

**Files:**
- `frontend/app/pages/admin/index.vue` - Dashboard
- `frontend/app/pages/admin/metrics.vue` - Metrics
- `frontend/app/pages/admin/settings.vue` - Settings

**Changes:**
- Update stat card backgrounds and borders
- Update chart backgrounds (requires Chart.js color scheme update)
- Update table backgrounds and row hover states
- Update badge colors for status indicators
- Update form input styling

#### 5.2 Consultations (2 pages)

**Files:**
- `frontend/app/pages/admin/consultations/index.vue` - List
- `frontend/app/pages/admin/consultations/[id].vue` - Detail

**Changes:**
- Update DataTable component styling
- Update filter bar backgrounds
- Update consultation detail cards
- Update message transcript styling
- Update status badges and indicators

#### 5.3 Knowledge Base - FCA (2 pages)

**Files:**
- `frontend/app/pages/admin/knowledge/fca/index.vue` - List
- `frontend/app/pages/admin/knowledge/fca/[id].vue` - Detail

**Changes:**
- Update knowledge article cards
- Update search/filter interface
- Update metadata display (sources, sections)
- Update code block backgrounds (currently hardcoded dark)
- Update vector indicator styling

#### 5.4 Knowledge Base - Pension (2 pages)

**Files:**
- `frontend/app/pages/admin/knowledge/pension/index.vue` - List
- `frontend/app/pages/admin/knowledge/pension/[id].vue` - Detail

**Changes:**
- Same pattern as FCA knowledge pages
- Update article list styling
- Update detail view cards and metadata

#### 5.5 Learning System (4 pages)

**Files:**
- `frontend/app/pages/admin/learning/memories/[id].vue` - Memory detail
- `frontend/app/pages/admin/learning/cases/[id].vue` - Case detail
- `frontend/app/pages/admin/learning/rules/index.vue` - Rules list
- `frontend/app/pages/admin/learning/rules/[id].vue` - Rule detail

**Changes:**
- Update memory/case/rule card styling
- Update JSON/code display areas
- Update metadata sections
- Update related items lists

#### 5.6 User Management (4 pages)

**Files:**
- `frontend/app/pages/admin/users/customers/index.vue` - Customer list
- `frontend/app/pages/admin/users/customers/[id].vue` - Customer detail

**Changes:**
- Update user table styling
- Update user profile cards
- Update consultation history embedded views
- Update action button styling

---

### Step 6: Update Components (~15 files)

#### 6.1 Common Components

**Files:**
- `frontend/app/components/common/LoadingState.vue`
- `frontend/app/components/common/ErrorState.vue`
- `frontend/app/components/common/EmptyState.vue`

**Changes:**
- Update background colors
- Update icon colors
- Update text colors for titles and descriptions
- Update button styling

#### 6.2 Admin Components

**Files:**
- `frontend/app/components/admin/DataTable.vue`
- `frontend/app/components/admin/DetailCard.vue`
- `frontend/app/components/admin/FilterBar.vue`
- `frontend/app/components/admin/LineChart.vue`
- `frontend/app/components/admin/MetadataView.vue`
- `frontend/app/components/admin/VectorIndicator.vue`

**Changes:**
- **DataTable**: Update row backgrounds, borders, hover states, pagination
- **DetailCard**: Update card backgrounds and borders
- **FilterBar**: Update input fields and button backgrounds
- **LineChart**: Update Chart.js color scheme configuration
- **MetadataView**: Fix hardcoded `bg-gray-900` for code blocks (conditional styling)
- **VectorIndicator**: Update badge colors

**Special Case - MetadataView.vue:**
Currently has hardcoded dark background for code blocks:
```vue
<pre class="bg-gray-900 text-gray-100">
```

Should be:
```vue
<pre class="bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-gray-100">
```

#### 6.3 Chat Components

**Files:**
- `frontend/app/components/chat/AIChat.vue`

**Changes:**
- Update message container backgrounds
- Update user vs AI message bubble styling
- Update input area backgrounds
- Update typing indicator colors
- Update metadata/timestamp colors

#### 6.4 Form Components

**Files:**
- `frontend/app/components/forms/CustomerProfileForm.vue`

**Changes:**
- Update form container background
- Update label text colors
- Input fields (should auto-update via Nuxt UI)
- Update validation message colors

---

### Step 7: Update Global Styles (if needed)

**File:** `frontend/app/assets/css/main.css`

**Potential Changes:**
- Add CSS variables for dark mode colors
- Update any custom CSS classes
- Ensure Chart.js tooltips have dark mode styling

---

## Phase 2: Playwright MCP Review & Testing

### Step 8: Start Development Server

**Commands:**
```bash
cd frontend
npm run dev
```

**Verify:**
- Frontend running at `http://localhost:3000`
- Backend running at `http://localhost:8000`
- All pages accessible

---

### Step 9: Review Customer Section (3 pages)

**Pages to Screenshot:**

1. **Home Page (`/`)**
   - Light mode: Profile form, welcome text, navigation
   - Dark mode: Same elements
   - Check: Form inputs, buttons, text contrast, background transitions

2. **History Page (`/history`)**
   - Light mode: Consultation list, filters, empty state
   - Dark mode: Same elements
   - Check: Card backgrounds, hover states, borders, text readability

3. **Live Chat Page (`/consultation/[id]`)**
   - Light mode: Chat messages, input area, metadata
   - Dark mode: Same elements
   - Check: Message bubbles, timestamps, streaming indicators, contrast

**Review Checklist per Page:**
- [ ] Backgrounds have proper dark variants
- [ ] Text has sufficient contrast (WCAG AA: 4.5:1)
- [ ] Borders are visible in dark mode
- [ ] Hover/focus states work in dark mode
- [ ] No "flash" of light mode on page load
- [ ] All Nuxt UI components adapt correctly
- [ ] Custom components have dark variants
- [ ] Icons are visible in dark mode

---

### Step 10: Review Admin Section (17 pages)

**Admin Pages to Screenshot:**

1. **Dashboard (`/admin`)**
   - Light/Dark modes
   - Check: Stat cards, charts, recent items table

2. **Metrics (`/admin/metrics`)**
   - Light/Dark modes
   - Check: Chart backgrounds, legends, tooltips, data tables

3. **Settings (`/admin/settings`)**
   - Light/Dark modes
   - Check: Form inputs, save buttons, section dividers

4. **Consultations List (`/admin/consultations`)**
   - Light/Dark modes
   - Check: Data table, filters, pagination, status badges

5. **Consultation Detail (`/admin/consultations/[id]`)**
   - Light/Dark modes
   - Check: Message transcript, metadata cards, action buttons

6. **FCA Knowledge List (`/admin/knowledge/fca`)**
   - Light/Dark modes
   - Check: Article cards, search bar, vector indicators

7. **FCA Knowledge Detail (`/admin/knowledge/fca/[id]`)**
   - Light/Dark modes
   - Check: Article content, metadata, code blocks, related items

8. **Pension Knowledge List (`/admin/knowledge/pension`)**
   - Light/Dark modes
   - Check: Similar to FCA list

9. **Pension Knowledge Detail (`/admin/knowledge/pension/[id]`)**
   - Light/Dark modes
   - Check: Similar to FCA detail

10. **Learning Memory Detail (`/admin/learning/memories/[id]`)**
    - Light/Dark modes
    - Check: JSON display, metadata, related consultations

11. **Learning Case Detail (`/admin/learning/cases/[id]`)**
    - Light/Dark modes
    - Check: Case information, timeline, related items

12. **Learning Rules List (`/admin/learning/rules`)**
    - Light/Dark modes
    - Check: Rules table, filters, create button

13. **Learning Rule Detail (`/admin/learning/rules/[id]`)**
    - Light/Dark modes
    - Check: Rule definition, metadata, edit form

14. **Customer List (`/admin/users/customers`)**
    - Light/Dark modes
    - Check: User table, search, pagination

15. **Customer Detail (`/admin/users/customers/[id]`)**
    - Light/Dark modes
    - Check: Profile card, consultation history, metadata

**Admin Review Checklist per Page:**
- [ ] Sidebar navigation readable in dark mode
- [ ] Active page highlighted appropriately
- [ ] DataTable has proper dark styling
- [ ] Charts have dark-compatible color schemes
- [ ] Status badges have sufficient contrast
- [ ] Code/JSON blocks are readable
- [ ] Hover states work on table rows
- [ ] Modal/dropdown overlays have dark styling
- [ ] Loading states visible in dark mode
- [ ] Error states visible in dark mode

---

### Step 11: Playwright Automation Script

**Create:** `frontend/tests/dark-mode-review.spec.ts`

**Script Features:**
- Navigate to each page systematically
- Toggle between light and dark modes
- Capture full-page screenshots
- Save to organized directory structure
- Generate HTML report with side-by-side comparisons

**Screenshot Organization:**
```
frontend/screenshots/dark-mode-review/
├── customer/
│   ├── home-light.png
│   ├── home-dark.png
│   ├── history-light.png
│   ├── history-dark.png
│   ├── chat-light.png
│   └── chat-dark.png
├── admin/
│   ├── dashboard-light.png
│   ├── dashboard-dark.png
│   ├── metrics-light.png
│   ├── metrics-dark.png
│   └── ... (30+ more screenshots)
└── report.html
```

---

### Step 12: Generate Recommendations Report

**Output File:** `specs/dark-mode-review-findings.md`

**Report Sections:**

1. **Executive Summary**
   - Overall dark mode implementation quality
   - Number of pages reviewed
   - Critical issues found
   - Accessibility compliance status

2. **Customer Section Findings**
   - Page-by-page review with screenshot references
   - Visual issues identified
   - Contrast ratio problems
   - Component-specific issues

3. **Admin Section Findings**
   - Same format as customer section
   - Additional focus on data visualization
   - Table and chart readability
   - Complex component interactions

4. **Component-Specific Issues**
   - List of components needing refinement
   - Missing dark variants
   - Contrast issues
   - Border visibility problems

5. **Accessibility Audit**
   - WCAG 2.1 AA compliance check
   - Contrast ratio failures
   - Focus indicator visibility
   - Color-only information warnings

6. **Recommendations**
   - Priority-ranked fixes
   - Suggested color palette adjustments
   - Component improvements
   - Best practices for maintenance

7. **Screenshots Gallery**
   - Embedded side-by-side comparisons
   - Annotated problem areas
   - Before/after for any issues fixed

---

## Success Criteria

### Implementation Phase
- [ ] All 3 layouts have dark mode toggle
- [ ] All 20 pages have complete dark mode styling
- [ ] All ~15 components support dark mode
- [ ] No hardcoded light-only colors remain
- [ ] Color mode preference persists across sessions
- [ ] System preference detection works
- [ ] No flash of unstyled content on page load

### Review Phase
- [ ] All pages screenshotted in both modes (40+ screenshots)
- [ ] Comprehensive findings document created
- [ ] All critical issues documented
- [ ] Accessibility audit completed
- [ ] Recommendations prioritized and actionable
- [ ] Side-by-side comparison report generated

---

## Estimated Timeline

**Phase 1: Implementation**
- Step 1-2 (Config & Toggle): 30 minutes
- Step 3 (Layouts): 1 hour
- Step 4 (Customer Pages): 1 hour
- Step 5 (Admin Pages): 3-4 hours
- Step 6 (Components): 2-3 hours
- **Total: 8-10 hours**

**Phase 2: Review**
- Step 8 (Setup): 15 minutes
- Step 9-10 (Screenshots): 2 hours
- Step 11 (Automation): 1 hour
- Step 12 (Report): 1-2 hours
- **Total: 4-5 hours**

**Grand Total: 12-15 hours**

---

## Risk Mitigation

**Potential Issues:**

1. **Chart.js Dark Mode**
   - Risk: Charts may not adapt automatically
   - Mitigation: Configure color schemes programmatically based on `useColorMode()`

2. **Custom CSS Conflicts**
   - Risk: Existing custom CSS may override Tailwind dark variants
   - Mitigation: Audit `main.css` and component-scoped styles

3. **Third-party Components**
   - Risk: External components may not support dark mode
   - Mitigation: Wrap in containers with explicit dark styling

4. **Contrast Ratio Failures**
   - Risk: Some color combinations may fail WCAG AA
   - Mitigation: Test with browser DevTools and adjust colors

5. **Flash of Wrong Theme**
   - Risk: Brief flash of light theme before dark mode applies
   - Mitigation: Nuxt UI handles this with `color-mode` script injection

---

## Maintenance Plan

**Post-Implementation:**
1. Document dark mode color system in a style guide
2. Add dark mode checks to PR review checklist
3. Create Playwright tests to prevent regressions
4. Establish color palette tokens for consistency
5. Set up automated visual regression testing

---

## Appendix: Color Reference

**Standard Dark Mode Palette:**

| Element | Light Mode | Dark Mode |
|---------|-----------|-----------|
| Primary Background | `bg-white` | `bg-gray-900` |
| Secondary Background | `bg-gray-50` | `bg-gray-800` |
| Tertiary Background | `bg-gray-100` | `bg-gray-800` |
| Card Background | `bg-white` | `bg-gray-800` |
| Primary Text | `text-gray-900` | `text-gray-100` |
| Secondary Text | `text-gray-600` | `text-gray-400` |
| Tertiary Text | `text-gray-500` | `text-gray-500` |
| Border | `border-gray-200` | `border-gray-700` |
| Border (strong) | `border-gray-300` | `border-gray-600` |
| Hover Background | `hover:bg-gray-50` | `hover:bg-gray-700` |

**Status Colors (maintain in both modes):**
- Success: `text-green-600 dark:text-green-400`
- Warning: `text-yellow-600 dark:text-yellow-400`
- Error: `text-red-600 dark:text-red-400`
- Info: `text-blue-600 dark:text-blue-400`

---

## Next Steps

Once this plan is approved:
1. Begin Phase 1 implementation systematically
2. Test each section as it's completed
3. Proceed to Phase 2 Playwright review
4. Generate final recommendations report
5. Address any critical issues found
6. Document dark mode system for team

---

**Plan Version:** 1.0
**Date:** 2025-11-04
**Status:** Awaiting Approval