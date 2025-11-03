# Validation Reasoning Display Implementation Plan

## Overview
Add validation reasoning storage and display on the consultation detail page in the admin UI.

## Current State

### What the Validation Agent Provides
1. ✅ **% Compliance Score** (0-1 scale, shown as percentage)
2. ✅ **Detailed Reasoning** - including analysis of 5 FCA compliance areas, overall assessment, and specific issues

### What's Currently Stored in Database
- **Per-message compliance scores** in `consultations.conversation` JSONB field
- **Average compliance score** in `consultations.outcome` JSONB field
- **No reasoning, no issues list, no pass/fail flags** are currently stored

### What's Available But Not Stored
The `ValidationResult` object (in `src/guidance_agent/compliance/validator.py`) contains:
- `reasoning: str` - Full LLM explanation with structured analysis
- `issues: list[ValidationIssue]` - Specific compliance problems found
- `passed: bool` - Pass/fail determination
- `requires_human_review: bool` - Flag for manual review
- `confidence: float` - 0-1 confidence score (currently stored)

### Current Admin UI Display
The admin UI already displays compliance scores extensively:
- Dashboard overview with compliance metrics
- Charts showing compliance over time
- Per-consultation compliance badges
- Per-message compliance scores

However, it **cannot show reasoning** since it's not stored in the database.

## Implementation Plan

### 1. Database Schema Update
**File**: `src/guidance_agent/core/database.py`

**Changes**:
- No schema changes needed (using flexible JSONB columns)
- Document the extended structure for `consultations.conversation` JSONB

**New structure for advisor messages in conversation JSONB**:
```python
{
    "role": "advisor",
    "content": "...",
    "timestamp": "...",
    "compliance_score": 0.95,
    "compliance_confidence": 0.95,
    "compliance_reasoning": "...",  # NEW: Full validation reasoning
    "compliance_issues": [...],      # NEW: List of specific issues
    "compliance_passed": true,       # NEW: Boolean pass/fail
    "requires_human_review": false   # NEW: Review flag
}
```

### 2. Backend API Updates

#### File: `src/guidance_agent/api/routers/consultations.py`

**Changes at line ~306-312**:
- Currently stores only `compliance_score` and `compliance_confidence`
- Extend to also store:
  - `validation.reasoning`
  - `validation.issues` (serialized to dict/list)
  - `validation.passed`
  - `validation.requires_human_review`

**Before**:
```python
advisor_message = {
    "role": "advisor",
    "content": advice,
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "compliance_score": validation.confidence,
    "compliance_confidence": validation.confidence,
}
```

**After**:
```python
advisor_message = {
    "role": "advisor",
    "content": advice,
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "compliance_score": validation.confidence,
    "compliance_confidence": validation.confidence,
    "compliance_reasoning": validation.reasoning,
    "compliance_issues": [
        {
            "category": issue.category,
            "severity": issue.severity,
            "description": issue.description
        }
        for issue in validation.issues
    ],
    "compliance_passed": validation.passed,
    "requires_human_review": validation.requires_human_review,
}
```

#### File: `src/guidance_agent/api/schemas.py`

**Changes**:
Add new optional fields to `ConversationTurn` schema:

```python
class ConversationTurn(BaseModel):
    role: str
    content: str
    timestamp: str
    compliance_score: Optional[float] = None
    compliance_confidence: Optional[float] = None
    compliance_reasoning: Optional[str] = None  # NEW
    compliance_issues: Optional[List[Dict[str, Any]]] = None  # NEW
    compliance_passed: Optional[bool] = None  # NEW
    requires_human_review: Optional[bool] = None  # NEW
```

#### File: `src/guidance_agent/api/routers/admin.py`

**Changes**:
- No changes needed - admin endpoints already return the full conversation JSONB
- The new fields will automatically be included in responses via existing `ConversationTurn` schema

### 3. Frontend Admin UI Updates

#### File: `frontend/app/pages/admin/consultations/[id].vue`

**Current state** (lines 98-105):
- Each conversation turn shows compliance score badge
- No reasoning is displayed

**Changes needed**:

1. **Add expandable reasoning section** to advisor messages:
   - Add toggle button/icon on compliance badge
   - Create collapsible section below message content
   - Display structured compliance analysis

