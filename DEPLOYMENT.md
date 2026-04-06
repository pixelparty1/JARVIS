#!/usr/bin/env python3
"""
JARVIS Production Deployment Guide

This file contains instructions and scripts for deploying JARVIS in production environments.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# ============================================================================
# DEPLOYMENT CONFIGURATION
# ============================================================================

DEPLOYMENT_CONFIGS = {
    "development": {
        "description": "Local development environment",
        "python_version": "3.8+",
        "dependencies": ["PyQt6", "groq", "psutil", "SpeechRecognition"],
        "optimization": "none",
        "gpu_support": False,
        "monitoring": False,
        "logging_level": "DEBUG",
    },
    
    "staging": {
        "description": "Testing environment before production",
        "python_version": "3.9+",
        "dependencies": ["PyQt6", "groq", "psutil", "SpeechRecognition"],
        "optimization": "moderate",
        "gpu_support": True,
        "monitoring": True,
        "logging_level": "INFO",
    },
    
    "production": {
        "description": "Production deployment",
        "python_version": "3.9+",
        "dependencies": ["PyQt6", "groq", "psutil"],  # Voice optional in prod
        "optimization": "maximum",
        "gpu_support": True,
        "monitoring": True,
        "logging_level": "WARNING",
    },
    
    "enterprise": {
        "description": "Large-scale enterprise deployment",
        "python_version": "3.10+",
        "dependencies": ["PyQt6", "groq", "psutil", "redis", "prometheus-client"],
        "optimization": "maximum",
        "gpu_support": True,
        "monitoring": True,
        "logging_level": "ERROR",
    },
}

# ============================================================================
# DEPLOYMENT GUIDE
# ============================================================================

DEPLOYMENT_GUIDE = """
================================================================================
JARVIS PRODUCTION DEPLOYMENT GUIDE
================================================================================

## Table of Contents

1. Pre-Deployment Checklist
2. Environment Setup
3. Installation & Configuration
4. Testing & Validation
5. Deployment Strategies
6. Monitoring & Maintenance
7. Troubleshooting
8. Rollback Procedures

================================================================================
1. PRE-DEPLOYMENT CHECKLIST
================================================================================

Before deploying JARVIS to production, verify:

[ ] Python 3.9+ installed and configured
[ ] System meets minimum requirements (4GB RAM, 500MB disk)
[ ] Network connectivity verified (for Groq API)
[ ] SSL/TLS certificates obtained (for API communication)
[ ] Firewall rules configured
[ ] Backup procedures established
[ ] Monitoring and alerting configured
[ ] Disaster recovery plan documented
[ ] User training completed
[ ] Manager approval obtained

System Requirements:
- CPU: 2+ cores recommended
- RAM: 4GB minimum, 8GB recommended
- GPU: Optional (for vision processing)
- Disk: 500MB for installation + logs
- Network: Stable internet connection
- OS: Windows 10+, macOS 10.14+, Linux

================================================================================
2. ENVIRONMENT SETUP
================================================================================

### Step 1: Create Production Directory Structure

```bash
# Create application directory
mkdir -p /opt/jarvis
mkdir -p /opt/jarvis/logs
mkdir -p /opt/jarvis/data
mkdir -p /opt/jarvis/config
mkdir -p /opt/jarvis/backups

# Set permissions
chmod 755 /opt/jarvis
chmod 755 /opt/jarvis/logs
chmod 755 /opt/jarvis/data
```

### Step 2: Create Python Virtual Environment

```bash
# Create venv
python3.9 -m venv /opt/jarvis/venv

# Activate (Linux/macOS)
source /opt/jarvis/venv/bin/activate

# Activate (Windows)
/opt/jarvis/venv/Scripts/activate
```

### Step 3: Configure Environment Variables

Create `/opt/jarvis/config/.env`:

```env
# AI OS Configuration
JARVIS_MODE=production
JARVIS_LOG_LEVEL=INFO
JARVIS_LOG_FILE=/opt/jarvis/logs/jarvis.log

# Groq API
GROQ_API_KEY=your_api_key_here

# Backend Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=9000
BACKEND_TIMEOUT=30

# UI Configuration
JARVIS_THEME=neon_dark
JARVIS_WINDOW_WIDTH=800
JARVIS_WINDOW_HEIGHT=600

# Voice Configuration (optional)
VOICE_ENABLED=false
VOICE_MODEL=groq

# Monitoring
MONITORING_ENABLED=true
METRICS_PORT=8000
```

