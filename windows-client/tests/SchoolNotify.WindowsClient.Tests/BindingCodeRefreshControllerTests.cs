using SchoolNotify.WindowsClient.Services;
using Xunit;

namespace SchoolNotify.WindowsClient.Tests;

public class BindingCodeRefreshControllerTests
{
    [Fact]
    public void ApplyBindingCode_SetsCodeAndRemainingSeconds()
    {
        var controller = new BindingCodeRefreshController();

        controller.ApplyBindingCode("123456", 30);

        Assert.Equal("123456", controller.Code);
        Assert.Equal(30, controller.RemainingSeconds);
    }

    [Fact]
    public void Tick_ReturnsFalseBeforeCountdownExpires()
    {
        var controller = new BindingCodeRefreshController();
        controller.ApplyBindingCode("123456", 3);

        var shouldRefresh = controller.Tick();

        Assert.False(shouldRefresh);
        Assert.Equal(2, controller.RemainingSeconds);
    }

    [Fact]
    public void Tick_ReturnsTrueWhenCountdownExpires()
    {
        var controller = new BindingCodeRefreshController();
        controller.ApplyBindingCode("123456", 1);

        var shouldRefresh = controller.Tick();

        Assert.True(shouldRefresh);
        Assert.Equal(0, controller.RemainingSeconds);
    }
}
