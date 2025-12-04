# Sentry Error Tracking Setup Guide

**Date:** 2025-12-04
**Status:** ✅ **IMPLEMENTATION COMPLETE**
**Components:** Python Backend + React Frontend
**Features:** Error tracking, Performance monitoring, Session replay, Data privacy

---

## 📋 Overview

Sentry is a comprehensive error tracking and performance monitoring platform for production environments. This setup provides:

- **Real-time Error Tracking**: Automatic capture of unhandled exceptions
- **Performance Monitoring**: Track response times, page load times, and API latency
- **Session Replay**: Record user sessions to understand what led to errors
- **Data Privacy**: Automatic filtering of sensitive data (auth tokens, cookies, file paths)
- **Alerting**: Real-time notifications when critical errors occur
- **Release Tracking**: Monitor errors across different app versions

---

## 🎯 Components Implemented

### 1. Python Backend - Sentry Integration

**File:** `src/monitoring/sentry_init.py`

**Features:**
- Flask integration for automatic error handling
- SQLAlchemy integration for database error tracking
- Sensitive data filtering (removes auth headers, cookies)
- File path redaction in error messages
- Environment-based configuration (development, staging, production)

**Key Functions:**
```python
# Initialize Sentry in your Flask app
init_sentry(environment='production', flask_app=app)

# Manual error capture
capture_exception(error, feature='claim_evaluation')
capture_message('Processing started', level='info', feature='game')

# User context
set_user_context(user_id='123', email='user@example.com')

# Custom context
set_context('claim_evaluation', {
    'patent_id': 'KR123456',
    'claim_type': 'independent',
})

# Tags for filtering
set_tag('evaluation_engine', 'ollama')
```

### 2. React Frontend - Sentry Integration

**File:** `web/src/monitoring/sentry.js`

**Features:**
- Automatic React error boundary support
- Performance monitoring with BrowserTracing
- Session replay (10% success rate, 100% on error)
- Custom profiler HOC for component performance tracking
- URL and console log filtering

**Key Functions:**
```javascript
// Initialize in App.js before rendering
initSentry({
  environment: 'production',
  dsn: process.env.REACT_APP_SENTRY_DSN,
  version: '0.1.0',
});

// Set user context
setSentryUser('123', 'user@example.com', 'john_doe');

// Manual error capture
captureError(error, { feature: 'claim_evaluation', action: 'submit' });

// Manual message logging
captureMessage('Game started', 'info', { level: 'level_2' });

// Component performance profiling
const GameScreen = withSentryProfiler(GameScreenComponent);

// Error boundary
<Sentry.ErrorBoundary>
  <YourComponent />
</Sentry.ErrorBoundary>
```

---

## 🚀 Setup Instructions

### Step 1: Create Sentry Account and Project

