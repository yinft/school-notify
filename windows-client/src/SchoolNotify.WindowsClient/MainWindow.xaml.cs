using System.IO;
using System.Net;
using System.Net.Http;
using System.Globalization;
using System.Windows;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Threading;
using Forms = System.Windows.Forms;
using QRCoder;
using SchoolNotify.WindowsClient.Models;
using SchoolNotify.WindowsClient.Services;

namespace SchoolNotify.WindowsClient;

public partial class MainWindow : Window
{
    private readonly DeviceApiClient _apiClient;

    private readonly DeviceAuthenticationCoordinator _deviceAuthenticationCoordinator;

    private readonly ClientSessionStore _clientSessionStore = new();

    private readonly ClientSettingsStore _clientSettingsStore = new();

    private readonly BannerSettingsStore _bannerSettingsStore = new();

    private readonly AutoStartService _autoStartService = new();

    private readonly SpeechAnnouncementService _speechAnnouncementService = new();

    private readonly UpdateService _updateService;

    private readonly DeviceWebSocketClient _webSocketClient;

    private readonly DispatcherTimer _heartbeatTimer;

    private readonly DispatcherTimer _bannerHideTimer;

    private readonly DispatcherTimer _reconnectTimer;

    private readonly DispatcherTimer _bindingCodeRefreshTimer;

    private readonly CancellationTokenSource _cancellationTokenSource = new();

    private readonly Forms.NotifyIcon _notifyIcon;

    private readonly BannerOverlayWindow _bannerOverlay = new();

    private readonly BindingCodeRefreshController _bindingCodeRefreshController = new();

    private ClientSession? _currentSession;

    private string? _deviceToken;

    private BannerSettings _bannerSettings = BannerSettings.Default;

    private ClientSettings _clientSettings = ClientSettings.Default;

    private int _reconnectAttempt;

    private bool _isExplicitExitRequested;

    private bool _isLoadingBannerSettings;

    private bool _isLoadingClientSettings;

    private bool _isRefreshingBindingCode;

    private bool _isHeartbeatInProgress;

    public MainWindow()
    {
        InitializeComponent();

        var serverConfig = new ServerConfigStore().Load();

        var httpClient = new HttpClient
        {
            BaseAddress = new Uri(serverConfig.BaseUrl),
            Timeout = TimeSpan.FromSeconds(10)
        };

        _apiClient = new DeviceApiClient(httpClient);
        _deviceAuthenticationCoordinator = new DeviceAuthenticationCoordinator(_apiClient.RegisterDeviceAsync);
        _updateService = new UpdateService(httpClient, AppDomain.CurrentDomain.BaseDirectory);
        _webSocketClient = new DeviceWebSocketClient(httpClient.BaseAddress!);
        _heartbeatTimer = new DispatcherTimer
        {
            Interval = TimeSpan.FromSeconds(30)
        };
        _bannerHideTimer = new DispatcherTimer
        {
            Interval = TimeSpan.FromSeconds(10)
        };
        _reconnectTimer = new DispatcherTimer();
        _bindingCodeRefreshTimer = new DispatcherTimer
        {
            Interval = TimeSpan.FromSeconds(1)
        };
        _heartbeatTimer.Tick += HeartbeatTimerOnTick;
        _bannerHideTimer.Tick += BannerHideTimerOnTick;
        _reconnectTimer.Tick += ReconnectTimerOnTick;
        _bindingCodeRefreshTimer.Tick += BindingCodeRefreshTimerOnTick;

        _notifyIcon = new Forms.NotifyIcon
        {
            Text = "思故桌面小喇叭",
            Icon = LoadTrayIcon(),
            Visible = true,
            ContextMenuStrip = BuildTrayMenu()
        };
        _notifyIcon.DoubleClick += (_, _) => RestoreFromTray();
        _notifyIcon.BalloonTipClicked += (_, _) => RestartForUpdate();

        Loaded += OnLoadedAsync;
        Closing += OnClosingAsync;
    }

