using System;
using SchoolNotify.WindowsClient.Services;
using Xunit;

namespace SchoolNotify.WindowsClient.Tests;

public sealed class ServerConfigStoreTests
{
    [Fact]
    public void ServerConfigStore_ReturnsDefaultBaseUrl_WhenEnvVarNotSet()
    {
        var original = Environment.GetEnvironmentVariable("SCHOOL_NOTIFY_BASE_URL");
        try
        {
            Environment.SetEnvironmentVariable("SCHOOL_NOTIFY_BASE_URL", null);
            var store = new ServerConfigStore();

            var config = store.Load();

            Assert.Equal("http://127.0.0.1:8000", config.BaseUrl);
        }
        finally
        {
            Environment.SetEnvironmentVariable("SCHOOL_NOTIFY_BASE_URL", original);
        }
    }

    [Fact]
    public void ServerConfigStore_LoadsBaseUrl_FromEnvVar()
    {
        var original = Environment.GetEnvironmentVariable("SCHOOL_NOTIFY_BASE_URL");
        try
        {
            Environment.SetEnvironmentVariable("SCHOOL_NOTIFY_BASE_URL", "https://www.schoolhelper.cn");
            var store = new ServerConfigStore();

            var config = store.Load();

            Assert.Equal("https://www.schoolhelper.cn", config.BaseUrl);
        }
        finally
        {
            Environment.SetEnvironmentVariable("SCHOOL_NOTIFY_BASE_URL", original);
        }
    }

    [Fact]
    public void ServerConfigStore_TrimsTrailingSlash()
    {
        var original = Environment.GetEnvironmentVariable("SCHOOL_NOTIFY_BASE_URL");
        try
        {
            Environment.SetEnvironmentVariable("SCHOOL_NOTIFY_BASE_URL", "https://example.com/");
            var store = new ServerConfigStore();

            var config = store.Load();

            Assert.Equal("https://example.com", config.BaseUrl);
        }
        finally
        {
            Environment.SetEnvironmentVariable("SCHOOL_NOTIFY_BASE_URL", original);
        }
    }
}
