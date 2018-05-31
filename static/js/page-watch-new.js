// Generated by CoffeeScript 1.8.0
(function() {
  $(document).ready(function() {
    var AppRouter, app_router, hideAll, showCapture, showDiffs, showError, showExistingCaptures, showSS, showSpinner, showStats;
    $("section.stats .header").click(function() {
      var $content, $header;
      $header = $(this);
      $content = $header.next();
      $content.slideToggle(500, function() {
        var new_text;
        new_text = function() {
          if ($content.is(":visible")) {
            return "Click to hide capture stats";
          } else {
            return "Captures below, click to show stats";
          }
        };
        $header.text(new_text);
      });
    });
    hideAll = function() {
      $(".subscribe-form .notification").hide();
      $("section.instructions").hide();
      $("section.spinner").hide();
      $("section.stats").hide();
      $("section.diffs").hide();
      $("section.url-status").hide();
      $("section.error").hide();
      $("section.subscribe").hide();
      $("section.screenshot").hide();
      return $(".success-fade").show();
    };
    showError = function(msg) {
      hideAll();
      $("footer").show();
      $("div.error-msg").text(msg);
      return $("section.error").show();
    };
    showSpinner = function(msg) {
      hideAll();
      $("footer").hide();
      $("div.spinner-msg").text(msg);
      return $("section.spinner").show();
    };
    showCapture = function(data, type) {
      $("div.overlay").html("");
      $("footer").show();
      hideAll();
      $("input[name='url']").val(data.url);
      if (data.img === true) {
        $("#img-yes").prop('checked', true);
      } else if (data.img === false) {
        $("#img-no").prop('checked', true);
      }
      if (type !== "d") {
        $("section.url-status div.url-status").html("<h2>Monitoring this page for changes every " + data.interval + ",\n<br />last checked " + data.last_check + "\n</h2>This page-watch will " + data.check_expiration);
        $("section.url-status").show();
        showSS(data);
      }
      if (data.prev_captures.length > 0) {
        showExistingCaptures(data);
      }
    };
    showExistingCaptures = function(data) {
      var capture, i, _i, _len, _ref;
      showStats(data);
      showDiffs(data);
      $(".page-diffs").html("");
      _ref = data.prev_captures;
      for (i = _i = 0, _len = _ref.length; _i < _len; i = ++_i) {
        capture = _ref[i];
        $('.page-diffs').append("<div class=\"preview-wrapper\">\n  <h2>Change detected " + capture.created + " <a href=\"#d/" + capture.hid + "\">[direct link]</a></h2>\n  <div class=\"preview preview-left\" id=\"preview-" + i + "\"> \n    <img src='" + capture.cap_highlight_small_url + "' alt=''>\n  </div>\n  <div class=\"preview preview-right\" id=\"preview-last-" + i + "\"> \n    <img src='" + capture.cap_last_highlight_small_url + "' alt=''>\n  </div>\n  <div class=\"loader\" id=\"loader-" + i + "\">loading preview</div>\n</div>");
        $('div.overlay').append("<div class=\"overlay-inner\" id=\"preview-overlay-" + i + "\"></div>\n<div class=\"overlay-inner\" id=\"preview-last-overlay-" + i + "\"></div>");
        $("#preview-overlay-" + i).zoom({
          url: "" + capture.cap_highlight_url,
          target: $("#preview-overlay-" + i).get(0),
          other_target: $("#preview-last-overlay-" + i).get(0),
          other_url: "" + capture.cap_last_highlight_url,
          $activate_target: $("#preview-" + i),
          $loader: $("#loader-" + i),
          on: "click"
        });
        $("#preview-last-overlay-" + i).zoom({
          url: "" + capture.cap_last_highlight_url,
          target: $("#preview-last-overlay-" + i).get(0),
          other_target: $("#preview-overlay-" + i).get(0),
          other_url: "" + capture.cap_highlight_url,
          $activate_target: $("#preview-last-" + i),
          $loader: $("#loader-" + i),
          on: "click"
        });
      }
    };
    showStats = function(data) {
      var attr, _i, _len, _ref;
      _ref = ["interval", "last_check", "last_change", "changes", "checks", "created"];
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        attr = _ref[_i];
        console.log(attr);
        console.log(data[attr]);
        $("section.stats ." + attr).text(data[attr]);
      }
      $("section.stats .screenshot").html("<a href=\"" + data.cap_url_small + "\">latest-screenshot</a>");
      return $("section.stats").show();
    };
    showDiffs = function(data) {
      return $("section.diffs").show();
    };
    showSS = function(data) {
      $("div.screenshot").html("<img src=\"" + data.cap_url_small + "\" alt=\"preview\">\n<div class=\"loader\" id=\"screenshot-loader\">loading preview</div>");
      $('div.overlay').append("<div class=\"overlay-full\" id=\"preview-overlay\"></div>");
      $("div.screenshot").zoom({
        url: "" + data.cap_url,
        target: $("#preview-overlay").get(0),
        $activate_target: $("div.screenshot"),
        $loader: $("#screenshot-loader"),
        on: "click"
      });
      $('div.rss-icon').html("<a href=\"/f/" + data.hid + ".xml\"><i class=\"fa fa-rss-square fa-5x rss-icon\"></i></a>");
      $("input[name='hid']").val(data.hid);
      $("section.subscribe").show();
      $("section.subscribe div.rss").show();
      $("section.subscribe div.subscribe-form").show();
      $("section.screenshot").show();
      $("section.screenshot div.overlay-text").show();
    };
    $("#email-subscribe").submit(function(e) {
      var form_data;
      e.preventDefault();
      $("button[name='subscribe']").prop("disabled", true);
      $("input[name='email']").prop("disabled", true);
      if ($("input[name='email']").val().length < 3) {
        $(".subscribe-form .notification").html("<div class=\"info\"><i class=\"fa fa-info-circle fa-2x\"></i>Invalid email</div>").fadeIn();
        return;
      }
      form_data = new FormData();
      form_data.append('hid', $("input[name='hid']").val());
      form_data.append('email', $("input[name='email']").val());
      $.ajax({
        url: '/s',
        dataType: 'json',
        data: form_data,
        success: function(data) {
          var email, hid;
          $("button[name='subscribe']").prop("disabled", false);
          $("input[name='email']").prop("disabled", false);
          hid = encodeURIComponent(data.hid);
          email = encodeURIComponent(data.email);
          if (data.status === 'processed') {
            return $(".success-fade").fadeOut("fast", function() {
              return $(".subscribe-form .notification").html("<div class=\"success\"><i class=\"fa fa-check fa-2x\">\n</i>Change notifications for this page will be sent \nto " + data.email + " <a href=\"/s?hid=" + hid + "&email=" + email + "\">unsubscribe</a></div>").fadeIn();
            });
          } else if (data.status === 'info') {
            return $(".subscribe-form .notification").html("<div class=\"info\"><i class=\"fa fa-info-circle fa-2x\"></i>" + data.reason + "\n<a href=\"/s?hid=" + hid + "&email=" + email + "\">unsubscribe</a></div>").fadeIn();
          } else if (data.status === 'errored') {
            return $(".subscribe-form .notification").html("<div class=\"error\"><i class=\"fa fa-exclamation-triangle fa-2x\"></i>" + data.reason + "</div>").fadeIn();
          } else {
            return $(".subscribe-form .notification").html("<div class=\"error\"><i class=\"fa fa-exclamation-triangle fa-2x\"></i>Unknown error :(</div>").fadeIn();
          }
        },
        error: function(e) {
          $("button[name='subscribe']").prop("disabled", false);
          $("input[name='email']").prop("disabled", false);
          return $(".subscribe-form .notification").html("<div class=\"error\"><i class=\"fa fa-exclamation-triangle fa-2x\"></i>Server error, please try again later</div>").fadeIn();
        },
        type: 'POST',
        cache: false,
        contentType: false,
        processData: false
      });
    });
    $("input[name=url]").focus(function() {
      $("input[type=radio]").removeClass("disabled");
      return $("input[type=radio]").prop("disabled", false);
    });
    $("#check-url").submit(function(e) {
      e.preventDefault();
      if ($("input[name='url']").val().length < 3) {
        return;
      }
      $("section.instructions").fadeOut("fast", function() {
        var form_data;
        hideAll();
        window.history.pushState("object or string", "Title", "");
        showSpinner("Processing");
        form_data = new FormData();
        form_data.append('url', $("input[name='url']").val());
        form_data.append('img', $('input[name=img]:checked').val());
        $("button[name=check]").prop("disabled", true);
        $("input[name=url]").prop("disabled", true);
        $("input[type=radio]").prop("disabled", true);
        $("input[type=radio]").addClass("disabled");
        return $.ajax({
          url: '/c',
          dataType: 'json',
          data: form_data,
          success: function(data) {
            var _ref;
            $("button[name='check']").prop("disabled", false);
            $("input[name='url']").prop("disabled", false);
            if ((_ref = data.status) === 'queued' || _ref === 'processing') {
              window.location.href = "#i/" + data.hid;
            } else if (data.status === 'processed') {
              window.history.pushState("object or string", "Title", "#i/" + data.hid);
              showCapture(data, "i");
            } else if (data.status === 'errored') {
              showError(data.reason);
            }
          },
          error: function(e) {
            $("button[name='check']").prop("disabled", false);
            $("input[name='url']").prop("disabled", false);
            return showError("Uh oh! we are experiencing server issues, try again later");
          },
          type: 'POST',
          cache: false,
          contentType: false,
          processData: false
        });
      });
    });
    AppRouter = Backbone.Router.extend({
      initialize: function() {
        this.route(/^(i|d)\/(.*)$/, "defaultRoute");
        return this.route(/^$/, "mainPageRoute");
      }
    });
    app_router = new AppRouter;
    app_router.on('route:mainPageRoute', function() {
      hideAll();
      return $("section.instructions").show();
    });
    app_router.on('route:defaultRoute', function(type, hid) {
      var process_path;
      process_path = function() {
        var data;
        data = {
          hid: hid
        };
        return $.ajax({
          url: '/u',
          dataType: 'json',
          data: data,
          success: function(data) {
            var _ref;
            if (((_ref = data.status) === 'processing' || _ref === 'queued') && type === 'i') {
              $("input[name='url']").val(data.url);
              if (data.status === 'processing') {
                showSpinner("Processing screenshot");
              } else if (data.status === 'queued' && data.queued_tasks > 0) {
                showSpinner("You are waiting behind " + data.queued_tasks + " other screenshots..");
              } else if (data.status === 'queued' && data.queued_tasks <= 0) {
                showSpinner("Generating screenshot");
              }
              setTimeout(process_path, 2000);
            } else if (data.status === 'processed') {
              showCapture(data, type);
            } else if (data.status === 'errored') {
              showError(data.reason);
            } else {
              showError("hmm. something bad happened");
            }
          },
          error: function(e) {
            showError("Uh oh! we are experiencing server issues, try again later");
          },
          type: 'GET'
        });
      };
      if (hid) {
        hideAll();
        $("input[type=radio]").prop("disabled", true);
        $("input[type=radio]").addClass("disabled");
        showSpinner("Processing");
        process_path();
      }
      return void 0;
    });
    Backbone.history.start();
  });

}).call(this);
