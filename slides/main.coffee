
top = null
mode = 'edit'
currentSlide = 0

slides = $('#slides')
slideshow = $('#slideshow')
codeViewer = $('#code-viewer')

$(window).on 'unload', ->
    viol.send('final_y_position', top || $('body').scrollTop());

$('body').on 'click', '.slide pre', ->
    code = $(this).text()
    showCode(code)
    
$('#code-viewer').on 'click', ->
    codeViewer.hide()

    if mode == 'edit'
        slides.show()
        $('body').scrollTop(top)
        top = null

$('body').on 'click', 'button.start', ->
    mode = 'slideshow'
    slides.hide()
    slideshow.show()
    showSlide(currentSlide)

    $(window).on 'keyup', (evt) ->
        code = evt.keyCode
        if code == 40
            goNextSlide()
        else if code == 38
            goPrevSlide()
        else if code == 27
            mode = 'edit'
            $(window).off('keyup')
            slideshow.hide()
            slides.show()

$('body').on 'click', 'div[demo] a', (evt) ->
    evt.preventDefault()
    viol.send('demo_path', $(this).attr('href'))

$('body').on 'click', 'div[demo] button', () ->
    div = $(this).parents('div[demo]')
    viol.send('run_demo', div.attr('demo'))

    window.open('http://localhost:8000', '_blank')
    
viol.on 'render_slides', (html) ->
    slides.empty()
    
    first = $('#first-slide').clone().attr('id', '').show()
    slides.append(first)
    
    slides.append(html)

    first.find('.slide-count').text(slides.find('div.slide').length - 1)
    first.find('.notes-count').text(slides.find('div.slide.notes').length - 1)

    index = 0
    slides.find('div.slide').each ->
        slide = $(this)
        if not slide.hasClass('notes')
            slide.attr('data-index', index)
            index++

viol.on 'demo_code', (code) ->
    showCode(code)

showCode = (code) ->
    codeViewer.show()

    pre = $('<pre></pre>')
    pre.text(code)
    codeViewer.empty().append(pre)

    if mode == 'edit'
        top = getTop()
        slides.hide()
    
getTop = ->
    return $('body').scrollTop()

goNextSlide = ->
    showSlide(currentSlide + 1)
        
goPrevSlide = ->
    showSlide(currentSlide - 1)
    
showSlide = (slideIndex) ->
    slide = slides.find('div.slide[data-index=' + slideIndex + ']')
    if slide.length != 0
        currentSlide = slideIndex
        slideshow.empty().append(slide.clone())
