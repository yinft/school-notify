namespace SchoolNotify.WindowsClient.Services;

public static class DeviceStatusText
{
    public const string AuthFailureSummary = "设备认证异常，请联系管理员";
    public const string AuthFailureConnectionStatus = "连接状态：认证异常";
    public const string RegisteredWaitingForBinding = "设备已注册，等待小程序绑定";
    public const string RestoredTokenWaitingForConnection = "已恢复本地设备令牌，等待连接";
    public const string HeartbeatHealthy = "设备连接正常，客户端在线";

    public static DeviceConnectionStatusPresentation BuildConnectionStatus(string status)
    {
        return status switch
        {
            "online" => new DeviceConnectionStatusPresentation("连接状态：在线", "SeaGreen"),
            "offline" => new DeviceConnectionStatusPresentation("连接状态：离线", "Crimson"),
            _ => new DeviceConnectionStatusPresentation("连接状态：未知", "SlateGray"),
        };
    }

    public static string FormatLastHeartbeat(DateTimeOffset lastSeenAt)
    {
        return $"最后心跳：{lastSeenAt:yyyy-MM-dd HH:mm:ss}";
    }
}

public sealed record DeviceConnectionStatusPresentation(string Text, string ColorName);
