---
name: Azure Meridian
colors:
  surface: '#f9f9ff'
  surface-dim: '#d3daea'
  surface-bright: '#f9f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f0f3ff'
  surface-container: '#e7eefe'
  surface-container-high: '#e2e8f8'
  surface-container-highest: '#dce2f3'
  on-surface: '#151c27'
  on-surface-variant: '#404848'
  inverse-surface: '#2a313d'
  inverse-on-surface: '#ebf1ff'
  outline: '#707978'
  outline-variant: '#bfc8c8'
  surface-tint: '#2e6767'
  primary: '#003535'
  on-primary: '#ffffff'
  primary-container: '#0d4d4d'
  on-primary-container: '#85bdbc'
  inverse-primary: '#98d1d0'
  secondary: '#0c6780'
  on-secondary: '#ffffff'
  secondary-container: '#9ae1ff'
  on-secondary-container: '#09657f'
  tertiary: '#4b240d'
  on-tertiary: '#ffffff'
  tertiary-container: '#663a21'
  on-tertiary-container: '#e3a585'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#b4edec'
  primary-fixed-dim: '#98d1d0'
  on-primary-fixed: '#002020'
  on-primary-fixed-variant: '#104f4f'
  secondary-fixed: '#baeaff'
  secondary-fixed-dim: '#89d0ed'
  on-secondary-fixed: '#001f29'
  on-secondary-fixed-variant: '#004d62'
  tertiary-fixed: '#ffdbca'
  tertiary-fixed-dim: '#f9b897'
  on-tertiary-fixed: '#331200'
  on-tertiary-fixed-variant: '#683c22'
  background: '#f9f9ff'
  on-background: '#151c27'
  surface-variant: '#dce2f3'
typography:
  headline-xl:
    fontFamily: Plus Jakarta Sans
    fontSize: 40px
    fontWeight: '700'
    lineHeight: '1.2'
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '600'
    lineHeight: '1.25'
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.3'
  body-lg:
    fontFamily: Manrope
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Manrope
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.5'
  body-sm:
    fontFamily: Manrope
    fontSize: 14px
    fontWeight: '400'
    lineHeight: '1.5'
  label-md:
    fontFamily: Manrope
    fontSize: 14px
    fontWeight: '600'
    lineHeight: '1'
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Manrope
    fontSize: 12px
    fontWeight: '700'
    lineHeight: '1'
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 4px
  container-max: 1280px
  gutter: 24px
  margin-mobile: 16px
  margin-desktop: 48px
  stack-sm: 8px
  stack-md: 16px
  stack-lg: 32px
---

## Brand & Style
This design system embodies a **Modern Corporate** aesthetic tailored for high-end travel logistics and AI-driven itinerary management. The brand personality is authoritative yet welcoming, focusing on "effortless precision." The target audience consists of frequent travelers and corporate planners who value efficiency and clarity over visual noise.

The style leverages a disciplined layout with ample white space, ensuring that complex travel data feels manageable. Depth is achieved through layering and soft environmental shadows rather than heavy textures. The emotional response is one of confidence and calm—moving the user from the chaos of planning to the serenity of the destination.

## Colors
The palette is anchored by **Deep Teal**, used for primary actions and navigation to establish a premium, grounded feel. **Sky Blue** acts as a supportive secondary color, used for information callouts, active states, and progress indicators, reflecting the openness of travel. 

**Warm Coral** is the strategic accent, reserved strictly for high-conversion buttons (e.g., "Book Now") or critical AI-driven insights to ensure they pop against the cooler backdrop. The neutral scale leans toward a cool **Slate Gray** to maintain a modern SaaS feel, while the background utilizes a very light gray (#F9FAFB) to provide subtle contrast against white surface cards.

## Typography
The typographic system uses a pairing of **Plus Jakarta Sans** for headings and **Manrope** for body and UI elements. Plus Jakarta Sans provides a friendly, optimistic quality to the headers, while Manrope offers the technical precision required for dense itinerary data and pricing tables.

Line heights are generous to prevent visual fatigue during long booking sessions. Tracking is slightly tightened on large headlines for a more premium, editorial look, while smaller labels use increased letter spacing and uppercase styling to improve scanability in data-heavy views.

## Layout & Spacing
The design system utilizes a **12-column fixed grid** for desktop environments to maintain a structured, professional feel, transitioning to a fluid single-column layout on mobile. The spacing rhythm is based on a **4px baseline grid**, ensuring all components align with mathematical consistency.

Vertical rhythm is established through "Stack" tokens: use `stack-sm` for related elements within a card, `stack-md` for spacing between content blocks, and `stack-lg` for section breaks. Margins are kept wide to frame the content and reinforce the premium tone.

## Elevation & Depth
Depth is conveyed through **Tonal Layering** and **Ambient Shadows**. The design system avoids harsh borders, preferring soft, diffused shadows to lift active elements from the background.

- **Level 0 (Base):** Background (#F9FAFB).
- **Level 1 (Card):** White surface (#FFFFFF) with a 1px stroke in a very light neutral and no shadow.
- **Level 2 (Overlay/Active):** White surface with a "Subtle Float" shadow (0px 4px 20px rgba(13, 77, 77, 0.08)).
- **Level 3 (Popovers/Modals):** White surface with a "High Depth" shadow (0px 12px 40px rgba(0, 0, 0, 0.12)).

AI-powered insights use a secondary-colored (Sky Blue) soft glow instead of a standard shadow to indicate "intelligence" or high-priority suggestions.

## Shapes
The shape language is defined by **Rounded (Level 2)** geometry. Standard components like buttons and input fields use an 8px (0.5rem) radius. Larger containers, such as travel cards or itinerary blocks, utilize 16px (1rem) for `rounded-lg` and 24px (1.5rem) for `rounded-xl`. 

This consistency in roundedness softens the professional tone, making the travel experience feel approachable and modern. Avoid sharp corners entirely to maintain the "seamless" brand promise.

## Components
- **Buttons:** Primary buttons use Deep Teal with white text. CTA buttons (e.g., "Confirm Flight") use Warm Coral. Ghost buttons use Sky Blue text with no background.
- **Input Fields:** 8px rounded corners, 1px light gray border. On focus, the border transitions to Sky Blue with a soft 2px outer glow.
- **Cards:** White backgrounds with `rounded-lg` corners. Use `stack-sm` for internal padding.
- **Chips/Badges:** Use "Pill-shaped" (rounded-full) geometry. High-priority AI suggestions should use a Sky Blue background with Deep Teal text.
- **Travel Timeline:** A vertical line component using Deep Teal dots for stops and dashed lines for transit segments, providing a clear visual path for itineraries.
- **AI Tooltips:** Distinctive small popovers with a subtle Sky Blue gradient border to signify machine-generated advice or price predictions.
- **Lists:** Clean, borderless rows with 16px vertical padding and a subtle divider line (#E5E7EB) between items.