    private static System.Drawing.Icon LoadTrayIcon()
    {
        var resource = System.Windows.Application.GetResourceStream(new Uri("pack://application:,,,/Assets/app.ico", UriKind.Absolute));
        if (resource?.Stream is null)
        {
            throw new InvalidOperationException("找不到客户端图标资源 Assets/app.ico");
        }

        using var stream = resource.Stream;
        return new System.Drawing.Icon(stream);
    }

    private async void OnLoadedAsync(object sender, RoutedEventArgs e)
    {
        await InitializeClientAsync();
    }

    private async Task InitializeClientAsync()
    {
        try
        {
            _currentSession = await _clientSessionStore.LoadOrCreateAsync();
            DeviceNameTextBlock.Text = $"设备名称：{_currentSession.DeviceName}";
            DeviceIdTextBlock.Text = $"设备 ID：{_currentSession.DeviceId}";
            ClientVersionTextBlock.Text = $"客户端版本：{_currentSession.ClientVersion}";
            UpdateStatusTextBlock.Text = "更新状态：等待检查";

            _clientSettings = await _clientSettingsStore.LoadAsync(_cancellationTokenSource.Token);
            ApplyClientSettingsToControls(_clientSettings);
            ApplyAutoStartSetting(_clientSettings);

            _bannerSettings = await _bannerSettingsStore.LoadAsync(_cancellationTokenSource.Token);
            ApplyBannerSettingsToControls(_bannerSettings);
            ApplyBannerSettingsToBanner(_bannerSettings);

            var authResult = await _deviceAuthenticationCoordinator.EnsureRegisteredAsync(_currentSession, _cancellationTokenSource.Token);
            await ApplyAuthenticationResultAsync(authResult);
            if (string.IsNullOrEmpty(_deviceToken))
            {
                throw new InvalidOperationException("服务端未返回设备令牌");
            }

            if (authResult.RegisteredDevice is not null)
            {
                ApplyDeviceState(authResult.RegisteredDevice, DeviceStatusText.RegisteredWaitingForBinding);
            }
            else
            {
                StatusSummaryTextBlock.Text = DeviceStatusText.RestoredTokenWaitingForConnection;
            }

            await RefreshBindingCodeAsync();
            _bindingCodeRefreshTimer.Start();

            await ConnectWebSocketAsync();
        }
        catch (Exception exception) when (IsDeviceAuthFailure(exception))
        {
            ShowDeviceAuthFailure();
        }
        catch (Exception exception)
        {
            ShowOperationalFailure($"初始化失败：{exception.Message}", "连接状态：异常");
        }
    }

    private async void HeartbeatTimerOnTick(object? sender, EventArgs e)
    {
        await SendHeartbeatAndApplyStateAsync(showCheckingStatus: true);
    }

    private async Task SendHeartbeatAndApplyStateAsync(bool showCheckingStatus)
    {
        if (_currentSession is null || string.IsNullOrEmpty(_deviceToken))
        {
            return;
        }

        if (_isHeartbeatInProgress)
        {
            return;
        }

        try
        {
            _isHeartbeatInProgress = true;
            if (showCheckingStatus && !_updateService.IsUpdatePending && !_updateService.IsDownloading)
            {
                UpdateStatusTextBlock.Text = "更新状态：正在检查更新...";
            }

            var heartbeat = await _apiClient.SendHeartbeatAsync(_currentSession.DeviceId, _deviceToken, _cancellationTokenSource.Token);
            ApplyDeviceState(heartbeat, DeviceStatusText.HeartbeatHealthy);

            if (heartbeat.Update is { Available: true })
            {
                if (_updateService.IsDownloading)
                {
                    UpdateStatusTextBlock.Text = $"更新状态：发现新版本 {heartbeat.Update.LatestVersion}，后台下载中";
                }
                else
                {
                    UpdateStatusTextBlock.Text = $"更新状态：发现新版本 {heartbeat.Update.LatestVersion}，后台下载中";
                    _ = TryApplyUpdateAsync(heartbeat.Update);
                }
            }
            else if (_updateService.IsUpdatePending)
            {
                UpdateStatusTextBlock.Text = "更新状态：新版本已就绪，请从托盘菜单立即更新";
            }
            else
            {
                UpdateStatusTextBlock.Text = "更新状态：当前已是最新推荐版本";
            }
        }
        catch (HttpRequestException exception) when (IsDeviceAuthFailure(exception))
        {
            ShowDeviceAuthFailure();
        }
        catch (Exception exception)
        {
            ShowOperationalFailure($"心跳失败：{exception.Message}", "连接状态：心跳失败");
            UpdateStatusTextBlock.Text = $"更新状态：检查更新失败：{exception.Message}";
        }
        finally
        {
            _isHeartbeatInProgress = false;
        }
    }

