---
name: seo-optimizer
description: Provides SEO optimization recommendations and execution for web projects. Use when the user wants to audit, improve, or fix SEO-related issues such as meta tags, semantic HTML, sitemaps, structured data, and performance metrics.
---

# SEO Optimizer

## Overview

This skill acts as an SEO optimization expert. It guides you through auditing a project's current SEO state, proposing a strategy for improvement, and executing the changes directly in the codebase.

## Workflow

### Phase 1: Audit & Discovery

**Goal**: Understand the current SEO health of the project.

1.  **Identify Project Type**:
    *   **Static Site (HTML/Jekyll/Hugo)**: Check `index.html`, `_layouts`, `_config.yml`.
    *   **SPA (React/Vue/Angular)**: Check `public/index.html`, router configs, Helmet/Meta components.
    *   **SSR/SSG (Next.js/Nuxt)**: Check `layout.tsx`, `head` configuration, `next-sitemap`.

2.  **Check Core SEO Elements**:
    *   **Meta Tags**: `<title>`, `<meta name="description">`, `<meta name="viewport">`.
    *   **Open Graph / Twitter Cards**: `og:title`, `og:image`, `twitter:card`.
    *   **Semantic Structure**: Correct usage of `<h1>` through `<h6>`, `<header>`, `<nav>`, `<main>`, `<footer>`.
    *   **Assets**: `robots.txt`, `sitemap.xml`, `favicon.ico`.
    *   **Accessibility (A11y)**: `alt` text on images, ARIA labels where necessary.

### Phase 2: Strategy Proposal

**Goal**: Define *what* needs to be done before doing it.

1.  **Categorize Issues**:
    *   **Critical**: Missing title/description, broken links, blocking `robots.txt`.
    *   **Important**: Missing Open Graph tags, non-semantic HTML, slow loading images.
    *   **Optimization**: JSON-LD structured data, advanced caching headers.

2.  **Propose Action Plan**:
    *   List specific files to modify.
    *   Draft the content for new tags (e.g., "Proposed Description: ...").
    *   Suggest libraries if needed (e.g., `react-helmet`, `next-sitemap`).

### Phase 3: Execution & Implementation

**Goal**: Apply the fixes.

1.  **Inject Meta Tags**:
    *   Add missing tags to the `<head>` section or configuration files.
    *   Ensure titles are unique per page where possible.

2.  **Improve Semantics**:
    *   Replace `<div>` soup with semantic tags (`<article>`, `<section>`) where appropriate.
    *   Ensure every page has exactly one `<h1>`.

3.  **Generate Assets**:
    *   Create or update `robots.txt` (allow all by default, disallow admin/private).
    *   Create or configure `sitemap.xml` generation.

4.  **Add Structured Data (JSON-LD)**:
    *   Inject `application/ld+json` script blocks for Organization, WebSite, or Article schemas.

## Checklist for Optimization

*   [ ] **Title & Description**: Present and optimal length (Title < 60 chars, Desc < 160 chars).
*   [ ] **Open Graph**: Title, Description, Image, URL present.
*   [ ] **Canonical URL**: Self-referencing canonical tag exists.
*   [ ] **Headings**: H1 -> H6 hierarchy is logical and unbroken.
*   [ ] **Images**: All images have meaningful `alt` text.
*   [ ] **Robots/Sitemap**: Files exist and are valid.
*   [ ] **Structured Data**: JSON-LD present for key entities.

## Common Patterns

### Adding JSON-LD
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "My Project",
  "url": "https://example.com"
}
</script>
```

### Next.js Metadata (App Router)
```typescript
export const metadata = {
  title: 'My Page Title',
  description: 'My page description',
  openGraph: {
    title: 'My Page Title',
    description: 'My page description',
    images: ['/og-image.jpg'],
  },
}
```
