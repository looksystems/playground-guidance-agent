# Frontend Mock Data Audit Report

**Date**: 2025-11-03
**Status**: Critical Issues Found
**Dev Server**: http://localhost:3001

## Executive Summary

A comprehensive review of the Nuxt frontend codebase revealed a **mixed implementation** with customer-facing features properly using backend API endpoints while admin pages contain extensive hardcoded mock data. The infrastructure for API integration exists (composables, utility functions, proxy configuration) but is not consistently used across all pages.

---

## 1. MOCK/DUMMY DATA LOCATIONS

### Critical Mock Data (Must be Removed/Replaced)

#### A. `/frontend-nuxt/app/pages/admin/index.vue`

**Lines 131-162**: Hardcoded consultations table data
```typescript
const consultations = ref<ConsultationRow[]>([
  {
    id: 'C-001',
    customer: 'John Smith',
    topic: 'Retirement Planning',
    date: '2025-11-01',
    messages: 12,
    compliance: 98,
    satisfactionEmoji: '😊',
    satisfactionText: 'Satisfied'
  },
  // ... more hardcoded rows
])
```
- **Status**: NOT using backend API
- **Impact**: Admin dashboard shows fake data instead of real consultations

**Lines 166-177**: Hardcoded compliance chart data
```typescript
const complianceData = ref({
  labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
  datasets: [{
    label: 'FCA Compliance Score',
    data: [94.2, 95.1, 95.8, 96.0, 96.2, 96.4],
    // ...
  }]
})
```
- **Status**: NOT using backend API
- **Impact**: Compliance chart shows static fake data

#### B. `/frontend-nuxt/app/pages/admin/consultations/[id].vue`

**Lines 128-170**: ~~Complete mock consultation review data~~ **FIXED - Phase 2 Complete**
```typescript
// OLD (Removed):
// const consultation = ref({
//   customer: 'John Smith',
//   age: 45,
//   compliance: 0.98,
//   ...
// })

// NEW (Lines 152-194):
const { data: apiData, pending, error } = await useFetch(`/api/admin/consultations/${id.value}`, {
  headers: { 'Authorization': 'Bearer admin-token' }
})

const consultation = computed(() => {
  if (!apiData.value) return null
  // Transform API data to UI structure
  return {
    customer: apiData.value.customer_name,
    age: apiData.value.customer_age,
    compliance: apiData.value.metrics?.avg_compliance_score || 0,
    transcript: apiData.value.conversation.filter(...).map(...),
    insights: { cases: ..., rules: ... }
  }
})
```
- **Status**: ✅ NOW using backend API `/api/admin/consultations/{id}`
- **Impact**: Admin consultation detail view now shows **real consultation data**
- **Added**: Loading states, error handling, and retry functionality
- **Tested**: Successfully displays real consultation data with transcript, compliance scores, and insights

#### C. `/frontend-nuxt/app/pages/admin/metrics.vue`

**Lines 113-134**: All metrics are hardcoded
```typescript
const complianceBreakdown = ref([
  { category: 'Risk Assessment', score: 98 },
  { category: 'Documentation', score: 96 },
  // ...
])

const topTopics = ref([
  { name: 'Retirement Planning', count: 342 },
  // ...
])

const peakHours = ref([
  { time: '9:00 AM - 10:00 AM', sessions: 45 },
  // ...
])
```
- **Status**: NOT using backend API
- **Impact**: Metrics page shows completely static data

#### D. `/frontend-nuxt/app/pages/admin/settings.vue`

**Lines 124-145**: Settings form with hardcoded values
```typescript
const settings = ref({
  systemName: 'Pension Guidance Service',
  supportEmail: 'support@pensionguidance.com',
  sessionTimeout: 30,
  // ... more settings
})

const aiModels = [
  { label: 'GPT-4', value: 'gpt-4' },
  // ...
]
```
- **Status**: NOT using backend API for load/save
- **Impact**: Settings are not persisted, show fake toast notifications

#### E. `/frontend-nuxt/app/pages/history.vue`

