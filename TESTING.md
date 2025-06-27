# Testing Guide

This document explains the testing setup and how to run tests for both frontend and backend components.

## Test Mode / Development Mode

The application includes a special test/development mode that bypasses Entra ID authentication for easier development and testing.

### Enabling Test Mode

**Frontend:**
```bash
# Set environment variable
NEXT_PUBLIC_TEST_MODE=true

# Or use the npm script
npm run dev:test
```

**Backend:**
```bash
# Set environment variable
TEST_MODE=true

# Or use the npm script  
npm run backend:test
```

**Both together:**
```bash
npm run dev:test-full
```

### Test Mode Features

- **No Authentication Required**: Bypasses Entra ID login
- **Mock User Data**: Uses predefined test user credentials
- **Test Mode Indicators**: Visual indicators in the UI
- **Simplified Development**: No need for Azure AD setup during development

## Frontend Testing

### Setup

Frontend tests use Jest with React Testing Library:

- **Jest**: Test runner and assertion library
- **React Testing Library**: Component testing utilities
- **@testing-library/user-event**: User interaction simulation
- **@testing-library/jest-dom**: Additional Jest matchers

### Running Frontend Tests

```bash
# Run all frontend tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage report
npm run test:coverage
```

### Test Files Location

```
src/
├── __tests__/
│   ├── CreateLinkForm.test.tsx
│   ├── LinkList.test.tsx
│   ├── testConfig.test.ts
│   └── integration.test.tsx
└── components/
    └── [component files]
```

### Writing Frontend Tests

Example test structure:

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MyComponent } from '../components/MyComponent';

describe('MyComponent', () => {
  test('renders correctly', () => {
    render(<MyComponent />);
    expect(screen.getByText('Expected Text')).toBeDefined();
  });
  
  test('handles user interaction', async () => {
    const user = userEvent.setup();
    render(<MyComponent />);
    
    await user.click(screen.getByRole('button'));
    expect(screen.getByText('Updated Text')).toBeDefined();
  });
});
```

## Backend Testing

### Setup

Backend tests use pytest with async support:

- **pytest**: Test runner and assertion library
- **pytest-asyncio**: Async/await support
- **pytest-cov**: Coverage reporting
- **httpx**: Async HTTP client for API testing

### Running Backend Tests

```bash
# Run all backend tests
npm run test:backend

# Run backend tests with coverage
npm run test:backend-coverage

# Run specific test file
cd backend && python -m pytest tests/test_api.py

# Run with verbose output
cd backend && python -m pytest -v
```

### Test Files Location

```
backend/
├── tests/
│   ├── conftest.py          # Test configuration and fixtures
│   ├── test_api.py          # API endpoint tests
│   └── test_models.py       # (Future) Model tests
├── main.py
└── requirements.txt
```

### Writing Backend Tests

Example test structure:

```python
import pytest
from httpx import AsyncClient

class TestAPI:
    async def test_create_link(self, async_client: AsyncClient, auth_headers: dict):
        response = await async_client.post(
            "/api/links",
            json={"original_url": "https://example.com"},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "short_code" in data
```

## Integration Testing

### Full Application Testing

```bash
# Run both frontend and backend tests
npm run test:all

# Start both servers in test mode
npm run dev:test-full
```

### Test Database

- Backend tests use a temporary SQLite database
- Database is created and destroyed for each test session
- No interference with development data

## Test Coverage

### Frontend Coverage

Run `npm run test:coverage` to generate coverage reports:

```
coverage/
├── lcov-report/
│   └── index.html       # Detailed HTML coverage report
└── lcov.info           # Machine-readable coverage data
```

### Backend Coverage

Run `npm run test:backend-coverage` to generate coverage reports:

```
backend/
├── htmlcov/
│   └── index.html       # Detailed HTML coverage report
└── .coverage           # Coverage database
```

## Continuous Integration

### GitHub Actions (Example)

```yaml
name: Tests
on: [push, pull_request]

jobs:
  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm test
      
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: pip install -r backend/requirements.txt
      - run: cd backend && python -m pytest
```

## Mocking and Test Data

### Frontend Mocks

- **API calls**: Mocked using Jest
- **MSAL authentication**: Mocked with test configuration
- **External dependencies**: Mocked in jest.setup.js

### Backend Mocks

- **Authentication**: Test mode bypasses JWT validation
- **Database**: Temporary database for each test session
- **External APIs**: Can be mocked using pytest fixtures

## Debugging Tests

### Frontend

```bash
# Debug specific test
npm test -- --testNamePattern="specific test name"

# Debug with additional output
npm test -- --verbose

# Debug in watch mode
npm run test:watch
```

### Backend

```bash
# Debug specific test
cd backend && python -m pytest -k "test_name" -s

# Debug with print statements
cd backend && python -m pytest --capture=no

# Debug with pdb
cd backend && python -m pytest --pdb
```

## Best Practices

### Frontend

1. **Use semantic queries**: `getByRole`, `getByLabelText`, etc.
2. **Test user behavior**: Focus on what users do, not implementation
3. **Mock external dependencies**: API calls, authentication, etc.
4. **Use proper async/await**: For user interactions and API calls

### Backend

1. **Use fixtures**: For common setup and test data
2. **Test error cases**: Not just happy paths
3. **Use async patterns**: Properly handle async operations
4. **Isolate tests**: Each test should be independent

### General

1. **Write descriptive test names**: Clearly describe what is being tested
2. **Keep tests focused**: One concept per test
3. **Use arrange-act-assert pattern**: Clear test structure
4. **Maintain test data**: Keep test data realistic but minimal
