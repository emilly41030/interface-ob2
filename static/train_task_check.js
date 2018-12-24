
var t1 = window.setInterval(()=>{
    $.ajax({
        type:'POST',
        url:'{{url_for("trainTask_post")}}',
        success:function(data){
            if(data=="0"){
                $('#train_nav').hide();
                clearInterval(t1);
            }                            
            else if(data=="1")
                $('#train_nav').show();
            
        },
    });
}, 1000);