### Step 4: Create Production Configuration

Create `/opt/jarvis/config/production_config.py`:

```python
import os
from pathlib import Path

class ProductionConfig:
    # Application Settings
    SERVICE_NAME = "JARVIS AI Operating System"
    VERSION = "1.0.0"
    ENVIRONMENT = "production"
    DEBUG = False
    
    # Paths
    BASE_DIR = Path("/opt/jarvis")
    LOG_DIR = BASE_DIR / "logs"
    DATA_DIR = BASE_DIR / "data"
    CONFIG_DIR = BASE_DIR / "config"
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_FILE = LOG_DIR / "jarvis.log"
    MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB
    BACKUP_COUNT = 5
    
    # Backend
    BACKEND_HOST = os.getenv("BACKEND_HOST", "0.0.0.0")
    BACKEND_PORT = int(os.getenv("BACKEND_PORT", 9000))
    BACKEND_TIMEOUT = int(os.getenv("BACKEND_TIMEOUT", 30))
    
    # Security
    ENABLE_SSL = True
    SSL_CERT_FILE = CONFIG_DIR / "cert.pem"
    SSL_KEY_FILE = CONFIG_DIR / "key.pem"
    
    # Database (optional)
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    # Cache
    ENABLE_CACHE = True
    CACHE_TTL = 3600  # 1 hour
    
    # Task Management
    MAX_CONCURRENT_TASKS = 10
    TASK_TIMEOUT = 300  # 5 minutes
    
    # Monitoring
    MONITORING_ENABLED = os.getenv("MONITORING_ENABLED", "true").lower() == "true"
    METRICS_PORT = int(os.getenv("METRICS_PORT", 8000))
```

================================================================================
3. INSTALLATION & CONFIGURATION
================================================================================

### Step 1: Clone/Download JARVIS

```bash
# Copy JARVIS files to production directory
cp -r jarvis/* /opt/jarvis/

# Set appropriate permissions
chmod 755 /opt/jarvis/ui/launcher.py
chmod 755 /opt/jarvis/ai_os/main.py
```

### Step 2: Install Dependencies

```bash
# Activate virtual environment
source /opt/jarvis/venv/bin/activate  # Linux/macOS
# or
/opt/jarvis/venv/Scripts/activate  # Windows

# Install production dependencies
pip install --upgrade pip setuptools
pip install -r /opt/jarvis/ui/requirements.txt

# Optional: GPU support
# pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Optional: Additional tools
# pip install prometheus-client  # For metrics
# pip install gunicorn  # For running as service
```

### Step 3: Configure Security

```bash
# Generate SSL certificates (self-signed for testing)
openssl req -x509 -newkey rsa:4096 -nodes \\
    -out /opt/jarvis/config/cert.pem \\
    -keyout /opt/jarvis/config/key.pem \\
    -days 365

# Set restrictive permissions
chmod 600 /opt/jarvis/config/*.pem
chmod 600 /opt/jarvis/config/.env
```

### Step 4: Create Systemd Service (Linux)

Create `/etc/systemd/system/jarvis.service`:

```ini
[Unit]
Description=JARVIS AI Operating System
After=network.target

[Service]
Type=simple
User=jarvis
WorkingDirectory=/opt/jarvis
Environment="PATH=/opt/jarvis/venv/bin"
Environment="PYTHONUNBUFFERED=1"
EnvironmentFile=/opt/jarvis/config/.env
ExecStart=/opt/jarvis/venv/bin/python /opt/jarvis/ui/launcher.py
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Enable and start service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable jarvis.service
sudo systemctl start jarvis.service
```

================================================================================
4. TESTING & VALIDATION
================================================================================

### Step 1: Run Component Tests

```bash
cd /opt/jarvis
source venv/bin/activate
python ui/test_components.py
```

Expected output:
```
JARVIS UI - Component Test Suite
========================================================
[1/8] Testing PyQt6 import... ✓ PASS
[2/8] Testing Groq import... ✓ PASS
[3/8] Testing psutil import... ✓ PASS
[4/8] Testing jarvis_ui module... ✓ PASS
[5/8] Testing launcher module... ✓ PASS
[6/8] Testing AI OS availability... ✓ PASS
[7/8] Testing Python version... ✓ PASS (3.9)
[8/8] Checking system resources... ✓ PASS (4096MB free)
========================================================
Results: 8 passed, 0 failed
```

### Step 2: Launch in Test Mode

