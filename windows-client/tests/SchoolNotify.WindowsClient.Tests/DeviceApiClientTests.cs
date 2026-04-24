using System.Net;
using System.Net.Http;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using SchoolNotify.WindowsClient.Models;
using SchoolNotify.WindowsClient.Services;
using Xunit;

namespace SchoolNotify.WindowsClient.Tests;

public class DeviceApiClientTests
{
    [Fact]
    public async Task RegisterDeviceAsync_PostsRegistrationPayload()
    {
        var handler = new RecordingHandler("{\"device_id\":\"device-001\",\"device_name\":\"值班室电脑\",\"client_version\":\"0.1.0\",\"status\":\"online\",\"last_seen_at\":\"2026-04-21T08:00:00Z\",\"device_token\":\"device-token-001\"}");
        var httpClient = new HttpClient(handler)
        {
            BaseAddress = new System.Uri("http://127.0.0.1:8000")
        };
        var apiClient = new DeviceApiClient(httpClient);

        var response = await apiClient.RegisterDeviceAsync(new DeviceRegistrationRequest("device-001", "值班室电脑", "0.1.0"));

        Assert.Equal(HttpMethod.Post, handler.LastRequest!.Method);
        Assert.Equal("http://127.0.0.1:8000/api/devices/register", handler.LastRequest.RequestUri!.ToString());
        Assert.Contains("\"device_id\"", handler.LastRequestBody);
        Assert.Contains("\"device_name\"", handler.LastRequestBody);
        Assert.Contains("\"client_version\"", handler.LastRequestBody);
        Assert.Equal("device-001", response.DeviceId);
        Assert.Equal("device-token-001", response.DeviceToken);
    }

    [Fact]
    public async Task RequestBindingCodeAsync_PostsDeviceIdAndReturnsCode()
    {
        var handler = new RecordingHandler("{\"device_id\":\"device-001\",\"code\":\"123456\",\"expires_in_seconds\":300}");
        var httpClient = new HttpClient(handler)
        {
            BaseAddress = new System.Uri("http://127.0.0.1:8000")
        };
        var apiClient = new DeviceApiClient(httpClient);

        var response = await apiClient.RequestBindingCodeAsync("device-001", "device-token-001");

        Assert.Equal("123456", response.Code);
        Assert.Equal("device-001", response.DeviceId);
        Assert.Equal(300, response.ExpiresInSeconds);
        Assert.Contains("\"device_id\"", handler.LastRequestBody);
        Assert.Equal("Bearer", handler.LastRequest!.Headers.Authorization!.Scheme);
        Assert.Equal("device-token-001", handler.LastRequest.Headers.Authorization.Parameter);
    }

    [Fact]
    public async Task SendHeartbeatAsync_PostsToHeartbeatEndpoint()
    {
        var handler = new RecordingHandler("{\"device_id\":\"device-001\",\"device_name\":\"值班室电脑\",\"client_version\":\"0.1.0\",\"status\":\"online\",\"last_seen_at\":\"2026-04-21T08:01:00Z\"}");
        var httpClient = new HttpClient(handler)
        {
            BaseAddress = new System.Uri("http://127.0.0.1:8000")
        };
        var apiClient = new DeviceApiClient(httpClient);

        await apiClient.SendHeartbeatAsync("device-001", "device-token-001");

        Assert.Equal(HttpMethod.Post, handler.LastRequest!.Method);
        Assert.Equal("http://127.0.0.1:8000/api/devices/device-001/heartbeat", handler.LastRequest.RequestUri!.ToString());
        Assert.Equal("device-token-001", handler.LastRequest.Headers.Authorization!.Parameter);
    }

    private sealed class RecordingHandler(string responseBody) : HttpMessageHandler
    {
        public HttpRequestMessage? LastRequest { get; private set; }

        public string LastRequestBody { get; private set; } = string.Empty;

        protected override async Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken cancellationToken)
        {
            LastRequest = request;
            LastRequestBody = request.Content is null ? string.Empty : await request.Content.ReadAsStringAsync(cancellationToken);

            return new HttpResponseMessage(HttpStatusCode.OK)
            {
                Content = new StringContent(responseBody, Encoding.UTF8, "application/json")
            };
        }
    }
}
