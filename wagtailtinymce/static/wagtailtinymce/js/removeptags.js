$(function() {
    String.prototype.replaceAll = function(target, replacement) {
        return this.split(target).join(replacement)
    }

    $('textarea:contains(<p>)').each(function () {
      var $this = $(this)
      var textHtml = $this.val()
      textHtml = textHtml.replace(/<p>\s/g, '<p>')
      textHtml = textHtml.replaceAll('<br/>', '')
      textHtml = textHtml.replaceAll('<p></p>', '')
      $this.val(textHtml)
    })
})
