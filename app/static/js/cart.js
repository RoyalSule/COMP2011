$(document).ready(function () {
    var csrf_token = $('meta[name=csrf-token]').attr('content');

    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrf_token);
            }
        }
    });

    $(".add-to-cart-button").on("click", function () {
        var clicked_obj = $(this);
        console.log(clicked_obj)

        var product_id = clicked_obj.attr('product-id');
        var quantity = 1

        $.ajax({
            url: '/add_to_cart',
            type: 'POST',
            data: JSON.stringify({ product_id: product_id, quantity: quantity}),
            contentType: "application/json; charset=utf-8", 
            dataType: "json",  
            success: function (response) {
                console.log(response);

                if (response.message) {
                    alert(response.message);  
                } else if (response.error) {
                    alert(response.error);  
                }
            },
            error: function (error) {
                console.log(error);
            }
        });
    });
});

