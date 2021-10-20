using Microsoft.Toolkit.Mvvm.ComponentModel;
using Microsoft.UI.Xaml.Controls;

namespace AIForLis.Models
{
    public class Notification : ObservableObject
    {
        private InfoBarSeverity severity;
        public InfoBarSeverity Severity
        {
            get => severity;
            set => SetProperty(ref severity, value);
        }

        private string title;
        public string Title
        {
            get => title;
            set => SetProperty(ref title, value);
        }

        private string message;
        public string Message
        {
            get => message;
            set => SetProperty(ref message, value);
        }

        private bool visible;
        public bool Visible
        {
            get => visible;
            set => SetProperty(ref visible, value);
        }

        public Notification()
        {
            this.Severity = InfoBarSeverity.Informational;
            this.Visible = false;
        }
    }
}