**Lines 100-109**: Partial mock data in data transformation
```typescript
return apiData.value.items.map((c: any) => ({
  id: c.id,
  title: 'Pension Consultation', // HARDCODED - should be dynamic
  advisor: c.advisor_name,
  date: new Date(c.created_at).toLocaleDateString(...),
  status: c.status,
  preview: 'Consultation in progress...', // HARDCODED - should extract from messages
  messages: 0, // HARDCODED - should count from conversation array
  compliance: 0, // HARDCODED - should calculate from conversation
  satisfactionEmoji: '😊', // HARDCODED
  satisfactionText: 'In progress' // HARDCODED
}))
```
- **Status**: PARTIALLY using backend API (fetches list but displays mock metadata)
- **Impact**: Shows real consultations but with placeholder values

### Non-Critical Static Data (Configuration/UI Options)

#### F. `/frontend-nuxt/app/components/forms/CustomerProfileForm.vue`

**Lines 147-153**: Topic options
```typescript
const topicOptions = [
  { value: 'consolidation', label: 'Consolidating pensions' },
  { value: 'withdrawal', label: 'Considering pension withdrawal' },
  // ...
]
```
- **Status**: Appropriate static configuration
- **Impact**: None - these are legitimate UI options

---

## 2. COMPONENTS CORRECTLY USING BACKEND API

### Properly Implemented Components

#### A. `/frontend-nuxt/app/components/forms/CustomerProfileForm.vue`

**Lines 164-181**: Creates consultation via API
```typescript
const data = await $fetch('/api/consultations', {
  method: 'POST',
  body: {
    name: event.data.firstName,
    age: event.data.age,
    initial_query: event.data.topic
  }
})
```
- **Status**: ✅ CORRECTLY using backend API
- **Endpoint**: POST /api/consultations

#### B. `/frontend-nuxt/app/components/chat/AIChat.vue`

**Lines 105-141**: Loads conversation history
```typescript
const response = await fetch(`/api/consultations/${props.consultationId}`)
const data = await response.json()
messages.value = data.conversation.map(...)
```
- **Status**: ✅ CORRECTLY using backend API
- **Endpoint**: GET /api/consultations/{id}

**Lines 162-244**: Sends messages and handles SSE streaming
```typescript
await fetch(`/api/consultations/${props.consultationId}/messages`, {
  method: 'POST',
  body: JSON.stringify({ content: currentInput })
})
const eventSource = new EventSource(`/api/consultations/${props.consultationId}/stream`)
```
- **Status**: ✅ CORRECTLY using backend API
- **Endpoints**:
  - POST /api/consultations/{id}/messages
  - GET /api/consultations/{id}/stream (SSE)

#### C. `/frontend-nuxt/app/pages/consultation/[id].vue`

**Lines 56-68**: Ends consultation
```typescript
await $fetch(`/api/consultations/${id.value}/end`, {
  method: 'POST',
  body: {}
})
```
- **Status**: ✅ CORRECTLY using backend API
- **Endpoint**: POST /api/consultations/{id}/end

#### D. `/frontend-nuxt/app/pages/history.vue`

**Line 92**: Fetches consultations list
```typescript
const { data: apiData, pending, error } = await useFetch('/api/consultations')
```
- **Status**: ✅ CORRECTLY using backend API (but transforms with mock data)
- **Endpoint**: GET /api/consultations

#### E. `/frontend-nuxt/app/components/common/BackendHealthBanner.vue`

Uses `useHealthCheck` composable properly

#### F. `/frontend-nuxt/app/composables/useHealthCheck.ts`

**Lines 38-48**: Health check implementation
```typescript
const response = await $fetch<HealthStatus>(`${backendUrl}/health`)
```
- **Status**: ✅ CORRECTLY implemented
- **Endpoint**: GET /health

#### G. `/frontend-nuxt/app/composables/useCustomerProfile.ts`

**Lines 18-66**: Customer profile operations
```typescript
const { data, error } = await useFetch(`/api/customers/${customerId}`)
const { data, error } = await useFetch(`/api/customers/${customerId}`, { method: 'PUT', body: updates })
const { data, error } = await useFetch(`/api/customers/${customerId}/consultations`, { query: params })
```
- **Status**: ✅ CORRECTLY implemented
- **Endpoints**:
  - GET /api/customers/{id}
  - PUT /api/customers/{id}
  - GET /api/customers/{id}/consultations

#### H. `/frontend-nuxt/app/composables/useConsultation.ts`