```bash
# Test interactive mode
python ui/launcher.py --interactive

# Test autonomous mode
python ui/launcher.py --autonomous

# Test demo
python ui/launcher.py --demo
```

### Step 3: Verify Backend

```bash
# Test AI OS
python ai_os/main.py --help

# Run demo workflow
python ai_os/main.py --help | grep demo
```

### Step 4: Load Testing (Optional)

```bash
# Simulate multiple concurrent tasks
# (Create load_test.py with appropriate tests)
python load_test.py --users 10 --duration 60
```

================================================================================
5. DEPLOYMENT STRATEGIES
================================================================================

### Strategy A: Direct Installation (Small Deployments)

1. Install on target machine
2. Configure environment
3. Start application
4. Verify operation

**Timeline**: 30 minutes
**Risk**: Medium
**Best for**: Individual users, small teams

### Strategy B: Staged Rollout (Medium Deployments)

1. Deploy to staging environment
2. Run full test suite
3. Deploy to production in phases
4. Monitor each phase

**Timeline**: 2-3 hours
**Risk**: Low
**Best for**: Organizations, critical systems

### Strategy C: Blue-Green Deployment (Large Deployments)

1. Maintain two identical production environments (Blue & Green)
2. Deploy to inactive environment (Green)
3. Run full tests on Green
4. Switch traffic to Green
5. Keep Blue as rollback

**Timeline**: 4-6 hours
**Risk**: Low
**Best for**: Mission-critical systems

### Strategy D: Canary Deployment (Progressive Rollout)

1. Deploy to small subset of users (5%)
2. Monitor metrics and errors
3. Gradually increase percentage (10%, 25%, 50%, 100%)
4. Automatic rollback on errors

**Timeline**: 1-2 days
**Risk**: Very Low
**Best for**: Large-scale deployments

================================================================================
6. MONITORING & MAINTENANCE
================================================================================

### Monitoring Tools

Set up monitoring for:
- CPU usage: Alert if > 80%
- Memory usage: Alert if > 85%
- Disk usage: Alert if > 90%
- API response time: Alert if > 5 seconds
- Error rate: Alert if > 1%
- Uptime: Track availability
- User count: Monitor concurrent users

### Health Checks

```bash
# Create health_check.py
#!/usr/bin/env python3
import requests
import sys

def check_health():
    try:
        # Check UI endpoint
        response = requests.get("http://localhost:9000/health", timeout=5)
        assert response.status_code == 200
        
        # Check AI OS endpoint
        response = requests.get("http://localhost:9000/api/status", timeout=5)
        assert response.status_code == 200
        
        print("✓ Health check passed")
        return 0
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(check_health())
```

### Scheduled Maintenance

Daily:
- Check logs for errors
- Monitor resource usage
- Verify all services running

Weekly:
- Backup user data
- Update security patches
- Review performance metrics
- Test disaster recovery

Monthly:
- Full system audit
- Update dependencies
- Review user feedback
- Plan capacity upgrades

================================================================================
7. TROUBLESHOOTING
================================================================================

### Issue: High Memory Usage

**Symptoms**: Memory grows over time
**Solution**:
1. Enable memory profiling
2. Identify memory leaks
3. Increase log cleanup frequency
4. Restart service daily (if needed)

### Issue: Slow Response Times

**Symptoms**: API calls taking > 5 seconds
**Solution**:
1. Check CPU usage
2. Monitor database queries
3. Enable caching
4. Scale horizontally if needed

### Issue: API Connection Failures

**Symptoms**: Cannot reach Groq API
**Solution**:
1. Check network connectivity
2. Verify API key
3. Check rate limiting
4. Review API status page

### Issue: UI Not Responsive

**Symptoms**: Frozen window, not responding
**Solution**:
1. Check for long-running tasks
2. Verify system resources
3. Check event loop blocking
4. Restart application

================================================================================
8. ROLLBACK PROCEDURES
================================================================================

### Quick Rollback (If Available)

```bash
# If using Blue-Green deployment:
# Switch back to previous environment
# Takes < 1 minute

# Example:
systemctl stop jarvis
# Point to previous environment
systemctl start jarvis
```

### Full Rollback

```bash
# 1. Stop current version
systemctl stop jarvis

# 2. Restore from backup
cp /opt/jarvis/backups/previous_version/* /opt/jarvis/

# 3. Verify configuration
grep "VERSION" /opt/jarvis/config/production_config.py

# 4. Restart service
systemctl start jarvis

# 5. Verify operation
python health_check.py
```

