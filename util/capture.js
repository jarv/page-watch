var args = require('system').args;
var page = require('webpage').create();
page.viewportSize = {width: 1280, height: 800};
page.settings.userAgent = 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36';

page.onResourceError = function(resourceError) {
    page.reason = resourceError.errorString;
    page.reason_url = resourceError.url;
};

if (args[3] === '--no-img') {
    console.log("skipping images");
    page.onResourceRequested = function(requestData, request) {
        if ((/https?:\/\/.+?\.(png|gif|jpeg|jpg|webp|tiff|bmp|rif|exif|svg)$/gi).test(requestData['url'])) {
            request.abort();
        }
    };
}

page.open(args[1], function (status) {
    console.log("opening " + args[1]);
    console.log("open complete");
    if (status !== 'success') {
        console.log('Unable to load, status: ' + status);
        console.log('  url:    ' + page.reason_url);
        console.log('  reason: ' + page.reason);
        phantom.exit();
    } else {
        window.setTimeout(function () {
            console.log("page.render");
            page.render(args[2]);
            phantom.exit();
        }, 2000);
    }
});
