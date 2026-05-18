# Windows Client Update Status Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Show the Windows client version and make recommended update checks happen immediately and visibly without adding a manual check button.

**Architecture:** Reuse the existing heartbeat response and update download path. Add two text blocks to the device information card and centralize heartbeat/update status handling in `MainWindow.xaml.cs` so startup, reconnect, and timer checks share behavior.

**Tech Stack:** WPF, .NET, xUnit layout tests

---

## File Structure

- Modify `windows-client/src/SchoolNotify.WindowsClient/MainWindow.xaml` to add `ClientVersionTextBlock` and `UpdateStatusTextBlock`.
- Modify `windows-client/src/SchoolNotify.WindowsClient/MainWindow.xaml.cs` to populate version/status text and run immediate heartbeat checks after startup and reconnect.
- Modify `windows-client/tests/SchoolNotify.WindowsClient.Tests/MainWindowLayoutTests.cs` to lock the new labels into the layout.

### Task 1: Add Layout Coverage

**Files:**
- Modify: `windows-client/tests/SchoolNotify.WindowsClient.Tests/MainWindowLayoutTests.cs`

- [ ] Add assertions that the main window XAML contains `ClientVersionTextBlock` and `UpdateStatusTextBlock`.
- [ ] Run `dotnet test --filter MainWindowLayoutTests` in `windows-client/` and confirm the test fails before implementation.

### Task 2: Add Client Version And Update Status UI

**Files:**
- Modify: `windows-client/src/SchoolNotify.WindowsClient/MainWindow.xaml`
- Modify: `windows-client/src/SchoolNotify.WindowsClient/MainWindow.xaml.cs`

- [ ] Add the new text blocks to the device information card.
- [ ] Set `ClientVersionTextBlock.Text` after the session is loaded.
- [ ] Initialize update status as `更新状态：等待检查`.
- [ ] Run `dotnet test --filter MainWindowLayoutTests` and confirm the layout test passes.

### Task 3: Reuse Heartbeat For Immediate Update Checks

**Files:**
- Modify: `windows-client/src/SchoolNotify.WindowsClient/MainWindow.xaml.cs`

- [ ] Extract the heartbeat body into a shared async method used by timer, startup, and reconnect.
- [ ] After authentication and binding-code refresh in startup, send one immediate heartbeat before starting the heartbeat timer.
- [ ] After successful WebSocket reconnect, send one immediate heartbeat before restarting the timer.
- [ ] Keep non-auth heartbeat/update failures visible in `UpdateStatusTextBlock` without blocking startup/reconnect.
- [ ] Run `dotnet test` in `windows-client/` and confirm the suite passes.
