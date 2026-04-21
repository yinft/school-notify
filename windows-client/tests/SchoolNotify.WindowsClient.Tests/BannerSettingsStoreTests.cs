using System;
using System.IO;
using System.Threading.Tasks;
using SchoolNotify.WindowsClient.Models;
using SchoolNotify.WindowsClient.Services;
using Xunit;

namespace SchoolNotify.WindowsClient.Tests;

public sealed class BannerSettingsStoreTests
{
    [Fact]
    public async Task BannerSettingsStore_RoundTripsSavedSettings()
    {
        var filePath = Path.Combine(Path.GetTempPath(), $"school-notify-banner-settings-{Guid.NewGuid():N}.json");

        try
        {
            var store = new BannerSettingsStore(filePath);
            var expected = new BannerSettings(
                ScrollSpeed: 220,
                FontSize: 30,
                NormalColorName: "SeaGreen",
                ImportantColorName: "Orange",
                UrgentColorName: "Red",
                DisplayDurationSeconds: 30);

            await store.SaveAsync(expected);
            var actual = await store.LoadAsync();

            Assert.Equal(expected, actual);
        }
        finally
        {
            if (File.Exists(filePath))
            {
                File.Delete(filePath);
            }
        }
    }

    [Fact]
    public void BannerSettings_Default_HasThreeLevelColors()
    {
        var defaults = BannerSettings.Default;

        Assert.NotNull(defaults.NormalColorName);
        Assert.NotNull(defaults.ImportantColorName);
        Assert.NotNull(defaults.UrgentColorName);
        Assert.NotEqual(defaults.NormalColorName, defaults.ImportantColorName);
        Assert.NotEqual(defaults.ImportantColorName, defaults.UrgentColorName);
    }
}
