# Validation Reasoning Display - UI Reference

## Visual Layout

This document describes the visual appearance and behavior of the validation reasoning display feature.

## 1. Collapsed State (Default)

```
┌─────────────────────────────────────────────────────────────────┐
│ 🏛️ Advisor - Turn 2                              10:30 AM       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ I understand you are considering withdrawing your entire        │
│ pension pot. Before proceeding, it is important to understand   │
│ the implications...                                              │
│                                                                  │
│ ┌──────────────────┐                                            │
│ │  92% ▼           │  ← Clickable badge with chevron           │
│ └──────────────────┘                                            │
│   (Green badge - score >= 85%)                                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Key Features:**
- Compliance badge shows percentage
- Chevron-down icon indicates expandable
- Cursor changes to pointer on hover
- No reasoning visible yet

---

## 2. Expanded State - PASSED (High Compliance)

```
┌─────────────────────────────────────────────────────────────────┐
│ 🏛️ Advisor - Turn 2                              10:30 AM       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ I understand you are considering withdrawing your entire        │
│ pension pot. Before proceeding, it is important to understand   │
│ the implications...                                              │
│                                                                  │
│ ┌──────────────────┐                                            │
│ │  92% ▲           │  ← Badge now shows chevron-up             │
│ └──────────────────┘                                            │
│                                                                  │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ REASONING CARD (Gray background)                            │ │
│ │                                                              │ │
│ │ ┌─────────┐                                                 │ │
│ │ │ PASSED  │  ← Green badge                                  │ │
│ │ └─────────┘                                                 │ │
│ │                                                              │ │
│ │ Issues Found:                                               │ │
│ │ ┌──────────────────────────────────────────────────────────┐│ │
│ │ │ ┌───────┐  Could include more comprehension checks to   ││ │
│ │ │ │ minor │  ensure customer understanding                 ││ │
│ │ │ └───────┘                                                 ││ │
│ │ │  (Yellow badge)                                           ││ │
│ │ └──────────────────────────────────────────────────────────┘│ │
│ │                                                              │ │
│ │ Detailed Analysis:                                          │ │
│ │ ┌──────────────────────────────────────────────────────────┐│ │
│ │ │ # Compliance Analysis                                    ││ │
│ │ │                                                           ││ │
│ │ │ ## 1. Guidance Boundary (Score: 0.95)                   ││ │
│ │ │ The advisor correctly stays within regulated guidance   ││ │
│ │ │ boundaries by explaining implications without making    ││ │
│ │ │ personal recommendations.                                ││ │
│ │ │                                                           ││ │
│ │ │ ## 2. Risk Disclosure (Score: 0.90)                     ││ │
│ │ │ Adequate risk disclosure provided, including tax        ││ │
│ │ │ implications and sustainability concerns.               ││ │
│ │ │                                                           ││ │
│ │ │ ## 3. Neutrality (Score: 0.93)                          ││ │
│ │ │ The response maintains neutrality by presenting         ││ │
│ │ │ options without bias.                                   ││ │
│ │ │                                                           ││ │
│ │ │ ## Overall Assessment                                    ││ │
│ │ │ The advisor's response demonstrates strong compliance   ││ │
│ │ │ with FCA guidance requirements.                         ││ │
│ │ └──────────────────────────────────────────────────────────┘│ │
│ │   (White background, bordered, monospace font)             │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Key Features:**
- Gray background distinguishes reasoning section
- Green PASSED badge prominent at top
- Yellow minor issue badge
- Pre-formatted detailed analysis preserves structure
- Clean, readable layout

---

## 3. Expanded State - FAILED (Low Compliance)

