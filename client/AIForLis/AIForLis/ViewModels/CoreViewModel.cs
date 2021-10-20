using AIForLis.Models;
using Microsoft.Toolkit.Mvvm.ComponentModel;
using Microsoft.UI.Xaml.Controls;
using System.Collections.ObjectModel;

namespace AIForLis.ViewModels
{
    public class CoreViewModel : ObservableObject
    {
        public ObservableCollection<SpeechRecognitionResult> SpeechRecognitionResults { get; }
        public Notification Notification { get; }

        public CoreViewModel()
        {
            this.SpeechRecognitionResults = new ObservableCollection<SpeechRecognitionResult>();
            this.Notification = new Notification();
        }

        public void NotifyUser(string message, string title = null, InfoBarSeverity severity = InfoBarSeverity.Informational)
        {
            if (title is null)
            {
                switch (severity)
                {
                    case InfoBarSeverity.Informational:
                        this.Notification.Title = "Information";
                        break;
                    case InfoBarSeverity.Success:
                        this.Notification.Title = "Success";
                        break;
                    case InfoBarSeverity.Warning:
                        this.Notification.Title = "Warning";
                        break;
                    case InfoBarSeverity.Error:
                        this.Notification.Title = "Error";
                        break;
                }
            }
            else
            {
                this.Notification.Title = title;
            }

            this.Notification.Severity = severity;
            this.Notification.Message = message;
            this.Notification.Visible = true;
        }
    }
}
