# Radio Button Testing Examples

## Playwright E2E Test Examples

### Example 1: Basic Click Interaction
```typescript
import { test, expect } from '@playwright/test';

test('should select radio button by clicking', async ({ page }) => {
  await page.goto('/');

  // Click using data-testid
  await page.click('[data-testid="topic-consolidation"]');

  // Verify selection via aria-checked
  await expect(page.locator('[data-testid="topic-consolidation"]'))
    .toHaveAttribute('aria-checked', 'true');

  // Verify other options are not selected
  await expect(page.locator('[data-testid="topic-withdrawal"]'))
    .toHaveAttribute('aria-checked', 'false');
});
```

### Example 2: Using Accessible Role and Name
```typescript
test('should select radio button using accessible selectors', async ({ page }) => {
  await page.goto('/');

  // Click using role and accessible name
  await page.getByRole('radio', { name: 'Consolidating pensions' }).click();

  // Verify checked state
  const radio = page.getByRole('radio', { name: 'Consolidating pensions' });
  await expect(radio).toHaveAttribute('aria-checked', 'true');
});
```

### Example 3: Keyboard Navigation
```typescript
test('should select radio button using keyboard', async ({ page }) => {
  await page.goto('/');

  // Tab to first name field
  await page.keyboard.press('Tab');
  await page.fill('[name="firstName"]', 'John');

  // Tab to age field
  await page.keyboard.press('Tab');
  await page.fill('[name="age"]', '55');

  // Tab to first radio option
  await page.keyboard.press('Tab');

  // Select with Space key
  await page.keyboard.press('Space');

  // Verify selection
  await expect(page.locator('[data-testid="topic-consolidation"]'))
    .toHaveAttribute('aria-checked', 'true');

  // Tab to next option
  await page.keyboard.press('Tab');

  // Select with Enter key
  await page.keyboard.press('Enter');

  // Verify new selection
  await expect(page.locator('[data-testid="topic-withdrawal"]'))
    .toHaveAttribute('aria-checked', 'true');
});
```

### Example 4: Form Submission with Radio Selection
```typescript
test('should submit form with selected radio value', async ({ page }) => {
  await page.goto('/');

  // Fill form
  await page.fill('[name="firstName"]', 'Jane');
  await page.fill('[name="age"]', '60');

  // Select radio option
  await page.click('[data-testid="topic-tax"]');

  // Intercept API call
  const responsePromise = page.waitForResponse('/api/consultations');

  // Submit form
  await page.click('button[type="submit"]');

  // Verify API payload
  const response = await responsePromise;
  const payload = await response.request().postDataJSON();

  expect(payload.initial_query).toBe('tax');
  expect(payload.name).toBe('Jane');
  expect(payload.age).toBe(60);
});
```

### Example 5: Visual Regression (Screenshot Comparison)
```typescript
test('should display selected radio button correctly', async ({ page }) => {
  await page.goto('/');

  // Take screenshot of unselected state
  const formSelector = '[class*="radio-group-wrapper"]';
  await expect(page.locator(formSelector)).toHaveScreenshot('radio-unselected.png');

  // Select option
  await page.click('[data-testid="topic-understanding"]');

  // Take screenshot of selected state
  await expect(page.locator(formSelector)).toHaveScreenshot('radio-selected.png');
});
```

### Example 6: Multiple Selection Changes
```typescript
test('should update selection when different option is clicked', async ({ page }) => {
  await page.goto('/');

  // Select first option
  await page.click('[data-testid="topic-consolidation"]');
  await expect(page.locator('[data-testid="topic-consolidation"]'))
    .toHaveAttribute('aria-checked', 'true');

  // Select second option
  await page.click('[data-testid="topic-withdrawal"]');

  // Verify first is deselected
  await expect(page.locator('[data-testid="topic-consolidation"]'))
    .toHaveAttribute('aria-checked', 'false');

  // Verify second is selected
  await expect(page.locator('[data-testid="topic-withdrawal"]'))
    .toHaveAttribute('aria-checked', 'true');
});
```

## Vitest Unit Test Examples

### Example 1: Direct Method Call
```typescript
import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import CustomerProfileForm from '~/components/forms/CustomerProfileForm.vue';

describe('CustomerProfileForm Radio Buttons', () => {
  it('should update form.topic when selectTopic is called', () => {
    const wrapper = mount(CustomerProfileForm);

    // Call exposed method
    wrapper.vm.selectTopic('consolidation');

    // Verify state updated
    expect(wrapper.vm.form.topic).toBe('consolidation');
  });

  it('should update when different values are selected', () => {
    const wrapper = mount(CustomerProfileForm);

    wrapper.vm.selectTopic('consolidation');
    expect(wrapper.vm.form.topic).toBe('consolidation');

    wrapper.vm.selectTopic('withdrawal');
    expect(wrapper.vm.form.topic).toBe('withdrawal');

    wrapper.vm.selectTopic('tax');
    expect(wrapper.vm.form.topic).toBe('tax');
  });
});
```

