function loadXMLDoc() {
    var cur_pwd = $('#cur_pwd').val(),
      new_pwd = $('#new_pwd').val(),
      confirm_pwd = $('#confirm_pwd').val();
    if(confirm_pwd !== new_pwd) {
      document.getElementById("message").innerHTML="Passwords don't match"
    }
    $.ajax({
      url: '/settings/change/',
      type: 'POST',
      data: { cur_pwd: cur_pwd, new_pwd: new_pwd }
    })
    .done(function( msg ) {
      console.log(msg);
      console.log(msg.message)
      document.getElementById("message").innerHTML=msg.message
    });
  }
$( document ).ready(function() {
    function csrfSafeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
      crossDomain: false, // obviates need for sameOrigin test
      beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type)) {
          xhr.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'));
        }
      }
    });
});
$(function(){
        $('#invitation').click(function(e){

          var email=$('#find_friend').val();
          var filter = /^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/;
          var re = /^([\w-]+(?:\.[\w-]+)*)@((?:[\w-]+\.)*\w[\w-]{0,66})\.([a-z]{2,6}(?:\.[a-z]{2})?)$/i;


          if (!re.test(email)) {
            $("#message1").dialog({ autoOpen: true ,resizable: false,draggable: false ,modal: true ,height: 200,width: 500,buttons: [ { text: "Ok", click: function() { $( this ).dialog( "close" ); } } ] }
);
            ChangeMessage1("Please provide a valid email address")
            email.focus;
            }
            else
            {
              $.ajax({
              type : 'POST',
              url: "/invite_friends/",
              data:{ email: email}

          })
         .done(function( msg ) {
            $("#message1").dialog({ autoOpen: true ,resizable: false,draggable: false ,modal: true ,height: 200,width: 500,buttons: [ { text: "Ok", click: function() { $( this ).dialog( "close" ); } } ] }
);          ChangeMessage1(msg)
            //alert(msg)
            console.log(msg);
            });
          }
        });
      });
            

 $(function(){
    $('#find_friend').autoComplete({
        minChars: 1,
         source: function( request, response ) {

          $.ajax({
              dataType: "json",
              type : 'POST',
              url: "/find_friend/",
            success: function(data) {
                console.log(data)
                console.log('success')
                response(data)  
                },
            error: function(data) {
                console.log("error")
            }
          });
        },
        
  });
  });
$(function(){
       $("#dialog").dialog({ autoOpen: false });
      $("#message1").dialog({ autoOpen: false });
 
        $("#Friends").click(
            function () {
              $("#dialog").dialog({ autoOpen: true ,resizable: false,draggable: false ,modal: true ,height: 500,width: 500,buttons: [ { text: "Ok", click: function() { $( this ).dialog( "close" ); } } ] }
);
              $.ajax({
                url: '/friend_list/',
              beforeSend: function () {
                ChangeMessage("<div class='loadcomment'><img src='/static/img/loading.gif'></div>");
               },
              success: function (data) {
                ChangeMessage(data)
                console.log(data)
              }
            });
                
                return false;
            });



       });
function ChangeMessage(Message) {           
            $("#dialog").html(Message);
        }
            
function ChangeMessage1(Message) {           
            $("#message1").html(Message);
        }
