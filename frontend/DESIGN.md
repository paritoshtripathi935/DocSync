# DocSync design system

Quiet paper-and-ink: warm paper in light mode, ink in dark; violet marks links, the open note and primary actions. Tokens live in `src/index.css`; components use only the Tailwind names in the token tables below (`bg-surface`, `text-muted`, `border-line-strong`, `text-h2`…). A component that hard-codes a hex value or a pixel font size is a bug.

This file was produced by running the `ui-design` plugin: `color-palette` (with `color-system`, `dark-mode-design`), `type-system` (with `typography-scale`, `visual-hierarchy`, `spacing-system`, `layout-grid`, `responsive-design`) and `responsive-audit`. Neither app has charts, so `data-visualization` did not apply.

## Color

### Tonal scales
Use these when you need a new tint, for example a badge background. Semantic tokens are picked from or near these scales.

| | 50 | 100 | 200 | 300 | 400 | 500 | 600 | 700 | 800 | 900 | 950 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Ink violet | `#f8f6ff` | `#f1ecff` | `#e3daff` | `#d2c4ff` | `#bca7ff` | `#a68aff` | `#8871d1` | `#6a58a3` | `#50427a` | `#382f57` | `#211c33` |
| Neutral | `#f3f3f4` | `#e8e7e9` | `#d1cfd4` | `#b6b4bc` | `#928f9a` | `#6e6a78` | `#5a5762` | `#46444d` | `#35333a` | `#252429` | `#161518` |

### Semantic tokens

| Token (Tailwind) | Role | Dark | Light |
|---|---|---|---|
| `bg` | Page background | `#0f0e13` | `#faf8f4` |
| `surface` | Sidebars, cards, composer | `#15141b` | `#ffffff` |
| `raised` | Inputs, nested cards | `#1c1a24` | `#f4f1eb` |
| `hover` | Hover/selected rows | `#24212e` | `#ece7de` |
| `line` | Dividers (decorative) | `#2e2a3a` | `#ddd6c9` |
| `line-strong` | Input edges (≥3:1) | `#6f6c77` | `#87837b` |
| `fg` | Primary text | `#ece9f3` | `#1c1a22` |
| `muted` | Secondary text | `#aaa5b8` | `#514c5b` |
| `dim` | Metadata, timestamps | `#8e899c` | `#645e6d` |
| `accent` | Primary action, active state, links | `#a68aff` | `#6438d9` |
| `ink` | Text on accent | `#12082b` | `#ffffff` |
| `success` | Done states | `#34d399` | `#137638` |
| `warn` | Running / pending | `#fbbf24` | `#975600` |
| `danger` | Errors, destructive | `#f87171` | `#c42828` |
| `info` | Informational | `#60a5fa` | `#1d4ed8` |

Tint backgrounds for status come from opacity (`bg-danger/10`), not extra tokens.

### Contrast matrix (WCAG 2.1)

Minimum ratio of each foreground against `bg`, `surface`, `raised` and `hover`. AA needs 4.5 for text and 3.0 for UI boundaries.

| Foreground | Dark (min) | Light (min) | Status |
|---|---|---|---|
| `text` | 13.2 | 14.0 | ✅ AA |
| `muted` | 6.6 | 6.7 | ✅ AA |
| `dim` | 4.7 | 5.1 | ✅ AA |
| `accent` | 5.8 | 5.5 | ✅ AA |
| `success` | 8.2 | 4.6 | ✅ AA |
| `warn` | 9.4 | 4.7 | ✅ AA |
| `danger` | 5.7 | 4.6 | ✅ AA |
| `info` | 6.2 | 5.4 | ✅ AA |
| `border-strong` | 3.1 | 3.1 | ✅ AA (UI) |
| `ink` on `accent` | 7.0 | 6.8 | ✅ AA |

Status is never shown by color alone: badges carry a text label, and missing wiki links are dashed as well as dimmed.

### Dark mode

