using SchoolNotify.WindowsClient.Services;
using Xunit;

namespace SchoolNotify.WindowsClient.Tests;

public class DeviceStatusTextTests
{
    [Fact]
    public void AuthFailure_UsesUnifiedSummaryAndConnectionStatus()
    {
        Assert.Equal("设备认证异常，请联系管理员", DeviceStatusText.AuthFailureSummary);
        Assert.Equal("连接状态：认证异常", DeviceStatusText.AuthFailureConnectionStatus);
    }

    [Fact]
    public void BuildsUnifiedSuccessMessages()
    {
        Assert.Equal("设备已注册，等待小程序绑定", DeviceStatusText.RegisteredWaitingForBinding);
        Assert.Equal("已恢复本地设备令牌，等待连接", DeviceStatusText.RestoredTokenWaitingForConnection);
        Assert.Equal("设备连接正常，客户端在线", DeviceStatusText.HeartbeatHealthy);
    }

    [Theory]
    [InlineData("online", "连接状态：在线", "SeaGreen")]
    [InlineData("offline", "连接状态：离线", "Crimson")]
    [InlineData("unknown", "连接状态：未知", "SlateGray")]
    public void BuildsChineseConnectionStatusWithColor(string status, string expectedText, string expectedColor)
    {
        var presentation = DeviceStatusText.BuildConnectionStatus(status);

        Assert.Equal(expectedText, presentation.Text);
        Assert.Equal(expectedColor, presentation.ColorName);
    }

    [Fact]
    public void FormatsLastHeartbeatWithoutApplyingAnotherTimezoneOffset()
    {
        var local = new DateTimeOffset(2026, 4, 21, 16, 1, 0, TimeSpan.Zero);

        var text = DeviceStatusText.FormatLastHeartbeat(local);

        Assert.Equal("最后心跳：2026-04-21 16:01:00", text);
    }
}