    private async Task TryApplyUpdateAsync(DeviceUpdateInfo updateInfo)
    {
        var downloaded = await _updateService.TryStartUpdateAsync(updateInfo, _cancellationTokenSource.Token);
        if (downloaded)
        {
            await Dispatcher.InvokeAsync(() =>
            {
                RebuildTrayMenu();
                UpdateStatusTextBlock.Text = $"更新状态：新版本 {updateInfo.LatestVersion} 已就绪，请从托盘菜单立即更新";
                _notifyIcon.ShowBalloonTip(5000, "思故桌面小喇叭",
                    $"新版本 {updateInfo.LatestVersion} 已就绪，请点击托盘菜单「立即更新」完成升级。",
                    Forms.ToolTipIcon.Info);
            });
        }
    }

    private async Task ConnectWebSocketAsync()
    {
        if (_currentSession is null)
        {
            return;
        }

        var authResult = await _deviceAuthenticationCoordinator.EnsureRegisteredAsync(_currentSession, _cancellationTokenSource.Token);
        await ApplyAuthenticationResultAsync(authResult);
        if (string.IsNullOrEmpty(_deviceToken))
        {
            return;
        }

        await _webSocketClient.ConnectAsync(
            _currentSession.DeviceId,
            _deviceToken,
            HandleNotificationAsync,
            HandleWebSocketDisconnectedAsync,
            _cancellationTokenSource.Token);

        _reconnectAttempt = 0;
        await SendHeartbeatAndApplyStateAsync(showCheckingStatus: true);
        _heartbeatTimer.Start();
        ReconnectStatusTextBlock.Text = "实时连接：已连接";
        ApplyConnectionStatus("online");
    }

    private Task HandleWebSocketDisconnectedAsync(Exception? exception)
    {
        return Dispatcher.InvokeAsync(() =>
        {
            _heartbeatTimer.Stop();
            if (IsDeviceAuthFailure(exception))
            {
                ShowDeviceAuthFailure();
                return;
            }

            ApplyConnectionStatus("offline");
            ScheduleReconnect(exception?.Message);
        }).Task;
    }

    private void ScheduleReconnect(string? reason)
    {
        _reconnectAttempt += 1;
        var delay = ReconnectPolicy.GetDelay(_reconnectAttempt);
        ReconnectStatusTextBlock.Text = $"实时连接：已断开，{delay.TotalSeconds:0} 秒后重试";
        StatusSummaryTextBlock.Text = string.IsNullOrWhiteSpace(reason)
            ? "WebSocket 连接已断开，准备重连"
            : $"WebSocket 已断开：{reason}";
        _reconnectTimer.Stop();
        _reconnectTimer.Interval = delay;
        _reconnectTimer.Start();
    }

    private async void ReconnectTimerOnTick(object? sender, EventArgs e)
    {
        _reconnectTimer.Stop();

        try
        {
            await ConnectWebSocketAsync();
        }
        catch (HttpRequestException exception) when (IsDeviceAuthFailure(exception))
        {
            ShowDeviceAuthFailure();
        }
        catch (Exception exception)
        {
            ScheduleReconnect(exception.Message);
        }
    }

    private void BannerHideTimerOnTick(object? sender, EventArgs e)
    {
        _bannerOverlay.HideNotification();
        _bannerHideTimer.Stop();
    }

    private async void BindingCodeRefreshTimerOnTick(object? sender, EventArgs e)
    {
        if (_isRefreshingBindingCode)
        {
            return;
        }

        var shouldRefresh = _bindingCodeRefreshController.Tick();
        UpdateBindingCodeCountdownText();
        if (!shouldRefresh)
        {
            return;
        }

        await RefreshBindingCodeAsync();
    }

