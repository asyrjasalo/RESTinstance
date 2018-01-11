module.exports.fetch_response = function(request, state, logger, callback) {

  if (typeof state.responses === "undefined") {
    state.responses = {};
  }

  if (state.responses[request.path]) {
    return callback(state.responses[request.path]);
  }

  var http = require("http");

  var path = request.path;
  if (Object.keys(request.query).length > 0) {
    const querystring = require("querystring");
    var path = path + '?' + querystring.stringify(request.query);
  }

  var options = {
    method: "get",
    hostname: "localhost",
    port: 8080,
    path: path,
  };

  var origin_request = http.request(options, response => {
    var body = "";
    response.setEncoding("utf8");
    response.on("data", chunk => {
      body += chunk;
    });
    response.on("end", function() {
      response.body = body;
      callback(response);
    });
  });

  origin_request.end();
}
