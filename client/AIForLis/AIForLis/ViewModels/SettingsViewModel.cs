using Microsoft.Toolkit.Mvvm.ComponentModel;
using System.Runtime.CompilerServices;
using Windows.Storage;

namespace AIForLis.ViewModels
{
    public class SettingsViewModel : ObservableObject
    {
        private ApplicationDataContainer LocalSettings { get; }

        public string SpeechRegion
        {
            get
            {
                string defaultRegion = "westeurope";
                return ReadSetting<string>(defaultRegion);
            }
            set
            {
                SaveSetting(value);
                OnPropertyChanged(nameof(SpeechRegion));
            }
        }

        public string SpeechLanguage
        {
            get
            {
                string defaultLanguage= "fr-FR";
                return ReadSetting<string>(defaultLanguage);
            }
            set
            {
                SaveSetting(value);
                OnPropertyChanged(nameof(SpeechLanguage));
            }
        }

        public string SpeechSubscriptionKey
        {
            get
            {
                return ReadSetting<string>(null);
            }
            set
            {
                SaveSetting(value);
                OnPropertyChanged(nameof(SpeechRegion));
            }
        }

        public SettingsViewModel()
        {
            this.LocalSettings = ApplicationData.Current.LocalSettings;
        }

        private T ReadSetting<T>(T defaultValue, [CallerMemberName] string key = null)
        {
            if (LocalSettings.Values.ContainsKey(key))
            {
                return (T)LocalSettings.Values[key];
            }

            if (null != defaultValue)
            {
                return defaultValue;
            }

            return default(T);
        }

        private void SaveSetting(object value, [CallerMemberName] string key = null)
        {
            LocalSettings.Values[key] = value;
        }
    }
}