    private async Task HandleNotificationAsync(DeviceNotificationMessage message)
    {
        var colorName = message.Payload.Level switch
        {
            "urgent" => _bannerSettings.UrgentColorName,
            "important" => _bannerSettings.ImportantColorName,
            _ => _bannerSettings.NormalColorName,
        };
        var bannerText = FormatBannerMessage(message.Payload.Title, message.Payload.Content);
        var notificationSettings = ResolveNotificationSettings(message.Payload);

        await Dispatcher.InvokeAsync(() =>
        {
            _bannerOverlay.ShowNotification(bannerText, colorName, notificationSettings);
            StatusSummaryTextBlock.Text = $"已收到通知：{message.Payload.Title}";
            _bannerHideTimer.Stop();
            _bannerHideTimer.Interval = TimeSpan.FromSeconds(notificationSettings.DisplayDurationSeconds);
            _bannerHideTimer.Start();
        });

        await _webSocketClient.SendReceiptAsync("receipt_displayed", message.Payload.NotificationId, _cancellationTokenSource.Token);

        try
        {
            var repeatCount = SpeechAnnouncementService.ResolveRepeatCount(
                message.Payload.TtsEnabled,
                message.Payload.Level,
                message.Payload.TtsRepeatCount);

            if (repeatCount <= 0)
            {
                return;
            }

            await _speechAnnouncementService.SpeakAsync(
                message.Payload.Title,
                message.Payload.Content,
                message.Payload.Level,
                repeatCount,
                _cancellationTokenSource.Token);
            await _webSocketClient.SendReceiptAsync("receipt_spoken", message.Payload.NotificationId, _cancellationTokenSource.Token);
        }
        catch
        {
            await Dispatcher.InvokeAsync(() =>
            {
                StatusSummaryTextBlock.Text = $"已收到通知：{message.Payload.Title}，但语音播报失败";
            });
        }
    }

    private async void OnClosingAsync(object? sender, System.ComponentModel.CancelEventArgs e)
    {
        if (TrayBehavior.ShouldMinimizeToTray(_isExplicitExitRequested))
        {
            e.Cancel = true;
            Hide();
            _notifyIcon.ShowBalloonTip(2000, "思故桌面小喇叭", "客户端仍在后台运行，可从系统托盘重新打开。", Forms.ToolTipIcon.Info);
            return;
        }

        _heartbeatTimer.Stop();
        _bannerHideTimer.Stop();
        _reconnectTimer.Stop();
        _bindingCodeRefreshTimer.Stop();
        _bannerOverlay.HideNotification();
        _cancellationTokenSource.Cancel();
        await _webSocketClient.DisconnectAsync(CancellationToken.None);
        _bannerOverlay.Close();
        _notifyIcon.Visible = false;
        _notifyIcon.Dispose();
        _cancellationTokenSource.Dispose();
        System.Windows.Application.Current.Shutdown();
    }

    private Forms.ContextMenuStrip BuildTrayMenu()
    {
        var menu = new Forms.ContextMenuStrip();
        if (_updateService.IsUpdatePending)
        {
            menu.Items.Add("立即更新", image: null, (_, _) => RestartForUpdate());
            menu.Items.Add(new Forms.ToolStripSeparator());
        }
        menu.Items.Add("打开主窗口", image: null, (_, _) => RestoreFromTray());
        menu.Items.Add("退出", image: null, (_, _) => ExitApplication());
        return menu;
    }

    private void RebuildTrayMenu()
    {
        var oldMenu = _notifyIcon.ContextMenuStrip;
        _notifyIcon.ContextMenuStrip = BuildTrayMenu();
        oldMenu?.Dispose();
    }

    private void RestartForUpdate()
    {
        _updateService.ApplyUpdateAndRestart();
    }

    private void RestoreFromTray()
    {
        Show();
        WindowState = WindowState.Normal;
        Activate();
    }

    private void ExitApplication()
    {
        _isExplicitExitRequested = true;
        Close();
    }

