Tailwind Build Integration

Commands

- Install dependencies (run in project root):

```bash
npm install
```

- Build production CSS:

```bash
npm run build:css
```

- Development (watch):

```bash
npm run dev:css
```

Notes

- The `build:css` script writes `static/css/tailwind.css`. Ensure `STATICFILES_DIRS` or `STATIC_ROOT` is configured in Django settings if needed.
- Templates include `static/css/tailwind.css` in `templates/base.html`.
