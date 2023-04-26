

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
    var stripe = Stripe($("#payment-button").attr('data-stripe-secret'));
    // Set up Stripe.js and Elements to use in checkout form
    const options = {
        clientSecret: $("#payment-button").attr('data-client-secret'),
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
    
    stripe.confirmPayment({
        elements,
        redirect: 'if_required'
        // confirmParams:{
        //     //return_url: getOrderCompleteUrl(),
        // },
    }).then(function(result) {
                if (result.error) {
                // Show error to your customer (for example, insufficient funds)
                console.log(result.error.message);
                setLoading(false);
                } else {
                // The payment has been processed!
                if (result.paymentIntent.status === 'requires_capture') {
                    // Show a success message to your customer
                    // There's a risk of the customer closing the window before callback
                    // execution. Set up a webhook or plugin to listen for the
                    // payment_intent.succeeded event that handles any business critical
                    // post-payment actions.
                    $.ajax({
                        url : $("#payment-button").attr('data-order-status-url'),
                        type: 'POST',
                        data:{
                            'order_number': $("#payment-button").attr('data-order-number'),
                            'transaction_id': result.paymentIntent.id,
                            'csrfmiddlewaretoken': $("input[name='csrfmiddlewaretoken']").val()
                        },
                        success: function (response){
                            if (response.status != 'New')
                                setTimeout(()=> {window.location.href = getOrderCompleteUrl();}, 2000); 
                            window.location.href = getOrderCompleteUrl();		                                

                        },
                        error: function(response){
                            console.log(response);
                        }
                      })
                }
            }
        });
    });
});