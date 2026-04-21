using System.Net.Http;
using System.Net.Http.Json;
using System.Text.Json;
using SchoolNotify.WindowsClient.Models;

namespace SchoolNotify.WindowsClient.Services;

public sealed class DeviceApiClient(HttpClient httpClient)
{
    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        PropertyNameCaseInsensitive = true
    };

    public async Task<DeviceResponse> RegisterDeviceAsync(DeviceRegistrationRequest request, CancellationToken cancellationToken = default)
    {
        using var response = await httpClient.PostAsJsonAsync("/api/devices/register", request, cancellationToken);
        response.EnsureSuccessStatusCode();
        return (await response.Content.ReadFromJsonAsync<DeviceResponse>(JsonOptions, cancellationToken))!;
    }

    public async Task<BindingCodeResponse> RequestBindingCodeAsync(string deviceId, CancellationToken cancellationToken = default)
    {
        using var response = await httpClient.PostAsJsonAsync("/api/bindings/code", new { device_id = deviceId }, cancellationToken);
        response.EnsureSuccessStatusCode();
        return (await response.Content.ReadFromJsonAsync<BindingCodeResponse>(JsonOptions, cancellationToken))!;
    }

    public async Task<DeviceResponse> SendHeartbeatAsync(string deviceId, CancellationToken cancellationToken = default)
    {
        using var response = await httpClient.PostAsync($"/api/devices/{deviceId}/heartbeat", content: null, cancellationToken);
        response.EnsureSuccessStatusCode();
        return (await response.Content.ReadFromJsonAsync<DeviceResponse>(JsonOptions, cancellationToken))!;
    }
}
