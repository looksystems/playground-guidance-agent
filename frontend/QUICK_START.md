# Quick Start Guide

## Getting Started

### Start Development Server
```bash
cd /Users/adrian/Work/guidance-agent/frontend-nuxt
npm run dev
```

Visit: http://localhost:3000

### Run Tests
```bash
npm run test
```

### Run Tests with UI
```bash
npm run test:ui
```

### Build for Production
```bash
npm run build
```

---

## Project Overview

This is a Nuxt 3 application configured with:
- **Nuxt UI 4** - Component library
- **AI SDK** - For AI-powered features
- **Pinia** - State management
- **Vitest** - Testing framework
- **TypeScript** - Type safety

---

## Key Features Configured

### 1. API Proxy
All `/api/*` requests are proxied to `http://localhost:8000`

Example:
```typescript
// This will call http://localhost:8000/api/messages
const { data } = await useFetch('/api/messages')
```

### 2. Runtime Config
Access API base URL:
```typescript
const config = useRuntimeConfig()
console.log(config.public.apiBase) // http://localhost:8000
```

### 3. Design Tokens
All CSS custom properties are available:
```vue
<style scoped>
.container {
  padding: var(--space-4);
  border-radius: var(--radius-md);
  background: var(--color-primary-100);
}
</style>
```

### 4. Nuxt UI Components
Use Nuxt UI components out of the box:
```vue
<template>
  <UButton>Click me</UButton>
  <UCard>
    <template #header>
      Card Header
    </template>
    Card content here
  </UCard>
</template>
```

---

## File Structure

```
app/
├── app.vue              # Root component
├── pages/               # Auto-routed pages
├── components/          # Auto-imported components (create this)
└── layouts/             # Layout components (create this)

assets/
└── css/
    └── design-tokens.css

tests/
├── setup.ts             # Test configuration
└── *.test.ts            # Test files
```

---

## Next Steps

1. Create layouts in `app/layouts/`
2. Add pages in `app/pages/`
3. Build components in `app/components/`
4. Set up Pinia stores in `stores/`
5. Add composables in `composables/`

---

## Useful Links

- [Nuxt 3 Docs](https://nuxt.com)
- [Nuxt UI Docs](https://ui.nuxt.com)
- [AI SDK Docs](https://sdk.vercel.ai)
- [Pinia Docs](https://pinia.vuejs.org)
- [Vitest Docs](https://vitest.dev)