```
┌─────────────────────────────────────────────────────────────────┐
│ 🏛️ Advisor - Turn 4                              10:45 AM       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ You should definitely invest in tech stocks right now!          │
│                                                                  │
│ ┌──────────────────┐                                            │
│ │  35% ▲           │  ← Red badge (score < 70%)                │
│ └──────────────────┘                                            │
│                                                                  │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ REASONING CARD (Gray background)                            │ │
│ │                                                              │ │
│ │ ┌────────┐ ┌──────────────────┐                            │ │
│ │ │ FAILED │ │ Requires Review  │  ← Red + Orange badges     │ │
│ │ └────────┘ └──────────────────┘                            │ │
│ │                                                              │ │
│ │ Issues Found:                                               │ │
│ │ ┌──────────────────────────────────────────────────────────┐│ │
│ │ │ ┌──────────┐  Response provides specific investment     ││ │
│ │ │ │ critical │  advice, crossing into regulated territory ││ │
│ │ │ └──────────┘  (Red badge)                                ││ │
│ │ └──────────────────────────────────────────────────────────┘│ │
│ │ ┌──────────────────────────────────────────────────────────┐│ │
│ │ │ ┌───────┐  Missing risk disclosure for investment       ││ │
│ │ │ │ major │  recommendations                               ││ │
│ │ │ └───────┘  (Orange badge)                                ││ │
│ │ └──────────────────────────────────────────────────────────┘│ │
│ │ ┌──────────────────────────────────────────────────────────┐│ │
│ │ │ ┌───────┐  Recommendation shows bias and lacks balanced ││ │
│ │ │ │ major │  perspective                                   ││ │
│ │ │ └───────┘  (Orange badge)                                ││ │
│ │ └──────────────────────────────────────────────────────────┘│ │
│ │                                                              │ │
│ │ Detailed Analysis:                                          │ │
│ │ ┌──────────────────────────────────────────────────────────┐│ │
│ │ │ # Compliance Analysis - CRITICAL FAILURE                ││ │
│ │ │                                                           ││ │
│ │ │ ## 1. Guidance Boundary (Score: 0.10)                   ││ │
│ │ │ **CRITICAL VIOLATION**: This response crosses into      ││ │
│ │ │ regulated advice territory by making specific           ││ │
│ │ │ investment recommendations.                              ││ │
│ │ │                                                           ││ │
│ │ │ ## Overall Assessment                                    ││ │
│ │ │ **FAILED** - This response constitutes regulated        ││ │
│ │ │ investment advice and violates FCA guidance boundaries. ││ │
│ │ │ Immediate correction required.                          ││ │
│ │ └──────────────────────────────────────────────────────────┘│ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Key Features:**
- Red FAILED badge (high visibility)
- Orange "Requires Review" badge for escalation
- Multiple issues with varying severity levels
- Critical issues highlighted in red
- Detailed reasoning explains the failure

---

## 4. Backward Compatibility - Old Message (No Reasoning)

```
┌─────────────────────────────────────────────────────────────────┐
│ 🏛️ Advisor - Turn 1                              10:15 AM       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ This is an old message created before reasoning was stored.     │
│                                                                  │
│ ┌──────────────┐                                                │
│ │  85%         │  ← Badge without chevron (not expandable)     │
│ └──────────────┘                                                │
│   (Green badge, but not clickable)                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Key Features:**
- Badge shows compliance score
- No chevron icon (indicating not expandable)
- Default cursor (not pointer)
- Clicking does nothing
- No errors or visual glitches

---

## 5. Color Scheme

### Compliance Score Badge Colors
- **Green (>= 85%)**: High compliance, good performance
- **Yellow (70-84%)**: Moderate compliance, needs attention
- **Red (< 70%)**: Low compliance, requires review

### Status Badge Colors
- **Green PASSED**: Compliant advice, approved
- **Red FAILED**: Non-compliant advice, rejected
- **Orange Requires Review**: Needs human oversight

### Severity Badge Colors
- **Red (critical)**: Serious compliance violation
- **Orange (major)**: Significant issue, high priority
- **Yellow (minor)**: Small issue, low priority

---

## 6. Responsive Behavior

### Desktop (> 1024px)
- Full layout as shown above
- Reasoning card expands to full width
- Adequate whitespace for readability

### Tablet (768px - 1024px)
- Similar layout, slightly condensed
- Text wraps appropriately
- Badges stack if needed

### Mobile (< 768px)
- Reasoning card takes full width
- Severity badges may stack vertically
- Increased padding for touch targets
- Font sizes adjust for readability

---

## 7. Interaction States

### Badge Hover (with reasoning)
```
┌──────────────────┐
│  92% ▼           │  ← Cursor: pointer, slight highlight
└──────────────────┘
```

### Badge Hover (without reasoning)
```
┌──────────────┐
│  85%         │  ← Cursor: default, no highlight
└──────────────┘
```

### Badge Active/Clicked
```
┌──────────────────┐
│  92% ▲           │  ← Chevron flips, reasoning appears
└──────────────────┘
```

---

## 8. Accessibility Features

### Keyboard Navigation
- Tab to badge: Badge receives focus ring
- Enter/Space: Toggle reasoning section
- Tab through reasoning: Focus moves through content
- Escape: (Future) Close reasoning section

### Screen Reader
- Badge announces: "Compliance score 92 percent, button, expanded/collapsed"
- Reasoning content is logically ordered
- Issues are announced as list items
- Severity is announced with issue

### Focus Indicators
- Visible focus ring on interactive elements
- High contrast focus indicators
- Logical tab order

---

## 9. Animation/Transitions

### Expand/Collapse
- Smooth height transition (duration: 200ms)
- Chevron rotates (duration: 150ms)
- Fade-in for content (duration: 100ms)

### No Jarring Movements
- Content below doesn't jump
- Smooth, professional feel
- Respects prefers-reduced-motion setting

---

## 10. Empty States

### No Issues
```
┌─────────────────────────────────────────────────────────────┐
│ ┌─────────┐                                                 │
│ │ PASSED  │                                                 │
│ └─────────┘                                                 │
│                                                              │
│ (No "Issues Found" section displayed)                       │
│                                                              │
│ Detailed Analysis:                                          │
│ ┌──────────────────────────────────────────────────────────┐│
│ │ All compliance areas scored 1.0. Exemplary guidance.    ││
│ └──────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

### Perfect Score (No Review Needed)
- Only PASSED badge shown
- No "Requires Review" badge
- Issues section omitted
- Clean, positive presentation

---

## Summary

The validation reasoning display provides:

✅ **Transparency**: Full visibility into AI decision-making
✅ **Clarity**: Color-coded severity and status
✅ **Efficiency**: Collapsed by default, expand on demand
✅ **Compatibility**: Works with old data seamlessly
✅ **Accessibility**: Keyboard and screen reader friendly
✅ **Professionalism**: Clean, modern design

The UI balances information density with usability, providing detailed compliance information without overwhelming the user interface.

