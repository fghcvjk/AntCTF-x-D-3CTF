$('.name').on("change keyup paste",
  function(){
    if($(this).val()){
      $('.icon-paper-plane').addClass("next");
    } else {
      $('.icon-paper-plane').removeClass("next");
    }
  }
);

$('.next-button').hover(
  function(){
    $(this).css('cursor', 'pointer');
  }
);

$('.next-button.name').click(
  function(){
    $('.name-section').addClass("fold-up");
    $('.password-section').removeClass("folded");
  }
);

$('.password').on("change keyup paste",
  function(){
    if($(this).val()){
      $('.icon-lock').addClass("next");
    } else {
      $('.icon-lock').removeClass("next");
    }
  }
);

$('.next-button').hover(
  function(){
    $(this).css('cursor', 'pointer');
  }
);

$('.next-button.password').click(
  function(){
    $('.password-section').addClass("fold-up");
    $('.repeat-password-section').removeClass("folded");
  }
);

$('.repeat-password').on("change keyup paste",
  function(){
    if($(this).val() === $('.password').val()){
      $('.icon-repeat-lock').addClass("next");
    } else {
      $('.icon-repeat-lock').removeClass("next");
    }
  }
);

$('.next-button.repeat-password').click(
    function(){
        $('.fa-paper-plane').removeClass("fa-paper-plane").addClass("fa-spinner fa-spin");
        $.ajax({
            type: 'POST',
            url: '/love',
            data: {
                name: $('.name').val(),
                password: $('.password').val()
            },
            success: function(data) {
                if (data === "Success") {
                    $('.repeat-password-section').addClass("fold-up");
                    $('.success').css("marginTop", 0);
                } else {
                    alert(data);
                    location.reload();
                }
            },
            error: function() {
                alert('Internal Server Error');
                location.reload();
            }
        })
    }
);