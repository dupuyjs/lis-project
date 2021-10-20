using AIForLis.ViewModels;
using Microsoft.Extensions.DependencyInjection;
using Windows.UI.Xaml.Controls;

namespace AIForLis.Views
{
    public sealed partial class SettingsPage : Page
    {
        private SettingsViewModel ViewModel => App.Current.Services.GetService<SettingsViewModel>();

        public SettingsPage()
        {
            this.InitializeComponent();
        }
    }
}
