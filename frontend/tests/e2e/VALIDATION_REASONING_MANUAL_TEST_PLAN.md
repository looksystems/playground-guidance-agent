# Manual Test Plan: Validation Reasoning Display

## Overview
This document describes the manual testing approach for the validation reasoning display feature in the consultation detail page.

## Test Environment Setup
1. Start backend server with actual database
2. Start frontend dev server: `npm run dev`
3. Create test consultations with validation reasoning data

## Test Scenarios

### 1. Basic Display and Toggle Functionality

#### Test 1.1: Reasoning Hidden by Default
**Steps:**
1. Navigate to a consultation detail page with advisor messages that have compliance reasoning
2. Locate an advisor message with a compliance score badge

**Expected Results:**
- Compliance badge is visible with percentage
- Chevron-down icon is visible on the badge (indicating expandable)
- Reasoning section is NOT visible (collapsed by default)
- "Detailed Analysis" heading is NOT visible

**Pass/Fail:** ___________

---

#### Test 1.2: Expand Reasoning on Click
**Steps:**
1. From Test 1.1, click on the compliance badge
2. Observe the UI changes

**Expected Results:**
- Reasoning section becomes visible below the message
- Chevron icon changes from down to up
- "Detailed Analysis" heading is visible
- Pass/Fail status badge is visible
- Issues section is visible (if issues exist)

**Pass/Fail:** ___________

---

#### Test 1.3: Toggle Collapse/Expand
**Steps:**
1. From Test 1.2 (expanded state), click the badge again
2. Click again to expand
3. Click again to collapse

**Expected Results:**
- First click: Reasoning collapses (becomes hidden)
- Second click: Reasoning expands (becomes visible)
- Third click: Reasoning collapses again
- Chevron icon updates correctly each time

**Pass/Fail:** ___________

---

### 2. Compliance Status Display

#### Test 2.1: PASSED Badge for Compliant Messages
**Steps:**
1. Find an advisor message with compliance_passed=true
2. Expand the reasoning section

**Expected Results:**
- Green "PASSED" badge is visible
- Badge uses solid variant (not soft/outline)
- Badge is displayed at the top of the reasoning section

**Pass/Fail:** ___________

---

#### Test 2.2: FAILED Badge for Non-Compliant Messages
**Steps:**
1. Find an advisor message with compliance_passed=false
2. Expand the reasoning section

**Expected Results:**
- Red "FAILED" badge is visible
- Badge uses solid variant
- Badge stands out with high contrast

**Pass/Fail:** ___________

---

#### Test 2.3: Requires Review Badge
**Steps:**
1. Find an advisor message with requires_human_review=true
2. Expand the reasoning section

**Expected Results:**
- Orange "Requires Review" badge is visible
- Badge is displayed next to the PASSED/FAILED badge
- Badge uses solid variant with warning color

**Pass/Fail:** ___________

---

#### Test 2.4: No Review Badge When Not Flagged
**Steps:**
1. Find an advisor message with requires_human_review=false or undefined
2. Expand the reasoning section

**Expected Results:**
- "Requires Review" badge is NOT visible
- Only PASSED/FAILED badge is shown

**Pass/Fail:** ___________

---

### 3. Compliance Issues Display

#### Test 3.1: Display Issues List
**Steps:**
1. Find an advisor message with multiple compliance_issues
2. Expand the reasoning section

**Expected Results:**
- "Issues Found:" heading is visible
- All issues are listed in a bulleted/structured format
- Each issue shows:
  - Severity badge (critical/major/minor)
  - Issue description text

**Pass/Fail:** ___________

---

#### Test 3.2: Severity Color Coding
**Steps:**
1. From Test 3.1, examine the severity badges

**Expected Results:**
- Critical severity: RED badge
- Major severity: ORANGE badge
- Minor severity: YELLOW badge
- Badges use small size (xs)

**Pass/Fail:** ___________

---

#### Test 3.3: No Issues Section When Empty
**Steps:**
1. Find an advisor message with compliance_issues=[] (empty array)
2. Expand the reasoning section

**Expected Results:**
- "Issues Found:" heading is NOT visible
- No issues list is displayed
- Reasoning section still shows other content (pass/fail, detailed analysis)

**Pass/Fail:** ___________

---

### 4. Detailed Reasoning Display

#### Test 4.1: Display Full Reasoning Text
**Steps:**
1. Expand a reasoning section
2. Locate the "Detailed Analysis:" section

**Expected Results:**
- "Detailed Analysis:" heading is visible
- Full compliance reasoning text is displayed
- Text includes compliance area scores (e.g., "Guidance Boundary: 0.95")
- Text includes overall assessment

**Pass/Fail:** ___________

---

#### Test 4.2: Preserve Formatting
**Steps:**
1. From Test 4.1, examine the reasoning text format

