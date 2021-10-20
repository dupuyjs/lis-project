using AIForLis.ViewModels;
using Microsoft.CognitiveServices.Speech;
using Microsoft.CognitiveServices.Speech.Audio;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.UI.Xaml.Controls;
using System;
using System.Diagnostics;
using System.Linq;
using System.Threading.Tasks;
using Windows.UI.Xaml;
using Windows.UI.Xaml.Controls;

namespace AIForLis.Views
{
    public sealed partial class SpeechPage : Page
    {
        private SpeechRecognizer recognizer = null;
        private CoreViewModel ViewModel => App.Current.Services.GetService<CoreViewModel>();

        public SpeechPage()
        {
            this.InitializeComponent();
            this.Loaded += OnPageLoaded;
            this.Unloaded += OnPageUnloaded;
        }

        private async void OnPageLoaded(object sender, RoutedEventArgs e)
        {
            bool isMicrophoneAvailable = await CheckMicrophoneRequirementAsync();

            if (isMicrophoneAvailable)
            {
                var settings = App.Current.Services.GetService<SettingsViewModel>();

                string subscriptionKey = settings.SpeechSubscriptionKey;
                string region = settings.SpeechRegion;
                string language = settings.SpeechLanguage;

                var config = SpeechConfig.FromSubscription(subscriptionKey, region);
                config.OutputFormat = OutputFormat.Detailed;
                config.RequestWordLevelTimestamps();

                var audioConfig = AudioConfig.FromDefaultMicrophoneInput();

                recognizer = new SpeechRecognizer(config, language, audioConfig);
                recognizer.Recognized += async (s, ev) =>
                {
                    if (ev.Result.Reason == ResultReason.RecognizedSpeech)
                    {
                        var result = ev.Result.Best().First();

                        if (!string.IsNullOrEmpty(result.Text))
                        {
                            var item = new Models.SpeechRecognitionResult()
                            {
                                Confidence = result.Confidence,
                                Text = result.Text
                            };

                            await Dispatcher.RunAsync(Windows.UI.Core.CoreDispatcherPriority.Normal, () => {
                                ViewModel.SpeechRecognitionResults.Add(item);
                            });
                        }
                    }
                    else if (ev.Result.Reason == ResultReason.NoMatch)
                    {
                        Debug.WriteLine($"NoMatch: Speech could not be recognized.");
                    }
                };

                recognizer.Canceled += async (s, ev) =>
                {
                    await Dispatcher.RunAsync(Windows.UI.Core.CoreDispatcherPriority.Normal, () => {
                        var title = "Speech Service";
                        var message = "The application was not able to use Speech Service. Please check subscription information and region name.";
                        ViewModel.NotifyUser(message, title, InfoBarSeverity.Warning);
                    });
                    
                    Debug.WriteLine($"Canceled: Reason={ev.Reason}");

                    if (ev.Reason == CancellationReason.Error)
                    {
                        Debug.WriteLine($"Canceled: ErrorCode={ev.ErrorCode}");
                        Debug.WriteLine($"Canceled: ErrorDetails={ev.ErrorDetails}");
                    }
                };

                await recognizer.StartContinuousRecognitionAsync();
            }
        }

        private async void OnPageUnloaded(object sender, RoutedEventArgs e)
        {
            await recognizer.StopContinuousRecognitionAsync().ConfigureAwait(false);
        }

        private async Task<bool> CheckMicrophoneRequirementAsync()
        {
            bool isMicrophoneAvailable = true;
            try
            {
                var mediaCapture = new Windows.Media.Capture.MediaCapture();
                var settings = new Windows.Media.Capture.MediaCaptureInitializationSettings
                {
                    StreamingCaptureMode = Windows.Media.Capture.StreamingCaptureMode.Audio
                };
                await mediaCapture.InitializeAsync(settings);
            }
            catch (Exception)
            {
                isMicrophoneAvailable = false;
            }
            if (!isMicrophoneAvailable)
            {
                await Windows.System.Launcher.LaunchUriAsync(new Uri("ms-settings:privacy-microphone"));
            }

            return isMicrophoneAvailable;
        }
    }
}
