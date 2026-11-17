---
name: Editorial Charcoal
colors:
  surface: '#051424'
  surface-dim: '#051424'
  surface-bright: '#2c3a4c'
  surface-container-lowest: '#010f1f'
  surface-container-low: '#0d1c2d'
  surface-container: '#122131'
  surface-container-high: '#1c2b3c'
  surface-container-highest: '#273647'
  on-surface: '#d4e4fa'
  on-surface-variant: '#c6c6cb'
  inverse-surface: '#d4e4fa'
  inverse-on-surface: '#233143'
  outline: '#909095'
  outline-variant: '#46474b'
  surface-tint: '#c6c6cd'
  primary: '#c6c6cd'
  on-primary: '#2e3036'
  primary-container: '#16181d'
  on-primary-container: '#808187'
  inverse-primary: '#5d5e64'
  secondary: '#bdc2ff'
  on-secondary: '#131e8c'
  secondary-container: '#2f3aa3'
  on-secondary-container: '#a8afff'
  tertiary: '#45dfa4'
  on-tertiary: '#003825'
  tertiary-container: '#001d11'
  on-tertiary-container: '#009467'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#e2e2e9'
  primary-fixed-dim: '#c6c6cd'
  on-primary-fixed: '#1a1b21'
  on-primary-fixed-variant: '#45474c'
  secondary-fixed: '#e0e0ff'
  secondary-fixed-dim: '#bdc2ff'
  on-secondary-fixed: '#000767'
  on-secondary-fixed-variant: '#2f3aa3'
  tertiary-fixed: '#68fcbf'
  tertiary-fixed-dim: '#45dfa4'
  on-tertiary-fixed: '#002114'
  on-tertiary-fixed-variant: '#005137'
  background: '#051424'
  on-background: '#d4e4fa'
  surface-variant: '#273647'
typography:
  display:
    fontFamily: Inter
    fontSize: 40px
    fontWeight: '700'
    lineHeight: 48px
    letterSpacing: -0.03em
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.025em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 26px
    fontWeight: '600'
    lineHeight: 34px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Inter
    fontSize: 22px
    fontWeight: '600'
    lineHeight: 30px
    letterSpacing: -0.015em
  headline-sm:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 26px
    letterSpacing: -0.01em
  body-lg:
    fontFamily: Inter
    fontSize: 17px
    fontWeight: '400'
    lineHeight: 28px
    letterSpacing: -0.005em
  body-md:
    fontFamily: Inter
    fontSize: 15px
    fontWeight: '400'
    lineHeight: 25px
  body-sm:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.04em
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 14px
    letterSpacing: 0.06em
  caption:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 18px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  gutter: 1.5rem
  gutter-mobile: 1rem
  margin: 2rem
  margin-mobile: 1rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2.5rem
  space-2xl: 4rem
---

## Brand & Style

This design system is tailored for an editorial-first digital morning paper focused on intelligence across technology, artificial intelligence, software engineering, and industry dynamics. The visual language conveys intellectual rigor, calm authority, and deliberate restraint, rejecting intrusive marketing elements, noisy cards, and aggressive dashboard clutter.

The aesthetic fuses utilitarian minimalism with high-density architectural newspaper layouts. Rhythm is established through disciplined typographic hierarchy, razor-sharp hairline dividers, and muted charcoal surfaces. Visual elevation relies on subtle tonal steps and precise structural framing rather than decorative effects or ambient drop shadows. The reading experience is prioritized above all else: generous line heights, optimal character measures, and subdued topic accents allow sustained concentration and rapid comprehension.

## Colors

The palette operates under a strict hierarchy of deep charcoal tones, functional metadata grays, high-legibility paper whites, and disciplined topical tints:

- **Foundation & Surfaces**: 
  - Canvas base: `#0F1115`
  - Primary surface / Card background: `#16181D`
  - Elevated inline surface / Briefing panel: `#1E2229`
  - Structural hairlines & rules: `#2A2E37`
  - Active borders & interactive strokes: `#333842`

- **Typography & Content**:
  - Primary headline and body: `#F1F3F5` (crisp high-contrast off-white)
  - Secondary metadata, captions, and bylines: `#94A3B8`
  - Subtle micro-labels and footnotes: `#64748B`

- **Topical Accents (Indicators Only)**:
  Category hues are strictly restricted to micro-indicators, inline tag borders, and topic labels. They never saturate large surface blocks:
  - *AI & Research*: Soft Indigo (`#818CF8`)
  - *Developer Tools*: Emerald (`#34D399`)
  - *Software & Infrastructure*: Sky Blue (`#38BDF8`)
  - *Jobs & Employment*: Amber (`#FBBF24`)
  - *Business & Markets*: Muted Coral (`#F87171`)
  - *Security*: Soft Orange (`#FB923C`)