    private void SettingsButtonClicked(object sender, RoutedEventArgs e)
    {
        SettingsPanel.BringIntoView();
        MainScrollViewer.ScrollToEnd();
    }

    private void ApplyDeviceState(DeviceResponse device, string summary)
    {
        StatusSummaryTextBlock.Text = summary;
        ApplyConnectionStatus(device.Status);
        LastHeartbeatTextBlock.Text = DeviceStatusText.FormatLastHeartbeat(device.LastSeenAt);
    }

    private void ApplyBindingCode(string code, int expiresInSeconds)
    {
        var payload = $"school-notify://bind?code={code}";
        _bindingCodeRefreshController.ApplyBindingCode(code, expiresInSeconds);
        BindingCodeTextBlock.Text = $"绑定码：{code}";
        UpdateBindingCodeCountdownText();
        BindingPayloadTextBlock.Text = $"扫码内容：{payload}";
        QrImage.Source = CreateQrImage(payload);
    }

    private void ApplyConnectionStatus(string status)
    {
        var presentation = DeviceStatusText.BuildConnectionStatus(status);
        ConnectionStatusTextBlock.Text = presentation.Text;
        ConnectionStatusTextBlock.Foreground = ResolveTextBrush(presentation.ColorName);
    }

    private async Task RefreshBindingCodeAsync()
    {
        if (_currentSession is null || string.IsNullOrEmpty(_deviceToken))
        {
            return;
        }

        if (_isRefreshingBindingCode)
        {
            return;
        }

        _isRefreshingBindingCode = true;
        BindingCodeCountdownTextBlock.Text = "二维码有效期：刷新中...";

        try
        {
            var bindingCode = await _apiClient.RequestBindingCodeAsync(_currentSession.DeviceId, _deviceToken, _cancellationTokenSource.Token);
            ApplyBindingCode(bindingCode.Code, bindingCode.ExpiresInSeconds);
        }
        catch (HttpRequestException exception) when (IsDeviceAuthFailure(exception))
        {
            BindingCodeCountdownTextBlock.Text = "二维码有效期：认证异常";
            ShowDeviceAuthFailure();
        }
        catch (Exception exception)
        {
            BindingCodeCountdownTextBlock.Text = "二维码有效期：刷新失败";
            ShowOperationalFailure($"绑定码刷新失败：{exception.Message}", null);
        }
        finally
        {
            _isRefreshingBindingCode = false;
        }
    }

    private async void RefreshBindingCodeButtonClicked(object sender, RoutedEventArgs e)
    {
        await RefreshBindingCodeAsync();
    }

    private void UpdateBindingCodeCountdownText()
    {
        BindingCodeCountdownTextBlock.Text = $"二维码有效期：{_bindingCodeRefreshController.RemainingSeconds} 秒";
    }

    private async Task ApplyAuthenticationResultAsync(DeviceAuthenticationResult result)
    {
        var hasChanged = _currentSession is null || _currentSession != result.Session;
        _currentSession = result.Session;
        _deviceToken = result.Session.DeviceToken;
        if (hasChanged)
        {
            await _clientSessionStore.SaveAsync(result.Session, _cancellationTokenSource.Token);
        }
    }

    private static bool IsDeviceAuthFailure(Exception? exception)
    {
        if (exception is HttpRequestException httpException)
        {
            return httpException.StatusCode is HttpStatusCode.Unauthorized or HttpStatusCode.Forbidden;
        }

        var message = exception?.Message;
        if (string.IsNullOrWhiteSpace(message))
        {
            return false;
        }

        return message.Contains("401", StringComparison.OrdinalIgnoreCase)
            || message.Contains("403", StringComparison.OrdinalIgnoreCase)
            || message.Contains("unauthorized", StringComparison.OrdinalIgnoreCase)
            || message.Contains("forbidden", StringComparison.OrdinalIgnoreCase);
    }

    private void ShowDeviceAuthFailure()
    {
        ShowOperationalFailure(DeviceStatusText.AuthFailureSummary, DeviceStatusText.AuthFailureConnectionStatus);
        ConnectionStatusTextBlock.Foreground = System.Windows.Media.Brushes.Crimson;
    }