**Lines 14-89**: Consultation operations
```typescript
await useFetch('/api/consultations', { query: params })
await useFetch(`/api/consultations/${consultationId}`)
await useFetch('/api/consultations', { method: 'POST', body: { customer_profile: customerProfile } })
await useFetch(`/api/consultations/${consultationId}/end`, { method: 'POST', body: { satisfaction_score: satisfactionScore } })
await useFetch(`/api/consultations/${consultationId}/metrics`)
```
- **Status**: ✅ CORRECTLY implemented (but NOT used in admin pages)
- **Endpoints**:
  - GET /api/consultations
  - GET /api/consultations/{id}
  - POST /api/consultations
  - POST /api/consultations/{id}/end
  - GET /api/consultations/{id}/metrics

#### I. `/frontend-nuxt/app/utils/api.ts`

**Lines 1-36**: API utility functions (wrapper layer)
- **Status**: ✅ CORRECTLY implemented (but NOT used in admin pages)

---

## 3. COMPONENTS NOT USING BACKEND API (BUT SHOULD BE)

### High Priority Issues

| Component | Issue | Backend Endpoint Available? | Recommended Action |
|-----------|-------|---------------------------|-------------------|
| **admin/index.vue** (Dashboard) | Uses hardcoded consultations array | ✅ Yes: `api.admin.consultations()` | Replace mock data with API call |
| **admin/index.vue** (Chart) | Uses hardcoded compliance chart data | ✅ Yes: `api.admin.complianceData()` | Replace with real API data |
| **admin/consultations/[id].vue** | ~~Entire component uses mock data~~ ✅ **FIXED** | ✅ Yes: `api.admin.consultation(id)` | ✅ **COMPLETED - Phase 2** |
| **admin/metrics.vue** | All metrics hardcoded | ⚠️ Partial: `api.admin.metrics()` exists | Implement full metrics API |
| **admin/settings.vue** | Settings not persisted | ❌ No API endpoint | Need backend endpoints for settings CRUD |
| **history.vue** | Uses placeholder values in transformation | ⚠️ Partial: API returns basic data | Backend should return complete metadata |

---

## 4. API INTEGRATION ANALYSIS

### Available Backend Endpoints (from api.ts)

```typescript
// Consultations
GET    /api/consultations
GET    /api/consultations/{id}
POST   /api/consultations
PATCH  /api/consultations/{id}

// Customers
POST   /api/customers/profile
GET    /api/customers/{id}
PUT    /api/customers/{id}
GET    /api/customers/{id}/consultations

// Admin
GET    /api/admin/consultations
GET    /api/admin/consultations/{id}
GET    /api/admin/metrics
GET    /api/admin/metrics/compliance

// Health
GET    /health
```

### API Proxy Configuration

**File**: `/frontend-nuxt/nuxt.config.ts`
**Lines 46-58**: Properly configured proxy to FastAPI backend
```typescript
nitro: {
  devProxy: {
    '/api': {
      target: 'http://localhost:8000/api',
      changeOrigin: true,
      prependPath: true
    }
  }
},
routeRules: {
  '/api/**': { proxy: 'http://localhost:8000/api/**' }
}
```
- **Status**: ✅ Correctly configured

---

## 5. UNUSED UTILITIES AND COMPOSABLES

### Available but Not Used

1. **useConsultation composable** - Lines 11-89
   - Properly implements API calls
   - **NOT used in admin pages** which have hardcoded data
   - Should be used in: admin/index.vue, admin/consultations/[id].vue

2. **api.ts utility functions**
   - Properly wraps API calls
   - **NOT used consistently** across codebase
   - Should be used instead of direct $fetch calls

3. **useConsultationsStore** (Pinia store)
   - Lines 1-43 in stores/consultations.ts
   - **NOT actively used** in any component
   - Could manage global consultation state

---

## 6. DATA FLOW ISSUES

### History Page Transformation Issue

**File**: `/frontend-nuxt/app/pages/history.vue`
**Problem**: Fetches real data from backend but overlays it with placeholder values

