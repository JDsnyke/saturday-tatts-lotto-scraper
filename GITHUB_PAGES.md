# GitHub Pages Setup Guide

This guide explains how to set up and maintain the GitHub Pages website for the Saturday Tatts Lotto Scraper & Analyzer project.

## 🚀 Quick Setup

### 1. Enable GitHub Pages

1. Go to your repository settings on GitHub
2. Scroll down to the "Pages" section
3. Under "Source", select "Deploy from a branch"
4. Choose the `gh-pages` branch
5. Click "Save"

### 2. Automatic Deployment

The website will automatically deploy when you push changes to the `main` branch thanks to the GitHub Actions workflow in `.github/workflows/deploy.yml`.

## 📁 File Structure

```
Lotto/
├── index.html              # Main website page
├── assets/
│   └── favicon.svg         # Website favicon
├── .github/workflows/
│   └── deploy.yml          # GitHub Actions deployment
└── GITHUB_PAGES.md         # This file
```

## 🎨 Customization

### Colors and Styling

The website uses CSS custom properties (variables) defined in the `:root` selector in `index.html`. You can easily customize:

- `--primary-color`: Main brand color (#2563eb)
- `--secondary-color`: Secondary accent color (#10b981)
- `--text-primary`: Main text color (#1f2937)
- `--bg-primary`: Background color (#ffffff)

### Content Updates

To update the website content:

1. Edit `index.html` directly
2. Commit and push to the `main` branch
3. GitHub Actions will automatically deploy the changes

## 🔧 Features

### Responsive Design
- Mobile-first approach
- Responsive navigation with hamburger menu
- Optimized for all screen sizes

### Performance
- Optimized images and assets
- Minimal external dependencies
- Fast loading times

### SEO Optimized
- Meta tags for social sharing
- Open Graph and Twitter Card support
- Semantic HTML structure

## 📱 Mobile Support

The website includes:
- Touch-friendly navigation
- Responsive grid layouts
- Mobile-optimized typography
- Smooth scrolling with header offset

## 🎯 Key Sections

1. **Header**: Hero section with project overview
2. **Features**: 6 key features with icons and descriptions
3. **Statistics**: Project metrics and capabilities
4. **Demo**: Interactive terminal simulation
5. **Installation**: Step-by-step setup guide
6. **Usage**: How to use the tool
7. **Architecture**: Project structure overview
8. **Footer**: Links and project information

## 🔄 Maintenance

### Regular Updates

- Update project statistics as the tool evolves
- Add new features to the features grid
- Update installation instructions if needed
- Keep links and references current

### Performance Monitoring

- Check page load times
- Monitor mobile responsiveness
- Verify all links work correctly
- Test on different browsers

## 🐛 Troubleshooting

### Common Issues

1. **Website not updating**: Check GitHub Actions workflow status
2. **Styling issues**: Verify CSS is properly loaded
3. **Mobile menu not working**: Check JavaScript console for errors
4. **Favicon not showing**: Clear browser cache

### Debug Steps

1. Check the GitHub Actions tab for deployment status
2. Verify the `gh-pages` branch exists and contains the website files
3. Test locally by opening `index.html` in a browser
4. Check browser developer tools for any errors

## 📞 Support

For issues with the GitHub Pages website:
- Check the GitHub Actions logs
- Verify all files are committed to the repository
- Ensure the `gh-pages` branch is properly configured

---

**Last Updated**: January 2025  
**Version**: 1.0.0 