sendEditMessage = ->
    viol.send('edit', {
        input: $('textarea[name=input]').val(),
        regex: $('textarea[name=regex]').val()
    })

$(document).ready ->
    $('textarea').on 'change', ->
        sendEditMessage()

    $('textarea').on 'keyup', ->
        sendEditMessage()

    $('textarea[name=regex]').on 'keydown', (evt) ->
        # If tab, then force focus back to input textarea.
        if evt.keyCode == 9
            evt.preventDefault()
            $('textarea[name=input]').focus()
