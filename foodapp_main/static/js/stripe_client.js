

function getOrderCompleteUrl(){
    return window.location.protocol + "//"+ window.location.host+$("#payment-button").attr('data-order-complete-url')
    +'?order_no=' + $("#payment-button").attr('data-order-number') + '&transaction_id=' + $("#payment-button").attr('data-transaction-id')
}

$(document).ready(function(){
    // Show a spinner on payment submission
    function setLoading(isLoading) {
        if (isLoading) {
            // Disable the button and show a spinner
            $("#payment-button").disabled = true;
            $("#spinner").removeClass("hidden");
            $("#button-text").addClass("hidden");
        
        } else {
            $("#payment-button").disabled = false;
            $("#spinner").addClass("hidden");
            $("#button-text").removeClass("hidden");
        }
    }
    var stripe = Stripe();
    // Set up Stripe.js and Elements to use in checkout form
    const options = {
        clientSecret: $("#payment-button").attr('data-secret'),
        // Fully customizable with appearance API.
        appearance: { 
            theme: 'flat',
            variables: {
                colorBackground: '#ea8e39',
            },
        },
        loader : 'auto',
        };

    var elements = stripe.elements(options);
    var style = {
        base: {
            color: "#32325d",
        }
    };

    const paymentElement = 
        elements.create('payment', {
                        paymentMethodOrder: ['apple_pay', 'google_pay', 'card', 'klarna'],
                        layout: {
                            type: 'accordion',
                            defaultCollapsed: false
                        },
                });
    
    paymentElement.mount("#payment-element");


    var form = document.getElementById('payment-form');

    form.addEventListener('submit', function(ev) {
    ev.preventDefault();
    setLoading(true);
    console.log($("#payment-button").attr('data-cart-items'));
    stripe.confirmPayment({
        elements,
        confirmParams:{
            return_url: getOrderCompleteUrl(),
        },
    }).then(function(result) {
                if (result.error) {
                // Show error to your customer (for example, insufficient funds)
                console.log(result.error.message);
                setLoading(false);
                } else {
                // The payment has been processed!
                if (result.paymentIntent.status === 'succeeded') {
                    // Show a success message to your customer
                    // There's a risk of the customer closing the window before callback
                    // execution. Set up a webhook or plugin to listen for the
                    // payment_intent.succeeded event that handles any business critical
                    // post-payment actions.
                   

                    $.ajax({
                        url : $("#payment-button").attr('data-payment-url'),
                        type: 'POST',
                        data:{
                            'order_number': $("#payment-button").attr('data-order-number'),
                            'transaction_id': result.paymentIntent.id,
                            'status': result.paymentIntent.id,
                            'payment_method': payment_method,
                            'csrfmiddlewaretoken': $("input[name='csrfmiddlewaretoken']").value()
                        },
                        success: function (response){
                            console.log(response);
                            window.location.href = order_complete + '?order_no=' + response.order_number + '&transaction_id=' + response.transaction_id;		
                        }
                      })
                }
            }
        });
    });
});