**Expected Results:**
- Text is displayed in a `<pre>` tag
- Line breaks are preserved
- Indentation is maintained
- Section headers (##) are visible as plain text
- Monospace font is used
- White background with border distinguishes it from surrounding content

**Pass/Fail:** ___________

---

### 5. Backward Compatibility

#### Test 5.1: Handle Messages Without Reasoning
**Steps:**
1. Find an old advisor message without compliance_reasoning field
2. Observe the message display

**Expected Results:**
- Message displays normally
- Compliance score badge is visible (if compliance_score exists)
- NO chevron icon on the badge
- Badge is NOT clickable (no cursor-pointer)
- Clicking badge does nothing (no error)

**Pass/Fail:** ___________

---

#### Test 5.2: Mixed Old and New Messages
**Steps:**
1. Find a consultation with both old (no reasoning) and new (with reasoning) messages
2. Examine both types of messages

**Expected Results:**
- Old messages: Badge visible, no chevron, not expandable
- New messages: Badge visible, chevron present, expandable
- Both types render without errors
- Page functions normally

**Pass/Fail:** ___________

---

### 6. Visual Design and UX

#### Test 6.1: Reasoning Section Styling
**Steps:**
1. Expand a reasoning section
2. Examine the visual styling

**Expected Results:**
- Reasoning card has gray background (bg-gray-50)
- Distinct visual separation from main message content
- Adequate padding and spacing
- Rounded corners
- Professional appearance

**Pass/Fail:** ___________

---

#### Test 6.2: Cursor Pointer on Badge
**Steps:**
1. Hover over a compliance badge with reasoning
2. Observe the cursor

**Expected Results:**
- Cursor changes to pointer (hand icon)
- Indicates the badge is clickable
- Badge without reasoning shows default cursor

**Pass/Fail:** ___________

---

#### Test 6.3: Issues List Readability
**Steps:**
1. Expand a message with multiple issues
2. Examine the issues list layout

**Expected Results:**
- Issues are in a `<ul>` list
- Each issue is on its own line
- Severity badge is left-aligned
- Description text wraps properly
- Adequate spacing between issues (space-y-2)
- Easy to scan and read

**Pass/Fail:** ___________

---

### 7. Multiple Messages

#### Test 7.1: Independent Toggle
**Steps:**
1. Find a consultation with multiple advisor messages
2. Expand the first message's reasoning
3. Expand the second message's reasoning
4. Collapse the first message

**Expected Results:**
- Both messages can be expanded simultaneously
- Expanding one doesn't affect the other
- Collapsing one doesn't affect the other
- Each message maintains its own toggle state

**Pass/Fail:** ___________

---

### 8. Compliance Score Color Coding

#### Test 8.1: Score Badge Colors
**Steps:**
1. Find messages with different compliance scores
2. Observe the badge colors

**Expected Results:**
- Score >= 0.85 (85%): GREEN badge
- Score >= 0.70 (70%): YELLOW badge
- Score < 0.70 (70%): RED badge
- Colors are applied correctly based on score

**Pass/Fail:** ___________

---

## Accessibility Testing

### Test A.1: Keyboard Navigation
**Steps:**
1. Use Tab key to navigate through the page
2. Try to activate compliance badge with Enter/Space key

**Expected Results:**
- Badge receives focus when tabbed to
- Focus indicator is visible
- Enter or Space key toggles the reasoning section
- Keyboard navigation works smoothly

**Pass/Fail:** ___________

---

### Test A.2: Screen Reader Compatibility
**Steps:**
1. Use a screen reader (e.g., VoiceOver, NVDA)
2. Navigate to an advisor message

**Expected Results:**
- Badge is announced with percentage
- Expanded/collapsed state is announced
- Issues are announced in order
- Content is logically structured

**Pass/Fail:** ___________

---

## Browser Compatibility

Test the feature in multiple browsers:
- [ ] Chrome/Chromium
- [ ] Firefox
- [ ] Safari
- [ ] Edge

Document any browser-specific issues:

---

## Performance Testing

### Test P.1: Large Consultations
**Steps:**
1. Load a consultation with 20+ messages
2. Expand multiple reasoning sections

**Expected Results:**
- Page remains responsive
- No noticeable lag when toggling
- Smooth animations/transitions
- No memory leaks

**Pass/Fail:** ___________

---

## Summary

**Total Tests:** 21 core tests + 3 accessibility + 1 performance
**Tests Passed:** ___________
**Tests Failed:** ___________
**Pass Rate:** ___________%

**Critical Issues Found:**

1. ___________________________________
2. ___________________________________
3. ___________________________________

**Minor Issues Found:**

1. ___________________________________
2. ___________________________________
3. ___________________________________

**Recommendations:**

1. ___________________________________
2. ___________________________________
3. ___________________________________

---

## Tested By

**Name:** _______________________
**Date:** _______________________
**Environment:** Frontend: _______________ Backend: _______________