### Backup Strategy

```bash
# Daily backup script (backup_jarvis.sh)
#!/bin/bash
BACKUP_DIR="/opt/jarvis/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup data
tar -czf "$BACKUP_DIR/jarvis_data_$DATE.tar.gz" \\
    /opt/jarvis/data \\
    /opt/jarvis/config

# Keep last 7 days
find "$BACKUP_DIR" -mtime +7 -delete

# Verify backup
tar -tzf "$BACKUP_DIR/jarvis_data_$DATE.tar.gz" > /dev/null && \\
    echo "✓ Backup successful" || echo "✗ Backup failed"
```

================================================================================
QUICK DEPLOYMENT CHECKLIST
================================================================================

[ ] System requirements verified
[ ] Python 3.9+ installed
[ ] Virtual environment created
[ ] Dependencies installed
[ ] Environment variables configured
[ ] Configuration files created
[ ] SSL certificates generated
[ ] Systemd service created
[ ] Component tests passed
[ ] Health checks working
[ ] Backup procedures established
[ ] Monitoring configured
[ ] Documentation updated
[ ] User training completed
[ ] Go-live approval obtained

================================================================================
SUPPORT & ESCALATION
================================================================================

### First Level Support (Automated)
1. Run health_check.py
2. Check logs in /opt/jarvis/logs/
3. Restart service if needed
4. Review troubleshooting section

### Second Level Support (Manual)
1. Collect logs and diagnostics
2. Reproduce issue
3. Review recent changes
4. Consult documentation

### Escalation Path
1. Level 1: Automated health checks
2. Level 2: Manual troubleshooting
3. Level 3: Development team review
4. Level 4: Architecture redesign (if needed)

================================================================================
DEPLOYMENT COMPLETE
================================================================================

Your JARVIS installation is now ready for production use!

For ongoing support:
- Check logs: tail -f /opt/jarvis/logs/jarvis.log
- Monitor status: systemctl status jarvis
- View metrics: curl http://localhost:8000/metrics
- Run health check: python health_check.py

Welcome to production! 🚀
"""

# ============================================================================
# DEPLOYMENT HELPER FUNCTIONS
# ============================================================================

def print_deployment_guide(environment="production"):
    """Print deployment guide for specified environment"""
    print(DEPLOYMENT_GUIDE)
    print(f"\n\n{'='*80}")
    print(f"ENVIRONMENT: {environment.upper()}")
    print(f"{'='*80}\n")
    
    if environment in DEPLOYMENT_CONFIGS:
        config = DEPLOYMENT_CONFIGS[environment]
        print(f"Description: {config['description']}")
        print(f"Python: {config['python_version']}")
        print(f"GPU Support: {'Yes' if config['gpu_support'] else 'No'}")
        print(f"Monitoring: {'Enabled' if config['monitoring'] else 'Disabled'}")
        print(f"Optimization: {config['optimization']}")
        print(f"Log Level: {config['logging_level']}")


def generate_deployment_script(environment="production"):
    """Generate deployment script for the specified environment"""
    script = f"""#!/bin/bash
# JARVIS Deployment Script for {environment.upper() } Environment
# Generated: {datetime.now().isoformat()}

set -e  # Exit on error

echo "JARVIS Deployment Script"
echo "Environment: {environment.upper()}"
echo "Started: $(date)"
echo ""

# Configuration
JARVIS_DIR="/opt/jarvis"
VENV_DIR="$JARVIS_DIR/venv"
CONFIG_DIR="$JARVIS_DIR/config"
LOG_FILE="$JARVIS_DIR/logs/deployment.log"

# Create directories
echo "[1/5] Creating directories..."
mkdir -p "$JARVIS_DIR"
mkdir -p "$JARVIS_DIR/logs"
mkdir -p "$JARVIS_DIR/data"
mkdir -p "$CONFIG_DIR"
mkdir -p "$JARVIS_DIR/backups"

# Create virtual environment
echo "[2/5] Creating Python virtual environment..."
python3.9 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

# Install dependencies
echo "[3/5] Installing dependencies..."
pip install --upgrade pip setuptools
pip install -r "$JARVIS_DIR/ui/requirements.txt" 2>> "$LOG_FILE"

# Configure environment
echo "[4/5] Configuring environment..."
cat > "$CONFIG_DIR/.env" << 'EOF'
JARVIS_MODE={environment}
JARVIS_LOG_LEVEL=INFO
BACKENDS_HOST=0.0.0.0
BACKEND_PORT=9000
GROQ_API_KEY=${{GROQ_API_KEY:-your_api_key}}
EOF

