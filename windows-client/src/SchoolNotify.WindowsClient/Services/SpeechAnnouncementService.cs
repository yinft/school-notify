namespace SchoolNotify.WindowsClient.Services;

public sealed class SpeechAnnouncementService
{
    public Task SpeakAsync(string title, string content, string level, int repeatCount, CancellationToken cancellationToken = default)
    {
        if (repeatCount <= 0)
        {
            return Task.CompletedTask;
        }

        var text = SpeechAnnouncementFormatter.Format(title, content, level);

        return Task.Run(() =>
        {
            var voiceType = Type.GetTypeFromProgID("SAPI.SpVoice");
            if (voiceType is null)
            {
                return;
            }

            var voice = Activator.CreateInstance(voiceType);
            if (voice is null)
            {
                return;
            }

            for (var i = 0; i < repeatCount; i += 1)
            {
                cancellationToken.ThrowIfCancellationRequested();
                voiceType.InvokeMember(
                    "Speak",
                    System.Reflection.BindingFlags.InvokeMethod,
                    binder: null,
                    target: voice,
                    args: new object[] { text });
            }
        }, cancellationToken);
    }

    public static int ResolveRepeatCount(bool ttsEnabled, string level, int? ttsRepeatCount)
    {
        if (!ttsEnabled)
        {
            return 0;
        }

        if (ttsRepeatCount is not null && ttsRepeatCount > 0)
        {
            return ttsRepeatCount.Value;
        }

        return level == "urgent" ? 3 : 1;
    }
}
