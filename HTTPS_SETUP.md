# HTTPS Setup Guide for FastAPI Backend

## Overview

This guide shows how to configure CyberPanel/OpenLiteSpeed to act as a reverse proxy for your FastAPI application, enabling HTTPS access.

## Architecture

```
Browser (HTTPS) → CyberPanel/OpenLiteSpeed (Port 443) → FastAPI (Port 21580)
```

## Method 1: CyberPanel Reverse Proxy (Recommended)

### Step 1: Create API Subdomain

1. Log into CyberPanel: `https://your-server-ip:8090`
2. Navigate to **Websites** → **Create Website**
3. Fill in:
   - **Domain Name**: `api.hosting.austerfortia.fr`
   - **Email**: Your email
   - **Package**: Default package
   - **PHP**: Any version (won't be used)
4. Click **Create Website**

### Step 2: Issue SSL Certificate

1. Navigate to **SSL** → **Issue SSL**
2. Select domain: `api.hosting.austerfortia.fr`
3. Click **Issue SSL**
4. Wait for Let's Encrypt to issue the certificate

### Step 3: Configure Reverse Proxy

#### Option A: Via CyberPanel Rewrite Rules

1. Go to **Websites** → **List Websites**
2. Click **Manage** next to `api.hosting.austerfortia.fr`
3. Look for **Rewrite Rules** section
4. Add this rule:

```apache
RewriteEngine On
RewriteCond %{REQUEST_URI} !^/\.well-known/acme-challenge/
RewriteRule ^(.*)$ http://127.0.0.1:21580/$1 [P,L]
```

#### Option B: Via Virtual Host Configuration

Find your virtual host config:

```bash
# List virtual hosts
ls -la /usr/local/lsws/conf/vhosts/

# Edit the config for your API subdomain
nano /usr/local/lsws/conf/vhosts/api.hosting.austerfortia.fr/vhost.conf
```

Add this inside the `<VirtualHost>` block:

```apache
docRoot                   $VH_ROOT/public_html

# Context for root path
context / {
  type                    proxy
  handler                 lsapi:proxy
  addDefaultCharset       off
}

# External app definition
extprocessor proxy {
  type                    proxy
  address                 http://127.0.0.1:21580
  maxConns                1000
  pcKeepAliveTimeout      60
  initTimeout             60
  retryTimeout            0
  respBuffer              0
}

# Rewrite rules
rewrite  {
  enable                  1
  autoLoadHtaccess        1
  rules                   <<<END_rules
RewriteEngine On
RewriteCond %{REQUEST_URI} !^/\.well-known/acme-challenge/
RewriteRule ^(.*)$ http://127.0.0.1:21580/$1 [P,L]
  END_rules
}
```

#### Option C: Simple Proxy Context (Easiest)

Edit the same vhost.conf file and add:

```apache
context / {
  type                    proxy
  handler                 1
  addDefaultCharset       off
}

extprocessor 1 {
  type                    proxy
  address                 http://127.0.0.1:21580
  maxConns                1000
  initTimeout             60
  retryTimeout            0
  respBuffer              0
}
```

### Step 4: Restart OpenLiteSpeed

```bash
# Restart OpenLiteSpeed
systemctl restart lsws

# Or use the control script
/usr/local/lsws/bin/lswsctrl restart

# Check status
systemctl status lsws
```

### Step 5: Verify Configuration

```bash
# Test locally
curl http://127.0.0.1:21580/

# Test through HTTPS proxy
curl https://api.hosting.austerfortia.fr/

# Test with your frontend domain in CORS
curl -H "Origin: https://hosting.austerfortia.fr" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     https://api.hosting.austerfortia.fr/auth/login
```

## Method 2: Using Nginx (Alternative)

If you prefer Nginx or if OpenLiteSpeed doesn't work well:

### Install Nginx (if not already installed)

```bash
apt update
apt install nginx
```

### Configure Nginx as Reverse Proxy

Create a new Nginx site:

```bash
nano /etc/nginx/sites-available/api.hosting.austerfortia.fr
```

Add this configuration:

```nginx
upstream fastapi_backend {
    server 127.0.0.1:21580;
}

server {
    listen 80;
    server_name api.hosting.austerfortia.fr;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.hosting.austerfortia.fr;

    # SSL Configuration (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/api.hosting.austerfortia.fr/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.hosting.austerfortia.fr/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Logs
    access_log /var/log/nginx/api_access.log;
    error_log /var/log/nginx/api_error.log;

    # Proxy settings
    location / {
        proxy_pass http://fastapi_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (if needed later)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Let's Encrypt challenge
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
}
```

### Enable the Site and Get SSL

```bash
# Enable the site
ln -s /etc/nginx/sites-available/api.hosting.austerfortia.fr /etc/nginx/sites-enabled/

# Test Nginx configuration
nginx -t

# If using Certbot for SSL
apt install certbot python3-certbot-nginx
certbot --nginx -d api.hosting.austerfortia.fr

# Restart Nginx
systemctl restart nginx
```

## Method 3: Keep FastAPI on Port (Quick but Less Secure)

If you want FastAPI to handle HTTPS directly (not recommended):

### Generate SSL Certificate

```bash
# Using Let's Encrypt with standalone mode
certbot certonly --standalone -d api.hosting.austerfortia.fr
```

### Update FastAPI to Use SSL

Modify your `server/main.py`:

```python
if __name__ == "__main__":
    import ssl

    ssl_context = None
    if not dbg:  # Production mode
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(
            '/etc/letsencrypt/live/api.hosting.austerfortia.fr/fullchain.pem',
            '/etc/letsencrypt/live/api.hosting.austerfortia.fr/privkey.pem'
        )

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=443 if not dbg else port,
        reload=dbg,
        workers=workersnb,
        log_level="warning",
        access_log=dbg,
        ssl_keyfile=None if dbg else '/etc/letsencrypt/live/api.hosting.austerfortia.fr/privkey.pem',
        ssl_certfile=None if dbg else '/etc/letsencrypt/live/api.hosting.austerfortia.fr/fullchain.pem'
    )
```

**Note**: This approach requires running FastAPI on port 443, which requires root privileges and conflicts with CyberPanel.

## Recommended Setup Summary

**Best Practice**: Use Method 1 (CyberPanel Reverse Proxy)

This approach:
- ✅ Lets CyberPanel manage SSL certificates automatically
- ✅ FastAPI runs on non-privileged port (21580)
- ✅ CyberPanel handles SSL renewal
- ✅ Can run FastAPI as non-root user
- ✅ Better security and separation of concerns
- ✅ Easy to manage through CyberPanel UI

## Troubleshooting

### Test if FastAPI is accessible locally

```bash
curl http://127.0.0.1:21580/
# Should return: "Hosting API is running"
```

### Check OpenLiteSpeed logs

```bash
tail -f /usr/local/lsws/logs/error.log
tail -f /usr/local/lsws/logs/access.log
```

### Check if port 443 is being used

```bash
netstat -tlnp | grep :443
# or
ss -tlnp | grep :443
```

### Test HTTPS connection

```bash
# Basic test
curl -I https://api.hosting.austerfortia.fr/

# Verbose test to see SSL handshake
curl -v https://api.hosting.austerfortia.fr/

# Test from browser
# Open: https://api.hosting.austerfortia.fr/
```

### Common Issues

**Issue**: 502 Bad Gateway
- **Cause**: FastAPI is not running or not accessible on 127.0.0.1:21580
- **Solution**: Check if FastAPI is running: `ps aux | grep python | grep main.py`

**Issue**: SSL certificate errors
- **Cause**: SSL not properly issued or expired
- **Solution**: Re-issue SSL from CyberPanel: SSL → Issue SSL

**Issue**: CORS errors in browser
- **Cause**: Origin not allowed in FastAPI CORS settings
- **Solution**: Check CORS configuration in `server/main.py` (already updated)

**Issue**: Connection refused
- **Cause**: Firewall blocking port or service not running
- **Solution**:
  ```bash
  # Check firewall
  ufw status

  # Allow HTTPS if needed
  ufw allow 443/tcp

  # Check if OpenLiteSpeed is running
  systemctl status lsws
  ```

## Testing the Complete Setup

Once everything is configured:

1. **Test API directly**:
   ```bash
   curl https://api.hosting.austerfortia.fr/
   # Expected: "Hosting API is running"
   ```

2. **Test login endpoint**:
   ```bash
   curl -X POST https://api.hosting.austerfortia.fr/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "password": "password123"}'
   ```

3. **Test from frontend**:
   - Build and deploy your Angular app
   - Navigate to your login page
   - Try logging in
   - Check browser console for any errors

## Security Checklist

- [x] HTTPS enabled with valid SSL certificate
- [x] CORS configured to allow only your frontend domain
- [x] FastAPI not exposed directly to internet (only via reverse proxy)
- [ ] Firewall configured to block direct access to port 21580
- [ ] Rate limiting enabled on sensitive endpoints
- [ ] SSL certificate auto-renewal configured

## Firewall Configuration

Block direct access to FastAPI port from external connections:

```bash
# Allow only localhost to access port 21580
ufw deny 21580/tcp
ufw allow from 127.0.0.1 to any port 21580

# Or use iptables
iptables -A INPUT -p tcp --dport 21580 -s 127.0.0.1 -j ACCEPT
iptables -A INPUT -p tcp --dport 21580 -j DROP
```

This ensures FastAPI is only accessible through the reverse proxy, not directly from the internet.