**Current behavior**:
```typescript
// Fetches real data ✅
const { data: apiData } = await useFetch('/api/consultations')

// But then adds placeholder values ❌
return apiData.value.items.map((c: any) => ({
  id: c.id,                                    // ✅ Real
  title: 'Pension Consultation',              // ❌ Hardcoded
  advisor: c.advisor_name,                     // ✅ Real
  preview: 'Consultation in progress...',      // ❌ Hardcoded
  messages: 0,                                 // ❌ Hardcoded
  compliance: 0,                               // ❌ Hardcoded
  satisfactionEmoji: '😊',                     // ❌ Hardcoded
  satisfactionText: 'In progress'              // ❌ Hardcoded
}))
```

**Solution**: Backend should return complete consultation objects with all metadata

---

## 7. RECOMMENDATIONS

### Immediate Actions Required

#### 1. Admin Dashboard Page (admin/index.vue)

- ✅ API endpoint exists: `api.admin.consultations()`
- ✅ API endpoint exists: `api.admin.complianceData()`
- **Action**: Replace lines 131-177 with API calls

**Suggested implementation**:
```typescript
// Replace mock data
const { data: consultations, pending } = await useFetch('/api/admin/consultations')
const { data: complianceData } = await useFetch('/api/admin/metrics/compliance')
```

#### 2. Admin Consultation Detail Page (admin/consultations/[id].vue)

- ✅ API endpoint exists: `api.admin.consultation(id)`
- **Action**: Replace lines 128-170 with API call

**Suggested implementation**:
```typescript
const { data: consultation } = await useFetch(`/api/admin/consultations/${id.value}`)
```

#### 3. Admin Metrics Page (admin/metrics.vue)

- ✅ API endpoint exists: `api.admin.metrics()`
- **Action**: Replace lines 113-134 with API call
- **Note**: Backend may need to provide additional metrics

#### 4. History Page (history.vue)

- ✅ Already fetching from API
- **Action**: Remove placeholder values in transformation (lines 100-109)
- **Note**: Backend should return complete metadata

### Backend Enhancements Needed

#### 1. Settings Endpoints (Missing)

Need to create:
- GET /api/admin/settings
- PUT /api/admin/settings

#### 2. Enhanced Consultation Metadata

The `/api/consultations` endpoint should return:
- `title` or `summary` field
- `preview` (first customer message excerpt)
- `message_count`
- `average_compliance_score`
- `satisfaction_data` (emoji and text)

Currently these are computed client-side with hardcoded placeholders.

### Code Quality Improvements

#### 1. Consistent API Usage

- Use the `api.ts` utility functions consistently instead of raw `$fetch` calls
- Benefits: Better type safety, easier to maintain, centralized error handling

#### 2. Use Pinia Store

- The consultations store exists but is unused
- Could manage global state for active consultations
- Reduce redundant API calls

#### 3. Error Handling

- Add proper error states for failed API calls in admin pages
- Currently only the history page and chat component have error handling

#### 4. Loading States

- Admin pages lack loading indicators
- User experience would improve with skeleton loaders

---

## 8. SUMMARY TABLE

| File Path | Mock Data? | Using API? | Priority | Action Needed |
|-----------|-----------|-----------|----------|---------------|
| pages/admin/index.vue | ✅ Yes (Lines 131-177) | ❌ No | 🔴 High | Replace with API calls |
| pages/admin/consultations/[id].vue | ~~✅ Yes (Lines 128-170)~~ | ✅ **YES** | ✅ **DONE** | ✅ **COMPLETED - Phase 2** |
| pages/admin/metrics.vue | ✅ Yes (Lines 113-134) | ❌ No | 🟡 Medium | Replace with API calls |
| pages/admin/settings.vue | ~~✅ Yes (Lines 124-145)~~ | ✅ **YES** | ✅ **DONE** | ✅ **COMPLETED - Phase 5** |
| pages/history.vue | ⚠️ Partial (Lines 100-109) | ⚠️ Partial | 🟡 Medium | Enhance backend response |
| pages/consultation/[id].vue | ❌ No | ✅ Yes | ✅ Good | None - working correctly |
| components/chat/AIChat.vue | ❌ No | ✅ Yes | ✅ Good | None - working correctly |
| components/forms/CustomerProfileForm.vue | ❌ No | ✅ Yes | ✅ Good | None - working correctly |
| composables/useConsultation.ts | ❌ No | ✅ Yes | 🔵 Info | Use in admin pages |
| composables/useCustomerProfile.ts | ❌ No | ✅ Yes | ✅ Good | Already implemented |
| composables/useHealthCheck.ts | ❌ No | ✅ Yes | ✅ Good | Already implemented |

