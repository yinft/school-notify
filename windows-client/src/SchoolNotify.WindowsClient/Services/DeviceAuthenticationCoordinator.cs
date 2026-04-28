using SchoolNotify.WindowsClient.Models;

namespace SchoolNotify.WindowsClient.Services;

public sealed class DeviceAuthenticationCoordinator(
    Func<DeviceRegistrationRequest, CancellationToken, Task<DeviceResponse>> registerDeviceAsync)
{
    public async Task<DeviceAuthenticationResult> EnsureRegisteredAsync(ClientSession session, CancellationToken cancellationToken)
    {
        if (!string.IsNullOrWhiteSpace(session.DeviceToken))
        {
            return new DeviceAuthenticationResult(session, null, false);
        }

        return await ReRegisterAsync(session, cancellationToken);
    }

    public async Task<DeviceAuthenticationResult> ReRegisterAsync(ClientSession session, CancellationToken cancellationToken)
    {
        var registeredDevice = await registerDeviceAsync(
            new DeviceRegistrationRequest(session.DeviceId, session.DeviceName, session.ClientVersion),
            cancellationToken);
        var nextSession = session with { DeviceToken = registeredDevice.DeviceToken };
        return new DeviceAuthenticationResult(nextSession, registeredDevice, true);
    }

}

public sealed record DeviceAuthenticationResult(ClientSession Session, DeviceResponse? RegisteredDevice, bool WasRegistered);
