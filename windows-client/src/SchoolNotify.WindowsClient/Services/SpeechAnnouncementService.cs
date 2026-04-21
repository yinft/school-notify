namespace SchoolNotify.WindowsClient.Services;

public sealed class SpeechAnnouncementService
{
    public Task SpeakAsync(string title, string content, string level, CancellationToken cancellationToken = default)
    {
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

            voiceType.InvokeMember(
                "Speak",
                System.Reflection.BindingFlags.InvokeMethod,
                binder: null,
                target: voice,
                args: new object[] { text });
        }, cancellationToken);
    }
}
