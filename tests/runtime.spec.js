const { test, expect } = require('@playwright/test');

test('runtime inicializa sem exceções JavaScript', async ({ page }) => {
  const pageErrors = [];
  const consoleErrors = [];
  page.on('pageerror', error => pageErrors.push(error.stack || error.message));
  page.on('console', msg => { if (msg.type() === 'error') consoleErrors.push(msg.text()); });
  await page.goto('/');
  await page.waitForTimeout(250);
  expect(pageErrors, `Page errors: ${pageErrors.join('\n---\n')}`).toEqual([]);
  expect(consoleErrors, `Console errors: ${consoleErrors.join('\n---\n')}`).toEqual([]);
  await expect(page.locator('#emotion_0')).toHaveCount(1);
  await expect(page.locator('#progressCard')).toHaveAttribute('role', 'progressbar');
});