- Both themes are first-class. With no saved choice the app follows `prefers-color-scheme`; the toggle saves a choice to `localStorage`, and an inline script in `index.html` applies it before first paint, so there is no flash.
- Elevation in dark mode comes from lighter surfaces (`bg` → `surface` → `raised` → `hover`), not shadows.
- Text is off-white rather than `#fff`. The accent is a deeper shade in light mode so it still reaches ≥4.6:1.

## Typography

Fonts: Newsreader (display + note reading) · Inter (UI) · JetBrains Mono (markdown source).

The scale is a major third (×1.25) from 16px. Every line height is a multiple of 4px, which puts text on the baseline grid.

| Class | Size / line | Tracking | Use |
|---|---|---|---|
| `text-display` | 56 / 64 | −0.02em | Landing hero (≥640px) |
| `text-h1` | 40 / 48 | −0.02em | Hero on phones; section titles (≥768px); note title (≥640px) |
| `text-h2` | 32 / 40 | −0.02em | Page titles; section titles on phones |
| `text-h3` | 24 / 32 | −0.01em | Card and modal headings |
| `text-sub` | 20 / 28 | 0 | Lead paragraphs, wordmark |
| `text-body` | 16 / 24 | 0 | Body copy (minimum for reading text) |
| `text-small` | 14 / 20 | 0 | UI chrome: buttons, nav, rows, inputs |
| `text-caption` | 12 / 16 | 0 (wider when uppercase) | Metadata, timestamps, eyebrows |

- Weights: 400 for body, 500 for UI emphasis, 600 for headings and buttons. Don't go above 600 except in the logo.
- Uppercase labels use `tracking-wider` (0.05em).
- Long-form paragraphs use `leading-7` (28px).
- Measure: landing copy is capped at `max-w-xl`. The note reading column is `max-w-[40rem]` at 18/28 serif, which measured 69 characters at 1440px.

## Spacing

The base unit is 4px. The scale in use is 2, 4, 8, 12, 16, 24, 32, 48, 64 and 96px (Tailwind `0.5`, `1`, `2`, `3`, `4`, `6`, `8`, `12`, `16`, `24`). Don't use other values.

| Intent | Steps |
|---|---|
| Inline (icon ↔ label) | 4–8 |
| Inset (buttons, inputs) | 12–16 horizontal, controlled by height |
| Stack inside a component | 8–16 |
| Between groups | 24–48 |
| Landing sections | 96 vertical |

## Layout grid and breakpoints

- **Breakpoints:** Tailwind defaults: `sm` 640, `md` 768, `lg` 1024, `xl` 1280.
- **Landing:** contained in `max-w-6xl` (1152px), with 16px margins on phones and 24px from `sm`. The hero is 1 column on phones and 2 from `lg`; feature grids go 1 → 2 → 3 columns.
- **App:** a 272px sidebar plus editor from `md`, and an info panel (backlinks, links, history) as a 288px third column from `xl`, toggled below that. On phones the sidebar is the home screen and a note takes the full width. Gutters are 16px, 32px from `sm`.
- **Touch:** interactive controls are at least 44px tall on coarse pointers (`pointer-coarse:h-11`) and at least 24px with a mouse.

## Responsive audit (2026-11-01)

Measured in the browser at 375, 768 and 1440px. Phones were emulated with touch, so `pointer: coarse` applies.

| Check | Result |
|---|---|
| Horizontal overflow | None at any width |
| Touch targets (coarse) | All ≥44px. **Fixed:** the tags field (20px), the note title (40px), the Write/Preview tabs and icon buttons (28–36px). |
| Header at 375px | **Fixed:** the save status was cut off to "Sav…"; the tabs now show icons only on phones and keep their `aria-label`s. |
| Pointer targets (fine) | All ≥24px. **Fixed:** landing nav links. |
| Smallest text | 12px (captions) |
| Line length | Note reading column 41 characters on phones, 69 at 1440px (was about 85). Landing 40 / 54. |

**Known gaps:** the note title and body fields are borderless, an editor convention. They are identified by labels and placeholders rather than a 3:1 boundary.
