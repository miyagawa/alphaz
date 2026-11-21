# ALPHAZ share_item landing page: proposed fix

Example: `https://xg.pasch.fan/share_item?type=post&id=d05c68c0-…&lang=en` (target_id 3846)

## What goes wrong today

| Current page | Effect |
|---|---|
| Body is empty except a hidden `<button>`. | The user never sees the post they tapped. |
| On iOS, script calls `button.click()` on load. | This isn't a user gesture. X's in-app browser (and others) block custom-scheme navigation without one, so the app never opens. |
| `setTimeout(…, 100)` always sets `location.href = https://xg.pasch.fan`. | The user lands on `/introduction#join-alphaz` every time, even with the app installed. The timer isn't cancelled on `visibilitychange`/`pagehide`, and 100 ms is too short for the iOS "Open in app?" prompt anyway. |
| The intro page has no app link, and there's no `/.well-known/apple-app-site-association`. | The user is stranded. Universal links can't work either. |
| `xgapp.page.link` is commented out. | Firebase Dynamic Links shut down in Aug 2025. This page was a stopgap. |

## What the proposed page does (index.html)

- Shows the post: the og:title and og:image rendered as a card. The OG and Twitter meta tags are unchanged.
- Adds a large **ALPHAZ で開く / Open in ALPHAZ** button. It's a real `<a href="xg-twitter-login://view?view_key=BD&target_id=…">`, so the navigation comes from the user's tap.
- **No automatic redirect, ever.** If the page is still visible 1.5 s after the tap, it only highlights the "open in Safari" tip.
- The fallbacks are links the user chooses to follow: App Store (id1597302854), Google Play (`fan.pasch.xgalx`), and the intro page.
- Adds a Smart App Banner (`apple-itunes-app` with `app-argument`) for Safari.
- Self-contained: inline CSS/JS, no external dependencies.

## The real fix: universal links (iOS) and App Links (Android)

With universal links, tapping `https://xg.pasch.fan/share_item?...` in X, LINE, and other apps opens the app directly. The page above becomes just the fallback.

1. Serve `https://xg.pasch.fan/.well-known/apple-app-site-association`. It must be HTTPS, `Content-Type: application/json`, with no redirect.
   ```json
   {
     "applinks": {
       "details": [{
         "appIDs": ["<TEAMID>.<bundle id>"],
         "components": [{ "/": "/share_item*", "comment": "shared posts" }]
       }]
     }
   }
   ```
2. In the app, add the Associated Domains entitlement `applinks:xg.pasch.fan`. Then handle `NSUserActivityTypeBrowsingWeb` in `scene(_:continue:)` by mapping `type`/`id` to the same screen as `view?view_key=BD&target_id=…`. The app could also accept the post UUID directly, which removes the need for the numeric target_id.
3. For Android, serve `/.well-known/assetlinks.json` for `fan.pasch.xgalx`, and add an `autoVerify` intent filter for `https://xg.pasch.fan/share_item`.
4. Keep the `apple-itunes-app` banner with `app-argument=<share_item URL>` for Safari users.

This is not verified on a device: in-app browsers such as X's may load the tapped URL themselves instead of handing it to the app. If so, a user tap on a link to a *different* universal-link path (e.g. `/open/share_item?...`) from the landing page is the usual way to get the app to open. Test this on a device once the AASA file is live.

## Reusing the page

- `python3 make_page.py original-ep3833.html > ep3833.html` reads an original share page and bakes its OG data and target_id into a copy of index.html.
- For quick testing, use query params: `index.html?target_id=3833&title=...&image=https://...`. These only change the visible page. Crawlers read the static OG tags, so the server should keep rendering those per post.
