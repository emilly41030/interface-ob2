;
(function ($) {

    $.fn.imageZoom = function (options) {  
 
     // The native width and height of the image.
    var native_width = 0,
        native_height = 0,
        current_width = 0,
        current_height = 0,
        $small = $(".small"),
        $large = $(".large");

    $(".magnify").mousemove(function (e) {       
      /* Act on the event */
        if (!native_width && !native_height) {           
         var image_object = new Image();
            image_object.src = $small.attr('src');  
                 
           // Gets the image native height and width.
            native_height = image_object.height;
            native_width = image_object.width;  
                     
           // Gets the image current height and width.
            current_height = $small.height();
            current_width = $small.width();

        } else {            
           
           // Gets .maginfy offset coordinates.
            var magnify_offset = $(this).offset(),               
           
            // Gets coordinates within .maginfy.
                mx = e.pageX - magnify_offset.left,
                my = e.pageY - magnify_offset.top;           
            
             // Checks the mouse within .maginfy or not.
            if (mx < $(this).width() && my < $(this).height() && mx > 0 && my > 0) {
                $large.fadeIn(100);
            } else {
                $large.fadeOut(100);
            } if ($large.is(":visible")) {                
             /* Gets the large image coordinate by ratio 
                   small.x / small.width = large.x / large.width
                   small.y / small.height = large.y / large.height
                   then we need to keep pointer in the centre, 
                   so deduct the half of .large width and height.
                */
                var rx = Math.round(mx / $small.width() * native_width - $large.width() / 2) * -1,
                    ry = Math.round(my / $small.height() * native_height - $large.height() / 2) * -1,
                    bgp = rx + "px " + ry + "px",
                    px = mx - $large.width() / 2,
                    py = my - $large.height() / 2;
                $large.css({
                    left: px,
                    top: py,
                    backgroundPosition: bgp
                });
            }

        }
    });
});