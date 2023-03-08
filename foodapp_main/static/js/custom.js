let autocomplete;

function initAutoComplete(){
autocomplete = new google.maps.places.Autocomplete(
    document.getElementById('id_address'),
    {
        types: ['geocode', 'establishment'],
        //default in this app is "IN" - add your country code
        componentRestrictions: {'country': ['gb']},
    })
// function to specify what should happen when the prediction is clicked
autocomplete.addListener('place_changed', onPlaceChanged);
}

function onPlaceChanged (){
    var place = autocomplete.getPlace();

    // User did not select the prediction. Reset the input field or alert()
    if (!place.geometry){
        document.getElementById('id_address').placeholder = "Start typing...";
    }
    else{
        console.log(place)
       // console.log('place name=>', place.name)
    }
    // get the address components and assign them to the fields
    var geocoder = new google.maps.Geocoder();
    var address = document.getElementById('id_address').value;
    geocoder.geocode({'address' : address}, function(results, status){
        var latitude = results[0].geometry.location.lat();
        var longitude = results[0].geometry.location.lng();

        $('#id_latitude').val(latitude);
        $('#id_longitude').val(longitude);
        $('#id_address').val(address);

    });

    //loop through address and assign other address fields
    console.log(place.address_components)

    for(var i=0; i < place.address_components.length; i++){
        for(var j=0; j < place.address_components[i].types.length; j++){

            //get the country
            if (place.address_components[i].types[j] == 'country')
               $('#id_country').val(place.address_components[i].long_name);
            
            if (place.address_components[i].types[j] == 'locality')
               $('#id_city').val(place.address_components[i].long_name);
            
            if (place.address_components[i].types[j] == 'postal_code')
               $('#id_postcode').val(place.address_components[i].long_name);
            else
               $('#id_postcode').val('');

            //Get the state
            // if (place.address_components[i].types[j] == 'administrative_area_level_1')
            //    $('#id_country').val(place.address_components[i].long_name);
        }
    }
}


