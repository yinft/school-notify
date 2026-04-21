namespace SchoolNotify.WindowsClient.Services;

public static class AutoStartCommandBuilder
{
    public static string Build(string executablePath)
    {
        return $"\"{executablePath}\"";
    }
}
