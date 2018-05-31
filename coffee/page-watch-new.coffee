$(document).ready(() ->
    
  $("section.stats .header").click(() ->
    $header = $(this)
    # getting the next element
    $content = $header.next()
    # open up the content needed - toggle the slide- if visible, slide up, if not slidedown.
    $content.slideToggle(500, () ->
      # execute this after slideToggle is done
      # change text of header based on visibility of content div
      new_text = () ->
        if $content.is(":visible")
          return "Click to hide capture stats"
        else
          return "Captures below, click to show stats"
      $header.text(new_text)
      return
    )
    return
  )

  hideAll = () ->
    $(".subscribe-form .notification").hide()
    $("section.instructions").hide()
    $("section.spinner").hide()
    $("section.stats").hide()
    $("section.diffs").hide()
    $("section.url-status").hide()
    $("section.error").hide()
    $("section.subscribe").hide()
    $("section.screenshot").hide()
    $(".success-fade").show()


  showError = (msg) ->
    hideAll()
    $("footer").show()
    $("div.error-msg").text(msg)
    $("section.error").show()

  showSpinner = (msg) ->
    hideAll()
    $("footer").hide()
    $("div.spinner-msg").text(msg)
    $("section.spinner").show()


  showCapture = (data, type) ->
    # type is either "i" for a full display with stats and history
    # or "d" for a direct link where we don't show as much
    # clear all of the overlays
    $("div.overlay").html("")
    $("footer").show()
    hideAll()
    $("input[name='url']").val(data.url)
    if data.img == true
      $("#img-yes").prop('checked', true)
    else if data.img == false
      $("#img-no").prop('checked', true)

    # This is called when there is a new URL
    # added to the list to be monitored

    if type != "d"
      $("section.url-status div.url-status").html("""
          <h2>Monitoring this page for changes every #{data.interval},
          <br />last checked #{data.last_check}
          </h2>This page-watch will #{data.check_expiration}
      """)
      $("section.url-status").show()
      showSS(data)

    if data.prev_captures.length > 0
      showExistingCaptures(data)
    return

  showExistingCaptures = (data) ->
    showStats(data)
    showDiffs(data)

    $(".page-diffs").html("")

    for capture, i in data.prev_captures

      $('.page-diffs').append("""
        <div class="preview-wrapper">
          <h2>Change detected #{capture.created} <a href="#d/#{capture.hid}">[direct link]</a></h2>
          <div class="preview preview-left" id="preview-#{i}"> 
            <img src='#{capture.cap_highlight_small_url}' alt=''>
          </div>
          <div class="preview preview-right" id="preview-last-#{i}"> 
            <img src='#{capture.cap_last_highlight_small_url}' alt=''>
          </div>
          <div class="loader" id="loader-#{i}">loading preview</div>
        </div>
      """)

      $('div.overlay').append("""
          <div class="overlay-inner" id="preview-overlay-#{i}"></div>
          <div class="overlay-inner" id="preview-last-overlay-#{i}"></div>
      """)

      $("#preview-overlay-#{i}").zoom({
        url: "#{capture.cap_highlight_url}",
        target: $("#preview-overlay-#{i}").get(0),
        other_target: $("#preview-last-overlay-#{i}").get(0),
        other_url: "#{capture.cap_last_highlight_url}",
        $activate_target: $("#preview-#{i}"),
        $loader: $("#loader-#{i}"),
        on: "click",
      })

      $("#preview-last-overlay-#{i}").zoom({
        url: "#{capture.cap_last_highlight_url}",
        target: $("#preview-last-overlay-#{i}").get(0),
        other_target: $("#preview-overlay-#{i}").get(0),
        other_url: "#{capture.cap_highlight_url}",
        $activate_target: $("#preview-last-#{i}"),
        $loader: $("#loader-#{i}"),
        on: "click",
      })
    return

  showStats = (data) ->
    for attr in ["interval", "last_check", "last_change", "changes", "checks", "created"]
      console.log(attr)
      console.log(data[attr])
      $("section.stats .#{attr}").text(data[attr])
    $("section.stats .screenshot").html("""<a href="#{data.cap_url_small}">latest-screenshot</a>""")
    $("section.stats").show()
     
  showDiffs = (data) ->
    $("section.diffs").show()
  
  showSS = (data) ->

    $("div.screenshot").html("""
      <img src="#{data.cap_url_small}" alt="preview">
      <div class="loader" id="screenshot-loader">loading preview</div>
    """)
    $('div.overlay').append("""
      <div class="overlay-full" id="preview-overlay"></div>
    """)
    $("div.screenshot").zoom({
      url: "#{data.cap_url}",
      target: $("#preview-overlay").get(0),
      $activate_target: $("div.screenshot"),
      $loader: $("#screenshot-loader"),
      on: "click",
    })

    $('div.rss-icon').html("""
      <a href="/f/#{data.hid}.xml"><i class="fa fa-rss-square fa-5x rss-icon"></i></a>
    """)

    # Add a hid to the hidden input field
    $("input[name='hid']").val(data.hid)
    $("section.subscribe").show()
    $("section.subscribe div.rss").show()
    $("section.subscribe div.subscribe-form").show()

    $("section.screenshot").show()
    $("section.screenshot div.overlay-text").show()
    return

  $("#email-subscribe").submit((e) ->
    e.preventDefault()
    $("button[name='subscribe']").prop("disabled",true)
    $("input[name='email']").prop("disabled",true)
    if $("input[name='email']").val().length < 3
      $(".subscribe-form .notification").html("""
        <div class="info"><i class="fa fa-info-circle fa-2x"></i>Invalid email</div>
      """).fadeIn()
      return
    form_data = new FormData()
    form_data.append('hid', $("input[name='hid']").val())
    form_data.append('email', $("input[name='email']").val())
    $.ajax({
      url: '/s',
      dataType: 'json',
      data: form_data,
      success: (data) ->
        $("button[name='subscribe']").prop("disabled",false)
        $("input[name='email']").prop("disabled",false)
        hid = encodeURIComponent(data.hid)
        email = encodeURIComponent(data.email)
        if data.status == 'processed'
          $(".success-fade").fadeOut("fast", ()->
            $(".subscribe-form .notification").html("""
              <div class="success"><i class="fa fa-check fa-2x">
              </i>Change notifications for this page will be sent 
              to #{data.email} <a href="/s?hid=#{hid}&email=#{email}">unsubscribe</a></div>
            """).fadeIn()
          )
        else if data.status == 'info'
          $(".subscribe-form .notification").html("""
            <div class="info"><i class="fa fa-info-circle fa-2x"></i>#{data.reason}
            <a href="/s?hid=#{hid}&email=#{email}">unsubscribe</a></div>
          """).fadeIn()
        else if data.status == 'errored'
          $(".subscribe-form .notification").html("""
            <div class="error"><i class="fa fa-exclamation-triangle fa-2x"></i>#{data.reason}</div>
          """).fadeIn()
        else
          $(".subscribe-form .notification").html("""
            <div class="error"><i class="fa fa-exclamation-triangle fa-2x"></i>Unknown error :(</div>
          """).fadeIn()

      error: (e) ->
        $("button[name='subscribe']").prop("disabled",false)
        $("input[name='email']").prop("disabled",false)
        $(".subscribe-form .notification").html("""
          <div class="error"><i class="fa fa-exclamation-triangle fa-2x"></i>Server error, please try again later</div>
        """).fadeIn()
      type: 'POST',
      cache: false,
      contentType: false,
      processData: false
    })
    return
  )

  $("input[name=url]").focus(() ->
    $("input[type=radio]").removeClass("disabled")
    $("input[type=radio]").prop("disabled", false)
  )


  $("#check-url").submit((e) ->
    e.preventDefault()
    if $("input[name='url']").val().length < 3
      return
    $("section.instructions").fadeOut("fast", () ->

      hideAll()
      window.history.pushState("object or string", "Title", "")
      showSpinner("Processing")
      form_data = new FormData()
      form_data.append('url', $("input[name='url']").val())
      form_data.append('img', $('input[name=img]:checked').val())
      $("button[name=check]").prop("disabled",true)
      $("input[name=url]").prop("disabled",true)
      $("input[type=radio]").prop("disabled", true)
      $("input[type=radio]").addClass("disabled")
      $.ajax({
        url: '/c',
        dataType: 'json',
        data: form_data,
        success: (data) ->
          $("button[name='check']").prop("disabled",false)
          $("input[name='url']").prop("disabled",false)
          if data.status in ['queued', 'processing']
            window.location.href = "#i/#{data.hid}"
          else if data.status == 'processed'
            window.history.pushState("object or string", "Title", "#i/#{data.hid}")
            showCapture(data, "i")
          else if data.status == 'errored'
            showError(data.reason)
          return
        error: (e) ->
          $("button[name='check']").prop("disabled",false)
          $("input[name='url']").prop("disabled",false)
          showError("Uh oh! we are experiencing server issues, try again later")
        type: 'POST',
        cache: false,
        contentType: false,
        processData: false
      })

    )

    return
  )

  ##################### Start URL routes
  AppRouter = Backbone.Router.extend({
    initialize: () ->
      @route(/^(i|d)\/(.*)$/, "defaultRoute")
      @route(/^$/, "mainPageRoute")
  })

  app_router = new AppRouter
  app_router.on('route:mainPageRoute', () ->
    hideAll()
    $("section.instructions").show()
  )


  app_router.on('route:defaultRoute', (type, hid) ->
    process_path = ()->
      data = {
        hid: hid
      }
      $.ajax({
        url: '/u',
        dataType: 'json',
        data: data,
        success: (data) ->
          if data.status in ['processing', 'queued'] and type == 'i'
            $("input[name='url']").val(data.url)
            if data.status == 'processing'
              showSpinner("Processing screenshot")
            else if data.status == 'queued' and data.queued_tasks > 0
              showSpinner("You are waiting behind #{data.queued_tasks} other screenshots..")
            else if data.status == 'queued' and data.queued_tasks <= 0
              showSpinner("Generating screenshot")
            setTimeout(process_path, 2000)
          else if data.status == 'processed'
            showCapture(data, type)
          else if data.status == 'errored'
            showError(data.reason)
          else
            showError("hmm. something bad happened")
          return
        error: (e) ->
          showError("Uh oh! we are experiencing server issues, try again later")
          return
        type: 'GET',
      })

    if hid
      hideAll()
      $("input[type=radio]").prop("disabled", true)
      $("input[type=radio]").addClass("disabled")
      showSpinner("Processing")
      process_path()
    undefined
  )
  ##################### End URL routes
 
  # Using backbone just for routes
  Backbone.history.start()

  return
)
