using System.Threading;
using System.Threading.Tasks;
using SchoolNotify.WindowsClient.Models;
using SchoolNotify.WindowsClient.Services;
using Xunit;

namespace SchoolNotify.WindowsClient.Tests;

public sealed class DeviceAuthenticationCoordinatorTests
{
    [Fact]
    public async Task EnsureRegisteredAsync_ReusesPersistedDeviceToken()
    {
        var session = new ClientSession(
            DeviceId: "device-001",
            DeviceName: "值班室电脑",
            ClientVersion: "0.1.0",
            DeviceToken: "device-token-001");
        var registerCalls = 0;
        var coordinator = new DeviceAuthenticationCoordinator(
            registerDeviceAsync: (_, _) =>
            {
                registerCalls += 1;
                return Task.FromResult(new DeviceResponse("device-001", "值班室电脑", "", "0.1.0", "online", System.DateTimeOffset.UtcNow, "device-token-002"));
            });

        var result = await coordinator.EnsureRegisteredAsync(session, CancellationToken.None);

        Assert.Equal(0, registerCalls);
        Assert.Equal("device-token-001", result.Session.DeviceToken);
    }

    [Fact]
    public async Task EnsureRegisteredAsync_RegistersWhenDeviceTokenMissing()
    {
        var session = new ClientSession(
            DeviceId: "device-001",
            DeviceName: "值班室电脑",
            ClientVersion: "0.1.0",
            DeviceToken: "");
        var registerCalls = 0;
        var coordinator = new DeviceAuthenticationCoordinator(
            registerDeviceAsync: (_, _) =>
            {
                registerCalls += 1;
                return Task.FromResult(new DeviceResponse("device-001", "值班室电脑", "", "0.1.0", "online", System.DateTimeOffset.UtcNow, "device-token-002"));
            });

        var result = await coordinator.EnsureRegisteredAsync(session, CancellationToken.None);

        Assert.Equal(1, registerCalls);
        Assert.Equal("device-token-002", result.Session.DeviceToken);
    }

    [Fact]
    public async Task ReRegisterAsync_RefreshesDeviceToken()
    {
        var session = new ClientSession(
            DeviceId: "device-001",
            DeviceName: "值班室电脑",
            ClientVersion: "0.1.0",
            DeviceToken: "device-token-001");
        var registerCalls = 0;
        var coordinator = new DeviceAuthenticationCoordinator(
            registerDeviceAsync: (_, _) =>
            {
                registerCalls += 1;
                return Task.FromResult(new DeviceResponse("device-001", "值班室电脑", "", "0.1.0", "online", System.DateTimeOffset.UtcNow, "device-token-003"));
            });

        var result = await coordinator.ReRegisterAsync(session, CancellationToken.None);

        Assert.Equal(1, registerCalls);
        Assert.Equal("device-token-003", result.Session.DeviceToken);
    }

}
