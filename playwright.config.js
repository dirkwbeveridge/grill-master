import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  timeout: 30000,
  expect: { timeout: 5000 },
  fullyParallel: false,
  reporter: [['list'], ['html', { open: 'never' }]],
  use: {
    baseURL: 'http://localhost:4173',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    trace: 'retain-on-failure',
  },
  projects: [
    {
      name: 'iphone',
      use: { ...devices['iPhone 15 Pro'] },
    },
  ],
  webServer: {
    command: 'npx http-server www -p 4173 -c-1 -s',
    url: 'http://localhost:4173',
    reuseExistingServer: true,
    timeout: 15000,
  },
});