**Legend**:
- 🔴 High Priority - Blocking real functionality
- 🟡 Medium Priority - Should be fixed soon
- 🔵 Info - Optimization opportunity
- ✅ Good - No action needed

---

## 9. TESTING RECOMMENDATIONS

Before removing mock data:
1. Verify backend endpoints return expected data structure
2. Test with empty/null data scenarios
3. Implement proper error handling
4. Add loading states for better UX
5. Use browser QA agent to test at http://localhost:3001

---

## 10. CONCLUSION

The Nuxt frontend has **good API integration for customer-facing features** (profile form, chat, consultation pages) but the **admin section relies heavily on mock data**. The infrastructure is in place (composables, API utils, proxy config), but admin pages need to be refactored to use the existing backend endpoints.

**Main Issue**: Admin pages were likely built with mock data for UI development and never connected to the real backend, even though the backend endpoints exist.

**Estimated Effort**:
- Admin pages cleanup: 4-6 hours
- Backend enhancements: 2-3 hours
- Testing: 2-3 hours
- **Total**: ~8-12 hours

---

## 11. IMPLEMENTATION PLAN

### Phase 1: Admin Dashboard (admin/index.vue)
1. Replace hardcoded consultations array with API call to `/api/admin/consultations`
2. Replace hardcoded compliance chart data with API call to `/api/admin/metrics/compliance`
3. Add loading states and error handling

### Phase 2: Admin Consultation Detail (admin/consultations/[id].vue) ✅ **COMPLETED**
1. ✅ Replace all mock consultation data with API call to `/api/admin/consultations/{id}`
2. ✅ Ensure transcript, insights, and compliance data come from backend
3. ✅ Add loading states and error handling

**Completion Date**: 2025-11-03
**Implementation Details**:
- Removed hardcoded mock data (lines 128-170)
- Added `useFetch` call to `/api/admin/consultations/{id}` with Bearer token authentication
- Implemented data transformation to map API response to UI structure:
  - `customer_name` → `customer`
  - `customer_age` → `age`
  - `metrics.avg_compliance_score` → `compliance`
  - `conversation` array → `transcript` array (filtered and formatted)
  - `outcome` data → `insights` object
- Added comprehensive loading state with spinner
- Added error state with retry button
- Added "no data" state for edge cases
- Tested with multiple consultation IDs:
  - Empty consultation (system message only)
  - Full consultation with customer/advisor messages
  - Non-existent consultation (404 error handling)

### Phase 3: Admin Metrics Page (admin/metrics.vue)
1. Replace all hardcoded metrics with API call to `/api/admin/metrics`
2. Update charts to use real data
3. Add loading states and error handling

### Phase 4: History Page (history.vue)
1. Remove placeholder values in data transformation (lines 100-109)
2. Ensure backend returns complete metadata (title, preview, message count, compliance, satisfaction)
3. If backend doesn't provide complete data, implement proper calculations from conversation array

### Phase 5: Admin Settings (admin/settings.vue) ✅ **COMPLETED**
1. ✅ Created backend settings endpoints: GET/PUT /api/admin/settings
2. ✅ Created database model (SystemSettings) with migration
3. ✅ Implemented Pydantic schemas with validation
4. ✅ Connected settings form to persist data to backend
5. ✅ Added comprehensive test suite (11 tests, all passing)
6. ✅ Tested settings persistence across page reloads

**Completion Date**: 2025-11-03
**Implementation Details**:
- Created single-row `system_settings` table in database
- Added GET/PUT endpoints with admin authentication
- Updated settings.vue to load/save from API with proper error handling
- Settings now persist correctly across page reloads
- Real toast notifications instead of fake ones
- Loading states and disabled buttons during save
- Comprehensive validation (email format, numeric ranges, required fields)
- Full test coverage with TDD approach

### Phase 6: Testing with Browser QA
1. Use Playwright browser agent to test at http://localhost:3001
2. Verify admin pages load real data correctly
3. Test error states and loading states
4. Verify no console errors or broken API calls