# Run tests
echo "[5/5] Running tests..."
cd "$JARVIS_DIR"
python "$JARVIS_DIR/ui/test_components.py" 2>> "$LOG_FILE"

echo ""
echo "✓ Deployment completed successfully!"
echo "Started: $(date)"
echo "Log: $LOG_FILE"
echo ""
echo "Next steps:"
echo "1. Configure environment variables in $CONFIG_DIR/.env"
echo "2. Start application: python $JARVIS_DIR/ui/launcher.py"
echo "3. Run health checks: python health_check.py"
echo ""
"""
    return script


def create_health_check_script():
    """Create health check script"""
    script = '''#!/usr/bin/env python3
"""
JARVIS Health Check Script

Verifies system is running correctly and all components are healthy.
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path

class HealthChecker:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "status": "unknown",
            "checks": {},
            "errors": []
        }
    
    def check_python_version(self):
        """Check Python version"""
        try:
            assert sys.version_info >= (3, 9)
            self.results["checks"]["python_version"] = "✓ PASS"
            return True
        except AssertionError:
            self.results["checks"]["python_version"] = f"✗ FAIL (Python {sys.version_info.major}.{sys.version_info.minor})"
            return False
    
    def check_dependencies(self):
        """Check all dependencies are installed"""
        dependencies = ["PyQt6", "groq", "psutil"]
        all_ok = True
        
        for dep in dependencies:
            try:
                __import__(dep.lower().replace("-", "_"))
                self.results["checks"][f"dependency_{dep}"] = "✓"
            except ImportError:
                self.results["checks"][f"dependency_{dep}"] = "✗"
                all_ok = False
        
        return all_ok
    
    def check_system_resources(self):
        """Check system has adequate resources"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=1)
            
            checks = {
                "memory_available": memory.available > 500 * 1024 * 1024,  # 500MB
                "cpu_usage": cpu_percent < 98,
            }
            
            self.results["checks"]["memory"] = f"✓ {memory.available // (1024*1024)}MB available"
            self.results["checks"]["cpu"] = f"✓ {cpu_percent}% usage"
            
            return all(checks.values())
        except Exception as e:
            self.results["checks"]["system_resources"] = f"✗ {e}"
            return False
    
    def check_directories(self):
        """Check required directories exist"""
        dirs = ["/opt/jarvis/logs", "/opt/jarvis/data", "/opt/jarvis/config"]
        all_ok = True
        
        for d in dirs:
            if Path(d).exists():
                self.results["checks"][f"directory_{d}"] = "✓"
            else:
                self.results["checks"][f"directory_{d}"] = "✗"
                all_ok = False
        
        return all_ok
    
    def run_all(self):
        """Run all health checks"""
        results = []
        results.append(self.check_python_version())
        results.append(self.check_dependencies())
        results.append(self.check_system_resources())
        results.append(self.check_directories())
        
        self.results["status"] = "healthy" if all(results) else "degraded"
        return self
    
    def print_report(self):
        """Print health check report"""
        print(f"\\nJARVIS Health Check Report")
        print(f"Status: {self.results['status'].upper()}")
        print(f"Timestamp: {self.results['timestamp']}")
        print(f"\\nChecks:")
        for check, result in self.results["checks"].items():
            print(f"  - {check}: {result}")
        
        if self.results["errors"]:
            print(f"\\nErrors:")
            for error in self.results["errors"]:
                print(f"  - {error}")
        
        return self
    
    def to_json(self):
        """Return health check as JSON"""
        return json.dumps(self.results, indent=2)

if __name__ == "__main__":
    checker = HealthChecker()
    checker.run_all().print_report()
    
    sys.exit(0 if checker.results["status"] == "healthy" else 1)
'''
    return script


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="JARVIS Deployment Guide")
    parser.add_argument("--environment", choices=["development", "staging", "production", "enterprise"],
                        default="production", help="Deployment environment")
    parser.add_argument("--generate-script", action="store_true", help="Generate deployment script")
    parser.add_argument("--health-check", action="store_true", help="Generate health check script")
    
    args = parser.parse_args()
    
    if args.generate_script:
        script = generate_deployment_script(args.environment)
        print(script)
    elif args.health_check:
        script = create_health_check_script()
        print(script)
    else:
        print_deployment_guide(args.environment)