*Note*: The logotype colors (`#FFFFFF` and `#E45BE9`) are strictly quarantined to the primary brand identity mark and are never applied to system UI components.

## Typography

The typographical structure is systematically executed using **Inter**. Headlines prioritize optical density and authoritative clarity through compact tracking, while long-form narrative body styles leverage an expanded line-height (1.65 to 1.7) to ease sustained reading on high-resolution displays.

All long-form editorial narratives must adhere to a strict measure between 680px and 760px to maintain line-length ergonomics. Section markers, metadata labels, and taxonomy chips employ uppercase transformation, reduced font sizing, and deliberate letter tracking (`0.04em` to `0.06em`) to echo classic broadsheet section indexes.

## Layout & Spacing

The layout model is anchored in a disciplined, responsive editorial grid:

- **Desktop (1024px+)**: A modular multi-column structure featuring a fixed-width long-form reading spine (720px) flanked by an asymmetric index column (240px) or expanding into a broadsheet 3-column brief layout across 1280px. Section borders utilize 1px hairline rules (`#2A2E37`).
- **Tablet (768px – 1023px)**: Reflows to a structured 2-column format with continuous vertical separators between adjacent dispatches. Outer canvas margins contract to `1.5rem`.
- **Mobile (< 768px)**: A singular, linear stream of briefings. Multi-column editorial modules stack cleanly into stacked dispatch rows separated by horizontal rules. Outer margins tighten to `1rem`.

Vertical flow maintains structural cadence using `space-lg` (1.5rem) between article elements and `space-2xl` (4rem) between topical editions or editions dividers.

## Elevation & Depth

This design system completely avoids floating drop shadows, synthetic blurs, or skeuomorphic bevels. Instead, elevation and spatial hierarchy are communicated purely through flat **tonal shifts** and **architectural hairline borders**:

1. **Base Layer (Canvas)**: `#0F1115` provides the deep reading baseline.
2. **Structural Layer (Content Blocks & Articles)**: `#16181D` delineates grouped editorial pieces, framed with 1px border lines in `#2A2E37`.
3. **Elevated Inline Layer (Expanded Briefings & Menus)**: `#1E2229` highlights active editorial expansions, floating panels, or pinned navigation tickers, bounded by `#333842`.
4. **Separators**: All division relies on 1px solid rules in `#2A2E37` to emulate traditional column rules in newspaper print design.

## Shapes

The design system employs **Soft (Level 1)** geometry, establishing a crisp, utilitarian silhouette:

- Standard elements (interactive tags, inline expanders, search inputs): `0.25rem` (4px).
- Expanded panels and card containers: `0.5rem` (8px).
- Topic indicator dots: Full circles (`9999px`) sized at 6px to 8px.

This controlled curvature prevents components from feeling round, soft, or playful, sustaining an authoritative, engineering-grade newspaper feel.

## Components

### Buttons & Interactive Links
- **Primary Action**: Crisp flat button with a `#F1F3F5` background, `#0F1115` text, and `rounded-sm` (4px). High contrast, functional.
- **Secondary / Ghost Action**: `#16181D` background with a 1px border in `#2A2E37`, shifting to `#333842` on hover. Text rendered in `#F1F3F5`.
- **Inline Text Trigger**: Subtle underline, transitions from `#94A3B8` to `#F1F3F5`.

### Editorial Dispatches & Cards
- Dispatches are framed with top or bottom hairline rules (`1px solid #2A2E37`), eliminating heavy container boxes.
- Hover states transition the title text color and delicately brighten the enclosing perimeter to `#333842` without shifting layout geometry.

### Inline Expandable Briefings
- Briefing items feature an inline toggle icon (+/- or subtle chevron) that unfolds deep-dive analysis directly in place (`#1E2229` background with a left accent border matching the topic color).
- Closing restores exact viewport scroll position to ensure unbroken reading rhythm.

### Category Tags & Status Indicators
- Rendered in uppercase `label-sm` tracking.
- Tag surface is translucent or transparent with a fine 1px border. A solid 6px circular dot (`rounded-full`) painted in the assigned topic accent precedes the category name.

### Form Inputs & Filters
- Clean rectangular fields with `0.25rem` corners, `#16181D` interior, and `#2A2E37` boundary line. Focus state applies a hairline highlight in `#94A3B8`. No glowing rings.