2. **Reasoning display components**:
   ```vue
   <div v-if="turn.role === 'advisor' && turn.compliance_reasoning" class="mt-2">
     <!-- Compliance Score Badge (existing) -->
     <UBadge
       :color="getComplianceColor(turn.compliance_score)"
       @click="toggleReasoning(index)"
       class="cursor-pointer"
     >
       {{ (turn.compliance_score * 100).toFixed(1) }}% Compliant
       <UIcon :name="expandedReasoning[index] ? 'i-heroicons-chevron-up' : 'i-heroicons-chevron-down'" />
     </UBadge>

     <!-- Expandable Reasoning Section (NEW) -->
     <UCard v-if="expandedReasoning[index]" class="mt-2 bg-gray-50">
       <div class="space-y-3">
         <!-- Pass/Fail Status -->
         <div class="flex items-center gap-2">
           <UBadge :color="turn.compliance_passed ? 'green' : 'red'">
             {{ turn.compliance_passed ? 'PASSED' : 'FAILED' }}
           </UBadge>
           <UBadge v-if="turn.requires_human_review" color="orange">
             Requires Review
           </UBadge>
         </div>

         <!-- Compliance Issues -->
         <div v-if="turn.compliance_issues && turn.compliance_issues.length > 0">
           <h4 class="font-semibold text-sm mb-2">Issues Found:</h4>
           <ul class="space-y-1">
             <li v-for="issue in turn.compliance_issues" :key="issue.description"
                 class="flex items-start gap-2">
               <UBadge :color="getSeverityColor(issue.severity)" size="xs">
                 {{ issue.severity }}
               </UBadge>
               <span class="text-sm">{{ issue.description }}</span>
             </li>
           </ul>
         </div>

         <!-- Detailed Reasoning -->
         <div>
           <h4 class="font-semibold text-sm mb-2">Detailed Analysis:</h4>
           <pre class="text-xs whitespace-pre-wrap bg-white p-3 rounded border">{{ turn.compliance_reasoning }}</pre>
         </div>
       </div>
     </UCard>
   </div>
   ```

3. **Add reactive state** for expandable sections:
   ```typescript
   const expandedReasoning = ref<Record<number, boolean>>({})

   const toggleReasoning = (index: number) => {
     expandedReasoning.value[index] = !expandedReasoning.value[index]
   }

   const getComplianceColor = (score: number) => {
     if (score >= 0.85) return 'green'
     if (score >= 0.7) return 'yellow'
     return 'red'
   }

   const getSeverityColor = (severity: string) => {
     switch (severity) {
       case 'critical': return 'red'
       case 'major': return 'orange'
       case 'minor': return 'yellow'
       default: return 'gray'
     }
   }
   ```

### 4. Testing Plan

#### Backend Tests
1. **Test validation result storage**:
   - Create consultation with advisor response
   - Verify all validation fields are stored in JSONB
   - Check reasoning, issues, passed, and review flags are present

2. **Test API responses**:
   - Verify admin consultation detail endpoint returns new fields
   - Check schema validation passes with new optional fields

#### Frontend Tests
1. **UI component testing**:
   - Verify reasoning section is hidden by default
   - Test toggle functionality
   - Check visual styling and layout
   - Test with/without issues
   - Test pass/fail status display

2. **Integration testing**:
   - Load consultation with stored reasoning
   - Verify reasoning displays correctly
   - Test expandable sections on multiple messages

## Files to Modify

### Backend
1. ✅ `src/guidance_agent/api/routers/consultations.py` (lines ~306-312)
   - Store validation reasoning in conversation JSONB

2. ✅ `src/guidance_agent/api/schemas.py`
   - Add optional fields to `ConversationTurn`

3. ✅ `src/guidance_agent/core/database.py` (documentation only)
   - Document extended JSONB structure

### Frontend
4. ✅ `frontend/app/pages/admin/consultations/[id].vue`
   - Add expandable reasoning display
   - Add toggle functionality
   - Add styling for compliance analysis

## Implementation Time Estimate
~30-45 minutes total:
- Backend changes: 15-20 minutes
- Frontend changes: 15-20 minutes
- Testing: 10 minutes

## Migration Considerations

### Backward Compatibility
- **Existing consultations**: Will not have reasoning data (stored before this change)
- **Solution**: UI should gracefully handle missing `compliance_reasoning` field
- **Implementation**: Use `v-if="turn.compliance_reasoning"` checks in Vue templates

### Data Migration
- **Not required**: Existing data remains valid
- **New consultations**: Will automatically include reasoning starting from deployment
- **Old consultations**: Will show compliance score but no reasoning (acceptable)

## Future Enhancements

### Potential Additions
1. **Search/Filter by reasoning keywords** - Find consultations with specific compliance issues
2. **Compliance report generation** - Export detailed compliance analysis
3. **Trends analysis** - Track common compliance issues over time
4. **AI-powered insights** - Identify patterns in compliance failures
5. **Human review workflow** - Dedicated UI for flagged consultations requiring review

## References

### Key Files
- **Validator**: `src/guidance_agent/compliance/validator.py` (lines 52-59, 289-291, 402)
- **Consultation Router**: `src/guidance_agent/api/routers/consultations.py` (lines 306-321)
- **Database Models**: `src/guidance_agent/core/database.py` (lines 95-110)
- **Admin UI Detail**: `frontend/app/pages/admin/consultations/[id].vue` (lines 98-105)

### Validation Result Structure
```python
@dataclass
class ValidationResult:
    passed: bool
    confidence: float  # 0-1 scale
    issues: list[ValidationIssue]
    requires_human_review: bool
    reasoning: str  # Full LLM explanation
```

### Validation Issue Structure
```python
@dataclass
class ValidationIssue:
    category: str  # e.g., "guidance_boundary", "risk_disclosure"
    severity: str  # "critical", "major", "minor"
    description: str
```
