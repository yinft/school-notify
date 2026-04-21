namespace SchoolNotify.WindowsClient.Services;

public static class TrayBehavior
{
    public static bool ShouldMinimizeToTray(bool isExplicitExitRequested)
    {
        return !isExplicitExitRequested;
    }
}
