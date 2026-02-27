# DNS Configuration for bemanproject.org

This document describes the DNS configuration required to make both `bemanproject.org` and `www.bemanproject.org` work correctly with GitHub Pages.

## Overview

The repository now includes a `CNAME` file in the `static/` directory that contains `bemanproject.org`. This file is automatically copied to the root of the build output during the build process and is used by GitHub Pages to configure the custom domain.

## Required DNS Configuration

To enable both the apex domain (`bemanproject.org`) and the www subdomain (`www.bemanproject.org`), the following DNS records must be configured with your DNS provider (Gandi.net):

### 1. A Records for Apex Domain (bemanproject.org)

Create **four A records** pointing the apex domain to GitHub Pages IP addresses:

```
Host: @
Type: A
Value: 185.199.108.153

Host: @
Type: A
Value: 185.199.109.153

Host: @
Type: A
Value: 185.199.110.153

Host: @
Type: A
Value: 185.199.111.153
```

### 2. CNAME Record for www Subdomain

Create a **CNAME record** pointing the www subdomain to the GitHub Pages default domain:

```
Host: www
Type: CNAME
Value: bemanproject.github.io
```

**Important:** The CNAME record should point to `bemanproject.github.io` (without any path or repository name).

## How It Works

Once both the CNAME file in the repository and the DNS records are configured:

1. GitHub Pages will automatically handle redirects between `bemanproject.org` and `www.bemanproject.org`
2. Accessing `www.bemanproject.org` will work correctly and redirect to `bemanproject.org` (or vice versa)
3. HTTPS will be available on both domains (may take up to 24 hours for certificate provisioning)

## DNS Propagation

DNS changes can take up to 24 hours to propagate globally. After configuring the DNS records, you can verify the configuration using these commands:

### Verify A Records
```bash
dig bemanproject.org +noall +answer -t A
```

Expected output:
```
bemanproject.org    3600    IN A     185.199.108.153
bemanproject.org    3600    IN A     185.199.109.153
bemanproject.org    3600    IN A     185.199.110.153
bemanproject.org    3600    IN A     185.199.111.153
```

### Verify CNAME Record
```bash
dig www.bemanproject.org +noall +answer -t CNAME
```

Expected output:
```
www.bemanproject.org    3600    IN CNAME    bemanproject.github.io.
```

## References

- [GitHub Pages: Managing a custom domain](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site#configuring-an-apex-domain-and-the-www-subdomain-variant)
- [GitHub Pages: About custom domains](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/about-custom-domains-and-github-pages)

## GitHub Pages Settings

After DNS configuration is complete, verify in the repository settings:

1. Go to Settings → Pages
2. Verify that "Custom domain" shows `bemanproject.org`
3. Wait for DNS check to complete (green checkmark)
4. Enable "Enforce HTTPS" (may take up to 24 hours to become available)
