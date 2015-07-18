define(['jquery', 'alertify.min', 'session-security-script', 'domReady'], function(jQuery, alertify) {
	require(['theme', 'autohidingnavbar'], function() {
        jQuery( document ).ready(function() {
            jQuery(".navbar-fixed-top").autoHidingNavbar();
        });
        function getCookie(name) {
            var cookieValue = null;
            if (document.cookie && document.cookie != '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) == (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
        var csrftoken = getCookie('csrftoken');
        function csrfSafeMethod(method) {
            // these HTTP methods do not require CSRF protection
            return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
        }
        jQuery.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });
        if (window.focusItem != undefined) {
            jQuery(document).ready(function() {
                jQuery(focusItem).focus();
            })
        }
	});
    return alertify;
});