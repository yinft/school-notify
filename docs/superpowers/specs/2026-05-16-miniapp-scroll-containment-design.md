# Miniapp Scroll Containment Design

## Goal

Prevent the miniapp from scrolling as a whole page by default. Keep the title bar visually fixed and allow only the page content area to scroll when content exceeds the available viewport height.

## Current State

- Each page renders a shared `native-title-bar` followed by a `.page` container.
- The global `.page` style currently uses `min-height: 100vh`, so long content expands the whole page and triggers full-page scrolling.
- Only the login state uses a fixed-height container with `overflow: hidden`.

## Chosen Approach

Use a shared fixed-height page shell for all non-login screens:

- Make `.page` a `height: 100vh` flex column with `overflow: hidden`.
- Add a shared `.page-body` content container that fills the remaining space and owns vertical scrolling.
- Wrap the non-login content of each miniapp page inside `.page-body`.
- Keep the login state on `.page-login` so the existing login gate layout remains isolated.

## Why This Approach

- It matches the desired behavior across all major pages instead of fixing only one screen.
- It keeps the current visual hierarchy and spacing with minimal markup changes.
- It avoids per-page scrolling hacks and makes future pages follow one consistent pattern.

## Affected Files

- `miniapp/app.wxss`
- `miniapp/pages/devices/index.wxml`
- `miniapp/pages/bind/index.wxml`
- `miniapp/pages/send/index.wxml`
- `miniapp/pages/records/index.wxml`
- `miniapp/pages/profile/index.wxml`

## Expected Behavior

- The outer page no longer scrolls vertically.
- The custom title bar stays at the top while content scrolls underneath within the page body.
- Long pages such as records and send scroll only inside the main content region.
- Short pages continue to fill the screen without layout regression.

## Risks And Mitigations

- Flex children may refuse to shrink without `min-height: 0`: set it on `.page-body`.
- Bottom content may be obscured by the custom tab bar: preserve the existing bottom safe-area padding in `.page-body`.
- Login layout could regress if forced into the new scroll shell: keep login-specific behavior on `.page-login` and do not wrap login content in `.page-body`.