### Example 2: Click Event Simulation
```typescript
it('should update form.topic when radio option is clicked', async () => {
  const wrapper = mount(CustomerProfileForm);

  // Find radio option wrapper
  const radioOption = wrapper.find('[data-testid="topic-withdrawal"]');

  // Simulate click
  await radioOption.trigger('click');

  // Verify state updated
  expect(wrapper.vm.form.topic).toBe('withdrawal');
});
```

### Example 3: Keyboard Event Simulation
```typescript
it('should update form.topic when Enter key is pressed', async () => {
  const wrapper = mount(CustomerProfileForm);

  // Find radio option wrapper
  const radioOption = wrapper.find('[data-testid="topic-understanding"]');

  // Simulate Enter key
  await radioOption.trigger('keydown.enter');

  // Verify state updated
  expect(wrapper.vm.form.topic).toBe('understanding');
});

it('should update form.topic when Space key is pressed', async () => {
  const wrapper = mount(CustomerProfileForm);

  // Find radio option wrapper
  const radioOption = wrapper.find('[data-testid="topic-other"]');

  // Simulate Space key
  await radioOption.trigger('keydown.space');

  // Verify state updated
  expect(wrapper.vm.form.topic).toBe('other');
});
```

### Example 4: Accessibility Attributes
```typescript
it('should have correct ARIA attributes', () => {
  const wrapper = mount(CustomerProfileForm);

  // Select a topic
  wrapper.vm.selectTopic('consolidation');

  // Find selected radio
  const selectedRadio = wrapper.find('[data-testid="topic-consolidation"]');

  // Verify ARIA attributes
  expect(selectedRadio.attributes('role')).toBe('radio');
  expect(selectedRadio.attributes('aria-checked')).toBe('true');
  expect(selectedRadio.attributes('aria-label')).toBe('Consolidating pensions');
  expect(selectedRadio.attributes('tabindex')).toBe('0');
});

it('should have correct ARIA attributes for unselected radio', () => {
  const wrapper = mount(CustomerProfileForm);

  // Select one topic
  wrapper.vm.selectTopic('consolidation');

  // Find unselected radio
  const unselectedRadio = wrapper.find('[data-testid="topic-withdrawal"]');

  // Verify ARIA attributes
  expect(unselectedRadio.attributes('role')).toBe('radio');
  expect(unselectedRadio.attributes('aria-checked')).toBe('false');
  expect(unselectedRadio.attributes('aria-label')).toBe('Considering pension withdrawal');
  expect(unselectedRadio.attributes('tabindex')).toBe('0');
});
```

### Example 5: Visual State Changes
```typescript
it('should update visual classes when selected', async () => {
  const wrapper = mount(CustomerProfileForm);

  // Select topic
  wrapper.vm.selectTopic('tax');
  await wrapper.vm.$nextTick();

  // Find label element
  const selectedLabel = wrapper.find('[data-testid="topic-tax"] label');

  // Verify selected classes
  expect(selectedLabel.classes()).toContain('border-primary-500');
  expect(selectedLabel.classes()).toContain('bg-primary-50');

  // Find unselected option
  const unselectedLabel = wrapper.find('[data-testid="topic-other"] label');

  // Verify unselected classes
  expect(unselectedLabel.classes()).toContain('border-gray-300');
  expect(unselectedLabel.classes()).toContain('bg-white');
});
```

### Example 6: Integration with Form Submission
```typescript
it('should include selected topic in form submission', async () => {
  const wrapper = mount(CustomerProfileForm);

  // Fill form
  wrapper.vm.form.firstName = 'John';
  wrapper.vm.form.age = 55;
  wrapper.vm.selectTopic('consolidation');

  // Mock API call
  const mockFetch = vi.fn().mockResolvedValue({ id: 'test-123' });
  global.$fetch = mockFetch;

  // Submit form
  await wrapper.vm.onSubmit({
    data: {
      firstName: 'John',
      age: 55,
      topic: 'consolidation'
    }
  });

  // Verify API called with correct data
  expect(mockFetch).toHaveBeenCalledWith(
    '/api/consultations',
    expect.objectContaining({
      method: 'POST',
      body: {
        name: 'John',
        age: 55,
        initial_query: 'consolidation'
      }
    })
  );
});
```

