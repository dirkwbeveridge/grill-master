import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  // Asset generators overwrite committed artwork; keep them out of readiness tests.
  testIgnore: ['**/screenshots.spec.js', '**/icon-gen.spec.js'],
  timeout: 30000,
  expect: { timeout: 5000 },
  fullyParallel: false,
  reporter: [['list'], ['html', { open: 'never' }]],
  use: {
    baseURL: 'http://localhost:4173',
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure',
  },
  projects: [
    {
      name: 'iphone',
      use: { ...devices['iPhone 15 Pro'] },
    },
    {
      name: 'mobile-chromium',
      use: {
        ...devices['iPhone 15 Pro'],
        browserName: 'chromium',
        launchOptions: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH
          ? { executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH }
          : {},
      },
    },
  ],
  webServer: {
    command: 'npx http-server www -p 4173 -c-1 -s',
    url: 'http://localhost:4173',
    reuseExistingServer: true,
    timeout: 15000,
  },
});