    private void ShowOperationalFailure(string summary, string? connectionStatus)
    {
        StatusSummaryTextBlock.Text = summary;
        if (!string.IsNullOrWhiteSpace(connectionStatus))
        {
            ConnectionStatusTextBlock.Text = connectionStatus;
        }
    }

    private static System.Windows.Media.Brush ResolveTextBrush(string colorName)
    {
        return colorName switch
        {
            "SeaGreen" => System.Windows.Media.Brushes.SeaGreen,
            "Crimson" => System.Windows.Media.Brushes.Crimson,
            _ => System.Windows.Media.Brushes.SlateGray,
        };
    }

    private static string FormatBannerMessage(string title, string content)
    {
        return $"{title}    |    {content}";
    }

    private BannerSettings ResolveNotificationSettings(DeviceNotificationPayload payload)
    {
        if (payload.DurationSeconds is null || payload.DurationSeconds <= 0)
        {
            return _bannerSettings;
        }

        return _bannerSettings with { DisplayDurationSeconds = payload.DurationSeconds.Value };
    }

    private static BitmapImage CreateQrImage(string payload)
    {
        using var qrGenerator = new QRCodeGenerator();
        using var qrCodeData = qrGenerator.CreateQrCode(payload, QRCodeGenerator.ECCLevel.Q);
        var pngQrCode = new PngByteQRCode(qrCodeData);
        var bytes = pngQrCode.GetGraphic(20);

        using var memoryStream = new MemoryStream(bytes);
        var image = new BitmapImage();
        image.BeginInit();
        image.CacheOption = BitmapCacheOption.OnLoad;
        image.StreamSource = memoryStream;
        image.EndInit();
        image.Freeze();
        return image;
    }

    private async void BannerSettingsControlChanged(object sender, RoutedEventArgs e)
    {
        if (_isLoadingBannerSettings || !IsLoaded)
        {
            return;
        }

        _bannerSettings = ReadBannerSettingsFromControls();
        ApplyBannerSettingsToBanner(_bannerSettings);
        await _bannerSettingsStore.SaveAsync(_bannerSettings, _cancellationTokenSource.Token);
        StatusSummaryTextBlock.Text = "横幅设置已更新";
    }

    private async void ClientSettingsControlChanged(object sender, RoutedEventArgs e)
    {
        if (_isLoadingClientSettings || !IsLoaded)
        {
            return;
        }

        _clientSettings = ReadClientSettingsFromControls();
        ApplyAutoStartSetting(_clientSettings);
        await _clientSettingsStore.SaveAsync(_clientSettings, _cancellationTokenSource.Token);
        StatusSummaryTextBlock.Text = _clientSettings.AutoStartEnabled ? "开机自启动已开启" : "开机自启动已关闭";
    }

    private void ApplyClientSettingsToControls(ClientSettings settings)
    {
        _isLoadingClientSettings = true;
        AutoStartCheckBox.IsChecked = settings.AutoStartEnabled;
        _isLoadingClientSettings = false;
    }

    private ClientSettings ReadClientSettingsFromControls()
    {
        return new ClientSettings(AutoStartEnabled: AutoStartCheckBox.IsChecked == true);
    }

    private void ApplyAutoStartSetting(ClientSettings settings)
    {
        _autoStartService.ApplyForCurrentUser(
            "SchoolNotifyWindowsClient",
            Environment.ProcessPath ?? string.Empty,
            settings.AutoStartEnabled);
    }

