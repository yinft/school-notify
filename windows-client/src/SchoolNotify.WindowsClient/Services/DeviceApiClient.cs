using System.Net.Http;
using System.Net.Http.Json;
using System.Net.Http.Headers;
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
        using var response = await httpClient.PostAsJsonAsync("/api/devices/register", request, JsonOptions, cancellationToken);
        response.EnsureSuccessStatusCode();
        return (await response.Content.ReadFromJsonAsync<DeviceResponse>(JsonOptions, cancellationToken))!;
    }

    public async Task<BindingCodeResponse> RequestBindingCodeAsync(string deviceId, string deviceToken, CancellationToken cancellationToken = default)
    {
        using var request = new HttpRequestMessage(HttpMethod.Post, "/api/bindings/code")
        {
            Content = JsonContent.Create(new { device_id = deviceId }, options: JsonOptions)
        };
        request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", deviceToken);
        using var response = await httpClient.SendAsync(request, cancellationToken);
        response.EnsureSuccessStatusCode();
        return (await response.Content.ReadFromJsonAsync<BindingCodeResponse>(JsonOptions, cancellationToken))!;
    }

    public async Task<DeviceResponse> SendHeartbeatAsync(string deviceId, string deviceToken, CancellationToken cancellationToken = default)
    {
        using var request = new HttpRequestMessage(HttpMethod.Post, $"/api/devices/{deviceId}/heartbeat");
        request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", deviceToken);
        using var response = await httpClient.SendAsync(request, cancellationToken);
        response.EnsureSuccessStatusCode();
        return (await response.Content.ReadFromJsonAsync<DeviceResponse>(JsonOptions, cancellationToken))!;
    }

    public async Task<DeviceUpdateInfo> CheckUpdateAsync(string deviceId, string deviceToken, CancellationToken cancellationToken = default)
    {
        using var request = new HttpRequestMessage(HttpMethod.Get, $"/api/devices/{deviceId}/update");
        request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", deviceToken);
        using var response = await httpClient.SendAsync(request, cancellationToken);
        response.EnsureSuccessStatusCode();
        return (await response.Content.ReadFromJsonAsync<DeviceUpdateInfo>(JsonOptions, cancellationToken))!;
    }
}
