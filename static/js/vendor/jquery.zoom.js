/*!
	Zoom v1.7.13 - 2014-04-29
	Enlarge images on click or mouseover.
	(c) 2014 Jack Moore - http://www.jacklmoore.com/zoom
	license: http://www.opensource.org/licenses/mit-license.php
*/
(function ($) {

  var getPointerEvent = function(event) {
      return event.originalEvent.targetTouches ? event.originalEvent.targetTouches[0] : event;
  };

	var defaults = {
		url: false,
		callback: false,
		target: false,
		duration: 120,
		on: 'mouseover', // other options: grab, click, toggle
		touch: true, // enables a touch fallback
		onZoomIn: false,
		onZoomOut: false,
		magnify: 1
	};

	// Core Zoom Logic, independent of event listeners.
	$.zoom = function(target, other_target, source, img, other_img, magnify) {
		var targetHeight,
			targetWidth,
      othertargetHeight,
      othertargetWidth,
			sourceHeight,
			sourceWidth,
			xRatio,
			yRatio,
			offset,
			position = $(target).css('position'),
			$source = $(source);

		// The parent element needs positioning so that the zoomed element can be correctly positioned within.
		target.style.position = /(absolute|fixed)/.test(position) ? position : 'relative';
		target.style.overflow = 'hidden';
    if (other_target) {
      other_target.style.position = /(absolute|fixed)/.test(position) ? position : 'relative';
      other_target.style.overflow = 'hidden';
    }

		img.style.width = img.style.height = '';
		other_img.style.width = other_img.style.height = '';

		$(img)
			.addClass('zoomImg')
			.css({
				position: 'absolute',
				top: 0,
				left: 0,
				opacity: 0,
				width: img.width * magnify,
				height: img.height * magnify,
				border: 'none',
				maxWidth: 'none',
				maxHeight: 'none'
			})
			.appendTo(target);
    if (other_target) {
      $(other_img)
        .addClass('zoomImg')
        .css({
          position: 'absolute',
          top: 0,
          left: 0,
          opacity: 0,
          width: img.width * magnify,
          height: img.height * magnify,
          border: 'none',
          maxWidth: 'none',
          maxHeight: 'none'
        })
        .appendTo(other_target);
    }

		return {
			init: function() {
				targetWidth = $(target).outerWidth();
				targetHeight = $(target).outerHeight();

        if (other_target) {
          other_targetWidth = $(other_target).outerWidth();
          other_targetHeight = $(other_target).outerHeight();
        }

				if (source === target) {
					sourceWidth = targetWidth;
					sourceHeight = targetHeight;
				} else {
					sourceWidth = $source.outerWidth();
					sourceHeight = $source.outerHeight();
				}

				xRatio = (img.width - targetWidth) / sourceWidth;
				yRatio = (img.height - targetHeight) / sourceHeight;

        if (other_target) { 
          other_xRatio = (img.width - other_targetWidth) / sourceWidth;
          other_yRatio = (img.height - other_targetHeight) / sourceHeight;
        }

				offset = $source.offset();
			},
			move: function (e) {
				var left = (e.pageX - offset.left),
					top = (e.pageY - offset.top);

				top = Math.max(Math.min(top, sourceHeight), 0);
				left = Math.max(Math.min(left, sourceWidth), 0);

				img.style.left = (left * -xRatio) + 'px';
				other_img.style.left = (left * -xRatio) + 'px';
				img.style.top = (top * -yRatio) + 'px';
				other_img.style.top = (top * -yRatio) + 'px';
			}
		};
	};

	$.fn.zoom = function (options) {
		return this.each(function () {
			var
			settings = $.extend({}, defaults, options || {}),
			//target will display the zoomed image
			target = settings.target || this,
      other_target = settings.other_target || undefined,
			//source will provide zoom location info (thumbnail)
			source = this,
			$source = $(source),
      $activate_target = settings.$activate_target || $source,
      $loader = settings.$loader,
			img = document.createElement('img'),
			other_img = document.createElement('img'),
			$img = $(img),
			$other_img = $(other_img),
			mousemove = 'mousemove.zoom',
			clicked = false,
			touched = false,
			$urlElement,
      zoom,
      currX = 0,
      currY = 0,
      cachedX = 0,
      cachedY = 0;

 
			// If a url wasn't specified, look for an image element.
			if (!settings.url) {
				$urlElement = $source.find('img');
				if ($urlElement[0]) {
					settings.url = $urlElement.data('src') || $urlElement.attr('src');
				}
				if (!settings.url) {
					return;
				}
			}

			(function(){
				var position = target.style.position;
				var overflow = target.style.overflow;

        if (other_target) {
          var other_position = other_target.style.position;
          var other_overflow = other_target.style.overflow;
        }

				$source.one('zoom.destroy', function(){
					$source.off(".zoom");
					target.style.position = position;
					target.style.overflow = overflow;
          if (other_img) {
            other_target.style.position = position;
            other_target.style.overflow = overflow;
					  $other_img.remove();
          }
					$img.remove();
				});
				
			}());

      function start(e) {
        
        img.src = settings.url;
        if (settings.other_url) {
          other_img.src = settings.other_url;
        } else {
          other_img.src = img.src;
        }
        $loader.show();
        $(other_img).one('load', function() {
          $(img).one('load', function () {
            $loader.hide();
            $(".overlay-text").hide();
            zoom = $.zoom(target, other_target, source, img, other_img, settings.magnify);

           $(".overlay").on(mousemove, zoom.move);
            $(".overlay").one('click.zoom',
              function () {
                stop();
                clicked = false;
                $(document).off(mousemove, zoom.move);
              }
            );

            $(".overlay")
              .on('touchstart.zoom', function (e) {
                e.preventDefault();
                touched = true;
                var pointer = getPointerEvent(e);
                // caching the current x
                cachedX = currX = pointer.pageX;
                // caching the current y
                cachedY = currY = pointer.pageY;
                setTimeout(function (){
                  if (!touched) {
                    stop();
                    clicked = false;
                  }
                },200);
              })
              .on('touchmove.zoom', function (e) {
                var pointer = getPointerEvent(e);
                currX = pointer.pageX;
                currY = pointer.pageY;
                e.preventDefault();
                zoom.move(pointer);
              }) 
              .on('touchend mouseup touchcancel',function (e){
                e.preventDefault();
                // here we can consider finished the touch event
                touched = false;
              });

            $(target).show();

            if (other_target) {
              $(other_target).show();
            }
            $(".fade").css({ top: $(window).scrollTop() });
            $(".fade").show();
            $(".overlay").css({ top: $(window).scrollTop() + Math.round(.10 * $(window).height()) });
            $(".overlay").show();
            $("body").css("overflow", "hidden");
            zoom.init();
            zoom.move(e);

            // Skip the fade-in for IE8 and lower since it chokes on fading-in
            // and changing position based on mousemovement at the same time.
            $img.stop()
            .fadeTo($.support.opacity ? settings.duration : 0, 1, $.isFunction(settings.onZoomIn) ? settings.onZoomIn.call(img) : false);

            $other_img.stop()
            .fadeTo($.support.opacity ? settings.duration : 0, 1, $.isFunction(settings.onZoomIn) ? settings.onZoomIn.call(other_img) : false);
          }).each(function() { if(this.complete) $(this).load(); });
        }).each(function() { if(this.complete) $(this).load(); });
      }

      function stop() {
        $(".overlay").hide();
        $(".fade").hide();
        $("body").css("overflow", "auto");
        $(target).hide();
        if (other_target) {
          $(other_target).hide();
        }
        $img.stop()
        .fadeTo(settings.duration, 0, $.isFunction(settings.onZoomOut) ? settings.onZoomOut.call(img) : false);
        $other_img.stop()
        .fadeTo(settings.duration, 0, $.isFunction(settings.onZoomOut) ? settings.onZoomOut.call(other_img) : false);
        $(".overlay-text").show();
      }

      $activate_target.on('click.zoom',
        function (e) {
          if (clicked) {
            // bubble the event up to the document to trigger the unbind.
            return;
          } else {
            clicked = true;
            start(e);
            return false;
          }
        }
      );

     
      if ($.isFunction(settings.callback)) {
        settings.callback.call(img);
      }
		});
	};

	$.fn.zoom.defaults = defaults;
}(window.jQuery));