## Accessibility Testing Examples (axe-core)

### Example 1: Basic Accessibility Scan
```typescript
import { injectAxe, checkA11y } from 'axe-playwright';

test('radio buttons should pass accessibility scan', async ({ page }) => {
  await page.goto('/');
  await injectAxe(page);

  // Run accessibility scan
  await checkA11y(page, '.radio-group-wrapper', {
    detailedReport: true,
    detailedReportOptions: { html: true }
  });
});
```

### Example 2: Specific WCAG Rules
```typescript
test('radio buttons should meet WCAG 2.1 AA', async ({ page }) => {
  await page.goto('/');

  const results = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
    .include('.radio-group-wrapper')
    .analyze();

  expect(results.violations).toEqual([]);
});
```

### Example 3: Keyboard Navigation Accessibility
```typescript
test('radio buttons should be keyboard accessible', async ({ page }) => {
  await page.goto('/');

  // Verify focusable
  const firstRadio = page.locator('[data-testid="topic-consolidation"]');
  await firstRadio.focus();

  const isFocused = await firstRadio.evaluate(el =>
    el === document.activeElement
  );
  expect(isFocused).toBe(true);

  // Verify tabindex
  await expect(firstRadio).toHaveAttribute('tabindex', '0');
});
```

### Example 4: Screen Reader Announcements
```typescript
test('radio buttons should have proper ARIA labels', async ({ page }) => {
  await page.goto('/');

  const radios = await page.locator('[role="radio"]').all();

  expect(radios.length).toBe(5); // 5 topic options

  for (const radio of radios) {
    // Each should have aria-label
    const ariaLabel = await radio.getAttribute('aria-label');
    expect(ariaLabel).toBeTruthy();

    // Each should have aria-checked
    const ariaChecked = await radio.getAttribute('aria-checked');
    expect(['true', 'false']).toContain(ariaChecked);
  }
});
```

## Mobile Testing Examples

### Example 1: Touch Interaction
```typescript
test.use({ viewport: { width: 375, height: 667 } }); // iPhone SE

test('should work on mobile with touch', async ({ page }) => {
  await page.goto('/');

  // Simulate touch
  await page.locator('[data-testid="topic-withdrawal"]').tap();

  // Verify selection
  await expect(page.locator('[data-testid="topic-withdrawal"]'))
    .toHaveAttribute('aria-checked', 'true');
});
```

### Example 2: Minimum Touch Target Size (WCAG 2.5.5)
```typescript
test('radio buttons should meet minimum touch target size', async ({ page }) => {
  await page.goto('/');

  const radio = page.locator('[data-testid="topic-consolidation"]');
  const box = await radio.boundingBox();

  // WCAG requires 44x44px minimum
  expect(box.height).toBeGreaterThanOrEqual(44);
  expect(box.width).toBeGreaterThanOrEqual(44);
});
```

## Performance Testing Examples

### Example 1: Measure Selection Speed
```typescript
test('radio selection should be fast', async ({ page }) => {
  await page.goto('/');

  const startTime = Date.now();

  // Select option
  await page.click('[data-testid="topic-tax"]');

  // Verify updated
  await expect(page.locator('[data-testid="topic-tax"]'))
    .toHaveAttribute('aria-checked', 'true');

  const endTime = Date.now();
  const duration = endTime - startTime;

  // Should complete in under 100ms
  expect(duration).toBeLessThan(100);
});
```

### Example 2: Rapid Selection Changes
```typescript
test('should handle rapid selection changes', async ({ page }) => {
  await page.goto('/');

  const options = [
    'consolidation',
    'withdrawal',
    'understanding',
    'tax',
    'other'
  ];

  // Rapidly select different options
  for (const option of options) {
    await page.click(`[data-testid="topic-${option}"]`);
    await expect(page.locator(`[data-testid="topic-${option}"]`))
      .toHaveAttribute('aria-checked', 'true');
  }

  // Verify final selection is correct
  await expect(page.locator('[data-testid="topic-other"]'))
    .toHaveAttribute('aria-checked', 'true');
});
```

## Summary

These testing examples demonstrate:
- ✅ Click interactions work with Playwright
- ✅ Keyboard navigation is fully functional
- ✅ Accessibility attributes are correct
- ✅ Visual states update properly
- ✅ Form submission includes correct values
- ✅ Mobile touch interactions work
- ✅ Performance is acceptable

All tests should pass with the fixed radio button implementation.
