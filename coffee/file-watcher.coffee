$(document).ready(() ->
  
  hideAll = () ->
    $(".spinner-wrapper").hide()
    $(".info-wrapper").hide()
    $(".notification-wrapper").hide()
    $(".error-wrapper").hide()

  showSpinner = () ->
    $(".spinner-wrapper").show()
    $(".info-wrapper").hide()
    $(".notification-wrapper").hide()
    $(".error-wrapper").hide()

  showError = () ->
    $(".spinner-wrapper").hide()
    $(".info-wrapper").hide()
    $(".notification-wrapper").hide()
    $(".error-wrapper").show()

  showInfo = () ->
    $(".spinner-wrapper").hide()
    $(".info-wrapper").show()
    $(".notification-wrapper").show()
    $(".error-wrapper").hide()

  updateInfo = (data) ->
    $('.info-wrapper .info').html("""
      <ul class="rounded-border">
        <li class="path"><a href="#{data.location}">#{data.gh_path.substr(1)}</a></li>
        <li class="updated">last checked on #{data.updated}</li>
        <li class="avatar"><img src="#{data.commit_avatar_url}" alt="#{data.user}" /></li>
        <li class="commit"><a href="#{data.html_url}">#{data.sha}</a></li>
        <li class="commit-msg">#{data.commit_msg}</li>
      </ul>
      """)
    showInfo()

  $("#watcher-submit").submit((e) ->
    app_router.navigate(null, { trigger: true })
    $('.info-wrapper .info').html("")
    form_data = new FormData()
    form_data.append('url', $("input.web-url").val())
    parser = document.createElement('a')
    parser.href = $("input.web-url").val()
    form_data.append('gh_path', parser.pathname)

    $.ajax({
      url: '/g',
      dataType: 'json',
      data: form_data,
      #data: $('form#watcher-submit').serialize(),
      success: (data) ->
        if data.status == 'processing'
          showSpinner()
          console.log("got processing")
          app_router.navigate(data.gh_path, { trigger: true })
        else if data.status == 'processed'
          updateInfo(data)
        else if data.status == 'errored'
          $(".error-message").html(data.reason)
          showError()
        undefined
      error: (e) ->
        console.log('error')
        console.log(e)
      type: 'POST',
      cache: false,
      contentType: false,
      processData: false
    })
    false
  )

  AppRouter = Backbone.Router.extend({
    routes: {
      "*actions": "defaultRoute"
    }
  })

  app_router = new AppRouter
    
  app_router.on('route:defaultRoute', (path) ->
    process_path = ()->
      data = {
        gh_path: path,
      }
      $.ajax({
        url: '/g',
        dataType: 'json',
        data: data,
        success: (data) ->
          if data.status == 'processing'
            showSpinner()
            setTimeout(process_path, 500)
          else if data.status == 'processed'
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
    if path
      console.log("fetching " + path)
      process_path()
    undefined
  )
 
  Backbone.history.start()

  undefined
)
