using AIForLis.ViewModels;
using Microsoft.Extensions.DependencyInjection;
using System;
using System.Collections.Generic;
using System.Linq;
using Windows.UI.Xaml;
using Windows.UI.Xaml.Controls;

namespace AIForLis.Views
{
    public sealed partial class ShellPage : Page
    {
        private CoreViewModel ViewModel => App.Current.Services.GetService<CoreViewModel>();

        public ShellPage()
        {
            this.InitializeComponent();
        }

        private readonly List<(string Tag, Type Page)> pages = new List<(string Tag, Type Page)>
        {
            ("Speech", typeof(SpeechPage)),
            ("Library", typeof(LibraryPage))
        };

        private void OnNavigationViewLoaded(object sender, RoutedEventArgs e)
        {
            contentFrame.Navigate(typeof(SpeechPage), null);
            this.navigationView.IsPaneOpen = false;
        }

        private void OnNavigationViewItemInvoked(NavigationView sender, NavigationViewItemInvokedEventArgs args)
        {
            Type page = null;

            if (args.IsSettingsInvoked)
            {
                page = typeof(SettingsPage);
            }
            else if (args.InvokedItemContainer != null)
            {
                var tag = args.InvokedItemContainer.Tag.ToString();
                var item = pages.FirstOrDefault(p => p.Tag.Equals(tag));
                page = item.Page;
            }

            // Get the page type before navigation so you can prevent duplicate
            // entries in the backstack.
            var previousPageType = contentFrame.CurrentSourcePageType;

            // Only navigate if the selected page isn't currently loaded.
            if (!(page is null) && !Type.Equals(previousPageType, page))
            {
                contentFrame.Navigate(page, null, args.RecommendedNavigationTransitionInfo);
            }
        }
    }
}
