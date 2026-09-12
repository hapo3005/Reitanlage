module.exports = {
  ci: {
    collect: {
      url: ['https://127.0.0.1:4174/'],
      numberOfRuns: 3,
      settings: {
        formFactor: 'mobile',
        screenEmulation: {
          mobile: true,
          width: 390,
          height: 844,
          deviceScaleFactor: 1,
          disabled: false,
        },
        throttlingMethod: 'simulate',
        chromeFlags: '--headless=new --no-sandbox --disable-dev-shm-usage --ignore-certificate-errors',
      },
    },
    assert: {
      assertions: {
        'categories:performance': ['error', { minScore: 0.95, aggregationMethod: 'median' }],
        'categories:accessibility': ['error', { minScore: 1, aggregationMethod: 'pessimistic' }],
        'categories:best-practices': ['error', { minScore: 1, aggregationMethod: 'pessimistic' }],
        'categories:seo': ['error', { minScore: 1, aggregationMethod: 'pessimistic' }],
        'first-contentful-paint': ['error', { maxNumericValue: 1800, aggregationMethod: 'median' }],
        'largest-contentful-paint': ['error', { maxNumericValue: 2500, aggregationMethod: 'median' }],
        'cumulative-layout-shift': ['error', { maxNumericValue: 0.1, aggregationMethod: 'pessimistic' }],
        'total-blocking-time': ['error', { maxNumericValue: 200, aggregationMethod: 'median' }],
      },
    },
    upload: {
      target: 'filesystem',
      outputDir: '_qa/lighthouse',
    },
  },
};
