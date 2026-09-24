# NutriTrack → Himalo rebrand checklist

The new logo and every icon size are generated in `branding/`. The app's source code and Firebase console live outside this repository, so the steps below have to be done there.

Current identifiers, read from the v2.2 APK:

| Thing | Old value | New value |
|---|---|---|
| App name | NutriTrack | Himalo |
| `applicationId` | `app.nutritrack` | `app.himalo` |
| Kotlin package / `namespace` | `com.example` | `app.himalo` |
| Application class | `NutriTrackApplication` | `HimaloApplication` |
| Logo drawable | `nutritrack_logo` | `himalo_logo` |
| Firebase project ID | `nutritrack-2bf22` | cannot be renamed (see below) |
| Hosting URL | `nutritrack-2bf22.web.app` | `himalo.web.app` (new site) or a custom domain |
| APK asset name | `nutritrack.apk` | `himalo.apk` |

## Quick path (about 15 minutes, no Claude needed)

1. **Code:** in your Android project folder, commit your work first, then run:
   ```
   git clone https://github.com/sasam17/nutritrack ../himalo-branding
   python3 ../himalo-branding/branding/rebrand_app.py           # preview
   python3 ../himalo-branding/branding/rebrand_app.py --apply   # do it
   ```
   It covers every item in section 1 below. In Android Studio, run *File → Sync Project with Gradle Files*.
2. **Firebase:** do steps 1–4 of section 2 (rename the project, add the Android app `app.himalo` with your SHA-1/SHA-256, download `google-services.json` into `app/`). Build and install the app, and check that sign-in works.
3. **Release:** attach the APK as `himalo.apk` (the script renames the updater's asset name) and a copy named `nutritrack.apk` for old installs.
4. The remaining Firebase, Play and GitHub items below can wait until you're ready to launch.

## 1. Android app code

`branding/rebrand_app.py` does all of this automatically:


1. Copy `branding/android/res/*` into `app/src/main/res/`, overwriting the existing `mipmap-*` folders. Delete the old `nutritrack_logo` drawable and point its references at `@drawable/himalo_logo`.
2. `app/build.gradle(.kts)`: set `applicationId = "app.himalo"` and `namespace = "app.himalo"`.
3. Move the sources from `com/example/...` to `app/himalo/...` (Android Studio: right-click the package → Refactor → Rename). Rename `NutriTrackApplication` to `HimaloApplication` and update `android:name` in `AndroidManifest.xml`.
4. `strings.xml`: `app_name` → `Himalo`. Search the whole project for `NutriTrack`, `Nutritrack` and `nutritrack`. Check the in-app Privacy Policy, Terms, Refund text, the review prompt, notification titles and the share text.
5. `FileProvider` authority: if it's hard-coded as `app.nutritrack.fileprovider`, change it to `${applicationId}.fileprovider`.
6. In-app updater: update the GitHub repo URL and the APK asset name if you rename either (step 4 below).
7. Rename the root project in `settings.gradle` to `Himalo`.

> **Package name warning:** on Android, a new `applicationId` makes it a different app. People who installed a NutriTrack APK won't receive the Himalo update through the in-app updater. They'll get a second app next to the old one and have to sign in again (their data is safe in Firebase, see below). Ship one final NutriTrack release that tells users to install Himalo, with a download link. Change the ID now, before the Play Store launch: once an app is published on Play, its package name can never change.

## 2. Firebase

A Firebase **project ID can't be renamed**, and changing it doesn't matter to users. Keep project `nutritrack-2bf22`. Staying in the same project keeps every user account, all Auth data and all Database/Storage data with no migration.

1. **Project display name:** Project settings → General → set *Project name* to `Himalo`.
2. **Register the new Android app:** Project settings → *Add app* → Android. Package `app.himalo`, nickname `Himalo`.
3. **SHA fingerprints:** add the SHA-1 and SHA-256 of your release keystore (and debug keystore) to the new app. Google Sign-In fails without them. Once on Play, also add the *Play App Signing* SHA-1 from Play Console → Test and release → App integrity.
4. Download the new `google-services.json` and replace `app/google-services.json`.
5. **Google Sign-In consent screen:** Google Cloud console → APIs & Services → OAuth consent screen → set app name to `Himalo`, upload `branding/playstore/icon-512.png` as the logo, and update the support email and links.
6. **Auth email templates:** Authentication → Templates → change the sender name and `%APP_NAME%` wording to Himalo. Firebase takes the app name from the project's public-facing name (Project settings → General → *Public-facing name*), so set that to `Himalo` too.
7. **Hosting:** Hosting → *Add another site* → `himalo` (you get `himalo.web.app`; if that's taken, try `himalo-app` or connect a custom domain). Deploy the site there, add `himalo.web.app` under Authentication → Settings → *Authorized domains*, then add a redirect on the old site so existing links keep working:
   ```json
   { "hosting": { "site": "nutritrack-2bf22", "redirects": [ { "source": "**", "destination": "https://himalo.web.app", "type": 301 } ] } }
   ```
8. Web icons for the site are in `branding/web/`.
9. After the Himalo release is live and old installs have migrated, delete the old `app.nutritrack` Android app from Firebase project settings.

## 3. Google Play listing

- App name: `Himalo: Calorie & Diet Tracker` (30 characters, the maximum)
- Icon: `branding/playstore/icon-512.png`
- Feature graphic: `branding/playstore/feature-graphic-1024x500.png`
- Short description: mention Nepali dishes, e.g. "Track calories for dal bhat, momo and food from anywhere."
- Upload the privacy-policy URL on the new hosting domain.

## 4. GitHub

- Rename this repository to `himalo` (Settings → General → Repository name). GitHub redirects the old URL and API paths, so older builds' updater keeps working, but point new builds at the new name.
- Name future release assets `himalo.apk` / `himalo-vX.Y.apk` and titles "Himalo X.Y". If old builds look for `nutritrack.apk`, keep attaching a copy under that name as well until old installs have migrated.
- Update the NutriTrack section on the portfolio site (`sasam17.github.io`): name, description and link.