$(document).ready(function(){
    //Add to cart
  $(".add_to_cart").on('click', function(e){
    e.preventDefault();

    food_id = $(this).attr('data-id');
    food_url = $(this).attr('data-url');
    
    $.ajax({
        url: food_url,
        type: 'GET',
        success: function(response){
            if (response.status == 'login_required'){
                swal(response.message, "", "info").then(function(){
                    window.location = '/login';
                });
            }
            else if (response.status == 'Failed'){
                swal(response.message, "", "error");
            }
            else{
                $("#cart_counter").html(response.cart_counter['cart_count']);
                $("#lblqty-"+food_id).html(response.qty);
                
                
                //subtotal, tax and grand total
                applyCartAmounts(
                    response.cart_amount['tax'],
                    response.cart_amount['subtotal'],
                    response.cart_amount['grand_total']
                );
            }
        }
    });
  });

  $(".item_qty").each(function(){
    var id = $(this).attr('data-id');
    var qty = $(this).attr('data-qty');
    console.log(id)
    $('#'+id).html(qty);
});
  //Decrease the cart
  $(".decrease_cart").on('click', function(e){
        e.preventDefault();
        cart_id = $(this).attr('id');
        food_id = $(this).attr('data-id');
        food_url = $(this).attr('data-url');
        
        $.ajax({
            url: food_url,
            type: 'GET',
            success: function(response){
                if (response.status == 'login_required')
                    swal("HungryBuff", "Please login", "info").then(function(){
                        window.location='/login'
                    });
                else if(response.status == 'Failed')
                    swal(response.message, "", "error");
                else{
                    $("#cart_counter").html(response.cart_counter['cart_count']);
                    $("#lblqty-"+food_id).html(response.qty);
                   
                     //subtotal, tax and grand total
                    applyCartAmounts(
                        response.cart_amount['tax'],
                        response.cart_amount['subtotal'],
                        response.cart_amount['grand_total']
                    );
                    if (window.location.pathname == '/cart/'){
                        removeCartItem(cart_id, response.qty);
                        checkEmptyCart();
                    }
                }
            }
        });
    });

    //Delete cart item
    $(".delete_cartItem").on('click', function(e){
        e.preventDefault();
      
        cart_id = $(this).attr('data-id');
        food_url = $(this).attr('data-url');

        $.ajax({
            url: food_url,
            type: 'GET',
            success: function(response){
                 if(response.status == 'Failed')
                    swal(response.message, "", "error");
                else{
                    $("#cart_counter").html(response.cart_counter['cart_count']);
                    
                    swal(response.status, response.message, "success")
                     //subtotal, tax and grand total
                    applyCartAmounts(
                        response.cart_amount['tax'],
                        response.cart_amount['subtotal'],
                        response.cart_amount['grand_total']
                    );

                    if (window.location.pathname == '/cart/'){
                        removeCartItem(cart_id, 0);
                        checkEmptyCart();
                    }
                }
                
            }
        });
    });

    //delete cart element if the quantity is 0
    function removeCartItem(cartItemId, qty){
        

        if (qty == 0){
            //remove the cart item
            document.getElementById('cart-item-' + cartItemId).remove();
        }
    }

    function checkEmptyCart(){
        var cart_counter = document.getElementById('cart_counter').innerHTML;
        if (cart_counter == 0){
            document.getElementById('empty-cart').style.display = 'block';
        }
    }

    //Apply cart amounts
    function applyCartAmounts(tax, subtotal, grand_total){
        console.log(window.location.pathname);
        if (window.location.pathname == '/cart/'){
            $('#subtotal').html(subtotal);
            $('#tax').html(tax);
            $('#grandtotal').html(grand_total);
        }
    }

 //opening_hours.html
 $('.add_hour').on('click', function(e){
        e.preventDefault();
        
        var day = document.getElementById('id_day').value;
        var from_hour = document.getElementById('id_from_hour').value;
        var to_hour = document.getElementById('id_to_hour').value;
        var is_closed = document.getElementById('id_is_closed').checked;
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        var addOpeningHourUrl = $('#addOpeningHourUrl').val();
        
        if ((is_closed && day != '') || 
            (day != '' && from_hour != '' && to_hour != ''))
            $.ajax({
                type: 'POST',
                url: addOpeningHourUrl,
                data : { "day" : day, "from_hour" : from_hour, "to_hour" : to_hour, "is_closed" : is_closed, "csrfmiddlewaretoken" : csrf_token},
                success: function(result){
                    console.log(result);
                    if (result.status == 'Success'){
                        if (result.is_closed != 'Closed'){
                            html = '<tr id=\''+ result.id +'\'><td><b>'+ result.day+'</b></td><td>'+result.from_hour+' - '+ result.to_hour +'</td><td><a class=\'btn btn-danger deleteOpeningHours\' href="{% url \'deleteOpeningHours\' '+ result.id +' %}">Remove</a></td></tr>'
                        }
                        else{
                            html = '<tr id=\''+ result.id +'\'><td><b>'+ result.day+'</b></td><td>'+ result.is_closed +'</td><td><a class=\'btn btn-danger deleteOpeningHours\' href="{% url \'deleteOpeningHours\' '+ result.id+' %}">Remove</a></td></tr>'
                        }
                        $('.opening_hours').append(html);
                        document.getElementById("opening_hours").reset();
                    }
                    else{

                        swal(result.message, '', 'error');
                    }
                }

            });
        else
            swal('Please fill all the details','','info');

    });   

    $('.deleteOpeningHours').on('click', function(e){
        e.preventDefault();

        var url = $('#'+ e.target.id).attr('data-url');

        $.ajax({
            url : url,
            type : 'GET',
            success : function(response){
                if (response.status == 'Success')
                    $('#row-'+ e.target.id).remove();
            }
        })
    });
//document ready close
});