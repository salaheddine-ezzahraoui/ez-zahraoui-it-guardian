# Security Considerations

## Current Implementation

### Secrets Management
- All secrets in `.env` files (not committed to Git)
- `.env.example` provided as template
- Docker Compose uses environment variables
- No hardcoded passwords in code

### Database Security
- PostgreSQL with dedicated user (not superuser)
- Connection via internal Docker network
- No external database port exposure in production
- SSL/TLS ready for production

### API Security
- CORS configured for specific frontend origin
- No authentication currently (internal tool)
- Input validation via Pydantic models
- SQL injection prevention via SQLAlchemy ORM

### Network Security
- Nginx reverse proxy with security headers
- Internal services not exposed externally
- Docker network isolation

### Container Security
- Non-root user in containers (where applicable)
- Minimal base images (alpine/slim)
- No unnecessary packages installed

## Production Hardening Checklist

### Mandatory
- [ ] Change all default passwords in `.env`
- [ ] Generate strong `SECRET_KEY` (32+ chars)
- [ ] Enable HTTPS with valid TLS certificates
- [ ] Configure firewall: only 80/443 open
- [ ] Set up PostgreSQL SSL connections
- [ ] Enable Docker content trust

### Recommended
- [ ] Implement JWT authentication
- [ ] Add rate limiting to API
- [ ] Set up WAF (ModSecurity)
- [ ] Configure fail2ban for SSH
- [ ] Enable audit logging
- [ ] Set up vulnerability scanning (Trivy, Snyk)
- [ ] Regular security updates

### Network
- [ ] Use Docker secrets for sensitive data
- [ ] Separate networks for frontend/backend/database
- [ ] Implement mTLS between services
- [ ] Restrict database to backend network only

### Monitoring
- [ ] Log all authentication attempts
- [ ] Alert on repeated failed logins
- [ ] Monitor for unusual API patterns
- [ ] Set up file integrity monitoring

## Threat Model

### Assets to Protect
1. **Production Data** - Asset inventory, monitoring history
2. **Incident Data** - Root causes, resolutions, technician info
3. **Infrastructure Credentials** - Database, API keys
4. **Network Topology** - Asset IPs, VLANs, criticality

### Attack Vectors
1. **API Abuse** - Unauthorized incident creation/modification
2. **Data Exfiltration** - Asset inventory reveals network topology
3. **Privilege Escalation** - Container breakout to host
4. **Supply Chain** - Compromised base images

### Mitigations
1. **Network Segmentation** - Internal tool, not internet-facing
2. **Input Validation** - Pydantic schemas on all endpoints
3. **Least Privilege** - Database user has minimal permissions
4. **Image Scanning** - Scan base images for CVEs

## Compliance

### GDPR
- No personal data stored (only asset/technician names)
- Technician names optional, can be anonymized
- Data retention: configure monitoring result TTL

### ISO 27001
- Asset inventory aligns with A.8.1
- Incident management aligns with A.16
- Monitoring aligns with A.12.4

## Incident Response

If security incident detected:
1. Isolate affected container/service
2. Rotate all secrets in `.env`
3. Review audit logs
4. Patch vulnerabilities
5. Document lessons learned

## Security Headers (Nginx)

```nginx
add_header X-Frame-Options DENY;
add_header X-Content-Type-Options nosniff;
add_header X-XSS-Protection "1; mode=block";
add_header Referrer-Policy strict-origin-when-cross-origin;
add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline';";
```

## Docker Security

```dockerfile
# Use non-root user
RUN adduser --disabled-password --gecos '' appuser
USER appuser

# Read-only filesystem where possible
# No shell in final image
```

## Dependency Security

```bash
# Scan Python dependencies
pip-audit

# Scan Node dependencies
npm audit

# Scan Docker images
docker scan it-guardian-backend
docker scan it-guardian-frontend
docker scan it-guardian-monitoring
```

## Regular Maintenance

- Weekly: `apt update && apt upgrade` on host
- Monthly: Review and rotate secrets
- Quarterly: Penetration test (internal)
- Annually: Full security audit