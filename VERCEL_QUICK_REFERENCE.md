# ⚡ Quick Reference: Avoiding FUNCTION_INVOCATION_FAILED

## 🔴 Common Causes (Checklist)

- [ ] Missing or incorrect entry point
- [ ] Unhandled exceptions in initialization
- [ ] Using `app.run()` instead of exporting WSGI app
- [ ] Database connection issues (SQLite on Vercel)
- [ ] Missing dependencies in requirements.txt
- [ ] Timeout (operation took > 10 seconds)
- [ ] Out of memory
- [ ] Cold start issues with heavy imports

---

## ✅ Quick Fixes

### 1. Proper Flask Entry Point for Vercel

```python
# ❌ WRONG (Traditional)
if __name__ == '__main__':
    app.run()

# ✅ CORRECT (Serverless)
app = Flask(__name__)
# ... your routes ...
# Vercel auto-discovers 'app'
```

### 2. Safe Database Initialization

```python
# ❌ WRONG
db.create_all()  # No context!

# ✅ CORRECT
with app.app_context():
    db.create_all()
```

### 3. Error Handling

```python
# ❌ WRONG
@app.route('/api/data')
def get_data():
    return expensive_operation()  # Might crash

# ✅ CORRECT
@app.route('/api/data')
def get_data():
    try:
        result = expensive_operation()
        return jsonify(result), 200
    except Exception as e:
        app.logger.error(f"Error in get_data: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
```

### 4. Use PostgreSQL, Not SQLite

```python
# ❌ WRONG (Vercel filesystem is read-only)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

# ✅ CORRECT
import os
database_url = os.getenv('DATABASE_URL', 'sqlite:///app.db')  # Fallback for local dev
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
```

---

## 🛠️ Files Needed for Vercel Deployment

### 1. `api/index.py` (Entry point)

```python
from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return 'Hello Vercel!'

# Don't call app.run()!
```

### 2. `vercel.json` (Configuration)

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ]
}
```

### 3. `requirements.txt` (Dependencies)

```
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-CORS==4.0.0
psycopg2-binary==2.9.9
gunicorn==21.2.0
```

### 4. `.vercelignore` (Exclude files)

```
venv/
__pycache__/
*.pyc
.env
*.db
.git/
tests/
```

---

## 🚨 Debugging Steps

### 1. Check Vercel Logs

```bash
vercel logs --follow
```

Look for:
- ImportError (missing dependency)
- NameError (undefined variable)
- Database connection errors
- Timeout errors

### 2. Test Locally

```bash
# Install Vercel CLI
npm i -g vercel

# Run locally
vercel dev

# Check if it works at http://localhost:3000
```

### 3. Verify Environment Variables

```bash
# List env vars
vercel env ls

# Add missing variable
vercel env add DATABASE_URL
```

### 4. Check Function Limits

| Plan | Max Duration | Memory |
|------|--------------|--------|
| Hobby | 10s | 1024 MB |
| Pro | 60s | 3008 MB |
| Enterprise | 900s | 3008 MB |

If timing out, optimize or upgrade plan.

---

## 🎯 Platform-Specific Entry Points

| Platform | Entry Point | Example |
|----------|-------------|---------|
| **Vercel** | `app` variable in `api/*.py` | `app = Flask(__name__)` |
| **AWS Lambda** | `lambda_handler` function | `def lambda_handler(event, context):` |
| **Google Cloud** | Function matching entry point | `def hello_world(request):` |
| **Azure** | Function.json binding | `def main(req):` |
| **Railway/Render** | `app.run()` OK | `python run.py` |

---

## 💡 Pro Tips

### Tip 1: Use Environment Detection

```python
import os

IS_VERCEL = os.getenv('VERCEL') == '1'
IS_DEV = os.getenv('FLASK_ENV') == 'development'

if IS_VERCEL:
    # Vercel-specific config
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
elif IS_DEV:
    # Local development
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dev.db'
```

### Tip 2: Lazy Load Heavy Dependencies

```python
# ❌ WRONG (Slow cold start)
import pandas as pd
import numpy as np
import tensorflow as tf

# ✅ CORRECT (Load on demand)
@app.route('/api/analyze')
def analyze():
    import pandas as pd  # Only when needed
    df = pd.DataFrame(data)
    return df.to_json()
```

### Tip 3: Add Health Check

```python
@app.route('/api/health')
def health():
    return {'status': 'ok', 'timestamp': datetime.utcnow().isoformat()}
```

Test it:
```bash
curl https://your-app.vercel.app/api/health
```

### Tip 4: Use Vercel's Build Output

```bash
# See what's being deployed
vercel build

# Check .vercel/output directory
ls -la .vercel/output/functions/
```

---

## 🔄 Migration Checklist

Moving from traditional Flask to Vercel:

- [ ] Create `api/index.py` with WSGI app export
- [ ] Remove `app.run()` calls
- [ ] Add `vercel.json` configuration
- [ ] Switch from SQLite to PostgreSQL
- [ ] Update `requirements.txt`
- [ ] Add error handling to all routes
- [ ] Configure environment variables
- [ ] Test with `vercel dev`
- [ ] Deploy with `vercel --prod`
- [ ] Monitor logs for errors

---

## 📊 Decision Matrix: Should I Use Vercel?

| Factor | Vercel Good | Traditional Server Better |
|--------|-------------|---------------------------|
| **Traffic** | Unpredictable, bursty | Steady, predictable |
| **Scale** | Need to auto-scale | Fixed capacity OK |
| **Budget** | Low (pay per use) | Have server budget |
| **Maintenance** | Want zero ops | OK with server management |
| **Database** | External DB OK | Need local SQLite |
| **Execution Time** | < 10s requests | Long-running tasks |
| **State** | Stateless OK | Need in-memory state |
| **Cold Starts** | Can tolerate 1-3s delay | Need instant response |

**Your NFC Attendance System:**
- ✅ Unpredictable traffic (bursty during classes)
- ✅ Need HTTPS (Web NFC requirement)
- ⚠️ SQLite in use (need to migrate to PostgreSQL)
- ✅ Simple CRUD operations (< 10s)
- ❌ Educational use (might prefer simplicity)

**Recommendation: Render or Railway** (simpler for your use case)

---

## 🆘 Emergency Rollback

If deployment fails:

```bash
# View all deployments
vercel ls

# Rollback to previous deployment
vercel rollback <deployment-url>

# Or promote a specific deployment
vercel promote <deployment-url>
```

---

## 📞 Quick Support

1. **Vercel Logs**: `vercel logs`
2. **GitHub Issues**: Check Vercel Python runtime issues
3. **Discord**: Vercel community support
4. **Stack Overflow**: Tag with `vercel` and `flask`

---

**Last Updated:** January 2026
**Tested With:** Flask 3.0, Python 3.11, Vercel @vercel/python
