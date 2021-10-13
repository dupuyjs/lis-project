using Microsoft.CognitiveServices.Speech;
using Microsoft.CognitiveServices.Speech.Audio;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices.WindowsRuntime;
using System.Threading.Tasks;
using Windows.Foundation;
using Windows.Foundation.Collections;
using Windows.UI.Xaml;
using Windows.UI.Xaml.Controls;
using Windows.UI.Xaml.Controls.Primitives;
using Windows.UI.Xaml.Data;
using Windows.UI.Xaml.Input;
using Windows.UI.Xaml.Media;
using Windows.UI.Xaml.Navigation;

// The Blank Page item template is documented at https://go.microsoft.com/fwlink/?LinkId=234238

namespace AIForLis.Views
{
    /// <summary>
    /// An empty page that can be used on its own or navigated to within a Frame.
    /// </summary>
    public sealed partial class HomePage : Page
    {
        SpeechRecognizer recognizer = null;

        public HomePage()
        {
            this.InitializeComponent();
        }

        private async void SpeechRecognitionFromMicrophone_ButtonClicked(object sender, RoutedEventArgs e)
        {
            var speechConfig = SpeechConfig.FromSubscription("<paste-your-speech-key-here>", "<paste-your-speech-location/region-here>");

            var audioConfig = AudioConfig.FromDefaultMicrophoneInput();
            var recognizer = new SpeechRecognizer(speechConfig, audioConfig);

            var result = await recognizer.RecognizeOnceAsync();
        }

        private async Task<bool> CheckMicrophoneRequirementAsync()
        {
            bool isMicAvailable = true;
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
                isMicAvailable = false;
            }
            if (!isMicAvailable)
            {
                _ = await Windows.System.Launcher.LaunchUriAsync(new Uri("ms-settings:privacy-microphone"));
            }

            return isMicAvailable;
        }

        private async void CaptureSwitch_Toggled(object sender, RoutedEventArgs e)
        {


            if (sender is ToggleSwitch toggleSwitch)
            {
                if (toggleSwitch.IsOn)
                {
                    bool isMicAvailable = await CheckMicrophoneRequirementAsync();

                    if(isMicAvailable)
                    {
                        string subscriptionKey = "f814d20faaba45b99610c52d9076a7f5";
                        string region = "westeurope";

                        var config = SpeechConfig.FromSubscription(subscriptionKey, region);
                        var audioConfig = AudioConfig.FromDefaultMicrophoneInput();

                        recognizer = new SpeechRecognizer(config, "fr-fr", audioConfig);
                        
                        recognizer.Recognized += async (s, ev) =>
                        {
                            if (ev.Result.Reason == ResultReason.RecognizedSpeech)
                            {
                                await Dispatcher.RunAsync(Windows.UI.Core.CoreDispatcherPriority.Normal, () => {
                                    Output.Items.Add($"RECOGNIZED: Text={ev.Result.Text}");
                                });
             
                                
                            }
                            else if (ev.Result.Reason == ResultReason.NoMatch)
                            {
                                Debug.WriteLine($"NOMATCH: Speech could not be recognized.");
                            }
                        };

                        recognizer.Canceled += (s, ev) =>
                        {
                            Debug.WriteLine($"CANCELED: Reason={ev.Reason}");

                            if (ev.Reason == CancellationReason.Error)
                            {
                                Debug.WriteLine($"CANCELED: ErrorCode={ev.ErrorCode}");
                                Debug.WriteLine($"CANCELED: ErrorDetails={ev.ErrorDetails}");
                                Debug.WriteLine($"CANCELED: Did you update the subscription info?");
                            }
                        };

                        await recognizer.StartContinuousRecognitionAsync();
                    }
                }
                else
                {
                    await recognizer.StopContinuousRecognitionAsync().ConfigureAwait(false);
                }
            }
        }
    }
}
