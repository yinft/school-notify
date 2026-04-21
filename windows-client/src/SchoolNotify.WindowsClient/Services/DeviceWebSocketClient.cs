using System.Net.WebSockets;
using System.Text;
using System.Text.Json;
using SchoolNotify.WindowsClient.Models;

namespace SchoolNotify.WindowsClient.Services;

public sealed class DeviceWebSocketClient
{
    private readonly Uri _baseUri;
    private ClientWebSocket? _socket;

    public DeviceWebSocketClient(Uri baseUri)
    {
        _baseUri = baseUri;
    }

    public async Task ConnectAsync(
        string deviceId,
        Func<DeviceNotificationMessage, Task> onNotification,
        Func<Exception?, Task>? onDisconnected,
        CancellationToken cancellationToken)
    {
        _socket = new ClientWebSocket();
        var websocketUri = new UriBuilder(_baseUri)
        {
            Scheme = _baseUri.Scheme == "https" ? "wss" : "ws",
            Path = $"/ws/devices/{deviceId}"
        }.Uri;

        await _socket.ConnectAsync(websocketUri, cancellationToken);
        _ = ReceiveLoopAsync(_socket, onNotification, onDisconnected, cancellationToken);
    }

    public async Task DisconnectAsync(CancellationToken cancellationToken)
    {
        if (_socket is null)
        {
            return;
        }

        if (_socket.State == WebSocketState.Open)
        {
            await _socket.CloseAsync(WebSocketCloseStatus.NormalClosure, "closing", cancellationToken);
        }

        _socket.Dispose();
        _socket = null;
    }

    public async Task SendReceiptAsync(string eventName, string notificationId, CancellationToken cancellationToken)
    {
        if (_socket is null || _socket.State != WebSocketState.Open)
        {
            return;
        }

        var json = ReceiptMessageBuilder.Build(eventName, notificationId);
        var bytes = Encoding.UTF8.GetBytes(json);
        await _socket.SendAsync(bytes, WebSocketMessageType.Text, true, cancellationToken);
    }

    private static async Task ReceiveLoopAsync(
        ClientWebSocket socket,
        Func<DeviceNotificationMessage, Task> onNotification,
        Func<Exception?, Task>? onDisconnected,
        CancellationToken cancellationToken)
    {
        try
        {
            var buffer = new byte[4096];

            while (socket.State == WebSocketState.Open && !cancellationToken.IsCancellationRequested)
            {
                var result = await socket.ReceiveAsync(buffer, cancellationToken);
                if (result.MessageType == WebSocketMessageType.Close)
                {
                    break;
                }

                var json = Encoding.UTF8.GetString(buffer, 0, result.Count);
                var document = JsonDocument.Parse(json);
                var eventName = document.RootElement.GetProperty("event").GetString();
                if (eventName != "notification_created")
                {
                    continue;
                }

                var message = JsonSerializer.Deserialize<DeviceNotificationMessage>(json, new JsonSerializerOptions
                {
                    PropertyNameCaseInsensitive = true
                });

                if (message is not null)
                {
                    await SendReceiptAsync(socket, "receipt_received", message.Payload.NotificationId, cancellationToken);
                    await onNotification(message);
                }
            }

            if (onDisconnected is not null && !cancellationToken.IsCancellationRequested)
            {
                await onDisconnected(null);
            }
        }
        catch (Exception exception) when (!cancellationToken.IsCancellationRequested)
        {
            if (onDisconnected is not null)
            {
                await onDisconnected(exception);
            }
        }
    }

    private static async Task SendReceiptAsync(ClientWebSocket socket, string eventName, string notificationId, CancellationToken cancellationToken)
    {
        var json = ReceiptMessageBuilder.Build(eventName, notificationId);
        var bytes = Encoding.UTF8.GetBytes(json);
        await socket.SendAsync(bytes, WebSocketMessageType.Text, true, cancellationToken);
    }
}
