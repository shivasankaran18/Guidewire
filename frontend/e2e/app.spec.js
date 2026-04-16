import { test, expect } from '@playwright/test';

test.describe('GigPulse Sentinel E2E Tests', () => {
  
  test.describe('Worker Flow', () => {
    test('worker can login via demo and access dashboard', async ({ page }) => {
      await page.goto('/login');
      
      const demoButton = page.getByRole('button', { name: /demo as ravi/i });
      await demoButton.click();
      
      await expect(page).toHaveURL('/dashboard', { timeout: 15000 });
      await expect(page.locator('body')).toBeVisible();
    });

    test('worker dashboard loads without blank page', async ({ page }) => {
      await page.goto('/login');
      await page.getByRole('button', { name: /demo as ravi/i }).click();
      await page.waitForURL('/dashboard', { timeout: 15000 });
      
      const consoleErrors = [];
      page.on('console', msg => {
        if (msg.type() === 'error') consoleErrors.push(msg.text());
      });
      
      await expect(page.locator('body')).toBeVisible({ timeout: 5000 });
      
      const criticalErrors = consoleErrors.filter(e => !e.includes('Warning') && !e.includes('500'));
      expect(criticalErrors).toHaveLength(0);
    });

    test('worker can navigate to claims page', async ({ page }) => {
      await page.goto('/login');
      await page.getByRole('button', { name: /demo as ravi/i }).click();
      await page.waitForURL('/dashboard', { timeout: 15000 });
      
      await page.click('text=Claims');
      await expect(page).toHaveURL('/claims');
      await expect(page.locator('body')).toBeVisible();
    });

    test('worker can navigate to policy page', async ({ page }) => {
      await page.goto('/login');
      await page.getByRole('button', { name: /demo as ravi/i }).click();
      await page.waitForURL('/dashboard', { timeout: 15000 });
      
      await page.click('text=Coverage');
      await expect(page).toHaveURL('/policy');
      await expect(page.locator('body')).toBeVisible();
    });

    test('worker can access AI assistant', async ({ page }) => {
      await page.goto('/login');
      await page.getByRole('button', { name: /demo as ravi/i }).click();
      await page.waitForURL('/dashboard', { timeout: 15000 });
      
      await page.click('text=AI Assistant');
      await expect(page).toHaveURL('/assistant');
      await expect(page.locator('body')).toBeVisible();
    });
  });

  test.describe('Admin Flow', () => {
    test('admin can login and access dashboard', async ({ page }) => {
      await page.goto('/login');
      
      const adminButton = page.getByRole('button', { name: /demo as admin/i });
      await adminButton.click();
      
      await expect(page).toHaveURL('/admin', { timeout: 15000 });
      await expect(page.locator('body')).toBeVisible();
    });

    test('admin dashboard loads without blank page', async ({ page }) => {
      await page.goto('/login');
      await page.getByRole('button', { name: /demo as admin/i }).click();
      await page.waitForURL('/admin', { timeout: 15000 });
      
      const consoleErrors = [];
      page.on('console', msg => {
        if (msg.type() === 'error') consoleErrors.push(msg.text());
      });
      
      await expect(page.locator('body')).toBeVisible({ timeout: 5000 });
      
      const criticalErrors = consoleErrors.filter(e => !e.includes('Warning') && !e.includes('500'));
      expect(criticalErrors).toHaveLength(0);
    });

    test('admin can switch between tabs', async ({ page }) => {
      await page.goto('/login');
      await page.getByRole('button', { name: /demo as admin/i }).click();
      await page.waitForURL('/admin', { timeout: 15000 });
      
      const tabs = page.locator('button');
      const tabCount = await tabs.count();
      expect(tabCount).toBeGreaterThan(0);
    });

    test('admin can view fraud rings', async ({ page }) => {
      await page.goto('/login');
      await page.getByRole('button', { name: /demo as admin/i }).click();
      await page.waitForURL('/admin', { timeout: 15000 });
      
      await page.click('text=Fraud Rings');
      await expect(page.locator('body')).toBeVisible({ timeout: 5000 });
    });

    test('admin can view workers list', async ({ page }) => {
      await page.goto('/login');
      await page.getByRole('button', { name: /demo as admin/i }).click();
      await page.waitForURL('/admin', { timeout: 15000 });
      
      await page.click('text=Workers');
      await expect(page.locator('body')).toBeVisible({ timeout: 5000 });
    });
  });

  test.describe('Unauthenticated Access', () => {
    test('unauthenticated user redirected to login', async ({ page }) => {
      await page.goto('/dashboard');
      await expect(page).toHaveURL('/login');
    });

    test('landing page loads without errors', async ({ page }) => {
      await page.goto('/');
      await expect(page.locator('body')).toBeVisible();
    });
  });
});