var system = require('system');


var host = "http://boxoffice.travis.dev:6500"; //presumably 127.0.0.1

casper.options.waitTimeout = 60000;
casper.options.stepTimeout = 60000;
// casper.options.logLevel = 'debug';
// casper.options.verbose = true;

// casper.on('resource.received', function(resource) {
//     casper.echo(resource.url);
// });


// Log remote console messages (useful for debugging)
// casper.on("remote.message", function(message) {
//   this.echo("remote console.log: " + message);
// });


items = {
    'conference': {
        'conference-ticket': {
            'add': 3,
            'subtract': 2,
            'discount': 0,
            'subtotal': 3500

        },
        'single-day': {
            'add': 2,
            'subtract': 6,
            'discount': 0,
            'subtotal': 0,
        },
    },
    'merchandise': {
        't-shirt': {
            'add': 6,
            'subtract': 1,
            'discount': 125,
            'subtotal': 2375,
        }
    }
};

total = 5875;


casper.test.begin('Order Workflow for Boxoffice', 9, function suite(test) {

    casper.start(host+'/testing', function() {
        test.assertHttpStatus(200, 'Boxoffice server is running');
    });
    
    casper.waitFor(function check() {
            return this.evaluate(function() {
                return document.querySelectorAll('#conference #conference-ticket .increment').length > 0;
            });
        }, function then() {
            test.assertVisible('.price', "Boxoffice widget is visible");
        }
    );

    casper.wait(500, function() {
        for (var itemCategory in items) {
            for (item in items[itemCategory]) {
                var add = items[itemCategory][item]['add'] || 0;
                var subtract = items[itemCategory][item]['subtract'] || 0;

                for (var i = 0; i < add; i++) {
                    casper.evaluate(function(itemCategory, item) {
                        document.querySelector("#"+itemCategory+" #"+item+" .increment").click();
                    }, itemCategory, item);
                }

                for (var i = 0; i < subtract; i++) {
                    casper.evaluate(function(itemCategory, item) {
                        document.querySelector("#"+itemCategory+" #"+item+" .decrement").click();
                    }, itemCategory, item);
                }
            }
        }
    });

    casper.wait(2000, function() {
        for (var itemCategory in items) {
            for (item in items[itemCategory]) {
                var discount = items[itemCategory][item]['discount'] || 0;
                var subtotal = items[itemCategory][item]['subtotal'] || 0;
                
                if (discount) {
                     test.assertEquals(casper.fetchText("#"+itemCategory+" #"+item+" .discount span"), " "+discount, "#"+itemCategory+" #"+item+" discount exists and is correct");
                } else {
                     test.assertEquals(casper.fetchText("#"+itemCategory+" #"+item+" .discount span"), "", "#"+itemCategory+" #"+item+" discount doesn't exist");
                }

                if (subtotal) {
                    test.assertEquals(casper.fetchText("#"+itemCategory+" #"+item+" .subtotal span"), " "+subtotal, "#"+itemCategory+" #"+item+" subtotal exists and is correct");
                } else {
                    test.assertEquals(casper.fetchText("#"+itemCategory+" #"+item+" .subtotal span"), "", "#"+itemCategory+" #"+item+" subtotal doesn't exist");
                }

            }
        }

        test.assertEquals(casper.fetchText(".price span"), " "+total, "Total is correct");
    });

    casper.run(function() {
        test.done();
    });
});
