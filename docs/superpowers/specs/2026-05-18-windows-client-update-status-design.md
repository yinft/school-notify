# Windows Client Update Status Design

## Goal

Make the Windows client update behavior visible and timely without adding a redundant manual update check button.

## Scope

- Show the current client version in the main window.
- Check for recommended updates immediately after startup registration and after a successful reconnect.
- Keep the existing 30-second heartbeat update check.
- Show a simple update status line so users can tell whether the client is current, checking, failed, or ready to install.
- Do not change the backend recommendation model: only published and recommended Windows versions trigger client updates.

## Client Behavior

The client continues to use the persisted `ClientSession.ClientVersion` as its current version. The device information card displays this value as `客户端版本：x.y.z`.

After registration succeeds during startup, the client sends a heartbeat immediately. This reuses the existing heartbeat response shape and update detection path, avoiding a new endpoint. After a reconnect succeeds, the client also sends a heartbeat immediately so update checks do not wait for the next timer tick.

The existing heartbeat timer remains the periodic background check. When a heartbeat response contains `update.available == true`, the client downloads the update with the existing `UpdateService`. Once downloaded, the tray menu exposes `立即更新` as it does today.

## Update Status Text

Add an update status line in the device information card:

- `更新状态：等待检查` before the first heartbeat/update check.
- `更新状态：正在检查更新...` while an immediate or periodic check is running.
- `更新状态：当前已是最新推荐版本` when the backend returns no update or `available=false`.
- `更新状态：新版本 x.y.z 已就绪，请从托盘菜单立即更新` after the package is downloaded.
- `更新状态：检查更新失败：...` for non-auth network/server failures.

Authentication failures continue to use the existing device-auth failure UI.

## Error Handling

Update checks must not break startup or reconnect. If the immediate heartbeat check fails for non-auth reasons, the status line records the failure and the periodic heartbeat can retry later.

If an update is already pending locally, future checks should not redownload it. The status line should keep telling users that an update is ready to install.

## Testing

- Add or adjust a Windows client test to verify the main window layout contains the client version and update status labels.
- Run the Windows client test suite, or at minimum the layout-focused tests, after implementation.