    private void ApplyBannerSettingsToControls(BannerSettings settings)
    {
        _isLoadingBannerSettings = true;
        BannerSpeedSlider.Value = settings.ScrollSpeed;
        BannerFontSizeSlider.Value = settings.FontSize;
        SelectRadioButtonByTag(settings.NormalColorName, NormalSteelBlueRadioButton, NormalSeaGreenRadioButton, NormalMediumPurpleRadioButton, NormalSlateGrayRadioButton);
        SelectRadioButtonByTag(settings.ImportantColorName, ImportantOrangeRadioButton, ImportantGoldRadioButton, ImportantCoralRadioButton, ImportantTomatoRadioButton);
        SelectRadioButtonByTag(settings.UrgentColorName, UrgentRedRadioButton, UrgentDarkRedRadioButton, UrgentOrangeRedRadioButton, UrgentCrimsonRadioButton);
        SelectRadioButtonByTag(settings.DisplayDurationSeconds.ToString(CultureInfo.InvariantCulture), Duration10RadioButton, Duration30RadioButton, Duration60RadioButton);
        SelectRadioButtonByTag(settings.DisplayMode, DisplayModeTopBannerRadioButton, DisplayModeFullScreenRadioButton);
        UpdateBannerSettingsSummary(settings);
        _isLoadingBannerSettings = false;
    }

    private void ApplyBannerSettingsToBanner(BannerSettings settings)
    {
        _bannerHideTimer.Interval = TimeSpan.FromSeconds(settings.DisplayDurationSeconds);
        UpdateBannerSettingsSummary(settings);
    }

    private BannerSettings ReadBannerSettingsFromControls()
    {
        var durationTag = ReadSelectedRadioTag(BannerSettings.Default.DisplayDurationSeconds.ToString(CultureInfo.InvariantCulture), Duration10RadioButton, Duration30RadioButton, Duration60RadioButton);
        if (!int.TryParse(durationTag, CultureInfo.InvariantCulture, out var duration))
        {
            duration = BannerSettings.Default.DisplayDurationSeconds;
        }

        return new BannerSettings(
            ScrollSpeed: BannerSpeedSlider.Value,
            FontSize: BannerFontSizeSlider.Value,
            NormalColorName: ReadSelectedRadioTag(BannerSettings.Default.NormalColorName, NormalSteelBlueRadioButton, NormalSeaGreenRadioButton, NormalMediumPurpleRadioButton, NormalSlateGrayRadioButton),
            ImportantColorName: ReadSelectedRadioTag(BannerSettings.Default.ImportantColorName, ImportantOrangeRadioButton, ImportantGoldRadioButton, ImportantCoralRadioButton, ImportantTomatoRadioButton),
            UrgentColorName: ReadSelectedRadioTag(BannerSettings.Default.UrgentColorName, UrgentRedRadioButton, UrgentDarkRedRadioButton, UrgentOrangeRedRadioButton, UrgentCrimsonRadioButton),
            DisplayDurationSeconds: duration,
            DisplayMode: ReadSelectedRadioTag(BannerSettings.Default.DisplayMode, DisplayModeTopBannerRadioButton, DisplayModeFullScreenRadioButton));
    }

    private void UpdateBannerSettingsSummary(BannerSettings settings)
    {
        BannerSpeedValueTextBlock.Text = $"{settings.ScrollSpeed:0} px/s";
        BannerFontSizeValueTextBlock.Text = $"{settings.FontSize:0} px";
    }

    private static void SelectRadioButtonByTag(string tag, params System.Windows.Controls.RadioButton[] radioButtons)
    {
        foreach (var radioButton in radioButtons)
        {
            if (string.Equals(radioButton.Tag?.ToString(), tag, StringComparison.Ordinal))
            {
                radioButton.IsChecked = true;
                return;
            }
        }

        if (radioButtons.Length > 0)
        {
            radioButtons[0].IsChecked = true;
        }
    }

    private static string ReadSelectedRadioTag(string fallback, params System.Windows.Controls.RadioButton[] radioButtons)
    {
        foreach (var radioButton in radioButtons)
        {
            if (radioButton.IsChecked == true)
            {
                return radioButton.Tag?.ToString() ?? fallback;
            }
        }

        return fallback;
    }

    private async void BannerResetToDefaultClicked(object sender, RoutedEventArgs e)
    {
        _bannerSettings = BannerSettings.Default;
        ApplyBannerSettingsToControls(_bannerSettings);
        ApplyBannerSettingsToBanner(_bannerSettings);
        await _bannerSettingsStore.SaveAsync(_bannerSettings, _cancellationTokenSource.Token);
        StatusSummaryTextBlock.Text = "横幅设置已恢复默认";
    }
}
