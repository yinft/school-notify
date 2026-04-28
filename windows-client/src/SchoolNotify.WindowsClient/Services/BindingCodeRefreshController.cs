namespace SchoolNotify.WindowsClient.Services;

public sealed class BindingCodeRefreshController
{
    public string Code { get; private set; } = string.Empty;

    public int RemainingSeconds { get; private set; }

    public void ApplyBindingCode(string code, int expiresInSeconds)
    {
        Code = code;
        RemainingSeconds = expiresInSeconds > 0 ? expiresInSeconds : 0;
    }

    public bool Tick()
    {
        if (RemainingSeconds <= 0)
        {
            return true;
        }

        RemainingSeconds -= 1;
        return RemainingSeconds == 0;
    }
}
