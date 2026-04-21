# Windows Banner Settings Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add client-side settings for banner speed, font size, color, and display duration, persist them locally, and apply them to the Windows banner at runtime.

**Architecture:** Keep the change local to the Windows client. Add one small settings model plus one JSON-backed store under `%LocalAppData%/SchoolNotify`, then bind a compact settings section in `MainWindow` to those values. Reuse the existing marquee animation path by feeding current settings into animation speed, font size, banner brush, and hide timer interval.

**Tech Stack:** .NET 8, WPF, xUnit, System.Text.Json

---

### Task 1: Add failing tests for banner settings persistence and animation timing

**Files:**
- Modify: `windows-client/tests/SchoolNotify.WindowsClient.Tests/NotificationRuntimeTests.cs`
- Create: `windows-client/tests/SchoolNotify.WindowsClient.Tests/BannerSettingsStoreTests.cs`
- Test: `windows-client/tests/SchoolNotify.WindowsClient.Tests/SchoolNotify.WindowsClient.Tests.csproj`

**Step 1: Write the failing persistence test**

Add a test that creates a `BannerSettingsStore` with a temp path, saves custom values, reloads them, and asserts the values round-trip.

**Step 2: Run test to verify it fails**

Run: `dotnet test "tests/SchoolNotify.WindowsClient.Tests/SchoolNotify.WindowsClient.Tests.csproj" --filter BannerSettings`
Expected: FAIL because the settings store and model do not exist yet.

**Step 3: Write the failing animation-speed test**

Add a test asserting the marquee animation duration changes when the configured speed changes.

**Step 4: Run test to verify it fails**

Run: `dotnet test "tests/SchoolNotify.WindowsClient.Tests/SchoolNotify.WindowsClient.Tests.csproj" --filter BannerScrollAnimationFactory`
Expected: FAIL because the animation factory does not yet accept speed.

### Task 2: Implement the settings model and local persistence

**Files:**
- Create: `windows-client/src/SchoolNotify.WindowsClient/Models/BannerSettings.cs`
- Create: `windows-client/src/SchoolNotify.WindowsClient/Services/BannerSettingsStore.cs`
- Modify: `windows-client/src/SchoolNotify.WindowsClient/Services/BannerScrollAnimationFactory.cs`

**Step 1: Add the settings model**

Create a minimal record with `ScrollSpeed`, `FontSize`, `ColorName`, and `DisplayDurationSeconds`.

**Step 2: Add the JSON-backed store**

Load defaults when the file is missing, save explicit values when the user changes settings, and keep the storage path under LocalAppData.

**Step 3: Update the animation factory**

Accept speed as an argument and compute duration from the configured pixels-per-second.

**Step 4: Run tests to verify they pass**

Run: `dotnet test "tests/SchoolNotify.WindowsClient.Tests/SchoolNotify.WindowsClient.Tests.csproj" --filter BannerSettings`
Expected: PASS.

### Task 3: Surface settings in the main window and apply them live

**Files:**
- Modify: `windows-client/src/SchoolNotify.WindowsClient/MainWindow.xaml`
- Modify: `windows-client/src/SchoolNotify.WindowsClient/MainWindow.xaml.cs`

**Step 1: Add a compact banner settings section**

Place four controls in the main window:
- speed slider
- font size slider
- color dropdown
- display duration dropdown

**Step 2: Load settings on startup**

Read saved settings after session initialization and update the controls.

**Step 3: Save and apply changes immediately**

When the user changes a setting, save it and apply it to the banner so the next notification uses the latest values.

**Step 4: Use settings in the notification path**

Apply:
- font size to the marquee text
- color to normal banner rendering
- duration to `_bannerHideTimer`
- speed to the marquee animation factory

**Step 5: Run tests to verify the feature remains green**

Run: `dotnet test "tests/SchoolNotify.WindowsClient.Tests/SchoolNotify.WindowsClient.Tests.csproj"`
Expected: PASS.

### Task 4: Verify the Windows client builds cleanly

**Files:**
- Modify: none
- Test: `windows-client/SchoolNotify.WindowsClient.sln`

**Step 1: Build the full solution**

Run: `dotnet build "SchoolNotify.WindowsClient.sln"`
Expected: build succeeds with 0 errors.
