$(document).ready(() ->

  formattedDate = (date_created) ->
    date = new Date(date_created)
    hours = date.getHours()
    minutes = date.getMinutes()
    seconds = date.getSeconds()
    year = date.getFullYear()
    month = date.getMonth() + 1
    day = date.getDate()
    formattedTime = year + '-' + pad(month,2) + '-' + pad(day,2) + ' ' + pad(hours,2) + ':' + pad(minutes,2)
    return formattedTime

  pluralize = (num) ->
    if num > 1
      return "s"
    else
      return ""

  formattedDelta = (date_created) ->
    fDelta = ""

    date = new Date(date_created)
    today = new Date()
    delta = Math.abs(today - date) / 1000

    days = Math.floor(delta / 86400)
    delta -= days * 86400
    if days
      fDelta += "#{days} day#{pluralize days} "

    hours = Math.floor(delta / 3600) % 24
    delta -= hours * 3600
  
    if hours
      fDelta += "#{hours} hour#{pluralize hours} "

    minutes = Math.floor(delta / 60) % 60
    delta -= minutes * 60
    
    if minutes
      fDelta += "#{minutes} minute#{pluralize minutes} "

    seconds = Math.floor(delta)

    if seconds
      fDelta += "#{seconds} second#{pluralize seconds} "

    return fDelta

  elemEnable = (enable=true) ->

    for elem in [
                  $("button[name='notification-button']"),
                  $("input[name='subscribe_email']"),
                  $("label[name='interval']"),
                  $("input[name='url']"),
                  $("button[name='url-button']")]
      if enable
        elem.prop("disabled", false)
        elem.css({'background-color' : ''})
      else
        elem.prop("disabled", true)
        elem.css({'background-color' : '#cfd8d4'})


  pad = (n) ->
    return String("0" + n).slice(-2)

  hideAll = () ->
    $(".fetch-loader").hide()
    $(".error-wrapper").hide()

  showSpinner = () ->
    $("#preview-zoom").html('')
    $(".diff-wrapper").html('')
    $(".overlay").html('')
    $(".screenshot-msg").hide()

    $(".fetch-loader").show()
    $(".diff-wrapper").hide()
    $(".error-wrapper").hide()

    $(".previews").removeClass("enable-preview")
    $(".previews").addClass("disable-preview")

    elemEnable(false)

    for stat in [$("#checks"), $("#last_check"), $("#changes"), $("#last_change"), $("#checks_remaining"), $("#sponsor")]
      stat.html('<img src="imgs/stats-spinner.gif" />')

  showError = () ->
    $(".fetch-loader").hide()
    $(".error-wrapper").show()
    $("input.subscribe-email").val('')
    for stat in [$("#checks"), $("#last_check"), $("#changes"), $("#last_change"), $("#checks_remaining"), $("#sponsor")]
      stat.html('- - - - ')
    elemEnable()
    $("input[name='subscribe_email']").prop("disabled", true)
    $("input[name='subscribe_email']").css({'background-color' : '#cfd8d4'})
    $("button[name='notification-button']").prop("disabled", true)
    $("button[name='notification-button']").css({'background-color' : '#cfd8d4'})

  showInfo = () ->
    $(".screenshot-msg").hide()
    $(".fetch-loader").hide()
    $(".diff-wrapper").show()
    $(".error-wrapper").hide()
    $(".previews").addClass("enable-preview")
    $(".previews").removeClass("disable-preview")

    elemEnable()

  showPreview = (data) ->

    feed_url = encodeURIComponent("http://page-watch.com/f#{data.url}.xml")
    $('.email-rss-wrapper .rss-icon').html("""
      <a href="/f/#{data.hid}.xml"><i class="fa fa-rss-square fa-5x rss-icon"></i></a>
    """)

    $('#preview-zoom').append("""
      <img class='magniflier' src='#{data.cap_url_small}' alt=''>
      <div class="loader" id="loader">loading preview</div>
    """)

    $('.overlay').append("""
        <div class="overlay-full" id="preview-overlay"></div>
    """)

    $("#preview-zoom").zoom({
      url: "#{data.cap_url}",
      target: $("#preview-overlay").get(0),
      $activate_target: $("#preview-zoom"),
      $loader: $("#loader"),
      on: "click",
    })

    $("#checks").html(data.checks)
    $("#last_check").html(formattedDelta(data.last_check))
    $("#changes").html(data.changes)
    $("#last_change").html(formattedDelta(data.last_change))
    if data.unlimited
      $("#checks_remaining").html("&infin;")
      $("#sponsor").html("page-watch.com")
    else
      $("#checks_remaining").html(data.checks_remaining)
      $("#sponsor").html(data.sponsor)
  
  
  
 
  updateInfo = (data) ->

    for capture,i in data.prev_captures
      fdate = formattedDate(capture.created)
      fdelta = formattedDelta(capture.created)

      $('.diff-wrapper').append("""
        <div class="preview-wrapper">
          <div class="preview-header">Change detected on #{fdate} (#{fdelta} ago) <a href="#/#{capture.interval}/#{capture.hid}">[direct link]</a></div>
          <div class="previews" id="preview-#{i}"> 
            <img class="magniflier" src='#{capture.cap_highlight_small_url}' alt=''>
            <div class="loader" id="loader-#{i}">loading preview</div>
          </div>
          <div class="previews" id="preview-last-#{i}"> 
            <img class="magniflier" src='#{capture.cap_last_highlight_small_url}' alt=''>
            <div class="loader" id="loader-last-#{i}">loading preview</div>
          </div>
        </div>
      """)
      $('.overlay').append("""
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
        $other_loader: $("#loader-last-#{i}"),
        on: "click",
      })

      $("#preview-last-overlay-#{i}").zoom({
        url: "#{capture.cap_last_highlight_url}",
        target: $("#preview-last-overlay-#{i}").get(0),
        other_target: $("#preview-overlay-#{i}").get(0),
        other_url: "#{capture.cap_highlight_url}",
        $activate_target: $("#preview-last-#{i}"),
        $loader: $("#loader-last-#{i}"),
        $other_loader: $("#loader-#{i}"),
        on: "click",
      })

      # $("#preview-last-#{i}").zoom({url: "#{capture.cap_last_highlight_url}"})


    showInfo()

  $("#watcher-submit").submit((e) ->
    window.history.pushState("object or string", "Title", window.location.href.split('#')[0])
    showSpinner()
    app_router.navigate(null, { trigger: true })
    form_data = new FormData()
    form_data.append('url', $("input.web-url").val())
    form_data.append('subscribe_email', $("input.subscribe-email").val())
    form_data.append('interval', $('input[name=interval]:checked', '#watcher-submit').val())
    $.ajax({
      url: '/c',
      dataType: 'json',
      data: form_data,
      success: (data) ->
        if data.status == 'queued'
          app_router.navigate(data.interval + '/' + data.hid, { trigger: true })
        else if data.status == 'processed'
          showPreview(data)
          updateInfo(data)
          window.history.pushState("object or string", "Title", "#/" + data.interval + '/' + data.hid)
        else if data.status == 'errored'
          $(".error-message").html(data.reason)
          showError()
        undefined
      error: (e) ->
        $(".error-message").html("Uh oh! we are experiencing server issues, try again later")
        showError()
      type: 'POST',
      cache: false,
      contentType: false,
      processData: false
    })
    false
  )

  AppRouter = Backbone.Router.extend({
    initialize: () ->
      @route(/^(h|d|w)\/(.*)$/, "defaultRoute")
  })

  app_router = new AppRouter

  app_router.on('route:defaultRoute', (interval, hid) ->
    process_path = ()->
      data = {
        interval: interval,
        hid: hid
      }
      $.ajax({
        url: '/u',
        dataType: 'json',
        data: data,
        success: (data) ->
          if data.status in ['processing', 'queued']
            $("input.web-url").val(data.url)
            showSpinner()
            q_msg = ""
            console.log(data.queued_tasks)
            if data.status == 'processing'
              q_msg = """
                <br />
                <span class="screenshot-queue"> Processing screenshot
                </span>
                """
            else if data.status == 'queued' and data.queued_tasks > 0
              q_msg = """
                <br />
                <span class="screenshot-queue">
                  You are waiting behind <b>#{data.queued_tasks}</b> other screenshots..
                </span>
                """
            else if data.status == 'queued' and data.queued_tasks <= 0
              q_msg = """
                <br />
                <span class="screenshot-queue">
                  Generating screenshot
                </span>
                """
            $('.spinner-message').html("Fetching information for this URL#{q_msg}")
            setTimeout(process_path, 2000)
          else if data.status == 'processed'
            $("input.web-url").val(data.url)
            showPreview(data)
            updateInfo(data)
          else if data.status == 'errored'
            $(".error-message").html(data.reason)
            showError()
          undefined
        error: (e) ->
          $(".error-message").html("Uh oh! we are experiencing server issues, try again later")
          showError()
        type: 'GET',
      })
    if interval and hid
      showSpinner()
      process_path()
    undefined
  )

  $("input.web-url").keydown(() ->
    window.history.pushState("object or string", "Title", window.location.href.split('#')[0])
  )

  $("input[name=interval]:radio").change(() ->
    interval = $('input[name=interval]:checked', '#watcher-submit').val()
    hid = new RegExp('[h|d|w]/(.*)').exec(window.location.href.split('#')[1])[1]
    app_router.navigate(interval + '/' + hid, { trigger: true })
  )

  Backbone.history.start()
  undefined
)
