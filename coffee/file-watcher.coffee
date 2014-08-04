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
        <li class="path"><a href="#{data.location}">#{data.path}</a></li>
        <li class="updated">last checked on #{data.updated}</li>
        <li class="avatar"><img src="#{data.commit_avatar_url}" alt="#{data.user}" /></li>
        <li class="commit"><a href="#{data.html_url}">#{data.sha}</a></li>
        <li class="commit-msg">#{data.commit_msg}</li>
      </ul>
      """)
    showInfo()

  process_status = ()->
    $.ajax({
      url: 'http://localhost/g',
      dataType: 'json',
      data: $('form#watcher-submit').serialize(),
      success: (data) ->
        if data.status == 'processing'
          showSpinner()
          setTimeout(process_status, 500)
        else if data.status == 'processed'
          updateInfo(data)
        else if data.status == 'errored'
          $(".error-message").html(data.reason)
          showError()
        undefined
      error: (e) ->
        console.log('error')
        console.log(e)
      type: 'GET',
    })
  $("#watcher-submit").submit((e) ->
    $('.info-wrapper .info').html("")
    $.ajax({
      url: 'http://localhost/g',
      dataType: 'json',
      data: $('form#watcher-submit').serialize(),
      success: (data) ->
        if data.status == 'processing'
          showSpinner()
          setTimeout(process_status, 500)
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
    })
    false
  )
  undefined
)
