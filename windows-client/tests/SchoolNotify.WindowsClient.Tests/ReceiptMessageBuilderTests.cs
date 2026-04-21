using SchoolNotify.WindowsClient.Services;
using Xunit;

namespace SchoolNotify.WindowsClient.Tests;

public class ReceiptMessageBuilderTests
{
    [Fact]
    public void Build_CreatesReceiptEnvelopeJson()
    {
        var json = ReceiptMessageBuilder.Build("receipt_displayed", "notification-1");

        Assert.Equal("{\"event\":\"receipt_displayed\",\"notification_id\":\"notification-1\"}", json);
    }
}
