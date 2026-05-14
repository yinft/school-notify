# Login Light Background Design

## Summary

Update the admin login page from a dark split-screen presentation to a light visual style while preserving the current layout, branding, and responsive behavior. The page should feel brighter and cleaner without becoming visually flat.

## Goals

- Replace the current deep blue hero background with a light blue-white gradient treatment.
- Keep the left-side brand area so the login page still feels distinct from a generic form.
- Convert the brand card from white-on-dark glassmorphism to a light card with dark text.
- Preserve the current login form structure and mobile stacking behavior.
- Limit implementation scope to login-related CSS unless a template change is required.

## Non-Goals

- No copy changes to the login page.
- No layout restructuring of the login screen.
- No changes to authentication behavior, routing, or form logic.
- No broader theme refactor for the rest of the admin application.

## Proposed Approach

Use a light gradient across the overall login shell, then soften the left hero section with a pale blue layered background. Keep both the brand card and form card as light surfaces, but give them enough border, blur, and shadow separation so the screen still has depth.

This approach keeps the existing two-column composition intact, minimizes code churn, and preserves the product's blue identity more effectively than switching to a pure white screen.

## Visual Changes

### Page Background

Apply a light blue-white gradient to the login shell so the full page reads as bright before the cards load into view.

### Hero Section

Replace the strong dark blue gradient with a pale blue gradient and subtle radial highlights. The hero should remain visually distinct, but no longer dominate the page.

### Brand Card

Keep the current card structure and icon placement. Change the card to a light translucent surface with dark primary text and muted secondary text. Retain a soft blur effect only if it supports separation against the lighter hero background.

### Login Panel and Form Card

Keep the right panel and form card in a white-based palette. Slightly strengthen edge definition through border or shadow so the card still stands out against the lighter page background.

## Data Flow and Behavior

There are no behavioral changes. The existing submit handler, router redirect, loading state, and form fields remain unchanged.

## Error Handling

No new error states are introduced. Existing login failure handling through `ElMessage.error` remains unchanged.

## Testing

- Verify the login page still renders correctly on desktop in the two-column layout.
- Verify the mobile breakpoint still stacks hero and panel without spacing regressions.
- Verify text contrast remains readable in the hero card and login form card.
- Verify the primary login button remains visually prominent after the surrounding background is lightened.

## Implementation Scope

Expected implementation should be limited to the login-related selectors in `src/styles/main.css`. `src/pages/login/LoginPage.vue` should only change if a class hook is found to be necessary during implementation.