1. Go to [sentry.io](https://sentry.io)
2. Sign up for a free account
3. Create a new organization
4. Create two projects:
   - Project 1: "Patent Claim Game - Backend" (Python/Flask)
   - Project 2: "Patent Claim Game - Frontend" (JavaScript/React)

### Step 2: Get DSN (Data Source Name)

After creating projects:

1. **For Backend (Python):**
   - Go to Project Settings > Client Keys (DSN)
   - Copy the DSN (looks like: `https://examplePublicKey@o0.ingest.sentry.io/0`)

2. **For Frontend (React):**
   - Go to Project Settings > Client Keys (DSN)
   - Copy the DSN

### Step 3: Configure Environment Variables

**Backend (.env file in project root):**
```bash
# Sentry Configuration
SENTRY_DSN=https://examplePublicKey@o0.ingest.sentry.io/0
ENVIRONMENT=production  # development, staging, production
APP_VERSION=0.1.0
```

**Frontend (.env file in web/ directory):**
```bash
# Sentry Configuration
REACT_APP_SENTRY_DSN=https://examplePublicKey@o0.ingest.sentry.io/0
REACT_APP_ENVIRONMENT=production
REACT_APP_VERSION=0.1.0
```

### Step 4: Integrate with Flask Application

**In `src/main.py` or your app factory:**

```python
from flask import Flask
from src.monitoring import init_sentry

def create_app():
    app = Flask(__name__)

    # Initialize Sentry BEFORE creating routes
    init_sentry(
        environment=os.getenv('ENVIRONMENT', 'development'),
        flask_app=app
    )

    # Rest of your Flask setup...
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=False)  # Always use debug=False in production
```

**In your route error handlers:**

```python
from src.monitoring import capture_exception, set_user_context

@app.route('/evaluate-claim', methods=['POST'])
def evaluate_claim():
    try:
        data = request.json

        # Set user context for this request
        if hasattr(request, 'user_id'):
            set_user_context(request.user_id)

        # Your evaluation logic
        result = evaluate(data['claim'])

        return {'result': result}, 200

    except Exception as e:
        # Sentry automatically captures this via @app.errorhandler
        # But you can also manually capture with additional context
        capture_exception(e, feature='claim_evaluation')
        raise
```

### Step 5: Integrate with React Application

**In `web/src/App.js` or top-level component:**

```javascript
import React from 'react';
import { initSentry, ErrorBoundary } from './monitoring/sentry';
import GameScreen from './components/GameScreen';

// Initialize Sentry BEFORE rendering
initSentry({
  environment: process.env.REACT_APP_ENVIRONMENT || 'development',
  dsn: process.env.REACT_APP_SENTRY_DSN,
  version: process.env.REACT_APP_VERSION,
});

function App() {
  return (
    <ErrorBoundary>
      <GameScreen />
    </ErrorBoundary>
  );
}

export default App;
```

**In components that need error tracking:**

```javascript
import { setSentryUser, captureError, captureMessage } from '../monitoring/sentry';

function GameScreen() {
  useEffect(() => {
    // Set user context when component mounts
    const userId = localStorage.getItem('userId');
    if (userId) {
      setSentryUser(userId);
    }
  }, []);

  const handleClaimSubmit = async (claim) => {
    try {
      captureMessage('Claim submitted', 'info', { claim_length: claim.length });

      const response = await fetch('/evaluate-claim', {
        method: 'POST',
        body: JSON.stringify({ claim }),
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      captureError(error, {
        component: 'GameScreen',
        action: 'submit_claim',
        claim_length: claim.length,
      });
      throw error;
    }
  };

  return (
    // Your component JSX
  );
}
```

---

## 🧪 Testing Sentry Locally

### Test 1: Verify Backend Sentry Connection

**Create `test_sentry.py`:**

```python
import os
os.environ['SENTRY_DSN'] = 'https://examplePublicKey@o0.ingest.sentry.io/0'

from src.monitoring import init_sentry, capture_exception

# Initialize
init_sentry(environment='development')

# Test error capture
try:
    result = 1 / 0
except Exception as e:
    capture_exception(e)
    print("✅ Error captured! Check Sentry dashboard.")
```

**Run:**
```bash
python test_sentry.py
```

### Test 2: Verify Frontend Sentry Connection

**In browser console (after starting React app):**

```javascript
import { captureMessage, captureError } from './monitoring/sentry';

// Test message
captureMessage('Test message from console', 'info');

// Test error
try {
  throw new Error('Test error from console');
} catch (e) {
  captureError(e);
}

console.log('✅ Events sent to Sentry!');
```

### Test 3: Monitor Performance

The performance monitoring is automatic. After running the app for a few minutes:

1. Go to Sentry Dashboard > Performance
2. You should see:
   - Page load times
   - HTTP request durations
   - Database query times
   - Component render times

### Test 4: Check Session Replay

After an error occurs:

1. Go to Sentry Dashboard > Issues
2. Click on an issue
3. Scroll down to "Session Replay"
4. Watch the user's actions leading up to the error

---

## 📊 Sentry Dashboard Guide

### Important Sections

**1. Issues Dashboard**
- Lists all errors and their frequency
- Shows affected users, browser versions, OS
- Allows assignment and resolution

**2. Performance**
- Shows slowest transactions
- Identifies bottlenecks in your app
- Tracks Core Web Vitals

**3. Alerts**
- Create alerts for critical errors
- Set thresholds (e.g., "Alert if error rate > 1%")
- Send to Slack, email, PagerDuty, etc.

**4. Releases**
- Track errors by version
- Compare error rates between versions
- Set up source maps for better error details

**5. Team Settings**
- Configure team members and permissions
- Set up integrations (GitHub, Slack, etc.)
- Manage notifications

---

## 🔒 Privacy and Data Security

### What Sentry Captures

By default, Sentry captures:
- Error messages and stack traces
- User IP address
- Browser version and OS
- Device information (mobile vs desktop)
- Page URL
- HTTP headers

### What We Filter Out

Our configuration removes:
- **Auth Headers**: Authorization, Cookie headers
- **Query Parameters**: URL query strings
- **File Paths**: Absolute file paths in error messages
- **Console Logs**: Only error/warning level logs

### Additional Privacy Measures

To further protect user data:

```python
# In backend error handler
from src.monitoring import set_context

def before_request():
    # Set context without storing PII
    set_context('request', {
        'endpoint': request.endpoint,
        'method': request.method,
        'ip': request.remote_addr,
    })
```

```javascript
// In frontend
import { setContext } from './monitoring/sentry';

setContext('user_session', {
    session_duration: sessionDuration,
    features_used: featuresUsed,
    // Don't include: name, email, phone, etc.
});
```

---

## 🎓 Best Practices

### 1. Set User Context for Better Investigation

```python
# Backend
from src.monitoring import set_user_context

@app.before_request
def identify_user():
    user = get_current_user()
    if user:
        set_user_context(user.id, email=user.email)
```

### 2. Use Tags for Filtering

```javascript
// Frontend
import { setTag } from './monitoring/sentry';

// Add context-specific tags
setTag('game_level', currentLevel);
setTag('claim_type', claimType);
setTag('evaluation_engine', 'ollama');
```

This allows filtering issues in Sentry dashboard:
- Issues > Filter by level: 2
- Issues > Filter by evaluation_engine: ollama

### 3. Capture Meaningful Messages

```python
# Good: Specific context
capture_message(
    'Claim evaluation started',
    level='info',
    engine='ollama',
    claim_length=len(claim)
)

# Bad: Generic message
capture_message('Processing started', level='info')
```

### 4. Use Environment Separation

```bash
# Development
ENVIRONMENT=development
SENTRY_DSN=https://dev-key@o0.ingest.sentry.io/1

# Staging
ENVIRONMENT=staging
SENTRY_DSN=https://staging-key@o0.ingest.sentry.io/2

# Production
ENVIRONMENT=production
SENTRY_DSN=https://prod-key@o0.ingest.sentry.io/3
```

### 5. Monitor Performance Bottlenecks

```javascript
// Mark important operations
import * as Sentry from '@sentry/react';

const evalResult = await Sentry.startActiveSpan(
  {
    op: 'claim_evaluation',
    name: 'Evaluate Patent Claim',
  },
  async (span) => {
    const result = await evaluateClaim(claim);
    span.setTag('result', result.isValid ? 'valid' : 'invalid');
    return result;
  }
);
```

---

## 🔄 CI/CD Integration

### GitHub Actions with Sentry

**In `.github/workflows/deploy.yml`:**

```yaml
- name: Deploy to Production
  if: github.ref == 'refs/heads/main'
  run: |
    npm run build
    # Send release to Sentry
    curl -X POST https://sentry.io/api/0/organizations/your-org/releases/ \
      -H 'Authorization: Bearer YOUR_SENTRY_AUTH_TOKEN' \
      -d '{"version": "'${{ github.sha }}'"}'

- name: Notify Sentry of Deployment
  run: |
    sentry-cli releases \
      --org your-org \
      --project your-project \
      deploys ${{ github.sha }} create \
      --environment production
```

---

## 🐛 Troubleshooting

### Issue 1: Events Not Appearing in Sentry

**Checklist:**
- [ ] Is the DSN correct? (Check in Sentry project settings)
- [ ] Is network request to sentry.io being blocked? (Check browser console)
- [ ] Is the environment variable set? (Check `process.env.REACT_APP_SENTRY_DSN`)
- [ ] Are you in development with `sample_rate: 0.5`? (May not capture all errors)

**Solution:**
```javascript
// Check if Sentry initialized
import * as Sentry from '@sentry/react';
console.log(Sentry.getCurrentHub().getClient()); // Should show client info
```

### Issue 2: Sensitive Data Leaking

**Problem:** Password or API key visible in Sentry

**Solution:**
```python
# Add custom redaction
def filter_sensitive_data(event, hint):
    if 'request' in event:
        for header in ['Authorization', 'X-API-Key']:
            if header in event['request'].get('headers', {}):
                event['request']['headers'][header] = '[REDACTED]'
    return event
```

### Issue 3: Too Many Events (High Costs)

**Solution:**
```python
# Reduce sample rate in development
sentry_sdk.init(
    dsn=dsn,
    sample_rate=0.1 if environment == 'production' else 0.01,
)
```

### Issue 4: Session Replay Not Recording

**Check:**
- Is the user experiencing an error? (Replay only captures on error by default)
- Is the browser supported? (Most modern browsers supported)
- Check browser console for errors

**Solution:**
```javascript
// Force record all sessions (more expensive)
new Sentry.Replay({
  maskAllText: true,
  blockAllMedia: true,
  // Record all sessions, not just on error
  sessionSampleRate: 1.0,
  replaysOnErrorSampleRate: 1.0,
})
```

---

## 📈 Monitoring Metrics

### Key Metrics to Track

1. **Error Rate**: Errors per minute
   - Alert if > 1 error/minute

2. **Affected Users**: Number of unique users affected
   - Alert if > 100 users affected per hour

3. **Average Response Time**: API latency
   - Alert if > 500ms

4. **Page Load Time**: Frontend performance
   - Alert if > 3 seconds

5. **Release Stability**: Error rate by version
   - Monitor after each deployment

---

## ✅ Checklist

- [ ] Sentry account created
- [ ] Projects created (Backend + Frontend)
- [ ] DSN keys copied
- [ ] Environment variables configured (.env files)
- [ ] Backend: `init_sentry()` called in Flask app factory
- [ ] Frontend: `initSentry()` called in App.js
- [ ] Error Boundary wrapped around components
- [ ] Test error captured successfully
- [ ] Sentry dashboard verified
- [ ] Team members invited
- [ ] Alerts configured
- [ ] GitHub Actions integration updated

---

## 📚 Resources

- [Sentry Documentation](https://docs.sentry.io/)
- [Sentry Python SDK](https://docs.sentry.io/platforms/python/)
- [Sentry React SDK](https://docs.sentry.io/platforms/javascript/guides/react/)
- [Performance Monitoring Guide](https://docs.sentry.io/product/performance/)
- [Session Replay Guide](https://docs.sentry.io/product/session-replay/)

---

## 🎯 Next Steps

### Phase 2 Completion
- [ ] Create Sentry account and projects
- [ ] Configure DSN environment variables
- [ ] Integrate Flask app initialization
- [ ] Integrate React app initialization
- [ ] Test error capture locally
- [ ] Deploy to staging and monitor

### Phase 3 (Optional Enhancements)
- [ ] Configure GitHub integration for issue creation
- [ ] Set up Slack alerts for critical errors
- [ ] Create custom dashboards for monitoring
- [ ] Implement performance budgets
- [ ] Set up source maps for better stack traces

---

**Status:** 🟢 **Ready for Implementation**
**Next:** Follow Setup Instructions to activate Sentry monitoring

